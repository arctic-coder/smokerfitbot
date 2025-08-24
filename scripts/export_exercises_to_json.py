# scripts/export_exercises_to_json.py
import os, json, re
import pandas as pd
from pathlib import Path

SHEET_NAME = "excercises"  # название листа в твоём xlsx

def _json_list(s):
    if isinstance(s, list):
        return [str(x).strip() for x in s]
    if isinstance(s, str):
        s2 = s.strip().replace("“", '"').replace("”", '"').replace("'", '"')
        try:
            v = json.loads(s2)
            return [str(x).strip() for x in v] if isinstance(v, list) else []
        except Exception:
            return []
    return []

def _fix_equipment_opts(s):
    """
    В XLSX колонка 'equipment_dnf' хранит ОПЦИИ инвентаря:
      - список строк: ["Ничего"]  -> интерпретируем как [["Ничего"]]
      - список списков: [["Турник","Тонкая резинка"], ["Турник"]]
    Чиним пропуски кавычек и приводим к list[list[str]].
    """
    if isinstance(s, list):
        if all(isinstance(x, list) for x in s):
            return [[str(y).strip() for y in x] for x in s] or [["Ничего"]]
        if all(isinstance(x, str) for x in s):
            return [[str(x).strip() for x in s]] or [["Ничего"]]
    if not isinstance(s, str):
        return [["Ничего"]]
    s2 = s.strip().replace("“", '"').replace("”", '"').replace("'", '"')
    s2 = re.sub(r'\["([^"]+)\]\]', r'["\1"]]', s2)
    s2 = re.sub(r'\["([^"]+)\]',  r'["\1"]',   s2)
    if s2 == "":
        return [["Ничего"]]
    try:
        v = json.loads(s2)
        if isinstance(v, list) and all(isinstance(x, str) for x in v):
            return [[str(x).strip() for x in v]] or [["Ничего"]]
        if isinstance(v, list) and all(isinstance(x, list) for x in v):
            return [[str(y).strip() for y in x] for x in v] or [["Ничего"]]
    except Exception:
        pass
    raw = s2.strip().strip("[]")
    toks = [t.strip().strip('"') for t in raw.split(",") if t.strip()]
    return [[t] for t in toks] or [["Ничего"]]

def _flatten_equipment(options):
    """Из опций [[A,B],[C]] собрать плоский список уникальных предметов без 'Ничего'."""
    flat = set()
    for group in options:
        for item in group:
            item = str(item).strip()
            if item and item != "Ничего":
                flat.add(item)
    return sorted(flat)

def main(xlsx_path: str, out_json: str = "data/exercises.json", sheet: str = SHEET_NAME):
    df = pd.read_excel(xlsx_path, sheet_name=sheet)
    rows = []

    for idx, row in df.iterrows():
        name = str(row.get("name", "")).strip()
        if not name:
            continue

        levels   = _json_list(row.get("levels"))
        allowed  = _json_list(row.get("allowed_limitations"))
        mg       = str(row.get("muscle_group") or "").strip()
        reps     = str(row.get("reps_note") or "").strip()
        url      = str(row.get("video_url") or "").strip()
        options  = _fix_equipment_opts(row.get("equipment_dnf"))
        equip    = _flatten_equipment(options)

        rows.append({
            "name": name,
            "levels": levels,                         # list[str]
            "equipment": equip,                       # list[str]
            "equipment_dnf": options,                 # list[list[str]]
            "allowed_limitations": allowed,           # list[str]
            "muscle_group": mg,
            "reps_note": reps,
            "video_url": url
        })

    Path(out_json).parent.mkdir(parents=True, exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

    print(f"Exported {len(rows)} exercises → {out_json}")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--file", required=True, help="Path to smokerfitbot_list.xlsx")
    p.add_argument("--sheet", default=SHEET_NAME)
    p.add_argument("--out", default="data/exercises.json")
    args = p.parse_args()
    main(args.file, args.out, args.sheet)
