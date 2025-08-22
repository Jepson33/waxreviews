from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
import json, time, requests
from .storage import read_config

def _iso_utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()

def get_checkouts_between(start_utc: datetime, end_utc: datetime) -> List[Dict[str, Any]]:
    """
    Returnerar gäster som checkat ut mellan start och slut.
    Om flags.use_mock_mews är true returneras fejkad data för enkel test.
    """
    cfg = read_config()
    if cfg.get("flags", {}).get("use_mock_mews", True):
        sample_checkout = datetime.now(timezone.utc) - timedelta(hours=25)
        return [{
            "reservation_id": "RES123",
            "full_name": "Sofia Andersson",
            "email": "sofia@example.com",
            "checkout_utc": _iso_utc(sample_checkout)
        }]
    # riktig anrop. fyll på med korrekta endpoints när ni har nycklarna
    url = cfg["mews"]["base_url"].rstrip("/") + "/api/connector/v1/reservations/getAll"
    body = {
        "ClientToken": cfg["mews"]["client_token"],
        "AccessToken": cfg["mews"]["access_token"],
        "ServiceId": cfg["mews"]["service_id"],
        "StartUtc": _iso_utc(start_utc),
        "EndUtc": _iso_utc(end_utc)
    }
    r = requests.post(url, json=body, timeout=30)
    r.raise_for_status()
    data = r.json()
    # mappa enligt riktig modell när du ser svaret
    guests: List[Dict[str, Any]] = []
    for res in data.get("Reservations", []):
        # placeholder tills ni mappar fälten
        pass
    return guests

