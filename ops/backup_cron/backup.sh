#!/usr/bin/env bash
set -euo pipefail

required_vars=(
  BACKUP_DATABASE_URL
  AWS_ACCESS_KEY_ID
  AWS_SECRET_ACCESS_KEY
  AWS_S3_BUCKET
  AWS_S3_REGION
  AWS_S3_ENDPOINT
)

missing=()
for v in "${required_vars[@]}"; do
  if [[ -z "${!v:-}" ]]; then
    missing+=("$v")
  fi
done
if ((${#missing[@]})); then
  printf 'Missing required env vars: %s\n' "${missing[*]}" >&2
  exit 2
fi

# Avoid AWS CLI trying IMDS in container environments.
export AWS_EC2_METADATA_DISABLED=true

prefix="${BUCKET_SUBFOLDER:-}"
if [[ -n "$prefix" && "${prefix: -1}" != "/" ]]; then
  prefix="${prefix}/"
fi

ts="$(date -u +%Y%m%dT%H%M%SZ)"
file_prefix="${BACKUP_FILE_PREFIX:-backup-}"
filename="${file_prefix}${ts}.dump"
s3_key="${prefix}${filename}"

tmp="$(mktemp -t pgdump.XXXXXX)"
cleanup() {
  rm -f "$tmp"
}
trap cleanup EXIT

echo "Waiting for database to accept connections..."
pg_isready --timeout=30 --dbname="$BACKUP_DATABASE_URL" >/dev/null

echo "Creating pg_dump (custom format)..."
pg_dump \
  --format=custom \
  --no-owner \
  --no-acl \
  ${BACKUP_OPTIONS:-} \
  --file "$tmp" \
  "$BACKUP_DATABASE_URL"

# Force path-style addressing; required for many S3-compatible providers (including R2).
aws configure set default.region "$AWS_S3_REGION" >/dev/null
aws configure set default.s3.addressing_style path >/dev/null

echo "Uploading to s3://${AWS_S3_BUCKET}/${s3_key}"
aws --endpoint-url "$AWS_S3_ENDPOINT" s3 cp "$tmp" "s3://${AWS_S3_BUCKET}/${s3_key}" >/dev/null

echo "Backup uploaded OK"

