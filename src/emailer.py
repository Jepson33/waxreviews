from __future__ import annotations
import smtplib
from email.message import EmailMessage
from typing import List, Optional

def send_email(
    smtp_host: str,
    smtp_port: int,
    username: str,
    password: str,
    sender: str,
    recipients: List[str],
    subject: str,
    html: str,
    text_fallback: Optional[str] = None,
) -> bool:
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg.set_content(text_fallback or "Se HTML-versionen")
    msg.add_alternative(html, subtype="html")

    try:
        if int(smtp_port) == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=30) as s:
                s.login(username, password)
                s.send_message(msg)
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as s:
                s.ehlo()
                s.starttls()
                s.ehlo()
                s.login(username, password)
                s.send_message(msg)
        return True
    except Exception as e:
        print(f"[EMAIL] Fel vid utskick. {e}")
        return False

