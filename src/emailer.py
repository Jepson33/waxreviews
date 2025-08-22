# src/emailer.py
from __future__ import annotations
from typing import List, Optional
from textwrap import shorten
from datetime import datetime

DEV_LOG_PREFIX = "[DEV EMAIL]"

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
    """
    Utvecklingsstub. Skickar ingenting.
    Loggar bara info till konsolen och returnerar True.
    Håll samma signatur som den riktiga SMTP-funktionen.
    """
    # Klipp ner innehåll för läsbarhet i terminal
    preview_html = shorten(html.replace("\n", " ").strip(), width=300, placeholder="...")
    preview_text = shorten((text_fallback or "").replace("\n", " ").strip(), width=200, placeholder="...")

    print(f"{DEV_LOG_PREFIX} {datetime.now().isoformat(timespec='seconds')}")
    print(f"{DEV_LOG_PREFIX} From: {sender}")
    print(f"{DEV_LOG_PREFIX} To: {', '.join(recipients)}")
    print(f"{DEV_LOG_PREFIX} Subject: {subject}")
    if text_fallback:
        print(f"{DEV_LOG_PREFIX} Text preview: {preview_text}")
    print(f"{DEV_LOG_PREFIX} HTML preview: {preview_html}")
    print(f"{DEV_LOG_PREFIX} Status: OK (emulated send)")
    return True
