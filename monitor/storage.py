"""監視状態の永続化"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class PageState:
    url: str
    content_hash: str
    last_checked: str
    notified: bool = False


@dataclass
class NotificationRecord:
    company_id: str
    company_name: str
    url: str
    secondary_hits: list[str]
    se_hits: list[str]
    snippets: list[str]
    notified_at: str


class StateStore:
    def __init__(self, path: Path):
        self.path = path
        self._data: dict = {"pages": {}, "notifications": []}
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            self._data = json.loads(self.path.read_text(encoding="utf-8"))

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._data, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def hash_content(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def get_page(self, url: str) -> PageState | None:
        raw = self._data["pages"].get(url)
        if raw is None:
            return None
        return PageState(**raw)

    def update_page(self, url: str, content_hash: str, notified: bool) -> None:
        self._data["pages"][url] = asdict(
            PageState(
                url=url,
                content_hash=content_hash,
                last_checked=datetime.now(timezone.utc).isoformat(),
                notified=notified,
            )
        )

    def add_notification(self, record: NotificationRecord) -> None:
        self._data["notifications"].append(asdict(record))
        # 直近100件のみ保持
        self._data["notifications"] = self._data["notifications"][-100:]

    def was_notified_for_hash(self, url: str, content_hash: str) -> bool:
        page = self.get_page(url)
        if page is None:
            return False
        return page.content_hash == content_hash and page.notified
