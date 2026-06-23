"""採用ページ取得"""

from __future__ import annotations

import logging
import re

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

try:
    import cloudscraper

    _scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "mobile": False}
    )
except ImportError:
    _scraper = None

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)

DEFAULT_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

TIMEOUT = 30


def _get(url: str) -> requests.Response:
    resp = requests.get(
        url,
        headers=DEFAULT_HEADERS,
        timeout=TIMEOUT,
        allow_redirects=True,
    )
    if resp.status_code == 403 and _scraper is not None:
        logger.info("Retrying with cloudscraper: %s", url)
        resp = _scraper.get(url, timeout=TIMEOUT)
    return resp


def fetch_page_text(url: str) -> str | None:
    try:
        resp = _get(url)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or "utf-8"
        return extract_text(resp.text)
    except requests.RequestException as exc:
        logger.warning("Failed to fetch %s: %s", url, exc)
        return None


def extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines))
