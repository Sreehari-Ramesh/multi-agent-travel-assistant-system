import smtplib
from email.mime.text import MIMEText
from typing import Optional

from .config import get_settings


def send_escalation_email(
    subject: str,
    body: str,
    to_email: Optional[str] = None,
) -> None:
    """
    Send an escalation email to the configured supervisor.

    In development, if SMTP is not configured, this function will just
    print the email contents to stdout so the flow can be demonstrated
    without a real email provider.
    """
    settings = get_settings()
    recipient = to_email or settings.supervisor_email

    if not recipient:
        # Fallback: console log for demo purposes.
        print("--- ESCALATION EMAIL (NO SMTP CONFIGURED) ---")
        print(f"To: (missing supervisor_email) ")
        print(f"Subject: {subject}")
        print(body)
        print("--------------------------------------------")
        return

    if not (
        settings.smtp_host
        and settings.smtp_port
        and settings.smtp_from_email
    ):
        # Fallback: console log when SMTP is incomplete.
        print("--- ESCALATION EMAIL (INCOMPLETE SMTP CONFIG) ---")
        print(f"To: {recipient}")
        print(f"Subject: {subject}")
        print(body)
        print("-------------------------------------------------")
        return

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from_email
    msg["To"] = recipient

    try:
        with smtplib.SMTP(settings.smtp_host, int(settings.smtp_port)) as server:
            if settings.smtp_username and settings.smtp_password:
                server.starttls()
                server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(msg)
    except Exception as exc:  # pragma: no cover - best effort logging
        print(f"[EmailService] Failed to send escalation email: {exc}")

