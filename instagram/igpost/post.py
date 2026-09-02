"""Instagram投稿スペックの読み込み、検証、承認ハッシュ生成。"""

from __future__ import annotations

import hashlib
import json
import re
import struct
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List, Optional

MAX_CAPTION_CHARS = 2200
MAX_HASHTAGS = 30
MAX_CAROUSEL_ITEMS = 10
MAX_IMAGE_BYTES = 8 * 1024 * 1024
MIN_ASPECT_RATIO = 4 / 5
MAX_ASPECT_RATIO = 1.91
MIN_IMAGE_WIDTH = 320
MAX_IMAGE_WIDTH = 1440

VALID_STATUS = {"draft", "ready", "publishing", "posted"}
VALID_MEDIA_TYPE = {"IMAGE", "CAROUSEL"}
IMAGE_SUFFIXES = {".jpg", ".jpeg"}
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class PostError(Exception):
    """投稿スペックの検証エラー。"""


@dataclass
class Post:
    slug: str
    caption: str
    images: List[str]
    path: Path
    media_type: str = "IMAGE"
    hashtags: List[str] = field(default_factory=list)
    alt_text: Optional[str] = None
    scheduled_for: Optional[datetime] = None
    status: str = "draft"
    approval: dict[str, Any] = field(default_factory=dict)
    publish_attempt: Optional[str] = None
    data: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_file(cls, path: Path) -> "Post":
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise PostError(f"{path.name}: JSONの構文エラー: {exc}") from exc
        if not isinstance(raw, dict):
            raise PostError(f"{path.name}: トップレベルはオブジェクトである必要があります")

        images = raw.get("images", [])
        hashtags = raw.get("hashtags", [])
        if not isinstance(images, list):
            raise PostError(f"{path.name}: imagesは配列にしてください")
        if not isinstance(hashtags, list):
            raise PostError(f"{path.name}: hashtagsは配列にしてください")

        scheduled_for = _parse_datetime(raw.get("scheduled_for"), path.name, "scheduled_for")
        approval = raw.get("approval") or {}
        if not isinstance(approval, dict):
            raise PostError(f"{path.name}: approvalはオブジェクトにしてください")

        return cls(
            slug=str(raw.get("slug") or path.stem).strip(),
            caption=str(raw.get("caption", "")),
            images=[str(item) for item in images],
            path=path,
            media_type=str(raw.get("media_type", "IMAGE")).upper().strip(),
            hashtags=[str(tag) for tag in hashtags],
            alt_text=str(raw["alt_text"]).strip() if raw.get("alt_text") else None,
            scheduled_for=scheduled_for,
            status=str(raw.get("status", "draft")).lower().strip(),
            approval=approval,
            publish_attempt=(str(raw["publish_attempt"]) if raw.get("publish_attempt") else None),
            data=raw,
        )

    def validate(self, queue_dir: Optional[Path] = None) -> None:
        errors: List[str] = []

        if not SLUG_RE.fullmatch(self.slug):
            errors.append("slugは半角英小文字・数字・ハイフンのみで指定してください")
        if self.path.stem != self.slug:
            errors.append(f"slugとJSONファイル名を一致させてください ({self.path.stem} != {self.slug})")
        if self.status not in VALID_STATUS:
            errors.append(f"statusは{sorted(VALID_STATUS)}のいずれかです (現在: {self.status})")
        if self.media_type not in VALID_MEDIA_TYPE:
            errors.append(f"media_typeは{sorted(VALID_MEDIA_TYPE)}のいずれかです")

        if not self.images:
            errors.append("imagesは最低1枚必要です")
        if self.media_type == "IMAGE" and len(self.images) != 1:
            errors.append("media_type=IMAGEでは画像を1枚だけ指定してください")
        if self.media_type == "CAROUSEL" and not 2 <= len(self.images) <= MAX_CAROUSEL_ITEMS:
            errors.append(f"CAROUSELは2〜{MAX_CAROUSEL_ITEMS}枚にしてください")

        for image in self.images:
            image_path = Path(image)
            if image_path.name != image or image_path.is_absolute() or ".." in image_path.parts:
                errors.append(f"画像はqueue直下のファイル名だけを指定してください: {image}")
                continue
            if image_path.suffix.lower() not in IMAGE_SUFFIXES:
                errors.append(f"Meta API対応のJPEGのみ使用できます: {image}")
                continue
            if not (image == f"{self.slug}{image_path.suffix.lower()}" or image.startswith(f"{self.slug}-")):
                errors.append(f"画像ファイル名はslugから始めてください: {image}")
            if queue_dir is not None:
                local = queue_dir / image
                if not local.is_file():
                    errors.append(f"画像が見つかりません: {local}")
                else:
                    errors.extend(_validate_jpeg(local))

        if not self.caption.strip():
            errors.append("captionが空です")
        if len(self.hashtags) > MAX_HASHTAGS:
            errors.append(f"ハッシュタグは最大{MAX_HASHTAGS}個です")
        if len(set(self.hashtags)) != len(self.hashtags):
            errors.append("ハッシュタグが重複しています")
        for tag in self.hashtags:
            if not tag.startswith("#") or any(char.isspace() for char in tag):
                errors.append(f"ハッシュタグは#始まり・空白なしで指定してください: {tag}")
        if len(self.full_caption()) > MAX_CAPTION_CHARS:
            errors.append(
                f"本文とハッシュタグの合計が{MAX_CAPTION_CHARS}文字を超えています "
                f"(現在: {len(self.full_caption())})"
            )

        if self.scheduled_for is not None and self.scheduled_for.tzinfo is None:
            errors.append("scheduled_forには+09:00などのタイムゾーンが必須です")
        if self.status in {"ready", "publishing"}:
            if self.scheduled_for is None:
                errors.append("ready/publishingにはscheduled_forが必須です")
            if queue_dir is None:
                errors.append("承認検証にはqueue_dirが必要です")
            else:
                errors.extend(self.approval_errors(queue_dir))
        if self.status == "publishing" and not self.publish_attempt:
            errors.append("publishingにはpublish_attemptが必要です")

        if errors:
            raise PostError(f"{self.path.name}:\n  - " + "\n  - ".join(errors))

    def full_caption(self) -> str:
        caption = self.caption.rstrip()
        return f"{caption}\n\n{' '.join(self.hashtags)}" if self.hashtags else caption

    def is_due(self, now: Optional[datetime] = None) -> bool:
        if self.scheduled_for is None:
            return False
        now = now or datetime.now(timezone.utc)
        return self.scheduled_for <= now

    def content_digest(self, queue_dir: Path) -> str:
        payload = {
            "slug": self.slug,
            "media_type": self.media_type,
            "images": self.images,
            "caption": self.caption,
            "hashtags": self.hashtags,
            "alt_text": self.alt_text,
            "scheduled_for": self.scheduled_for.isoformat() if self.scheduled_for else None,
        }
        digest = hashlib.sha256(
            json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        )
        for filename in self.images:
            path = queue_dir / filename
            if not path.is_file():
                raise PostError(f"{self.path.name}: 画像が見つかりません: {path}")
            digest.update(filename.encode("utf-8"))
            digest.update(path.read_bytes())
        return digest.hexdigest()

    def approval_errors(self, queue_dir: Path) -> List[str]:
        errors: List[str] = []
        approved_by = str(self.approval.get("approved_by", "")).strip()
        approved_at_raw = self.approval.get("approved_at")
        approved_digest = str(self.approval.get("content_sha256", "")).strip()
        if not approved_by:
            errors.append("approval.approved_byがありません")
        if not approved_at_raw:
            errors.append("approval.approved_atがありません")
        else:
            try:
                approved_at = datetime.fromisoformat(str(approved_at_raw))
                if approved_at.tzinfo is None:
                    errors.append("approval.approved_atにはタイムゾーンが必須です")
            except ValueError:
                errors.append("approval.approved_atはISO8601形式にしてください")
        try:
            current = self.content_digest(queue_dir)
            if not approved_digest:
                errors.append("approval.content_sha256がありません")
            elif approved_digest != current:
                errors.append("承認後に本文・予約時刻・画像のいずれかが変更されています。再承認してください")
        except PostError as exc:
            errors.append(str(exc))
        return errors

    def resolve_image_urls(self, base_url: str, queue_dir: Path) -> List[str]:
        if not base_url.startswith("https://"):
            raise PostError("IG_IMAGE_BASE_URLは公開HTTPS URLにしてください")
        urls: List[str] = []
        for filename in self.images:
            local = queue_dir / filename
            if not local.is_file():
                raise PostError(f"{self.path.name}: 画像が見つかりません: {local}")
            urls.append(f"{base_url.rstrip('/')}/{filename}")
        return urls

    def save(self, **updates: Any) -> None:
        for key, value in updates.items():
            if value is _DELETE:
                self.data.pop(key, None)
            else:
                self.data[key] = value
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class _DeleteSentinel:
    pass


_DELETE = _DeleteSentinel()
DELETE = _DELETE


def load_posts(queue_dir: Path) -> List[Post]:
    return [Post.from_file(path) for path in sorted(queue_dir.glob("*.json"))]


def _parse_datetime(value: Any, filename: str, field_name: str) -> Optional[datetime]:
    if value in (None, ""):
        return None
    try:
        return datetime.fromisoformat(str(value))
    except ValueError as exc:
        raise PostError(f"{filename}: {field_name}はISO8601形式にしてください: {exc}") from exc


def _validate_jpeg(path: Path) -> List[str]:
    errors: List[str] = []
    if path.stat().st_size > MAX_IMAGE_BYTES:
        errors.append(f"JPEGは8MB以下にしてください: {path.name}")
    try:
        width, height = _jpeg_dimensions(path)
    except PostError as exc:
        return [str(exc)]
    if not MIN_IMAGE_WIDTH <= width <= MAX_IMAGE_WIDTH:
        errors.append(f"画像幅は{MIN_IMAGE_WIDTH}〜{MAX_IMAGE_WIDTH}pxにしてください: {path.name} ({width}px)")
    ratio = width / height
    if not MIN_ASPECT_RATIO <= ratio <= MAX_ASPECT_RATIO:
        errors.append(f"アスペクト比は4:5〜1.91:1にしてください: {path.name} ({width}x{height})")
    return errors


def _jpeg_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if len(data) < 4 or data[:2] != b"\xff\xd8":
        raise PostError(f"JPEGとして読み取れません: {path.name}")
    index = 2
    sof_markers = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
    while index + 4 <= len(data):
        if data[index] != 0xFF:
            index += 1
            continue
        marker = data[index + 1]
        index += 2
        if marker in {0xD8, 0xD9}:
            continue
        if index + 2 > len(data):
            break
        length = struct.unpack(">H", data[index:index + 2])[0]
        if length < 2 or index + length > len(data):
            break
        if marker in sof_markers and length >= 7:
            height, width = struct.unpack(">HH", data[index + 3:index + 7])
            return width, height
        index += length
    raise PostError(f"JPEGの寸法を取得できません: {path.name}")
