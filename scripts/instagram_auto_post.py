#!/usr/bin/env python3
"""
Instagram 自動投稿スクリプト(Meta Content Publishing API)

投稿キュー(JSON)を読み込み、予約時刻を過ぎた未投稿のものを Instagram へ自動投稿する。
フィード画像 / カルーセル / リール / ストーリーズに対応。

必要なパッケージ:
    pip install requests

環境変数(.env またはCI Secrets):
    IG_USER_ID          Instagram ビジネスアカウントID(数値)
    IG_ACCESS_TOKEN     長期アクセストークン(推奨: システムユーザートークン)
    GRAPH_API_VERSION   Graph APIバージョン(既定: v25.0)
    IG_API_BASE         APIホスト(既定: graph.facebook.com / IGログイン時は graph.instagram.com)
    IG_QUEUE_PATH       投稿キューのパス(既定: marketing/instagram/post_queue.json)

使い方:
    python scripts/instagram_auto_post.py --dry-run      # 投稿せず対象だけ確認
    python scripts/instagram_auto_post.py                # 予約時刻を過ぎたものを投稿
    python scripts/instagram_auto_post.py --post-id p001 # ID指定で即時投稿
    python scripts/instagram_auto_post.py --limit 1      # 1件だけ投稿

詳細な手順は docs/guides/instagram_auto_post_manual.md を参照。
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

JST = ZoneInfo("Asia/Tokyo")

API_BASE = os.getenv("IG_API_BASE", "graph.facebook.com")
API_VERSION = os.getenv("GRAPH_API_VERSION", "v25.0")
ENDPOINT = f"https://{API_BASE}/{API_VERSION}"

IG_USER_ID = os.getenv("IG_USER_ID", "")
ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN", "")
QUEUE_PATH = os.getenv("IG_QUEUE_PATH", "marketing/instagram/post_queue.json")

# 動画コンテナの処理完了待ち(秒)
CONTAINER_POLL_INTERVAL = 10
CONTAINER_TIMEOUT = 600

# API呼び出しのリトライ
MAX_RETRIES = 3
RETRY_BACKOFF = 5


class InstagramPostError(Exception):
    """投稿処理の失敗(APIエラー・入力不備の両方)"""


class MediaNotReady(Exception):
    """メディアの公開URLがまだ配信されていない(次回実行で再試行する)"""


# ---------------------------------------------------------------- 事前検証

# Instagramフィードの許容アスペクト比(幅÷高さ)
MIN_ASPECT_RATIO = 0.8   # 4:5
MAX_ASPECT_RATIO = 1.91  # 1.91:1
MAX_IMAGE_BYTES = 8 * 1024 * 1024


def verify_image(url):
    """
    投稿前に画像の公開URLを検証する。

    GitHub Pagesへの反映待ちなど「まだ取得できない」場合は MediaNotReady を投げ、
    仕様違反(サイズ超過・比率外)は InstagramPostError を投げる。
    """
    try:
        res = requests.get(url, timeout=60, stream=True)
    except requests.RequestException as e:
        raise MediaNotReady(f"画像URLに到達できません: {e}") from e

    if res.status_code == 404:
        raise MediaNotReady(f"画像URLがまだ公開されていません(404): {url}")
    if res.status_code >= 400:
        raise MediaNotReady(f"画像URLの取得に失敗({res.status_code}): {url}")

    content = res.content
    if len(content) > MAX_IMAGE_BYTES:
        raise InstagramPostError(
            f"画像が8MBを超えています({len(content) // 1024 // 1024}MB): {url}"
        )

    content_type = res.headers.get("content-type", "")
    if "image" not in content_type:
        raise InstagramPostError(
            f"画像ではないコンテンツが返りました(content-type={content_type}): {url}"
        )

    try:
        from PIL import Image
    except ImportError:
        print("  [warn] Pillow未導入のため画像サイズの検証をスキップします")
        return

    import io

    with Image.open(io.BytesIO(content)) as image:
        width, height = image.size
        image_format = image.format

    ratio = width / height
    if not MIN_ASPECT_RATIO <= ratio <= MAX_ASPECT_RATIO:
        raise InstagramPostError(
            f"アスペクト比が範囲外です({width}×{height} = {ratio:.2f}:1)。"
            f"{MIN_ASPECT_RATIO}〜{MAX_ASPECT_RATIO} に収めてください: {url}"
        )
    if image_format != "JPEG":
        print(f"  [warn] JPEG以外の形式です({image_format})。失敗する場合はJPEGに変換してください")

    print(f"  画像OK: {width}×{height} ({ratio:.2f}:1) / {len(content) // 1024}KB")


def verify_video(url):
    """動画URLが到達可能かだけ確認する(内容の検証はInstagram側に任せる)。"""
    try:
        res = requests.head(url, timeout=60, allow_redirects=True)
    except requests.RequestException as e:
        raise MediaNotReady(f"動画URLに到達できません: {e}") from e

    if res.status_code >= 400:
        raise MediaNotReady(f"動画URLがまだ公開されていません({res.status_code}): {url}")


def verify_media(post):
    """投稿タイプに応じて、使用するすべてのメディアURLを検証する。"""
    media_type = post.get("type", "IMAGE").upper()

    if media_type == "CAROUSEL":
        for child in post.get("children") or []:
            if child.get("video_url"):
                verify_video(child["video_url"])
            elif child.get("image_url"):
                verify_image(child["image_url"])
        return

    if post.get("video_url"):
        verify_video(post["video_url"])
    elif post.get("image_url"):
        verify_image(post["image_url"])


# ---------------------------------------------------------------- API 共通

def _request(method, path, params):
    """Graph APIを叩く。一時的なエラーは指数バックオフでリトライする。"""
    url = f"{ENDPOINT}/{path}"
    payload = dict(params, access_token=ACCESS_TOKEN)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            if method == "GET":
                res = requests.get(url, params=payload, timeout=60)
            else:
                res = requests.post(url, data=payload, timeout=120)
        except requests.RequestException as e:
            if attempt == MAX_RETRIES:
                raise InstagramPostError(f"通信エラー: {e}") from e
            time.sleep(RETRY_BACKOFF * attempt)
            continue

        if res.status_code < 400:
            return res.json()

        # 429(レート制限)と5xxはリトライ、それ以外は即エラー
        if res.status_code in (429, 500, 502, 503, 504) and attempt < MAX_RETRIES:
            time.sleep(RETRY_BACKOFF * attempt)
            continue

        raise InstagramPostError(
            f"APIエラー [{res.status_code}] {path}: {_error_message(res)}"
        )

    raise InstagramPostError(f"APIエラー: {path} のリトライ上限に達しました")


def _error_message(res):
    try:
        err = res.json().get("error", {})
        return (
            f"{err.get('message', res.text)} "
            f"(code={err.get('code')}, subcode={err.get('error_subcode')})"
        )
    except ValueError:
        return res.text


def api_get(path, params=None):
    return _request("GET", path, params or {})


def api_post(path, params):
    return _request("POST", path, params)


# ---------------------------------------------------------------- 投稿処理

def check_publishing_limit():
    """24時間あたりの投稿枠の残りを返す(上限50件)。取得できない場合はNone。"""
    try:
        data = api_get(
            f"{IG_USER_ID}/content_publishing_limit",
            {"fields": "config,quota_usage"},
        )
    except InstagramPostError as e:
        print(f"  [warn] 投稿枠の取得に失敗(処理は継続): {e}")
        return None

    entry = (data.get("data") or [{}])[0]
    used = entry.get("quota_usage", 0)
    total = (entry.get("config") or {}).get("quota_total", 50)
    print(f"  投稿枠: {used}/{total} 使用済み(24時間あたり)")
    return total - used


def create_container(params):
    """メディアコンテナを作成し、コンテナIDを返す。"""
    res = api_post(f"{IG_USER_ID}/media", params)
    container_id = res.get("id")
    if not container_id:
        raise InstagramPostError(f"コンテナIDが取得できません: {res}")
    return container_id


def wait_for_container(container_id):
    """動画コンテナの処理完了を待つ。画像は即FINISHEDになる。"""
    deadline = time.time() + CONTAINER_TIMEOUT
    while time.time() < deadline:
        res = api_get(container_id, {"fields": "status_code,status"})
        status = res.get("status_code")

        if status == "FINISHED":
            return
        if status in ("ERROR", "EXPIRED"):
            raise InstagramPostError(
                f"コンテナ処理に失敗: {status} / {res.get('status')}"
            )

        print(f"  コンテナ処理中... ({status})")
        time.sleep(CONTAINER_POLL_INTERVAL)

    raise InstagramPostError(
        f"コンテナ処理がタイムアウトしました({CONTAINER_TIMEOUT}秒)"
    )


def build_container_params(post):
    """投稿タイプごとにコンテナ作成パラメータを組み立てる。"""
    media_type = post.get("type", "IMAGE").upper()
    caption = post.get("caption", "")

    if media_type == "IMAGE":
        params = {"image_url": _require(post, "image_url"), "caption": caption}

    elif media_type == "REELS":
        params = {
            "media_type": "REELS",
            "video_url": _require(post, "video_url"),
            "caption": caption,
            "share_to_feed": str(post.get("share_to_feed", True)).lower(),
        }
        if post.get("cover_url"):
            params["cover_url"] = post["cover_url"]
        if post.get("thumb_offset") is not None:
            params["thumb_offset"] = post["thumb_offset"]

    elif media_type == "STORIES":
        params = {"media_type": "STORIES"}
        if post.get("video_url"):
            params["video_url"] = post["video_url"]
        else:
            params["image_url"] = _require(post, "image_url")

    elif media_type == "CAROUSEL":
        params = {"media_type": "CAROUSEL", "caption": caption}

    else:
        raise InstagramPostError(f"未対応の投稿タイプです: {media_type}")

    if post.get("location_id"):
        params["location_id"] = post["location_id"]

    return media_type, params


def create_carousel_children(post):
    """カルーセルの子メディア(2〜10枚)を作成し、コンテナIDのリストを返す。"""
    children = post.get("children") or []
    if not 2 <= len(children) <= 10:
        raise InstagramPostError(
            f"カルーセルは2〜10枚である必要があります(現在{len(children)}枚)"
        )

    ids = []
    for i, child in enumerate(children, 1):
        params = {"is_carousel_item": "true"}
        if child.get("video_url"):
            params["media_type"] = "VIDEO"
            params["video_url"] = child["video_url"]
        else:
            params["image_url"] = _require(child, "image_url")

        child_id = create_container(params)
        wait_for_container(child_id)
        print(f"  カルーセル {i}/{len(children)} 作成完了: {child_id}")
        ids.append(child_id)

    return ids


def publish_post(post):
    """1件を投稿し、公開されたメディアの情報を返す。"""
    verify_media(post)
    media_type, params = build_container_params(post)

    if media_type == "CAROUSEL":
        params["children"] = ",".join(create_carousel_children(post))

    container_id = create_container(params)
    print(f"  コンテナ作成: {container_id}")
    wait_for_container(container_id)

    res = api_post(f"{IG_USER_ID}/media_publish", {"creation_id": container_id})
    media_id = res.get("id")
    if not media_id:
        raise InstagramPostError(f"公開に失敗しました: {res}")

    permalink = ""
    try:
        permalink = api_get(media_id, {"fields": "permalink"}).get("permalink", "")
    except InstagramPostError:
        pass  # 公開自体は成功しているのでURL取得失敗は無視する

    return {"media_id": media_id, "permalink": permalink}


# ---------------------------------------------------------------- キュー操作

def _require(obj, key):
    value = obj.get(key)
    if not value:
        raise InstagramPostError(f"必須項目 '{key}' がありません")
    return value


def load_queue(path):
    if not os.path.exists(path):
        raise SystemExit(f"投稿キューが見つかりません: {path}")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else data.get("posts", [])


def save_queue(path, posts):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"posts": posts}, f, ensure_ascii=False, indent=2)
        f.write("\n")


def parse_scheduled_at(value):
    """予約時刻(JST)をパースする。タイムゾーン省略時はJSTとみなす。"""
    dt = datetime.fromisoformat(value)
    return dt.replace(tzinfo=JST) if dt.tzinfo is None else dt


def select_targets(posts, now, post_id=None, limit=None, retry_errors=False):
    """投稿対象を抽出する。"""
    postable = [None, "", "scheduled"] + (["error"] if retry_errors else [])

    targets = []
    for post in posts:
        if post_id:
            if post.get("id") == post_id:
                targets.append(post)
            continue

        if post.get("status") not in postable:
            continue

        scheduled_at = post.get("scheduled_at")
        if not scheduled_at:
            continue
        try:
            if parse_scheduled_at(scheduled_at) <= now:
                targets.append(post)
        except ValueError:
            print(f"  [warn] {post.get('id')}: 予約時刻の書式が不正です({scheduled_at})")

    targets.sort(key=lambda p: p.get("scheduled_at", ""))
    return targets[:limit] if limit else targets


# ---------------------------------------------------------------- エントリ

def main():
    parser = argparse.ArgumentParser(description="Instagram 自動投稿")
    parser.add_argument("--queue", default=QUEUE_PATH, help="投稿キューのパス")
    parser.add_argument("--post-id", help="ID指定で即時投稿(予約時刻を無視)")
    parser.add_argument("--limit", type=int, help="1回の実行で投稿する最大件数")
    parser.add_argument("--dry-run", action="store_true", help="投稿せず対象のみ表示")
    parser.add_argument(
        "--retry-errors", action="store_true", help="status=error の投稿も再試行する"
    )
    args = parser.parse_args()

    now = datetime.now(JST)
    print(f"=== Instagram 自動投稿 {now:%Y-%m-%d %H:%M:%S} JST ===")
    print(f"API: {ENDPOINT}")

    posts = load_queue(args.queue)
    targets = select_targets(
        posts, now, args.post_id, args.limit, args.retry_errors
    )

    if not targets:
        print("投稿対象はありません。")
        return 0

    print(f"投稿対象: {len(targets)}件")
    for post in targets:
        print(f"  - {post.get('id')} [{post.get('type', 'IMAGE')}] {post.get('scheduled_at', '')}")

    if args.dry_run:
        print("\n[dry-run] 実際の投稿は行いませんでした。")
        return 0

    if not IG_USER_ID or not ACCESS_TOKEN:
        raise SystemExit("IG_USER_ID と IG_ACCESS_TOKEN を設定してください。")

    remaining = check_publishing_limit()
    if remaining is not None and remaining <= 0:
        print("24時間あたりの投稿上限に達しています。次回の実行まで待機します。")
        return 0

    failed = 0
    skipped = 0
    for post in targets:
        print(f"\n▶ {post.get('id')} を投稿します")
        try:
            result = publish_post(post)
            post["status"] = "published"
            post["published_at"] = datetime.now(JST).isoformat(timespec="seconds")
            post["media_id"] = result["media_id"]
            post["permalink"] = result["permalink"]
            post.pop("error", None)
            print(f"  ✅ 公開完了: {result['permalink'] or result['media_id']}")
        except MediaNotReady as e:
            # 画像の配信待ちなど。statusは変えず、次回の実行で再試行する
            skipped += 1
            print(f"  ⏳ 見送り(次回再試行): {e}")
        except InstagramPostError as e:
            failed += 1
            post["status"] = "error"
            post["error"] = str(e)
            print(f"  ❌ 失敗: {e}")

        save_queue(args.queue, posts)

    published = len(targets) - failed - skipped
    print(f"\n完了: 成功 {published}件 / 見送り {skipped}件 / 失敗 {failed}件")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
