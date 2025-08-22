from __future__ import annotations
import sys
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from .storage import read_config, now_ts
from .scheduler import enqueue_yesterdays_checkouts, due_invites, mark_sent, build_score_links
from .emailer import send_email

def render_template(name: str, **ctx) -> str:
    env = Environment(
        loader=FileSystemLoader(Path(__file__).resolve().parent / "templates"),
        autoescape=select_autoescape(["html", "xml"])
    )
    return env.get_template(name).render(**ctx)

def cmd_enqueue():
    added = enqueue_yesterdays_checkouts()
    print(f"Lade till {added} gäster i kön.")

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

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Använd: py -m src.main enqueue  eller  py -m src.main process")
        sys.exit(0)
    cmd = sys.argv[1].lower()
    if cmd == "enqueue":
        cmd_enqueue()
    elif cmd == "process":
        cmd_process()
    else:
        print("Okänt kommando.")

