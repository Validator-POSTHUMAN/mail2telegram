#!/usr/bin/env python3
import email
import imaplib
import logging
import os
import time
from email.header import decode_header
import requests

IMAP_SERVER = os.getenv("IMAP_SERVER", "mail.privateemail.com")
IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
FROM_FILTERS = os.getenv("FROM_FILTERS", "").split(",")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "300"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

def decode_mime_header(header):
    if header is None:
        return ""
    decoded = decode_header(header)
    result = []
    for part, charset in decoded:
        if isinstance(part, bytes):
            result.append(part.decode(charset or "utf-8", errors="ignore"))
        else:
            result.append(part)
    return "".join(result)

def get_email_body(msg):
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                try:
                    body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                    break
                except:
                    pass
    else:
        try:
            body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
        except:
            pass
    return body[:3500]

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=10)
        return r.ok
    except Exception as e:
        logging.error(f"Telegram error: {e}")
        return False

def check_emails():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("INBOX")
        all_ids = []
        for f in FROM_FILTERS:
            f = f.strip()
            if not f:
                continue
            status, msgs = mail.search(None, f"(UNSEEN FROM "{f}")")
            if status == "OK" and msgs[0]:
                all_ids.extend(msgs[0].split())
        for eid in list(set(all_ids)):
            status, data = mail.fetch(eid, "(RFC822)")
            if status != "OK":
                continue
            msg = email.message_from_bytes(data[0][1])
            subject = decode_mime_header(msg["Subject"])
            from_addr = decode_mime_header(msg["From"])
            body = get_email_body(msg)
            text = f"New Email
From: {from_addr}
Subject: {subject}

{body}"
            if send_telegram(text):
                logging.info(f"Sent: {subject}")
                mail.store(eid, "+FLAGS", "\Seen")
            else:
                logging.error(f"Failed: {subject}")
        mail.logout()
    except Exception as e:
        logging.error(f"IMAP error: {e}")

def main():
    if not all([EMAIL_USER, EMAIL_PASS, TELEGRAM_TOKEN, CHAT_ID]):
        logging.error("Missing env vars")
        return
    logging.info("mail2telegram started")
    while True:
        check_emails()
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
