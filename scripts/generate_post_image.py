#!/usr/bin/env python3
"""
Instagram 投稿画像の自動生成スクリプト

投稿キューの `image` ブロック(テキスト情報)から、HTMLテンプレートをレンダリングして
1080×1350(4:5)のJPEGを `public/instagram/` に書き出す。
デザイナーが作ったJPEGを直接置く場合は `image` ブロックを書かなければよい。

必要なパッケージ:
    pip install pillow

必要な外部コマンド:
    Chromium(ヘッドレス)。環境変数 CHROMIUM_PATH で明示指定できる。

使い方:
    python scripts/generate_post_image.py                # 未生成の画像だけ作る
    python scripts/generate_post_image.py --force        # 既存も作り直す
    python scripts/generate_post_image.py --post-id xxx  # 1件だけ

詳細は docs/guides/instagram_auto_post_manual.md を参照。
"""

import argparse
import html
import json
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image

QUEUE_PATH = os.getenv("IG_QUEUE_PATH", "marketing/instagram/post_queue.json")
TEMPLATE_DIR = "marketing/instagram/templates"
OUTPUT_DIR = "public/instagram"

WIDTH, HEIGHT = 1080, 1350
CAPTURE_MARGIN = 250   # 撮影時に確保する下方向の余白(切り出し前)
MEASURE_HEIGHT = 2200  # はみ出し検知用に高さ制限を外して描画するときのビューポート高
JPEG_QUALITY = 88
MAX_BYTES = 8 * 1024 * 1024  # Instagramの画像サイズ上限

CHROMIUM_CANDIDATES = [
    os.getenv("CHROMIUM_PATH", ""),
    "/opt/pw-browsers/chromium",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/usr/bin/google-chrome",
]


def find_chromium():
    for path in CHROMIUM_CANDIDATES:
        if path and os.path.exists(path):
            return path
    found = shutil.which("chromium") or shutil.which("google-chrome")
    if found:
        return found
    raise SystemExit(
        "Chromiumが見つかりません。CHROMIUM_PATH を設定してください。"
    )


def render_html(spec):
    """テンプレートにテキストを流し込んでHTML文字列を返す。"""
    template_name = spec.get("template", "seminar")
    template_path = os.path.join(TEMPLATE_DIR, f"{template_name}.html")
    if not os.path.exists(template_path):
        raise SystemExit(f"テンプレートがありません: {template_path}")

    with open(template_path, encoding="utf-8") as f:
        template = f.read()

    bullets = "".join(
        f"<li>{html.escape(b)}</li>" for b in spec.get("bullets", [])
    )

    photo = spec.get("photo", "")
    values = {
        "THEME": spec.get("theme", "navy"),
        "BADGE": html.escape(spec.get("badge", "")),
        "TITLE": spec.get("title_html") or html.escape(spec.get("title", "")),
        "SECTION_LABEL": html.escape(spec.get("section_label", "セミナー内容")),
        "BULLETS": bullets,
        "YEAR": html.escape(str(spec.get("year", ""))),
        "MONTH": html.escape(str(spec.get("month", ""))),
        "DAY": html.escape(str(spec.get("day", ""))),
        "WEEKDAY": html.escape(spec.get("weekday", "")),
        "TIME": html.escape(spec.get("time", "")),
        "PLACE": html.escape(spec.get("place", "")).replace("\n", "<br>"),
        "FORMAT": html.escape(spec.get("format", "")),
        "HOST": html.escape(spec.get("host", "")),
        "SPEAKERS": html.escape(spec.get("speakers", "")),
        "SUPPORT": html.escape(spec.get("support", "")),
        "PHOTO": html.escape(photo),
        "PHOTO_CLASS": "" if photo else "hidden",
    }

    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    return template


def run_chromium(html_text, png_path, tmpdir, viewport_height):
    """HTMLをヘッドレスChromiumで撮影してPNGに保存する。"""
    html_path = os.path.join(tmpdir, f"page_{viewport_height}.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_text)

    cmd = [
        find_chromium(),
        "--headless",
        "--no-sandbox",
        "--disable-gpu",
        "--hide-scrollbars",
        "--force-device-scale-factor=1",
        "--virtual-time-budget=4000",
        f"--screenshot={png_path}",
        f"--window-size={WIDTH},{viewport_height}",
        f"--user-data-dir={os.path.join(tmpdir, f'profile_{viewport_height}')}",
        f"file://{html_path}",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if not os.path.exists(png_path):
        raise SystemExit(
            f"スクリーンショットに失敗しました:\n{result.stderr[-2000:]}"
        )


def check_overflow(html_text, tmpdir, post_id):
    """
    高さ制限を外して描画し、内容が1350pxに収まっているかを確認する。

    テキストを増やしたときに、下部(主催・後援など)が黙って切れるのを防ぐ。
    """
    measure_css = (
        "<style>body{height:auto !important;min-height:"
        f"{HEIGHT}px !important;overflow:visible !important;}}</style>"
    )
    measured_html = html_text.replace("</head>", measure_css + "</head>")

    png_path = os.path.join(tmpdir, "measure.png")
    run_chromium(measured_html, png_path, tmpdir, MEASURE_HEIGHT)

    with Image.open(png_path) as image:
        rgb = image.convert("RGB")
        background = rgb.getpixel((4, MEASURE_HEIGHT - 4))

        content_bottom = 0
        for y in range(MEASURE_HEIGHT - 1, -1, -1):
            row = [rgb.getpixel((x, y)) for x in range(0, WIDTH, 12)]
            if any(
                sum(abs(a - b) for a, b in zip(pixel, background)) > 24
                for pixel in row
            ):
                content_bottom = y + 1
                break

    if content_bottom > HEIGHT:
        raise SystemExit(
            f"[{post_id}] レイアウトが縦{HEIGHT}pxに収まりません"
            f"(実際の高さ {content_bottom}px)。\n"
            "  箇条書きの文字数を減らすか、テンプレートの文字サイズを調整してください。"
        )
    return content_bottom


def screenshot(html_text, output_path, post_id=""):
    """ヘッドレスChromiumでHTMLを撮影し、JPEGとして保存する。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_bottom = check_overflow(html_text, tmpdir, post_id)
        print(f"  レイアウト高さ: {content_bottom}px / {HEIGHT}px")

        # ビューポート高ぴったりで撮ると描画完了前に切れることがあるため、
        # 余裕を持たせて撮影し、あとから 1080×1350 に切り出す
        png_path = os.path.join(tmpdir, "post.png")
        run_chromium(html_text, png_path, tmpdir, HEIGHT + CAPTURE_MARGIN)

        # Instagramは RGB のJPEG しか受け付けないため変換する
        image = Image.open(png_path).convert("RGB").crop((0, 0, WIDTH, HEIGHT))

        quality = JPEG_QUALITY
        while True:
            image.save(output_path, "JPEG", quality=quality, optimize=True)
            if os.path.getsize(output_path) <= MAX_BYTES or quality <= 60:
                break
            quality -= 8


def load_queue(path):
    if not os.path.exists(path):
        raise SystemExit(f"投稿キューが見つかりません: {path}")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else data.get("posts", [])


def output_path_for(post):
    """image_url のファイル名から出力先を決める。"""
    filename = os.path.basename(post.get("image_url", "").split("?")[0])
    if not filename:
        filename = f"{post.get('id', 'post')}.jpg"
    return os.path.join(OUTPUT_DIR, filename)


def main():
    parser = argparse.ArgumentParser(description="Instagram 投稿画像の生成")
    parser.add_argument("--queue", default=QUEUE_PATH)
    parser.add_argument("--post-id", help="ID指定で1件だけ生成")
    parser.add_argument("--force", action="store_true", help="既存画像も作り直す")
    args = parser.parse_args()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    posts = load_queue(args.queue)

    generated = 0
    for post in posts:
        spec = post.get("image")
        if not spec:
            continue  # デザイナー作成の画像を使う投稿
        if args.post_id and post.get("id") != args.post_id:
            continue
        if post.get("status") == "published" and not args.force:
            continue

        out = output_path_for(post)
        if os.path.exists(out) and not args.force:
            print(f"スキップ(生成済み): {out}")
            continue

        print(f"生成中: {post.get('id')} → {out}")
        screenshot(render_html(spec), out, post.get("id", ""))
        size_kb = os.path.getsize(out) // 1024
        print(f"  ✅ 完了 {WIDTH}×{HEIGHT} / {size_kb}KB")
        generated += 1

    print(f"\n生成: {generated}件")
    return 0


if __name__ == "__main__":
    sys.exit(main())
