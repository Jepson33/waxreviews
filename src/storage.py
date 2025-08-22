from __future__ import annotations
import csv, json, os, time
from pathlib import Path
from typing import Dict, Any, List, Optional

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

PENDING = DATA / "pending.json"
SENT = DATA / "sent.csv"
FEEDBACK = DATA / "feedback.csv"

def read_config() -> Dict[str, Any]:
    cfg_path = Path(__file__).resolve().parent / "config.json"
    if not cfg_path.exists():
        # fall back to example for dev
        cfg_path = Path(__file__).resolve().parent / "config.example.json"
    return json.loads(cfg_path.read_text(encoding="utf-8"))

def load_pending() -> List[Dict[str, Any]]:
    if not PENDING.exists():
        return []
    return json.loads(PENDING.read_text(encoding="utf-8"))

def save_pending(items: List[Dict[str, Any]]) -> None:
    PENDING.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

def append_sent(row: Dict[str, Any]) -> None:
    new = not SENT.exists()
    with SENT.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "timestamp","reservation_id","email","full_name","send_after","invite_id"
        ])
        if new:
            w.writeheader()
        w.writerow(row)

def append_feedback(row: Dict[str, Any]) -> None:
    new = not FEEDBACK.exists()
    with FEEDBACK.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "timestamp","reservation_id","email","full_name","score","invite_id","user_agent","ip"
        ])
        if new:
            w.writeheader()
        w.writerow(row)

def now_ts() -> int:
    return int(time.time())

