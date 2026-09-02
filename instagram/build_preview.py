#!/usr/bin/env python3
"""Netlify Deploy Preview用のInstagram投稿確認ページを生成する。"""

from __future__ import annotations

import argparse
import base64
import html
import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))

from igpost import Post, PostError  # noqa: E402

HERE = Path(__file__).resolve().parent
QUEUE_DIR = HERE / "queue"
POSTED_DIR = HERE / "posted"
DEFAULT_OUTPUT = HERE.parent / "public" / "instagram" / "index.html"
JST = ZoneInfo("Asia/Tokyo")
STATUS_LABEL = {
    "draft": "下書き",
    "ready": "承認済み・投稿待ち",
    "publishing": "投稿処理中・自動再試行停止",
    "posted": "投稿済み",
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def image_data_uri(directory: Path, filename: str) -> str | None:
    path = directory / filename
    if not path.is_file():
        return None
    return "data:image/jpeg;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def load_section(directory: Path) -> tuple[list[Post], list[str]]:
    posts: list[Post] = []
    errors: list[str] = []
    for path in sorted(directory.glob("*.json")):
        try:
            post = Post.from_file(path)
            post.validate(directory)
            posts.append(post)
        except PostError as exc:
            errors.append(str(exc))
    return posts, errors


def approval_text(post: Post) -> str:
    if post.status == "draft":
        return "未承認"
    reviewer = post.approval.get("approved_by", "不明")
    digest = str(post.approval.get("content_sha256", ""))[:12]
    return f"承認者: {reviewer} / 内容ハッシュ: {digest}"


def render_card(post: Post, directory: Path) -> str:
    image = image_data_uri(directory, post.images[0]) if post.images else None
    media = (
        f'<img class="thumb" src="{image}" alt="{esc(post.alt_text or post.slug)}">'
        if image else '<div class="thumb empty">画像なし</div>'
    )
    scheduled = "未設定"
    if post.scheduled_for:
        scheduled = post.scheduled_for.astimezone(JST).strftime("%Y-%m-%d %H:%M JST")
    tags = " ".join(post.hashtags)
    caption = esc(post.caption).replace("\n", "<br>")
    last_error = ""
    if post.data.get("last_error"):
        last_error = f'<p class="error">停止理由: {esc(post.data["last_error"])}</p>'
    return f"""
    <article class="card">
      <div class="media">{media}</div>
      <div class="body">
        <div><span class="badge {esc(post.status)}">{esc(STATUS_LABEL.get(post.status, post.status))}</span></div>
        <h3>{esc(post.slug)}</h3>
        <p class="meta">予約: {esc(scheduled)}<br>{esc(approval_text(post))}</p>
        <p>{caption}</p>
        <p class="tags">{esc(tags)}</p>
        {last_error}
      </div>
    </article>"""


def render_section(title: str, posts: list[Post], directory: Path) -> str:
    cards = "".join(render_card(post, directory) for post in posts)
    if not cards:
        cards = '<p class="notice">該当する投稿はありません。</p>'
    return f'<section><h2>{esc(title)} <span>{len(posts)}</span></h2><div class="grid">{cards}</div></section>'


def build(output: Path) -> None:
    queue, queue_errors = load_section(QUEUE_DIR)
    posted, posted_errors = load_section(POSTED_DIR)
    errors = queue_errors + posted_errors
    error_html = ""
    if errors:
        items = "".join(f"<li>{esc(error)}</li>" for error in errors)
        error_html = f'<aside class="errors"><strong>検証エラー（承認・投稿不可）</strong><ul>{items}</ul></aside>'
    generated = datetime.now(timezone.utc).astimezone(JST).strftime("%Y-%m-%d %H:%M JST")
    counts = {status: sum(post.status == status for post in queue) for status in STATUS_LABEL}
    document = TEMPLATE.format(
        generated=generated,
        ready=counts["ready"],
        draft=counts["draft"],
        publishing=counts["publishing"],
        errors=error_html,
        queue=render_section("投稿キュー", queue, QUEUE_DIR),
        posted=render_section("投稿済みアーカイブ", posted, POSTED_DIR),
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(document, encoding="utf-8")
    print(f"✓ プレビュー生成: {output} / queue={len(queue)} / errors={len(errors)}")


TEMPLATE = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow,noarchive">
<title>Instagram投稿承認プレビュー | 一般社団法人デジラボビュティ</title>
<style>
:root{{--lav:#8b77c7;--soft:#f3effb;--ink:#2c2740;--muted:#6c657e;--line:#ded6ef;--ok:#18794e;--warn:#9a6700;--danger:#b42318}}
*{{box-sizing:border-box}} body{{margin:0;background:#faf9fd;color:var(--ink);font:15px/1.7 system-ui,-apple-system,"Noto Sans JP",sans-serif}}
.wrap{{max-width:1100px;margin:auto;padding:28px 18px 72px}} header{{text-align:center}} h1{{font-size:clamp(22px,4vw,32px);margin:.3em 0}}
.brand{{color:var(--lav);font-weight:700;letter-spacing:.08em}} .meta,.sub{{color:var(--muted);font-size:13px}}
.stats{{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin:20px 0}} .stat{{background:#fff;border:1px solid var(--line);border-radius:12px;padding:10px 18px}}
.stat b{{font-size:24px;display:block}} .notice,.errors{{background:#fff;border:1px solid var(--line);border-radius:12px;padding:18px}}
.errors{{border-color:#f4b4ae;color:var(--danger);margin:20px 0;text-align:left}} h2{{margin-top:36px;border-bottom:2px solid var(--line);padding-bottom:8px;font-size:19px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:18px}} .card{{background:#fff;border:1px solid var(--line);border-radius:16px;overflow:hidden}}
.media{{aspect-ratio:1/1;background:var(--soft)}} .thumb{{width:100%;height:100%;object-fit:contain;display:flex;align-items:center;justify-content:center}}
.body{{padding:16px}} h3{{font-size:13px;color:var(--muted);word-break:break-all}} .badge{{display:inline-block;border-radius:999px;padding:3px 11px;background:var(--soft);font-size:12px;font-weight:700}}
.badge.ready{{background:#e8f5ee;color:var(--ok)}} .badge.draft{{background:#fff3d6;color:var(--warn)}} .badge.publishing{{background:#fde9e7;color:var(--danger)}}
.tags{{color:var(--lav);font-size:12px}} .error{{color:var(--danger);font-weight:700}} footer{{margin-top:48px;color:var(--muted);font-size:12px;text-align:center}}
</style>
</head>
<body><main class="wrap">
<header><div class="brand">一般社団法人デジラボビュティ</div><h1>Instagram 投稿承認プレビュー</h1>
<p class="sub">閲覧しただけでは承認になりません。内容ハッシュ付きの承認だけが投稿対象です。生成 {generated}</p>
<div class="stats"><div class="stat"><b>{ready}</b>承認済み</div><div class="stat"><b>{draft}</b>下書き</div><div class="stat"><b>{publishing}</b>処理停止中</div></div></header>
{errors}{queue}{posted}
<footer>Netlify Deploy Preview専用。公開前の機密素材は、この公開リポジトリに保存しないでください。</footer>
</main></body></html>"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()
    build(Path(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
