"""Instagram Graph API クライアント(フィード投稿)。

画像1枚(IMAGE)およびカルーセル(CAROUSEL)のフィード投稿に対応。
依存は標準ライブラリのみ(urllib)。

投稿フロー(Meta Graph API):
  IMAGE:
    1. POST /{ig_user_id}/media            (image_url, caption) -> creation_id
    2. POST /{ig_user_id}/media_publish    (creation_id)        -> media_id
  CAROUSEL:
    1. 各画像を POST /{ig_user_id}/media    (image_url, is_carousel_item=true) -> child_id
    2. POST /{ig_user_id}/media            (media_type=CAROUSEL, children, caption) -> creation_id
    3. POST /{ig_user_id}/media_publish    (creation_id) -> media_id

前提:
  - Instagram はプロアカウント(ビジネス/クリエイター)で Facebook ページに連携済み
  - image_url は公開アクセス可能な URL(本リポジトリでは raw.githubusercontent.com を利用)
  - 長期アクセストークン(ig_user_id に対する instagram_content_publish 権限)
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import List, Optional

DEFAULT_API_VERSION = "v21.0"
GRAPH_BASE = "https://graph.facebook.com"


class InstagramAPIError(Exception):
    """Graph API 呼び出しの失敗。"""


class InstagramClient:
    def __init__(
        self,
        ig_user_id: str,
        access_token: str,
        api_version: str = DEFAULT_API_VERSION,
        timeout: int = 60,
    ) -> None:
        if not ig_user_id or not access_token:
            raise InstagramAPIError("ig_user_id と access_token は必須です")
        self.ig_user_id = ig_user_id
        self.access_token = access_token
        self.base = f"{GRAPH_BASE}/{api_version}"
        self.timeout = timeout

    # ---- 低レベル HTTP ----------------------------------------------------

    def _post(self, path: str, params: dict) -> dict:
        url = f"{self.base}/{path}"
        data = dict(params)
        data["access_token"] = self.access_token
        body = urllib.parse.urlencode(data).encode("utf-8")
        req = urllib.request.Request(url, data=body, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise InstagramAPIError(
                f"POST {path} が失敗しました (HTTP {exc.code}): {detail}"
            ) from exc
        except urllib.error.URLError as exc:
            raise InstagramAPIError(f"POST {path} で通信エラー: {exc.reason}") from exc

    def _get(self, path: str, params: Optional[dict] = None) -> dict:
        query = dict(params or {})
        query["access_token"] = self.access_token
        url = f"{self.base}/{path}?{urllib.parse.urlencode(query)}"
        try:
            with urllib.request.urlopen(url, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise InstagramAPIError(
                f"GET {path} が失敗しました (HTTP {exc.code}): {detail}"
            ) from exc
        except urllib.error.URLError as exc:
            raise InstagramAPIError(f"GET {path} で通信エラー: {exc.reason}") from exc

    # ---- 公開メソッド -----------------------------------------------------

    def verify_credentials(self) -> dict:
        """アカウント情報を取得して認証を確認。"""
        return self._get(self.ig_user_id, {"fields": "id,username"})

    def _create_image_container(
        self, image_url: str, caption: Optional[str] = None,
        alt_text: Optional[str] = None, is_carousel_item: bool = False,
    ) -> str:
        params: dict = {"image_url": image_url}
        if caption is not None:
            params["caption"] = caption
        if alt_text:
            params["alt_text"] = alt_text
        if is_carousel_item:
            params["is_carousel_item"] = "true"
        result = self._post(f"{self.ig_user_id}/media", params)
        creation_id = result.get("id")
        if not creation_id:
            raise InstagramAPIError(f"コンテナ生成に失敗: {result}")
        return creation_id

    def _wait_until_ready(self, creation_id: str, attempts: int = 10, delay: int = 3) -> None:
        """コンテナの status_code が FINISHED になるまで待機。"""
        for _ in range(attempts):
            status = self._get(creation_id, {"fields": "status_code"})
            code = status.get("status_code")
            if code == "FINISHED":
                return
            if code == "ERROR":
                raise InstagramAPIError(f"コンテナ処理でエラー: {status}")
            time.sleep(delay)
        # タイムアウトしても publish を試みる(多くは処理済み)

    def _publish(self, creation_id: str) -> str:
        result = self._post(f"{self.ig_user_id}/media_publish", {"creation_id": creation_id})
        media_id = result.get("id")
        if not media_id:
            raise InstagramAPIError(f"公開に失敗: {result}")
        return media_id

    def publish_image(
        self, image_url: str, caption: str, alt_text: Optional[str] = None,
    ) -> str:
        """画像1枚のフィード投稿。公開された media_id を返す。"""
        creation_id = self._create_image_container(image_url, caption=caption, alt_text=alt_text)
        self._wait_until_ready(creation_id)
        return self._publish(creation_id)

    def publish_carousel(
        self, image_urls: List[str], caption: str, alt_text: Optional[str] = None,
    ) -> str:
        """複数画像のカルーセル投稿。公開された media_id を返す。"""
        if not 2 <= len(image_urls) <= 10:
            raise InstagramAPIError("カルーセルは 2〜10 枚にしてください")
        children: List[str] = []
        for url in image_urls:
            child_id = self._create_image_container(
                url, alt_text=alt_text, is_carousel_item=True
            )
            self._wait_until_ready(child_id)
            children.append(child_id)
        parent = self._post(
            f"{self.ig_user_id}/media",
            {"media_type": "CAROUSEL", "children": ",".join(children), "caption": caption},
        )
        creation_id = parent.get("id")
        if not creation_id:
            raise InstagramAPIError(f"カルーセル親コンテナ生成に失敗: {parent}")
        self._wait_until_ready(creation_id)
        return self._publish(creation_id)
