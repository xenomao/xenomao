#!/usr/bin/env python3
"""
@AIマーケティング - LINE Webhook 受け口

LINEプラットフォームからのWebhookイベントを受信し、ステップラインと連携する。

処理するイベント:
  follow    : 友だち追加      → プロフィール取得 → 購読者登録 → on_friend_add シナリオへ自動エンロール
  unfollow  : ブロック/友だち解除 → 購読者ステータスを 'ブロック' に更新
  message   : メッセージ受信  → 受信ログ（必要に応じ拡張）

セキュリティ:
  X-Line-Signature ヘッダ（HMAC-SHA256 + Base64）を LINE_CHANNEL_SECRET で検証する。
  署名が一致しないリクエストは 400 で拒否。

必要なパッケージ:
pip install flask requests python-dotenv

環境変数(.env):
LINE_CHANNEL_SECRET=（チャネルシークレット / LINE Developers「チャネル基本設定」）
LINE_CHANNEL_ACCESS_TOKEN=（プロフィール取得・送信用）
LINE_DRY_RUN=1
DB_PATH=path/to/digilab_beauty.db

起動:
  python line_webhook.py          # 0.0.0.0:8000 で起動
  （LINE DevelopersのWebhook URLに https://<公開ドメイン>/callback を設定）
"""

import os
import hmac
import base64
import hashlib

from flask import Flask, request, abort
from dotenv import load_dotenv

import step_line
from line_harness import LineHarness, LineHarnessError

load_dotenv()

CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "")
PORT = int(os.getenv("PORT", "8000"))

app = Flask(__name__)


def verify_signature(body_bytes, signature):
    """X-Line-Signature を検証する。CHANNEL_SECRET 未設定時は False。"""
    if not CHANNEL_SECRET or not signature:
        return False
    digest = hmac.new(CHANNEL_SECRET.encode("utf-8"), body_bytes, hashlib.sha256).digest()
    expected = base64.b64encode(digest).decode("utf-8")
    return hmac.compare_digest(expected, signature)


def handle_event(event):
    """単一のWebhookイベントを処理する。"""
    etype = event.get("type")
    source = event.get("source", {})
    line_user_id = source.get("userId")

    if not line_user_id:
        return  # グループ等、userIdが取れないソースは対象外

    if etype == "follow":
        # プロフィール取得（dry_run時はダミー名）
        display_name = None
        try:
            profile = LineHarness().get_profile(line_user_id)
            display_name = profile.get("displayName")
        except LineHarnessError as e:
            app.logger.warning("プロフィール取得失敗: %s", e)

        sub_id = step_line.upsert_subscriber(line_user_id, display_name=display_name, segment="新規")
        enrolled = step_line.enroll_by_trigger(sub_id, "on_friend_add")
        app.logger.info("follow: %s (%s) → enrolled=%s", line_user_id, display_name, enrolled)

    elif etype == "unfollow":
        step_line.set_subscriber_status(line_user_id, "ブロック")
        app.logger.info("unfollow: %s → ブロック", line_user_id)

    elif etype == "message":
        msg = event.get("message", {})
        app.logger.info("message: %s type=%s", line_user_id, msg.get("type"))
        # 必要に応じて応答や受信ログ保存を実装

    else:
        app.logger.info("未処理イベント: %s", etype)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body_bytes = request.get_data()

    if not verify_signature(body_bytes, signature):
        app.logger.warning("署名検証に失敗しました")
        abort(400, "invalid signature")

    payload = request.get_json(silent=True) or {}
    for event in payload.get("events", []):
        try:
            handle_event(event)
        except Exception as e:  # 1イベントの失敗で全体を落とさない
            app.logger.exception("イベント処理エラー: %s", e)

    return "OK", 200


@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok", "dry_run": LineHarness().dry_run}, 200


if __name__ == "__main__":
    if not CHANNEL_SECRET:
        print("⚠ LINE_CHANNEL_SECRET が未設定です。署名検証が常に失敗します（.envに設定してください）。")
    print(f"LINE Webhook を起動: http://0.0.0.0:{PORT}/callback")
    app.run(host="0.0.0.0", port=PORT)
