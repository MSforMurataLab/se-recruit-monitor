"""キーワードマッチングロジック"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class MatchResult:
    matched: bool
    secondary_hits: tuple[str, ...]
    se_hits: tuple[str, ...]
    context_snippets: tuple[str, ...]


def _find_hits(text: str, keywords: list[str]) -> list[str]:
    hits: list[str] = []
    for kw in keywords:
        if kw in text:
            hits.append(kw)
    return hits


def _extract_snippets(text: str, keyword: str, window: int = 80) -> list[str]:
    snippets: list[str] = []
    start = 0
    while True:
        idx = text.find(keyword, start)
        if idx == -1:
            break
        lo = max(0, idx - window)
        hi = min(len(text), idx + len(keyword) + window)
        snippet = re.sub(r"\s+", " ", text[lo:hi]).strip()
        snippets.append(f"...{snippet}...")
        start = idx + len(keyword)
        if len(snippets) >= 3:
            break
    return snippets


def _proximity_match(text: str, secondary_kws: list[str], se_kws: list[str], max_distance: int = 200) -> bool:
    """同一文または近接範囲内で二次募集×SEキーワードが共存するか判定"""
    sentences = re.split(r"[。\n\r!?！？]", text)
    for sentence in sentences:
        has_secondary = any(kw in sentence for kw in secondary_kws)
        has_se = any(kw in sentence for kw in se_kws)
        if has_secondary and has_se:
            return True

    secondary_positions = [text.find(kw) for kw in secondary_kws if kw in text]
    se_positions = [text.find(kw) for kw in se_kws if kw in text]
    for s_pos in secondary_positions:
        for e_pos in se_positions:
            if abs(s_pos - e_pos) <= max_distance:
                return True
    return False


def _is_false_positive(text: str, secondary_keyword: str) -> bool:
    """セミナー追加日程など、採用二次募集ではない既知の誤検知を除外"""
    false_positive_patterns = [
        r"セミナー.{0,20}追加日程",
        r"追加日程.{0,20}セミナー",
        r"インターンシップ.{0,30}追加日程",
        r"イベント.{0,20}追加日程",
    ]
    for pattern in false_positive_patterns:
        if re.search(pattern, text):
            if secondary_keyword in ("追加募集", "追加エントリー", "追加選考"):
                continue
            return True
    return False


def analyze_text(
    text: str,
    secondary_keywords: list[str],
    se_keywords: list[str],
) -> MatchResult:
    normalized = re.sub(r"\s+", " ", text)
    secondary_hits = [
        kw for kw in _find_hits(normalized, secondary_keywords)
        if not _is_false_positive(normalized, kw)
    ]
    se_hits = _find_hits(normalized, se_keywords)

    if not secondary_hits:
        return MatchResult(False, tuple(), tuple(), tuple())

    # 採用ページ上で二次募集キーワードが出た場合、
    # SEキーワードがページ内にあれば通知（各社はIT/SE採用ページを監視）
    matched = bool(se_hits) or _proximity_match(normalized, list(secondary_hits), se_keywords)

    snippets: list[str] = []
    for kw in secondary_hits:
        snippets.extend(_extract_snippets(normalized, kw))

    return MatchResult(
        matched=matched,
        secondary_hits=tuple(secondary_hits),
        se_hits=tuple(se_hits),
        context_snippets=tuple(snippets[:5]),
    )
