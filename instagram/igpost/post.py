"""投稿スペック(FABLE5 が生成する JSON)の読み込み・検証・整形。

1件の投稿は次の2ファイルで構成される(同一 slug):

    instagram/queue/<slug>.json   … 投稿スペック(本モジュールが扱う)
    instagram/queue/<slug>.png    … 投稿画像(caption 内の images で参照)

JSON スキーマ:

    {
      "slug":          "2026-08-10-ai-counseling",   # 必須・ファイル名と一致
      "media_type":    "IMAGE",                       # IMAGE | CAROUSEL(既定 IMAGE)
      "images":        ["2026-08-10-ai-counseling.png"],  # 必須・queue 相対 or 絶対URL
      "caption":       "本文…",                       # 必須
      "hashtags":      ["#美容AI", "#エステ"],         # 任意・最大30
      "alt_text":      "代替テキスト",                 # 任意(アクセシビリティ)
      "scheduled_for": "2026-08-10T10:00:00+09:00",   # 任意・この時刻以降に投稿
      "status":        "ready"                         # draft | ready | posted
    }
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

# Instagram の仕様上の上限
MAX_CAPTION_CHARS = 2200
MAX_HASHTAGS = 30
MAX_CAROUSEL_ITEMS = 10

VALID_STATUS = {"draft", "ready", "posted"}
VALID_MEDIA_TYPE = {"IMAGE", "CAROUSEL"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg"}


class PostError(Exception):
    """投稿スペックの検証エラー。"""


@dataclass
class Post:
    """1件の Instagram 投稿スペック。"""

    slug: str
    caption: str
    images: List[str]
    path: Path
    media_type: str = "IMAGE"
    hashtags: List[str] = field(default_factory=list)
    alt_text: Optional[str] = None
    scheduled_for: Optional[datetime] = None
    status: str = "ready"

    # ---- 読み込み ---------------------------------------------------------

    @classmethod
    def from_file(cls, path: Path) -> "Post":
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise PostError(f"{path.name}: JSON の構文エラー: {exc}") from exc
        if not isinstance(raw, dict):
            raise PostError(f"{path.name}: トップレベルはオブジェクトである必要があります")

        slug = str(raw.get("slug") or path.stem).strip()
        media_type = str(raw.get("media_type", "IMAGE")).upper().strip()
        images = raw.get("images", [])
        if isinstance(images, str):
            images = [images]

        scheduled_raw = raw.get("scheduled_for")
        scheduled_for = None
        if scheduled_raw:
            try:
                scheduled_for = datetime.fromisoformat(str(scheduled_raw))
            except ValueError as exc:
                raise PostError(
                    f"{path.name}: scheduled_for は ISO8601 形式にしてください "
                    f"(例 2026-08-10T10:00:00+09:00): {exc}"
                ) from exc

        post = cls(
            slug=slug,
            caption=str(raw.get("caption", "")),
            images=[str(i) for i in images],
            path=path,
            media_type=media_type,
            hashtags=[str(h) for h in raw.get("hashtags", [])],
            alt_text=(str(raw["alt_text"]) if raw.get("alt_text") else None),
            scheduled_for=scheduled_for,
            status=str(raw.get("status", "ready")).lower().strip(),
        )
        return post

    # ---- 検証 -------------------------------------------------------------

    def validate(self) -> None:
        """内容の妥当性を検証。問題があれば PostError を送出。"""
        errors: List[str] = []

        if not self.slug:
            errors.append("slug が空です")
        if self.status not in VALID_STATUS:
            errors.append(f"status は {sorted(VALID_STATUS)} のいずれか (現在: {self.status})")
        if self.media_type not in VALID_MEDIA_TYPE:
            errors.append(f"media_type は {sorted(VALID_MEDIA_TYPE)} のいずれか (現在: {self.media_type})")

        if not self.images:
            errors.append("images が空です(最低1枚必要)")
        if self.media_type == "IMAGE" and len(self.images) != 1:
            errors.append("media_type=IMAGE は images をちょうど1枚にしてください")
        if self.media_type == "CAROUSEL":
            if not 2 <= len(self.images) <= MAX_CAROUSEL_ITEMS:
                errors.append(f"CAROUSEL は 2〜{MAX_CAROUSEL_ITEMS} 枚にしてください")

        for img in self.images:
            if not _is_url(img) and Path(img).suffix.lower() not in IMAGE_SUFFIXES:
                errors.append(f"画像の拡張子は png/jpg/jpeg にしてください: {img}")

        if not self.caption.strip():
            errors.append("caption が空です")
        if len(self.hashtags) > MAX_HASHTAGS:
            errors.append(f"ハッシュタグは最大 {MAX_HASHTAGS} 個です (現在: {len(self.hashtags)})")
        for tag in self.hashtags:
            if not tag.startswith("#"):
                errors.append(f"ハッシュタグは # で始めてください: {tag}")

        caption = self.full_caption()
        if len(caption) > MAX_CAPTION_CHARS:
            errors.append(
                f"キャプション(本文+ハッシュタグ)が {MAX_CAPTION_CHARS} 文字を超えています "
                f"(現在: {len(caption)})"
            )

        if errors:
            raise PostError(f"{self.path.name}:\n  - " + "\n  - ".join(errors))

    # ---- 整形 -------------------------------------------------------------

    def full_caption(self) -> str:
        """本文とハッシュタグを結合した最終キャプション。"""
        caption = self.caption.rstrip()
        if self.hashtags:
            caption = f"{caption}\n\n{' '.join(self.hashtags)}"
        return caption

    def is_due(self, now: Optional[datetime] = None) -> bool:
        """scheduled_for が未指定、または現在時刻以前なら True。"""
        if self.scheduled_for is None:
            return True
        now = now or datetime.now(timezone.utc)
        scheduled = self.scheduled_for
        if scheduled.tzinfo is None:  # タイムゾーン無指定は JST とみなさず UTC 扱いを避ける
            scheduled = scheduled.replace(tzinfo=timezone.utc)
        return scheduled <= now

    def resolve_image_urls(self, base_url: str, queue_dir: Path) -> List[str]:
        """images を公開URLへ解決。絶対URLはそのまま、相対はローカル存在も確認。"""
        urls: List[str] = []
        for img in self.images:
            if _is_url(img):
                urls.append(img)
                continue
            local = queue_dir / img
            if not local.exists():
                raise PostError(f"{self.path.name}: 画像が見つかりません: {local}")
            urls.append(f"{base_url.rstrip('/')}/{img}")
        return urls


def _is_url(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://")


def load_posts(queue_dir: Path) -> List[Post]:
    """queue ディレクトリ内の *.json をすべて読み込む(slug 昇順)。"""
    posts = [Post.from_file(p) for p in sorted(queue_dir.glob("*.json"))]
    return posts
