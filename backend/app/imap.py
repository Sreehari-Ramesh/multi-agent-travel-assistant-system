import os
import re
import time
import imaplib
import email
from email.header import decode_header
from urllib.parse import urljoin
from config import get_settings
import email.utils


import requests


settings = get_settings()
IMAP_HOST = settings.supervisor_imap_host
IMAP_PORT = settings.supervisor_imap_port
IMAP_EMAIL = settings.supervisor_imap_email
IMAP_APP_PASSWORD = settings.supervisor_imap_app_password

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:8000")
API_PREFIX = os.getenv("API_PREFIX", "/api")  # keep default unless you changed it
SUBJECT_TAG = os.getenv("ESCALATION_SUBJECT_TAG", "[Dubai Travel Assistant]")

POLL_SECONDS = int(os.getenv("IMAP_POLL_SECONDS", "15"))

# Extract conversation_id from subject like: conversation_id=demo-conversation
CONV_RE = re.compile(r"conversation_id=([A-Za-z0-9_\-]+)")



def _decode_mime_words(s: str) -> str:
    parts = decode_header(s)
    out = []
    for text, enc in parts:
        if isinstance(text, bytes):
            out.append(text.decode(enc or "utf-8", errors="ignore"))
        else:
            out.append(text)
    return "".join(out)

def _get_plain_text_body(msg: email.message.Message) -> str:
    # Prefer text/plain
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            disp = str(part.get("Content-Disposition", ""))
            if ctype == "text/plain" and "attachment" not in disp.lower():
                payload = part.get_payload(decode=True) or b""
                charset = part.get_content_charset() or "utf-8"
                return payload.decode(charset, errors="ignore").strip()
        # Fallback to first non-attachment part
        for part in msg.walk():
            disp = str(part.get("Content-Disposition", ""))
            if "attachment" not in disp.lower():
                payload = part.get_payload(decode=True) or b""
                charset = part.get_content_charset() or "utf-8"
                text = payload.decode(charset, errors="ignore").strip()
                if text:
                    return text
        return ""
    else:
        payload = msg.get_payload(decode=True) or b""
        charset = msg.get_content_charset() or "utf-8"
        return payload.decode(charset, errors="ignore").strip()

def _strip_quoted_reply(text: str) -> str:
    """
    Demo-grade cleanup: take top part of reply before common quote markers.
    """
    markers = [
        "\nOn ",           # Gmail/Outlook style
        "\nFrom:",         # quoted block
        "\n-----Original Message-----",
        "\n> ",            # inline quote
    ]
    cut = len(text)
    for m in markers:
        idx = text.find(m)
        if idx != -1:
            cut = min(cut, idx)
    return text[:cut].strip()

def inject_supervisor_message(conversation_id: str, message: str) -> None:
    endpoint = f"{API_PREFIX}/escalations/{conversation_id}/supervisor-reply"
    url = urljoin(BACKEND_BASE_URL, endpoint)
    r = requests.post(url, json={"message": message}, timeout=15)
    r.raise_for_status()

def main():
    if not IMAP_EMAIL or not IMAP_APP_PASSWORD:
        raise SystemExit("Missing SUPERVISOR_IMAP_EMAIL or SUPERVISOR_IMAP_APP_PASSWORD env vars.")

    print(f"[IMAP] Connecting to {IMAP_HOST}:{IMAP_PORT} as {IMAP_EMAIL}")
    while True:
        try:
            print("Step 1: Creating IMAP4_SSL")
            mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)

            print("Step 2: Logging in")
            mail.login(IMAP_EMAIL, IMAP_APP_PASSWORD)

            print("Step 3: Selecting INBOX")
            mail.select("INBOX")

            print("Step 4: Searching UNSEEN")
            status, data = mail.search(None, "UNSEEN")

            print("Step 5: Search complete")
            print(f"[IMAP] Search status: {status}, found {len(data[0].split())} messages")
            if status != "OK":
                mail.logout()
                time.sleep(POLL_SECONDS)
                continue

            ids = data[0].split()
            for msg_id in ids:
                status, msg_data = mail.fetch(msg_id, "(RFC822)")
                if status != "OK":
                    continue

                raw = msg_data[0][1]
                msg = email.message_from_bytes(raw)

                subject = _decode_mime_words(msg.get("Subject", "") or "")
                from_ = _decode_mime_words(msg.get("From", "") or "")
                # print("DEBUG SUBJECT:", subject)
                print("DEBUG FROM:", from_)

                # Only process supervisor replies to our escalations

                # Extract clean sender email
                raw_from = msg.get("From", "")
                sender_email = email.utils.parseaddr(raw_from)[1].lower()
                print("DEBUG SENDER_EMAIL:", sender_email)
                print("supervisor_email:", settings.supervisor_email)

                if sender_email != settings.supervisor_email.lower():
                    print(f"[IMAP] Skipping non-supervisor email from {sender_email}")
                    mail.store(msg_id, "+FLAGS", "\\Seen")
                    continue

                # For demo, inject into known conversation
                conversation_id = "demo-conversation"
                
                body = _get_plain_text_body(msg)
                clean = _strip_quoted_reply(body)

                if not clean:
                    print(f"[IMAP] Empty body, skipping: subject={subject}")
                    mail.store(msg_id, "+FLAGS", "\\Seen")
                    continue

                print(f"[IMAP] New supervisor reply from={from_} conv={conversation_id} subject={subject}")
                print(f"[IMAP] Injecting message: {clean[:200]}{'...' if len(clean) > 200 else ''}")

                inject_supervisor_message(conversation_id, clean)

                # Mark as seen so it won't be processed again
                mail.store(msg_id, "+FLAGS", "\\Seen")

            mail.logout()
        except Exception as e:
            print(f"[IMAP] Error: {e}")

        time.sleep(POLL_SECONDS)

if __name__ == "__main__":
    main()

#Terminal 2 (poller):
# python -m app.imap_poller