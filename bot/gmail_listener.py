#!/usr/bin/env python3
"""
Gmail listener utility for forwarding incoming emails to Telegram chats.
"""

import asyncio
import imaplib
import logging
import os
import re
from dataclasses import dataclass
from email import message_from_bytes
from email.header import decode_header
from email.utils import parseaddr
from typing import List, Optional, Set


@dataclass
class EmailPayload:
    """Lightweight container for processed email data."""

    uid: int
    subject: str
    body: str
    date: str
    sender_email: str
    sender_name: str


class GmailListener:
    """Poll Gmail inbox for new messages from configured correspondents."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.username = os.getenv("GMAIL_USERNAME")
        self.password = os.getenv("GMAIL_APP_PASSWORD")
        self.server = os.getenv("GMAIL_IMAP_SERVER", "imap.gmail.com")
        self.interval = self._safe_int(os.getenv("MAIL_CHECK_INTERVAL", "60"), fallback=60)
        correspondents_raw = os.getenv("CORRESPONDENTS", "")
        self.correspondents = {
            addr.strip().lower()
            for addr in re.split(r"[;,]", correspondents_raw)
            if addr.strip()
        }
        self.logger = logger or logging.getLogger(__name__)
        self._lock = asyncio.Lock()
        self._last_uid: Optional[int] = None
        self._processed_uids: Set[int] = set()

    @staticmethod
    def _safe_int(value: str, fallback: int) -> int:
        try:
            parsed = int(value)
            return parsed if parsed > 0 else fallback
        except (ValueError, TypeError):
            return fallback

    def is_configured(self) -> bool:
        """Return True if listener has all required configuration."""

        return bool(self.username and self.password and self.correspondents)

    async def job_handler(self, context) -> None:
        """Async callback for telegram JobQueue."""

        if not self.is_configured():
            return

        notify_callback = (context.job.data or {}).get("notify")
        if notify_callback is None:
            self.logger.warning("Missing notify callback for Gmail listener job")
            return

        async with self._lock:
            messages = await asyncio.to_thread(self._fetch_new_messages)

        if not messages:
            return

        for payload in messages:
            try:
                await notify_callback(context.bot, payload)
            except Exception as exc:  # pragma: no cover - defensive logging
                self.logger.exception("Failed to dispatch email UID %s: %s", payload.uid, exc)

    def format_notification(self, payload: EmailPayload) -> str:
        """Format email payload into human-readable Telegram message."""

        sender_display = payload.sender_name or payload.sender_email
        subject = payload.subject or "(No subject)"
        body = payload.body.strip() or "(No content)"
        date = payload.date or "Unknown date"

        # Telegram messages have 4096 char limit; keep some headroom.
        max_length = 3900
        if len(body) > max_length:
            body = f"{body[:max_length]}…"

        lines = [
            "📧 New email received",
            f"From: {sender_display} <{payload.sender_email}>",
            f"Subject: {subject}",
            f"Date: {date}",
            "",
            body,
        ]
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _fetch_new_messages(self) -> List[EmailPayload]:
        messages: List[EmailPayload] = []

        try:
            with imaplib.IMAP4_SSL(self.server) as mail:
                mail.login(self.username, self.password)
                mail.select("INBOX")

                if self._last_uid is None:
                    status, data = mail.uid("search", None, "ALL")
                    if status == "OK":
                        uids = self._parse_uids(data)
                        self._last_uid = max(uids) if uids else 0
                    else:
                        self.logger.warning("Unable to initialize Gmail baseline UID: %s", status)
                        self._last_uid = 0
                    return messages

                query = f"UID {self._last_uid + 1}:*"
                status, data = mail.uid("search", None, query)
                if status != "OK":
                    self.logger.warning("Gmail UID search failed with status %s", status)
                    return messages

                new_uids = self._parse_uids(data)
                if not new_uids:
                    return messages

                for uid in new_uids:
                    if uid in self._processed_uids:
                        continue

                    status, payload = mail.uid("fetch", str(uid), "(BODY.PEEK[])")
                    if status != "OK" or not payload or not payload[0]:
                        continue

                    raw_email = payload[0][1]
                    email_message = message_from_bytes(raw_email)

                    sender_name, sender_email = self._extract_sender(email_message.get("From", ""))
                    if not sender_email or sender_email.lower() not in self.correspondents:
                        continue

                    subject = self._decode_mime_words(email_message.get("Subject", ""))
                    body = self._extract_body(email_message)
                    date_header = email_message.get("Date", "")

                    messages.append(
                        EmailPayload(
                            uid=uid,
                            subject=subject,
                            body=body,
                            date=date_header,
                            sender_email=sender_email,
                            sender_name=sender_name,
                        )
                    )

                    self._remember_uid(uid)

                if new_uids:
                    self._last_uid = max([self._last_uid] + new_uids)

        except imaplib.IMAP4.error as exc:
            self.logger.error("IMAP error while checking Gmail: %s", exc)
        except Exception:  # pragma: no cover - defensive logging
            self.logger.exception("Unexpected error while polling Gmail")

        return messages

    @staticmethod
    def _parse_uids(data) -> List[int]:
        if not data:
            return []
        if isinstance(data[0], bytes):
            raw = data[0]
        elif isinstance(data[0], str):
            raw = data[0].encode()
        else:
            raw = b""
        return [int(uid) for uid in raw.split()] if raw else []

    def _extract_sender(self, header_value: str) -> (str, str):
        name, email_addr = parseaddr(header_value)
        decoded_name = self._decode_mime_words(name)
        return decoded_name.strip(), email_addr.strip().lower()

    def _decode_mime_words(self, text: str) -> str:
        if not text:
            return ""
        decoded_parts: List[str] = []
        for part, charset in decode_header(text):
            if isinstance(part, bytes):
                encoding = charset or "utf-8"
                try:
                    decoded_parts.append(part.decode(encoding, errors="replace"))
                except LookupError:
                    decoded_parts.append(part.decode("utf-8", errors="replace"))
            else:
                decoded_parts.append(part)
        return "".join(decoded_parts)

    def _extract_body(self, message) -> str:
        text = self._extract_preferred_part(message, "text/plain")
        if text:
            return text

        html = self._extract_preferred_part(message, "text/html")
        if html:
            return self._strip_html_tags(html)

        payload = message.get_payload(decode=True)
        if payload:
            charset = message.get_content_charset() or "utf-8"
            try:
                return payload.decode(charset, errors="replace").strip()
            except LookupError:
                return payload.decode("utf-8", errors="replace").strip()
        return ""

    def _extract_preferred_part(self, message, content_type: str) -> str:
        if message.is_multipart():
            for part in message.walk():
                if part.get_content_maintype() != "text":
                    continue
                if part.get_content_type() != content_type:
                    continue
                if part.get_content_disposition() in {"attachment", "inline"}:
                    continue
                payload = part.get_payload(decode=True)
                if not payload:
                    continue
                charset = part.get_content_charset() or "utf-8"
                try:
                    return payload.decode(charset, errors="replace").strip()
                except LookupError:
                    return payload.decode("utf-8", errors="replace").strip()
        elif message.get_content_type() == content_type:
            payload = message.get_payload(decode=True)
            if payload:
                charset = message.get_content_charset() or "utf-8"
                try:
                    return payload.decode(charset, errors="replace").strip()
                except LookupError:
                    return payload.decode("utf-8", errors="replace").strip()
        return ""

    @staticmethod
    def _strip_html_tags(value: str) -> str:
        cleaned = re.sub(r"<[^>]+>", "", value)
        return re.sub(r"\s+", " ", cleaned).strip()

    def _remember_uid(self, uid: int) -> None:
        self._processed_uids.add(uid)
        if len(self._processed_uids) > 512:
            # Keep only the newest half of remembered UIDs to bound memory
            preserved = sorted(self._processed_uids)[-256:]
            self._processed_uids = set(preserved)


