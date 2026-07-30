#!/usr/bin/env python3
"""
@AIマーケティング - LINEハーネス（LINE Messaging API クライアント）

LINE公式アカウントのMessaging APIを薄くラップした送信ハーネス。
ステップライン（step_line.py）から呼び出され、実際のメッセージ送信を担う。

必要なパッケージ:
pip install requests python-dotenv

環境変数(.env):
LINE_CHANNEL_ACCESS_TOKEN=長期チャネルアクセストークン
LINE_DRY_RUN=1   # 1のとき実送信せずログ出力のみ（既定: 1）

参考:
- Push API:      https://api.line.me/v2/bot/message/push
- Multicast API: https://api.line.me/v2/bot/message/multicast
- Profile API:   https://api.line.me/v2/bot/profile/{userId}
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

LINE_API_BASE = "https://api.line.me/v2/bot"
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
# 既定はドライラン（誤送信防止）。実送信するには .env で LINE_DRY_RUN=0 を設定。
DRY_RUN = os.getenv("LINE_DRY_RUN", "1") not in ("0", "false", "False", "")

# multicast の宛先上限（LINE仕様）
MULTICAST_LIMIT = 500


class LineHarnessError(Exception):
    """LINEハーネスの送信エラー"""


class LineHarness:
    """LINE Messaging API の送信ハーネス。

    dry_run=True のときはAPIを叩かず、送信内容を辞書で返す（テスト/プレビュー用）。
    """

    def __init__(self, access_token=None, dry_run=None, timeout=10):
        self.access_token = access_token if access_token is not None else CHANNEL_ACCESS_TOKEN
        self.dry_run = DRY_RUN if dry_run is None else dry_run
        self.timeout = timeout

        if not self.dry_run and not self.access_token:
            raise LineHarnessError(
                "LINE_CHANNEL_ACCESS_TOKEN が未設定です。"
                ".env に設定するか dry_run=True で実行してください。"
            )

    # ------------------------------------------------------------------
    # 内部ユーティリティ
    # ------------------------------------------------------------------
    def _headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }

    @staticmethod
    def _text_message(text):
        """テキストメッセージオブジェクトを生成（5000文字上限で安全に切り詰め）"""
        return {"type": "text", "text": text[:5000]}

    def _post(self, path, payload):
        """LINE APIへPOST。dry_runならモックレスポンスを返す。"""
        if self.dry_run:
            return {
                "dry_run": True,
                "path": path,
                "payload": payload,
            }

        url = f"{LINE_API_BASE}{path}"
        try:
            res = requests.post(
                url, headers=self._headers(), data=json.dumps(payload), timeout=self.timeout
            )
            res.raise_for_status()
            # Push/Multicastは成功時 200 で本文は空 or {}
            return {"status_code": res.status_code, "body": res.text}
        except requests.exceptions.HTTPError as e:
            body = e.response.text if e.response is not None else ""
            raise LineHarnessError(f"LINE APIエラー [{path}]: {e} {body}") from e
        except requests.exceptions.RequestException as e:
            raise LineHarnessError(f"LINE API通信エラー [{path}]: {e}") from e

    # ------------------------------------------------------------------
    # 公開メソッド
    # ------------------------------------------------------------------
    def push_text(self, line_user_id, text):
        """単一ユーザーにテキストを送信（Push API）"""
        payload = {"to": line_user_id, "messages": [self._text_message(text)]}
        return self._post("/message/push", payload)

    def multicast_text(self, line_user_ids, text):
        """複数ユーザーに同一テキストを一斉送信（Multicast API）。

        上限(500件)を超える場合は自動でバッチ分割して送信する。
        """
        if not line_user_ids:
            return []

        results = []
        message = self._text_message(text)
        for i in range(0, len(line_user_ids), MULTICAST_LIMIT):
            batch = line_user_ids[i : i + MULTICAST_LIMIT]
            payload = {"to": batch, "messages": [message]}
            results.append(self._post("/message/multicast", payload))
        return results

    def get_profile(self, line_user_id):
        """ユーザープロフィールを取得（表示名・アイコン等）"""
        if self.dry_run:
            return {"dry_run": True, "userId": line_user_id, "displayName": "(dry_run)"}

        url = f"{LINE_API_BASE}/profile/{line_user_id}"
        try:
            res = requests.get(url, headers=self._headers(), timeout=self.timeout)
            res.raise_for_status()
            return res.json()
        except requests.exceptions.RequestException as e:
            raise LineHarnessError(f"プロフィール取得エラー: {e}") from e

    def quota(self):
        """当月の送信可能メッセージ数（無料枠）を取得"""
        if self.dry_run:
            return {"dry_run": True, "type": "limited", "value": 0}

        url = f"{LINE_API_BASE}/message/quota"
        try:
            res = requests.get(url, headers=self._headers(), timeout=self.timeout)
            res.raise_for_status()
            return res.json()
        except requests.exceptions.RequestException as e:
            raise LineHarnessError(f"クォータ取得エラー: {e}") from e


def main():
    """疎通確認（ドライラン）。実送信はしない。"""
    print("=" * 60)
    print("LINEハーネス 疎通確認（ドライラン）")
    print("=" * 60)

    harness = LineHarness(dry_run=True)
    sample = harness.push_text("Uxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", "テスト配信です。")
    print("\npush_text のペイロード:")
    print(json.dumps(sample, ensure_ascii=False, indent=2))

    multi = harness.multicast_text(
        ["Uaaa", "Ubbb"], "一斉配信のテストです。"
    )
    print("\nmulticast_text のペイロード:")
    print(json.dumps(multi, ensure_ascii=False, indent=2))

    print("\n✓ ドライラン完了（実送信なし）")
    print(f"  実送信する場合は .env に LINE_CHANNEL_ACCESS_TOKEN と LINE_DRY_RUN=0 を設定")


if __name__ == "__main__":
    main()
