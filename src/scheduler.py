from __future__ import annotations
from datetime import datetime, timedelta, timezone
import hmac, hashlib, uuid
from typing import Dict, Any, List

from .storage import load_pending, save_pending, append_sent, now_ts, read_config
from .mews_client import get_checkouts_between

def enqueue_yesterdays_checkouts() -> int:
    cfg = read_config()
    delay_hours = int(cfg["reviews"].get("delay_hours", 24))

    # Vi definierar "igår" brett, för att mocken ska träffa.
    start = datetime.now(timezone.utc) - timedelta(days=2)
    end = datetime.now(timezone.utc) - timedelta(hours=1)

    guests = get_checkouts_between(start, end)
    pending = load_pending()
    added = 0

    for g in guests:
        invite_id = str(uuid.uuid4())
        send_after = datetime.now(timezone.utc) + timedelta(hours=delay_hours)
        item = {
            "invite_id": invite_id,
            "reservation_id": g["reservation_id"],
            "full_name": g["full_name"],
            "email": g["email"],
            "send_after": int(send_after.timestamp()),
            "status": "queued"
        }
        pending.append(item)
        append_sent({
            "timestamp": now_ts(),
            "reservation_id": g["reservation_id"],
            "email": g["email"],
            "full_name": g["full_name"],
            "send_after": item["send_after"],
            "invite_id": invite_id
        })
        added += 1

    save_pending(pending)
    return added

def _sign(invite_id: str, reservation_id: str, score: int, secret: str) -> str:
    msg = f"{invite_id}:{reservation_id}:{score}".encode("utf-8")
    return hmac.new(secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()

def due_invites(now_ts_int: int) -> List[Dict[str, Any]]:
    return [i for i in load_pending() if i["status"] == "queued" and i["send_after"] <= now_ts_int]

def mark_sent(invite_id: str) -> None:
    pending = load_pending()
    for i in pending:
        if i["invite_id"] == invite_id:
            i["status"] = "sent"
            break
    save_pending(pending)

def build_score_links(invite: Dict[str, Any]) -> Dict[int, str]:
    cfg = read_config()
    domain = cfg["reviews"]["domain"].rstrip("/")
    secret = cfg["reviews"]["hmac_secret"]
    links = {}
    for s in [1,2,3,4,5]:
        sig = _sign(invite["invite_id"], invite["reservation_id"], s, secret)
        links[s] = f"{domain}/feedback?rid={invite['reservation_id']}&iid={invite['invite_id']}&score={s}&sig={sig}"
    return links
