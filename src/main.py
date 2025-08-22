from __future__ import annotations
import sys
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

from .storage import read_config, now_ts, load_pending, save_pending
from .scheduler import enqueue_yesterdays_checkouts, due_invites, mark_sent, build_score_links
from .emailer import send_email

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

def render_template(name: str, **ctx) -> str:
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(["html", "xml"])
    )
    return env.get_template(name).render(**ctx)

def cmd_enqueue():
    added = enqueue_yesterdays_checkouts()
    print(f"Lade till {added} gäster i kön.")

def cmd_enqueue_now():
    cfg = read_config()
    pending = load_pending()
    item = {
        "invite_id": "TEST-" + str(len(pending) + 1),
        "reservation_id": "TEST-RES",
        "full_name": "Test Gäst",
        "email": cfg.get("email", {}).get("username") or "test@example.com",
        "send_after": now_ts(),  # direkt
        "status": "queued",
    }
    pending.append(item)
    save_pending(pending)
    print("La till 1 testgäst för omedelbart utskick.")

def cmd_queue_clear():
    save_pending([])
    print("Tömde kön.")

def cmd_process():
    cfg = read_config()
    invites = due_invites(now_ts())
    if not invites:
        print("Inga utskick för tillfället.")
        return
    for inv in invites:
        links = build_score_links(inv)
        first_name = inv["full_name"].split()[0] if inv["full_name"] else "Gäst"
        html = render_template(
            "email_invite.html",
            first_name=first_name,
            full_name=inv["full_name"],
            links=links
        )
        ok = send_email(
            smtp_host=cfg["email"]["smtp_host"],
            smtp_port=int(cfg["email"]["smtp_port"]),
            username=cfg["email"]["username"],
            password=cfg["email"]["password"],
            sender=cfg["email"]["from"],
            recipients=[inv["email"]],
            subject="Tack för din vistelse på Waxholms Hotell",
            html=html,
            text_fallback=f"Hej {first_name}. Hur upplevde du din vistelse. 1 2 3 4 5."
        )
        print(f"Skickade till {inv['email']}: {ok}")
        if ok:
            mark_sent(inv["invite_id"])

def main():
    if len(sys.argv) < 2:
        print("Använd:")
        print("  py -m src.main enqueue")
        print("  py -m src.main enqueue-now")
        print("  py -m src.main process")
        print("  py -m src.main queue:clear")
        return
    cmd = sys.argv[1].lower()
    if cmd == "enqueue":
        cmd_enqueue()
    elif cmd == "enqueue-now":
        cmd_enqueue_now()
    elif cmd == "process":
        cmd_process()
    elif cmd == "queue:clear":
        cmd_queue_clear()
    else:
        print("Okänt kommando.")

if __name__ == "__main__":
    main()
