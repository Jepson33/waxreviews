from __future__ import annotations
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
import hmac, hashlib, time

from .storage import append_feedback, read_config, load_pending
from .emailer import send_email

app = FastAPI()

def _env() -> Environment:
    return Environment(
        loader=FileSystemLoader(Path(__file__).resolve().parent / "templates"),
        autoescape=select_autoescape(["html", "xml"])
    )

def _valid_sig(iid: str, rid: str, score: int, sig: str, secret: str) -> bool:
    msg = f"{iid}:{rid}:{score}".encode("utf-8")
    digest = hmac.new(secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()
    return hmac.compare_digest(digest, sig)

def _find_invite(iid: str) -> dict | None:
    for item in load_pending():
        if item.get("invite_id") == iid:
            return item
    return None

def _send_internal_alert(cfg: dict, reservation_id: str, guest_email: str, guest_name: str, score: int, ua: str, ip: str) -> None:
    to_list = cfg.get("email", {}).get("internal_alert_to", [])
    if not to_list:
        return
    subject = f"[Waxreviews] Låg feedback {score}/5 för reservation {reservation_id}"
    html = f"""
    <html><body style="font-family:Arial,sans-serif;">
      <h3>Ny låg feedback</h3>
      <p><strong>Reservation:</strong> {reservation_id}</p>
      <p><strong>Gäst:</strong> {guest_name or '-'} &lt;{guest_email or '-'}&gt;</p>
      <p><strong>Betyg:</strong> {score} / 5</p>
      <p><strong>User-Agent:</strong> {ua or '-'}</p>
      <p><strong>IP:</strong> {ip or '-'}</p>
    </body></html>
    """
    send_email(
        smtp_host=cfg["email"]["smtp_host"],
        smtp_port=int(cfg["email"]["smtp_port"]),
        username=cfg["email"]["username"],
        password=cfg["email"]["password"],
        sender=cfg["email"]["from"],
        recipients=to_list,
        subject=subject,
        html=html,
        text_fallback=f"Låg feedback {score}/5 för reservation {reservation_id}. Gäst {guest_name} <{guest_email}>."
    )

@app.get("/", response_class=HTMLResponse)
def root():
    return "<h3>Waxreviews server uppe</h3>"

@app.get("/healthz", response_class=JSONResponse)
def healthz():
    return {"ok": True, "ts": int(time.time())}

@app.get("/feedback", response_class=HTMLResponse)
def feedback(request: Request, rid: str, iid: str, score: int, sig: str):
    cfg = read_config()
    if not _valid_sig(iid, rid, int(score), sig, cfg["reviews"]["hmac_secret"]):
        raise HTTPException(status_code=400, detail="Ogiltig signatur")

    invite = _find_invite(iid) or {}
    guest_email = invite.get("email", "")
    guest_name = invite.get("full_name", "")
    reservation_id = invite.get("reservation_id", rid)

    ua = request.headers.get("user-agent", "")
    ip = request.client.host if request.client else ""
    append_feedback({
        "timestamp": int(time.time()),
        "reservation_id": reservation_id,
        "email": guest_email,
        "full_name": guest_name,
        "score": int(score),
        "invite_id": iid,
        "user_agent": ua,
        "ip": ip
    })

    env = _env()
    if int(score) >= 4:
        tpl = env.get_template("thank_you_positive.html")
        html = tpl.render(
            google=cfg["reviews"]["links"]["google"],
            tripadvisor=cfg["reviews"]["links"]["tripadvisor"]
        )
        return HTMLResponse(content=html, status_code=200)

    tpl = env.get_template("thank_you_neutral.html")
    html = tpl.render()
    _send_internal_alert(cfg, reservation_id, guest_email, guest_name, int(score), ua, ip)
    return HTMLResponse(content=html, status_code=200)
