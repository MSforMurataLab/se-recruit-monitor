"""監視メインロジック"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

import yaml

from monitor.fetcher import fetch_page_text
from monitor.matcher import analyze_text
from monitor.notifier import send_notification
from monitor.storage import NotificationRecord, StateStore

logger = logging.getLogger(__name__)


def load_config(config_path: Path) -> dict:
    with config_path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_check(
    config_path: Path,
    state_path: Path,
    dry_run: bool = False,
    force_notify: bool = False,
) -> list[NotificationRecord]:
    config = load_config(config_path)
    store = StateStore(state_path)
    notify_email = config.get("notify_email", "m.shinoharaforrecruit@gmail.com")
    secondary_keywords = config["secondary_keywords"]
    se_keywords = config["se_keywords"]

    sent: list[NotificationRecord] = []

    for company in config["companies"]:
        company_id = company["id"]
        company_name = company["name"]
        logger.info("Checking %s...", company_name)

        for url in company["urls"]:
            text = fetch_page_text(url)
            if text is None:
                continue

            content_hash = StateStore.hash_content(text)
            match = analyze_text(text, secondary_keywords, se_keywords)

            if not match.matched:
                store.update_page(url, content_hash, notified=False)
                logger.debug("No match: %s", url)
                continue

            already_notified = store.was_notified_for_hash(url, content_hash)
            if already_notified and not force_notify:
                logger.info("Already notified for %s (unchanged)", url)
                store.update_page(url, content_hash, notified=True)
                continue

            record = NotificationRecord(
                company_id=company_id,
                company_name=company_name,
                url=url,
                secondary_hits=list(match.secondary_hits),
                se_hits=list(match.se_hits),
                snippets=list(match.context_snippets),
                notified_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            )

            if dry_run:
                logger.info("[DRY RUN] Would notify: %s - %s", company_name, url)
                logger.info("  Secondary: %s", match.secondary_hits)
                logger.info("  SE: %s", match.se_hits)
            else:
                if send_notification(record, notify_email):
                    sent.append(record)
                    store.add_notification(record)
                    store.update_page(url, content_hash, notified=True)
                else:
                    store.update_page(url, content_hash, notified=False)
                    continue

            if dry_run:
                store.update_page(url, content_hash, notified=False)

    store.save()
    return sent
