from __future__ import annotations
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
import hmac, hashlib
from .storage import append_feedback, read_config
from .emailer import send_email
from pathlib import Path

app = FastAPI()

def _valid_sig(iid: str, rid: str, score: int, sig: str, secret: str) -> bool:
    msg = f"{iid}:{rid}:{score}".encode("utf-8")
    digest = hmac.new(secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()
    return hmac.compare_digest(digest, sig)

def _load_template(name: str) -> str:
    p = Path(__file__).resolve().parent / "templates" / name
    return p.read_text(encoding="utf-8")

@app.get("/", response_class=HTMLResponse)
def root():
    return "<h3>Waxreviews server uppe</h3>"

@app.get("/feedback", response_class=HTMLResponse)
def feedback(request: Request, rid: str, iid: str, score: int, sig: str):
    cfg = read_config()
    if not _valid_sig(iid, rid, score, sig, cfg["reviews"]["hmac_secret"]):
        raise HTTPException(400, "Ogiltig signatur")

    ua = request.headers.get("user-agent", "")
    ip = request.client.host if request.client else ""

    # I en riktig lösning hämtar du gästinfo från pending eller DB.
    # Här loggar vi utan e-post om den inte finns tillgänglig.
    append_feedback({
        "timestamp": __import__("time").time(),
        "reservation_id": rid,
        "email": "",
        "full_name": "",
        "score": score,
        "invite_id": iid,
        "user_agent": ua,
        "ip": ip
    })

    if score >= 4:
        html = _load_template("thank_you_positive.html")
        # Valfritt, skicka uppföljande mail med länkar
        # send_email(...)

    else:
        html = _load_template("thank_you_neutral.html")
        # Notifiera internt om du vill
        # internal_to = cfg["email"].get("internal_alert_to", [])
        # if internal_to:
        #     send_email(...)

    return HTMLResponse(content=html, status_code=200)

