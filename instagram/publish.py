#!/usr/bin/env python3
"""一般社団法人デジラボビュティ Instagram安全投稿パブリッシャ。"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from igpost import DELETE, InstagramAPIError, InstagramClient, Post, PostError, load_posts  # noqa: E402

HERE = Path(__file__).resolve().parent
QUEUE_DIR = HERE / "queue"
POSTED_DIR = HERE / "posted"


def default_image_base_url() -> str:
    repo = os.getenv("GITHUB_REPOSITORY", "xenomao/xenomao")
    immutable_ref = os.getenv("GITHUB_SHA") or "main"
    return f"https://raw.githubusercontent.com/{repo}/{immutable_ref}/instagram/queue"


def load_and_validate(queue_dir: Path) -> tuple[list[Post], int]:
    valid: list[Post] = []
    failures = 0
    try:
        posts = load_posts(queue_dir)
    except PostError as exc:
        print(f"✗ 読み込みエラー: {exc}", file=sys.stderr)
        return [], 1
    for post in posts:
        try:
            post.validate(queue_dir)
            if post.status == "posted":
                raise PostError(f"{post.path.name}: postedはqueueではなくposted/へ置いてください")
            valid.append(post)
        except PostError as exc:
            failures += 1
            print(f"✗ 検証エラー: {exc}", file=sys.stderr)
    return valid, failures


def select_due(posts: list[Post], now: datetime) -> list[Post]:
    due: list[Post] = []
    for post in posts:
        if post.status != "ready":
            continue
        if post.is_due(now):
            due.append(post)
        else:
            print(f"– 予約時刻前: {post.slug} ({post.scheduled_for.isoformat()})")
    return due


def find_post(queue_dir: Path, slug: str) -> Post:
    path = queue_dir / f"{slug}.json"
    if not path.is_file():
        raise PostError(f"投稿が見つかりません: {slug}")
    return Post.from_file(path)


def approve(queue_dir: Path, slug: str, approved_by: str, schedule: str | None) -> int:
    post = find_post(queue_dir, slug)
    if post.status == "publishing":
        raise PostError("publishing中の投稿は再承認できません。Instagram確認後に--recoverを使用してください")
    updates: dict = {}
    if schedule:
        try:
            scheduled = datetime.fromisoformat(schedule)
        except ValueError as exc:
            raise PostError(f"--scheduleはISO8601形式で指定してください: {exc}") from exc
        if scheduled.tzinfo is None:
            raise PostError("--scheduleには+09:00などのタイムゾーンが必須です")
        updates["scheduled_for"] = scheduled.isoformat()
    if updates:
        post.save(**updates)
        post = find_post(queue_dir, slug)
    if post.scheduled_for is None or post.scheduled_for.tzinfo is None:
        raise PostError("承認前にタイムゾーン付きscheduled_forを設定してください")

    post.save(status="draft", approval=DELETE, publish_attempt=DELETE, claimed_at=DELETE, last_error=DELETE)
    post = find_post(queue_dir, slug)
    post.validate(queue_dir)
    approval = {
        "approved_by": approved_by.strip(),
        "approved_at": datetime.now(timezone.utc).isoformat(),
        "content_sha256": post.content_digest(queue_dir),
    }
    if not approval["approved_by"]:
        raise PostError("--approved-byは必須です")
    post.save(status="ready", approval=approval)
    find_post(queue_dir, slug).validate(queue_dir)
    print(f"✓ 承認済み: {slug} / reviewer={approval['approved_by']} / {approval['content_sha256'][:12]}")
    return 0


def claim_due(queue_dir: Path, attempt: str) -> int:
    posts, failures = load_and_validate(queue_dir)
    if failures:
        return 1
    due = select_due(posts, datetime.now(timezone.utc))
    claimed_at = datetime.now(timezone.utc).isoformat()
    for post in due:
        post.save(status="publishing", publish_attempt=attempt, claimed_at=claimed_at, last_error=DELETE)
        print(f"✓ claim: {post.slug} / attempt={attempt}")
    print(f"claim件数: {len(due)}")
    return 0


def client_from_env() -> InstagramClient:
    return InstagramClient(
        os.getenv("IG_USER_ID", ""),
        os.getenv("IG_ACCESS_TOKEN", ""),
        api_version=os.getenv("IG_GRAPH_API_VERSION", "v26.0"),
    )


def preflight(expected_username: str) -> int:
    client = client_from_env()
    account = client.verify_credentials()
    actual = str(account.get("username", "")).lstrip("@").lower()
    expected = expected_username.lstrip("@").lower()
    if not expected:
        raise InstagramAPIError("想定ユーザー名が空です")
    if actual != expected:
        raise InstagramAPIError(
            f"投稿先アカウント不一致: expected=@{expected}, actual=@{actual or 'unknown'}"
        )
    print(f"✓ Meta事前確認OK: @{actual} / Graph API {os.getenv('IG_GRAPH_API_VERSION', 'v26.0')}")
    return 0


def archive(post: Post, media_id: str, published_at: str) -> None:
    POSTED_DIR.mkdir(exist_ok=True)
    post.save(
        status="posted",
        media_id=media_id,
        published_at=published_at,
        last_error=DELETE,
    )
    shutil.move(str(post.path), str(POSTED_DIR / post.path.name))
    for image in post.images:
        source = post.path.parent / image
        if source.exists():
            shutil.move(str(source), str(POSTED_DIR / image))


def publish_claimed(queue_dir: Path, attempt: str) -> int:
    posts, failures = load_and_validate(queue_dir)
    if failures:
        return 1
    claimed = [post for post in posts if post.status == "publishing" and post.publish_attempt == attempt]
    if not claimed:
        print("このattemptでclaimされた投稿はありません。")
        return 0
    client = client_from_env()
    base_url = os.getenv("IG_IMAGE_BASE_URL") or default_image_base_url()
    failed = 0
    for post in claimed:
        try:
            urls = post.resolve_image_urls(base_url, queue_dir)
            if post.media_type == "CAROUSEL":
                media_id = client.publish_carousel(urls, post.full_caption(), post.alt_text)
            else:
                media_id = client.publish_image(urls[0], post.full_caption(), post.alt_text)
            archive(post, media_id, datetime.now(timezone.utc).isoformat())
            print(f"✓ 投稿成功: {post.slug} -> media_id={media_id}")
        except (InstagramAPIError, PostError) as exc:
            failed += 1
            safe_error = str(exc).replace(os.getenv("IG_ACCESS_TOKEN", ""), "[REDACTED]")[:500]
            post.save(last_error=safe_error)
            print(f"✗ 投稿失敗（publishingのまま停止）: {post.slug}: {safe_error}", file=sys.stderr)
    return 1 if failed else 0


def recover(queue_dir: Path, slug: str, result: str, media_id: str | None) -> int:
    post = find_post(queue_dir, slug)
    if post.status != "publishing":
        raise PostError("recoverはstatus=publishingの投稿だけに使用できます")
    if result == "posted":
        if not media_id:
            raise PostError("--result postedには--media-idが必須です")
        archive(post, media_id, datetime.now(timezone.utc).isoformat())
        print(f"✓ 投稿済みとして復旧: {slug}")
    else:
        post.save(
            status="draft",
            approval=DELETE,
            publish_attempt=DELETE,
            claimed_at=DELETE,
            last_error=DELETE,
        )
        print(f"✓ draftへ戻しました（再確認・再承認が必要）: {slug}")
    return 0


def dry_run(queue_dir: Path) -> int:
    posts, failures = load_and_validate(queue_dir)
    if failures:
        return 1
    due = select_due(posts, datetime.now(timezone.utc))
    base_url = os.getenv("IG_IMAGE_BASE_URL") or default_image_base_url()
    for post in due:
        urls = post.resolve_image_urls(base_url, queue_dir)
        print(f"[DRY-RUN] {post.slug} / {post.media_type} / {post.scheduled_for.isoformat()}")
        print(f"  approval={post.approval.get('content_sha256', '')[:12]} / images={urls}")
    print(f"[DRY-RUN] 投稿対象: {len(due)}件（実投稿なし）")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Instagram安全投稿パブリッシャ")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--validate", action="store_true")
    action.add_argument("--dry-run", action="store_true")
    action.add_argument("--preflight", action="store_true")
    action.add_argument("--approve", metavar="SLUG")
    action.add_argument("--claim", action="store_true")
    action.add_argument("--publish-claimed", action="store_true")
    action.add_argument("--recover", metavar="SLUG")
    parser.add_argument("--queue", default=str(QUEUE_DIR))
    parser.add_argument("--approved-by")
    parser.add_argument("--schedule")
    parser.add_argument("--attempt")
    parser.add_argument("--expected-username", default="digilab.beauty_official")
    parser.add_argument("--result", choices=["posted", "retry"])
    parser.add_argument("--media-id")
    args = parser.parse_args()
    queue_dir = Path(args.queue)
    if not queue_dir.is_dir():
        print(f"キューディレクトリがありません: {queue_dir}", file=sys.stderr)
        return 1

    try:
        if args.validate:
            posts, failures = load_and_validate(queue_dir)
            print(f"検証OK: {len(posts)}件 / 検証NG: {failures}件")
            return 1 if failures else 0
        if args.dry_run:
            return dry_run(queue_dir)
        if args.preflight:
            return preflight(args.expected_username)
        if args.approve:
            if not args.approved_by:
                raise PostError("--approveには--approved-byが必須です")
            return approve(queue_dir, args.approve, args.approved_by, args.schedule)
        if args.claim:
            if not args.attempt:
                raise PostError("--claimには--attemptが必須です")
            return claim_due(queue_dir, args.attempt)
        if args.publish_claimed:
            if not args.attempt:
                raise PostError("--publish-claimedには--attemptが必須です")
            return publish_claimed(queue_dir, args.attempt)
        if args.recover:
            if not args.result:
                raise PostError("--recoverには--resultが必須です")
            return recover(queue_dir, args.recover, args.result, args.media_id)
    except (PostError, InstagramAPIError) as exc:
        print(f"エラー: {exc}", file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
