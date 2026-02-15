# Subscription test plan (Postgres)

## Infra
- Start Postgres for tests via `docker-compose -f docker-compose.test.yml up -d db`.
- Tests use `DATABASE_URL` (default `postgresql://postgres:postgres@localhost:5432/smokerfit_test`).
- Schema is created by `init_db()`; tables truncated between tests in `tests/conftest.py`.

## User journeys to cover
- New checkout
  - No existing subscription: creates pending payment with correct amount/plan metadata and receipt email required.
  - Promo applied: overrides amount/description/metadata; stored price matches promo cents.
  - Re-use pending: second `/subscribe` returns same pending payment/url when params match.
- Activation of initial payment (`check_and_activate`)
  - Succeeded payment without prior sub: status `active`, `current_period_end` = now + plan, `next_charge_at` = cpe - 1 day, amount/currency saved.
  - Renewal while active (not cancelled): extends from existing `current_period_end` (not from now), keeps plan, updates amount/currency.
  - Renewal while status=cancelled but cpe in future: reactivates, extends from existing `current_period_end`, preserves payment_method_id when saved.
  - Idempotency: repeated `check_and_activate` on same payment does not double-extend or duplicate side effects.
  - Failed/pending payment paths: statuses recorded, no subscription mutation.
- Cancel flow
  - `cancel_subscription` flips status to cancelled without clearing cpe; `is_active(include_cancelled=False)` blocks new checkout; `include_cancelled=True` still treats as active for paywall.
- Recurring charge (`charge_recurring`)
  - Skips when not due (`next_charge_at` in future) or missing payment_method_id/status not active.
  - Success: extends from current `current_period_end` by plan months, sets `next_charge_at = new_cpe - 1 day`, resets retries/precharge_notified.
  - Pending payment already exists: skips and returns pending.
  - Failure with retries < 2: increments `retry_attempts`, moves `next_charge_at` +1 day.
  - Failure with retries >= 2: sets status cancelled, `next_charge_at=None`; notifier called with last-attempt payload.
  - Idempotent apply: if `mark_payment_applied` already ran, no double extension.
- Precharge notifications (`send_precharge_notifications`)
  - Sends once when `next_charge_at` within 24h, `retry_attempts=0`, `precharge_notified=False`, status active.
  - Does not send when retries>0, already notified, or status not active.
- Paywall/form flow
  - Free workout allowed once; subsequent request with inactive subscription triggers plan choice; promo prompt appears when promocodes exist.
  - Active or cancelled-with-future-cpe keeps access via `is_active` default path.

## Edge conditions
- Timezone parsing: `current_period_end`/`next_charge_at` stored as aware datetimes; string inputs parse correctly.
- Plan normalization: invalid plan in metadata is treated as month.
- Multiple pending payments: `cancel_other_pendings` leaves only the current payment pending.
