from __future__ import annotations

import json
import struct
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

INSTAGRAM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(INSTAGRAM_DIR))

from igpost import Post, PostError  # noqa: E402
import publish  # noqa: E402


def write_jpeg(path: Path, width: int = 1080, height: int = 1080) -> None:
    # 検証器に必要なSOI/SOFセグメントだけを持つテスト用バイト列。
    sof = b"\xff\xc0\x00\x11\x08" + struct.pack(">HH", height, width) + b"\x03" + b"\x01\x11\x00" * 3
    path.write_bytes(b"\xff\xd8" + sof + b"\xff\xd9")


def write_spec(queue: Path, slug: str = "2026-09-03-safe-post", **updates: object) -> Path:
    data = {
        "slug": slug,
        "media_type": "IMAGE",
        "images": [f"{slug}.jpg"],
        "caption": "人が確認した内容だけを投稿します。",
        "hashtags": ["#美容AI", "#デジラボビュティ"],
        "alt_text": "白い背景の告知画像",
        "scheduled_for": None,
        "status": "draft",
    }
    data.update(updates)
    path = queue / f"{slug}.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    write_jpeg(queue / f"{slug}.jpg")
    return path


class PostValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.queue = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_missing_status_defaults_to_draft(self) -> None:
        path = write_spec(self.queue)
        data = json.loads(path.read_text(encoding="utf-8"))
        del data["status"]
        path.write_text(json.dumps(data), encoding="utf-8")
        post = Post.from_file(path)
        self.assertEqual(post.status, "draft")
        post.validate(self.queue)

    def test_ready_requires_schedule_and_approval(self) -> None:
        post = Post.from_file(write_spec(self.queue, status="ready"))
        with self.assertRaisesRegex(PostError, "scheduled_for"):
            post.validate(self.queue)

    def test_naive_schedule_is_rejected(self) -> None:
        post = Post.from_file(write_spec(self.queue, scheduled_for="2026-09-03T10:00:00"))
        with self.assertRaisesRegex(PostError, "タイムゾーン"):
            post.validate(self.queue)

    def test_png_is_rejected(self) -> None:
        path = write_spec(self.queue)
        data = json.loads(path.read_text(encoding="utf-8"))
        data["images"] = ["2026-09-03-safe-post.png"]
        path.write_text(json.dumps(data), encoding="utf-8")
        (self.queue / "2026-09-03-safe-post.png").write_bytes(b"png")
        with self.assertRaisesRegex(PostError, "JPEG"):
            Post.from_file(path).validate(self.queue)

    def test_path_traversal_is_rejected(self) -> None:
        path = write_spec(self.queue)
        data = json.loads(path.read_text(encoding="utf-8"))
        data["images"] = ["../outside.jpg"]
        path.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaisesRegex(PostError, "queue直下"):
            Post.from_file(path).validate(self.queue)


class ApprovalWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.queue = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_approval_digest_detects_caption_change(self) -> None:
        path = write_spec(self.queue)
        schedule = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        self.assertEqual(publish.approve(self.queue, path.stem, "reviewer", schedule), 0)
        approved = Post.from_file(path)
        approved.validate(self.queue)
        data = json.loads(path.read_text(encoding="utf-8"))
        data["caption"] = "承認後に変更された本文"
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        with self.assertRaisesRegex(PostError, "再承認"):
            Post.from_file(path).validate(self.queue)

    def test_approval_digest_detects_image_change(self) -> None:
        path = write_spec(self.queue)
        schedule = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        publish.approve(self.queue, path.stem, "reviewer", schedule)
        image = self.queue / "2026-09-03-safe-post.jpg"
        image.write_bytes(image.read_bytes() + b"changed")
        with self.assertRaisesRegex(PostError, "再承認"):
            Post.from_file(path).validate(self.queue)

    def test_due_post_is_claimed_before_publish(self) -> None:
        path = write_spec(self.queue)
        schedule = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
        publish.approve(self.queue, path.stem, "reviewer", schedule)
        self.assertEqual(publish.claim_due(self.queue, "run-1"), 0)
        claimed = Post.from_file(path)
        self.assertEqual(claimed.status, "publishing")
        self.assertEqual(claimed.publish_attempt, "run-1")
        claimed.validate(self.queue)

    def test_retry_recovery_forces_reapproval(self) -> None:
        path = write_spec(self.queue)
        schedule = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
        publish.approve(self.queue, path.stem, "reviewer", schedule)
        publish.claim_due(self.queue, "run-1")
        publish.recover(self.queue, path.stem, "retry", None)
        recovered = Post.from_file(path)
        self.assertEqual(recovered.status, "draft")
        self.assertEqual(recovered.approval, {})

    def test_publishing_post_cannot_be_reapproved(self) -> None:
        path = write_spec(self.queue)
        schedule = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
        publish.approve(self.queue, path.stem, "reviewer", schedule)
        publish.claim_due(self.queue, "run-1")
        with self.assertRaisesRegex(PostError, "recover"):
            publish.approve(self.queue, path.stem, "reviewer", schedule)


if __name__ == "__main__":
    unittest.main()
