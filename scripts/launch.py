#!/usr/bin/env python3
"""
DigiLab Beauty - ステップライン ランチャー

これ1つを実行するだけで全部動きます:
  1. ngrokでHTTPSトンネルを開通
  2. Webhook URLを画面に表示
  3. ステップ配信（本日分）を実行
  4. LINEからのWebhookを待ち受け開始

使い方:
    python scripts/launch.py

終了: Ctrl+C
"""

import os
import sys
import sqlite3
import threading
import time
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

# .env を読み込む
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

DB_PATH = os.getenv("DB_PATH") or str(ROOT / "db" / "digilab_beauty.db")
os.environ["DB_PATH"] = DB_PATH

PORT = int(os.getenv("PORT", "8000"))


def check_setup():
    """セットアップ状況を確認し、未完了なら案内して終了"""
    missing = []
    if not os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "").strip():
        missing.append("LINE_CHANNEL_ACCESS_TOKEN")
    if not os.getenv("LINE_CHANNEL_SECRET", "").strip():
        missing.append("LINE_CHANNEL_SECRET")

    if missing:
        print("\n  ⚠ 以下の設定が未完了です:")
        for m in missing:
            print(f"     - {m}")
        print("\n  先に以下を実行してください:")
        print("      python scripts/setup.py")
        print()
        sys.exit(1)

    if not Path(DB_PATH).exists():
        print("\n  ⚠ データベースが見つかりません。先にセットアップを実行してください:")
        print("      python scripts/setup.py")
        print()
        sys.exit(1)

    # シナリオ確認
    try:
        conn = sqlite3.connect(DB_PATH)
        count = conn.execute("SELECT COUNT(*) FROM step_scenarios").fetchone()[0]
        conn.close()
        if count == 0:
            print("\n  ⚠ シナリオが未登録です。先に setup.py を実行してください。")
            sys.exit(1)
    except sqlite3.OperationalError:
        print("\n  ⚠ ステップラインテーブルが未作成です。先に setup.py を実行してください。")
        sys.exit(1)


def run_step_delivery():
    """本日分のステップ配信を実行"""
    import step_line
    print("\n  ─── ステップ配信（本日分）を実行中 ───")
    result = step_line.run(dry_run=False)
    total = result["sent"] + result["completed"] + result["skipped"]
    if total == 0:
        print("  （本日の配信予定なし）")
    print()


def start_ngrok(port):
    """ngrokでHTTPSトンネルを開通し、公開URLを返す"""
    try:
        from pyngrok import ngrok, conf
        # ログを抑制
        conf.get_default().log_level = "CRITICAL"
        tunnel = ngrok.connect(port, "http")
        return tunnel.public_url.replace("http://", "https://")
    except ImportError:
        return None
    except Exception as e:
        print(f"  ⚠ ngrokの起動に失敗: {e}")
        return None


def print_banner(ngrok_url):
    """起動情報を大きく表示"""
    print()
    print("╔" + "═" * 58 + "╗")
    print("║   DigiLab Beauty - LINEステップライン 起動中             ║")
    print("╠" + "═" * 58 + "╣")
    if ngrok_url:
        print("║                                                          ║")
        print("║  ▼ LINE DevelopersにこのURLを設定してください ▼         ║")
        print("║                                                          ║")
        url_line = f"  {ngrok_url}/callback"
        print(f"║  {url_line:<56}  ║")
        print("║                                                          ║")
        print("╠" + "═" * 58 + "╣")
        print("║  設定場所:                                               ║")
        print("║  LINE Developers → チャネル → Messaging API設定         ║")
        print("║  → Webhook URL に貼り付け → 更新 → 検証                 ║")
        print("║  → 「Webhookの利用」を ON                                ║")
    else:
        print("║  ⚠ ngrokが使えません。手動でサーバーを公開してください  ║")
        print(f"║  ローカルURL: http://localhost:{PORT}/callback             ║")
    print("╠" + "═" * 58 + "╣")
    print("║  友だち追加 → 自動でステップライン開始                  ║")
    print("║  終了: Ctrl+C                                            ║")
    print("╚" + "═" * 58 + "╝")
    print()


def start_webhook():
    """FlaskのWebhookサーバーを別スレッドで起動"""
    import line_webhook
    # Flask のログを最小限に
    import logging
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.WARNING)
    line_webhook.app.run(host="0.0.0.0", port=PORT, use_reloader=False, threaded=True)


def main():
    print("\n  DigiLab Beauty ステップライン 起動中...")

    # セットアップ確認
    check_setup()

    # 本日分のステップ配信を実行
    run_step_delivery()

    # ngrok起動
    print("  ngrokでHTTPSトンネルを開通中...")
    ngrok_url = start_ngrok(PORT)

    # バナー表示
    print_banner(ngrok_url)

    # Webhookサーバーをメインスレッドで起動
    try:
        start_webhook()
    except KeyboardInterrupt:
        print("\n\n  停止しました。お疲れ様でした。\n")
        try:
            from pyngrok import ngrok
            ngrok.kill()
        except Exception:
            pass


if __name__ == "__main__":
    main()
