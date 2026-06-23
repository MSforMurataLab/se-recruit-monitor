#!/usr/bin/env python3
"""SE職 二次応募/追加募集 監視システム"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

from monitor.checker import run_check

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.yaml"
STATE_PATH = ROOT / "data" / "state.json"


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="指定6社のSE職 二次応募/追加募集を監視しメール通知します",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="1回だけチェックして終了（デフォルト）",
    )
    parser.add_argument(
        "--loop",
        action="store_true",
        help="定期的にチェックを繰り返す",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=3600,
        help="--loop 時のチェック間隔（秒）。デフォルト: 3600",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="メール送信せず、検出結果のみ表示",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="既通知済みでも再送信（テスト用）",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="詳細ログを出力",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    setup_logging(args.verbose)
    load_dotenv(ROOT / ".env")

    if args.loop:
        logging.info("Loop mode: checking every %d seconds", args.interval)
        while True:
            sent = run_check(CONFIG_PATH, STATE_PATH, dry_run=args.dry_run, force_notify=args.force)
            logging.info("Check complete. Notifications sent: %d", len(sent))
            time.sleep(args.interval)
    else:
        sent = run_check(CONFIG_PATH, STATE_PATH, dry_run=args.dry_run, force_notify=args.force)
        logging.info("Check complete. Notifications sent: %d", len(sent))
        return 0 if sent or args.dry_run else 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
