# tools/json_to_sql.py
import json, hashlib
from pathlib import Path

def q(s: str) -> str:
    if s is None:
        return "NULL"
    return "'" + str(s).replace("'", "''") + "'"

def arr(a):
    if not a:
        return "ARRAY[]::text[]"
    return "ARRAY[" + ",".join(q(x) for x in a) + "]::text[]"

def jsonb_literal(obj) -> str:
    j = json.dumps(obj, ensure_ascii=False)
    tag = "json"
    i = 0
    while f"${tag}$" in j:
        i += 1
        tag = f"json{i}"
    return f"${tag}${j}${tag}$::jsonb"

DDL = """-- Generated SQL to seed 'exercises' table (DDL + UPSERTs)
SET client_encoding = 'UTF8';

DROP TABLE exercises;

CREATE TABLE IF NOT EXISTS exercises (
  name                TEXT PRIMARY KEY,
  levels              TEXT[],
  equipment           TEXT[],
  equipment_dnf       JSONB,
  allowed_limitations TEXT[],
  muscle_group        TEXT NOT NULL,
  reps_note           TEXT,
  video_url           TEXT
);

BEGIN;
"""

UPSERT_TMPL = """INSERT INTO exercises
(name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
VALUES ({name}, {levels}, {equipment}, {equipment_dnf}, {allowed_limitations}, {muscle_group}, {reps_note}, {video_url})
ON CONFLICT (name) DO UPDATE SET
  levels              = EXCLUDED.levels,
  equipment           = EXCLUDED.equipment,
  equipment_dnf       = EXCLUDED.equipment_dnf,
  allowed_limitations = EXCLUDED.allowed_limitations,
  muscle_group        = EXCLUDED.muscle_group,
  reps_note           = EXCLUDED.reps_note,
  video_url           = EXCLUDED.video_url;
"""

FOOTER = "COMMIT;\n"

def build_sql(json_path: str, out_path: str):
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("JSON root must be a list")

    stmts = [DDL]
    for item in data:
        stmts.append(UPSERT_TMPL.format(
            name=q(item["name"]),
            levels=arr(item.get("levels") or []),
            equipment=arr(item.get("equipment") or []),
            equipment_dnf=jsonb_literal(item.get("equipment_dnf") or []),
            allowed_limitations=arr(item.get("allowed_limitations") or []),
            muscle_group=q(item["muscle_group"]),
            reps_note=q(item.get("reps_note")) if item.get("reps_note") else "NULL",
            video_url=q(item.get("video_url")) if item.get("video_url") else "NULL",
        ))

    stmts.append(FOOTER)

    Path(out_path).write_text("".join(stmts), encoding="utf-8")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="inp", required=True, help="path to exercises.json")
    p.add_argument("--out", dest="out", required=True, help="path to output .sql")
    args = p.parse_args()
    build_sql(args.inp, args.out)
