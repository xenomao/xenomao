#!/usr/bin/env python3
"""DigiLab Beauty — Instagram 自動投稿パブリッシャ。

instagram/queue/ 内の投稿スペック(FABLE5 が生成)を読み込み、
status=ready かつ scheduled_for を過ぎたものを Instagram へ投稿する。
投稿に成功したスペックと画像は instagram/posted/ へ移動する。

使い方:
  # 検証のみ(APIを呼ばない)
  python instagram/publish.py --validate

  # 投稿せず対象を確認(ドライラン)
  python instagram/publish.py --dry-run

  # 実際に投稿(要 環境変数 IG_USER_ID / IG_ACCESS_TOKEN)
  python instagram/publish.py

環境変数:
  IG_USER_ID          Instagram プロアカウントの user id(数値)
  IG_ACCESS_TOKEN     長期アクセストークン
  IG_IMAGE_BASE_URL   画像の公開URLベース(省略時は GitHub raw から自動生成)
  GITHUB_REPOSITORY   "owner/repo"(Actions が自動設定)
  GITHUB_REF_NAME     ブランチ名(Actions が自動設定)
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from igpost import InstagramAPIError, InstagramClient, Post, PostError, load_posts  # noqa: E402

HERE = Path(__file__).resolve().parent
QUEUE_DIR = HERE / "queue"
POSTED_DIR = HERE / "posted"


def default_image_base_url() -> str:
    """GitHub raw URL から画像の公開URLベースを組み立てる。"""
    repo = os.getenv("GITHUB_REPOSITORY", "xenomao/xenomao")
    ref = os.getenv("GITHUB_REF_NAME", "main")
    return f"https://raw.githubusercontent.com/{repo}/{ref}/instagram/queue"


def load_and_validate(queue_dir: Path) -> tuple[list[Post], int]:
    """検証を通った Post 一覧と、失敗件数を返す。"""
    posts = load_posts(queue_dir)
    valid: list[Post] = []
    failures = 0
    for post in posts:
        try:
            post.validate()
            valid.append(post)
        except PostError as exc:
            failures += 1
            print(f"✗ 検証エラー: {exc}", file=sys.stderr)
    return valid, failures


def select_due(posts: list[Post], now: datetime) -> list[Post]:
    due: list[Post] = []
    for post in posts:
        if post.status != "ready":
            print(f"– スキップ (status={post.status}): {post.slug}")
            continue
        if not post.is_due(now):
            print(f"– スキップ (予約時刻前 {post.scheduled_for}): {post.slug}")
            continue
        due.append(post)
    return due


def archive(post: Post) -> None:
    """スペックと参照画像を posted/ へ移動。"""
    POSTED_DIR.mkdir(exist_ok=True)
    shutil.move(str(post.path), str(POSTED_DIR / post.path.name))
    for img in post.images:
        if img.startswith("http"):
            continue
        src = QUEUE_DIR / img
        if src.exists():
            shutil.move(str(src), str(POSTED_DIR / img))


def main() -> int:
    parser = argparse.ArgumentParser(description="Instagram 自動投稿パブリッシャ")
    parser.add_argument("--validate", action="store_true", help="検証のみ実行(投稿しない)")
    parser.add_argument("--dry-run", action="store_true", help="対象を表示するが投稿しない")
    parser.add_argument("--queue", default=str(QUEUE_DIR), help="キューディレクトリ")
    args = parser.parse_args()

    queue_dir = Path(args.queue)
    if not queue_dir.exists():
        print(f"キューディレクトリがありません: {queue_dir}", file=sys.stderr)
        return 1

    posts, failures = load_and_validate(queue_dir)
    print(f"検証OK: {len(posts)} 件 / 検証NG: {failures} 件")
    if args.validate:
        return 1 if failures else 0
    if failures:
        print(f"※ 検証NGの {failures} 件はスキップして続行します。", file=sys.stderr)

    now = datetime.now(timezone.utc)
    due = select_due(posts, now)
    if not due:
        print("投稿対象はありません。")
        return 0

    base_url = os.getenv("IG_IMAGE_BASE_URL") or default_image_base_url()
    print(f"画像ベースURL: {base_url}")

    if args.dry_run:
        for post in due:
            urls = post.resolve_image_urls(base_url, queue_dir)
            print(f"\n[DRY-RUN] {post.slug} ({post.media_type})")
            print(f"  画像: {urls}")
            print(f"  キャプション:\n{_indent(post.full_caption())}")
        print(f"\n[DRY-RUN] {len(due)} 件が投稿対象です(実投稿はしていません)。")
        return 0

    ig_user_id = os.getenv("IG_USER_ID", "")
    access_token = os.getenv("IG_ACCESS_TOKEN", "")
    try:
        client = InstagramClient(ig_user_id, access_token)
    except InstagramAPIError as exc:
        print(f"認証情報エラー: {exc}", file=sys.stderr)
        print("IG_USER_ID と IG_ACCESS_TOKEN を設定してください。", file=sys.stderr)
        return 1

    failures = 0
    for post in due:
        urls = post.resolve_image_urls(base_url, queue_dir)
        try:
            if post.media_type == "CAROUSEL":
                media_id = client.publish_carousel(urls, post.full_caption(), post.alt_text)
            else:
                media_id = client.publish_image(urls[0], post.full_caption(), post.alt_text)
            print(f"✓ 投稿成功: {post.slug} -> media_id={media_id}")
            archive(post)
        except (InstagramAPIError, PostError) as exc:
            failures += 1
            print(f"✗ 投稿失敗: {post.slug}: {exc}", file=sys.stderr)

    return 1 if failures else 0


def _indent(text: str, prefix: str = "    ") -> str:
    return "\n".join(prefix + line for line in text.splitlines())


if __name__ == "__main__":
    raise SystemExit(main())
