"""メール通知"""

from __future__ import annotations

import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from monitor.storage import NotificationRecord

logger = logging.getLogger(__name__)


def _build_subject(record: NotificationRecord) -> str:
    return f"【SE採用通知】{record.company_name} - 二次応募/追加募集の可能性"


def _build_body(record: NotificationRecord) -> str:
    lines = [
        f"企業: {record.company_name}",
        f"URL: {record.url}",
        f"検出日時: {record.notified_at}",
        "",
        "【検出キーワード（二次募集系）】",
        ", ".join(record.secondary_hits) or "（なし）",
        "",
        "【検出キーワード（SE系）】",
        ", ".join(record.se_hits) or "（なし）",
        "",
        "【該当箇所の抜粋】",
    ]
    for i, snippet in enumerate(record.snippets, 1):
        lines.append(f"{i}. {snippet}")
    lines.extend(
        [
            "",
            "---",
            "このメールは se-recruit-monitor により自動送信されました。",
            "採用ページの内容変更を検知したものです。最新情報は各社採用サイトでご確認ください。",
        ]
    )
    return "\n".join(lines)


def send_notification(record: NotificationRecord, to_email: str | None = None) -> bool:
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_password = os.environ.get("SMTP_PASSWORD", "")
    recipient = to_email or os.environ.get("NOTIFY_EMAIL_TO", "m.shinoharaforrecruit@gmail.com")

    if not smtp_user or not smtp_password:
        logger.error(
            "SMTP_USER / SMTP_PASSWORD が未設定です。.env ファイルを設定してください。"
        )
        return False

    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = recipient
    msg["Subject"] = _build_subject(record)
    msg.attach(MIMEText(_build_body(record), "plain", "utf-8"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        logger.info("Notification sent to %s for %s", recipient, record.company_name)
        return True
    except smtplib.SMTPException as exc:
        logger.error("Failed to send email: %s", exc)
        return False
