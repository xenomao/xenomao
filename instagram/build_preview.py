#!/usr/bin/env python3
"""投稿キューのプレビューページを生成する。

instagram/queue/ と instagram/posted/ の投稿スペックを読み込み、
ブラウザで内容を確認できる自己完結型ダッシュボード HTML を
public/instagram/index.html に出力する(画像は base64 埋め込み)。

使い方:
  python instagram/build_preview.py
  python instagram/build_preview.py --output path/to/index.html
"""

from __future__ import annotations

import argparse
import base64
import html
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from igpost import Post, PostError, load_posts  # noqa: E402

HERE = Path(__file__).resolve().parent
QUEUE_DIR = HERE / "queue"
POSTED_DIR = HERE / "posted"
DEFAULT_OUTPUT = HERE.parent / "public" / "instagram" / "index.html"

STATUS_LABEL = {"draft": "下書き", "ready": "投稿可", "posted": "投稿済み"}
MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}


def image_data_uri(directory: Path, filename: str) -> str | None:
    if filename.startswith("http"):
        return filename
    path = directory / filename
    if not path.exists():
        return None
    mime = MIME.get(path.suffix.lower(), "image/png")
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def render_card(post: Post, directory: Path) -> str:
    status = post.status if post.status in STATUS_LABEL else "draft"
    badge = STATUS_LABEL.get(status, status)
    uri = image_data_uri(directory, post.images[0]) if post.images else None
    if uri:
        media = f'<img class="thumb" src="{uri}" alt="{esc(post.alt_text or post.slug)}">'
    else:
        media = '<div class="thumb thumb--empty">画像未生成</div>'

    extra = ""
    if len(post.images) > 1:
        extra = f'<span class="pill">カルーセル {len(post.images)}枚</span>'

    schedule = ""
    if post.scheduled_for:
        schedule = f'<span class="pill">⏰ {esc(post.scheduled_for.isoformat())}</span>'

    tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in post.hashtags)
    caption_html = esc(post.caption).replace("\n", "<br>")

    return f"""
    <article class="card">
      <div class="card__media">{media}</div>
      <div class="card__body">
        <div class="card__meta">
          <span class="badge badge--{status}">{badge}</span>
          <span class="pill">{esc(post.media_type)}</span>
          {extra}{schedule}
        </div>
        <h3 class="card__slug">{esc(post.slug)}</h3>
        <p class="card__caption">{caption_html}</p>
        <div class="card__tags">{tags}</div>
      </div>
    </article>"""


def render_section(title: str, posts: list[Post], directory: Path, empty_note: str) -> str:
    if not posts:
        cards = f'<p class="empty">{empty_note}</p>'
    else:
        cards = '<div class="grid">' + "".join(render_card(p, directory) for p in posts) + "</div>"
    return f'<section><h2 class="section-title">{esc(title)} <span class="count">{len(posts)}</span></h2>{cards}</section>'


def safe_load(directory: Path) -> list[Post]:
    posts: list[Post] = []
    for path in sorted(directory.glob("*.json")):
        try:
            posts.append(Post.from_file(path))
        except PostError as exc:
            print(f"警告: 読み込みスキップ {path.name}: {exc}", file=sys.stderr)
    return posts


def build(output: Path) -> None:
    queue = safe_load(QUEUE_DIR)
    posted = safe_load(POSTED_DIR)

    counts = {"draft": 0, "ready": 0, "posted": 0}
    for p in queue:
        counts[p.status if p.status in counts else "draft"] += 1
    generated = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M %Z")

    queue_html = render_section("投稿キュー", queue, QUEUE_DIR, "キューは空です。")
    posted_html = render_section("投稿済みアーカイブ", posted, POSTED_DIR, "まだ投稿済みの記録はありません。")

    doc = PAGE_TEMPLATE.format(
        generated=esc(generated),
        ready=counts["ready"],
        draft=counts["draft"],
        posted=len(posted),
        queue=queue_html,
        posted_section=posted_html,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(doc, encoding="utf-8")
    print(f"✓ プレビュー生成: {output}  (キュー {len(queue)}件 / 投稿済み {len(posted)}件)")


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Instagram 投稿プレビュー | Digilab beauty</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;600&family=Noto+Sans+JP:wght@400;500;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --lav: #b7a5e0; --lav-soft: #f3effb; --lav-line: #e5ddf5;
    --ink: #2c2740; --muted: #7c7592; --bg: #faf8fe; --card: #ffffff;
    --ok: #3aa76d; --ok-bg: #e6f6ee; --warn: #c8891f; --warn-bg: #fbf1dc;
    --posted: #6b6480; --posted-bg: #efedf5;
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: var(--bg); color: var(--ink);
    font-family: "Noto Sans JP", system-ui, sans-serif; line-height: 1.7; }}
  .wrap {{ max-width: 1080px; margin: 0 auto; padding: 32px 20px 80px; }}
  header {{ text-align: center; margin-bottom: 28px; }}
  .logo {{ font-family: Poppins, sans-serif; font-weight: 600; letter-spacing: .22em;
    color: var(--lav); text-transform: none; font-size: 14px; }}
  h1 {{ font-size: clamp(22px, 4vw, 30px); margin: 6px 0 4px; }}
  .sub {{ color: var(--muted); font-size: 13px; margin: 0; }}
  .stats {{ display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; margin: 22px 0 8px; }}
  .stat {{ background: var(--card); border: 1px solid var(--lav-line); border-radius: 14px;
    padding: 12px 22px; min-width: 92px; text-align: center; }}
  .stat b {{ display: block; font-size: 26px; font-family: Poppins, sans-serif; }}
  .stat span {{ font-size: 12px; color: var(--muted); }}
  .section-title {{ font-size: 18px; margin: 40px 0 16px; padding-bottom: 8px;
    border-bottom: 2px solid var(--lav-line); }}
  .count {{ display: inline-block; background: var(--lav-soft); color: var(--lav);
    font-size: 13px; border-radius: 999px; padding: 1px 12px; vertical-align: middle; margin-left: 6px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }}
  .card {{ background: var(--card); border: 1px solid var(--lav-line); border-radius: 18px;
    overflow: hidden; display: flex; flex-direction: column; box-shadow: 0 6px 20px rgba(120,100,180,.06); }}
  .card__media {{ aspect-ratio: 1/1; background: var(--lav-soft); }}
  .thumb {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
  .thumb--empty {{ display: flex; align-items: center; justify-content: center;
    color: var(--muted); font-size: 14px; height: 100%; }}
  .card__body {{ padding: 16px 18px 18px; }}
  .card__meta {{ display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 10px; }}
  .badge {{ font-size: 12px; font-weight: 700; border-radius: 999px; padding: 2px 12px; }}
  .badge--ready {{ background: var(--ok-bg); color: var(--ok); }}
  .badge--draft {{ background: var(--warn-bg); color: var(--warn); }}
  .badge--posted {{ background: var(--posted-bg); color: var(--posted); }}
  .pill {{ font-size: 11px; color: var(--muted); background: var(--lav-soft);
    border-radius: 999px; padding: 2px 10px; }}
  .card__slug {{ font-family: Poppins, sans-serif; font-size: 13px; color: var(--muted);
    margin: 4px 0 8px; word-break: break-all; }}
  .card__caption {{ font-size: 14px; margin: 0 0 12px; white-space: normal; }}
  .card__tags {{ display: flex; flex-wrap: wrap; gap: 5px; }}
  .tag {{ font-size: 11px; color: var(--lav); background: var(--lav-soft);
    border-radius: 6px; padding: 2px 8px; }}
  .empty {{ color: var(--muted); background: var(--card); border: 1px dashed var(--lav-line);
    border-radius: 14px; padding: 24px; text-align: center; }}
  footer {{ text-align: center; color: var(--muted); font-size: 12px; margin-top: 48px; }}
</style>
</head>
<body>
  <div class="wrap">
    <header>
      <div class="logo">Digilab beauty</div>
      <h1>Instagram 投稿プレビュー</h1>
      <p class="sub">FABLE5 が生成した投稿の内部確認用ページ・生成日時 {generated}</p>
      <div class="stats">
        <div class="stat"><b>{ready}</b><span>投稿可 (ready)</span></div>
        <div class="stat"><b>{draft}</b><span>下書き (draft)</span></div>
        <div class="stat"><b>{posted}</b><span>投稿済み</span></div>
      </div>
    </header>
    {queue}
    {posted_section}
    <footer>このページは <code>instagram/build_preview.py</code> により自動生成されます(noindex・社内確認用)。</footer>
  </div>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Instagram 投稿プレビュー生成")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="出力先 HTML パス")
    args = parser.parse_args()
    build(Path(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
