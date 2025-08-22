from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from .storage import read_config

def _iso_utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()

def get_checkouts_between(start_utc: datetime, end_utc: datetime) -> List[Dict[str, Any]]:
    cfg = read_config()
    if cfg.get("flags", {}).get("use_mock_mews", True):
        # En gäst som checkade ut för 25 timmar sedan
        sample_checkout = datetime.now(timezone.utc) - timedelta(hours=25)
        return [{
            "reservation_id": "RES123",
            "full_name": "Sofia Andersson",
            "email": cfg.get("email", {}).get("username") or "sofia@example.com",
            "checkout_utc": _iso_utc(sample_checkout)
        }]
    # Byt till riktiga API-anrop när ni får nycklar.
    return []
