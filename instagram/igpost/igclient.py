"""Instagram Graph APIクライアント（画像・カルーセル投稿）。"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import List, Optional

DEFAULT_API_VERSION = "v26.0"
GRAPH_BASE = "https://graph.facebook.com"


class InstagramAPIError(Exception):
    """Graph API呼び出しの失敗。"""


class InstagramClient:
    def __init__(
        self,
        ig_user_id: str,
        access_token: str,
        api_version: str = DEFAULT_API_VERSION,
        timeout: int = 60,
    ) -> None:
        if not ig_user_id or not access_token:
            raise InstagramAPIError("ig_user_idとaccess_tokenは必須です")
        if not api_version.startswith("v"):
            raise InstagramAPIError("api_versionはv26.0の形式で指定してください")
        self.ig_user_id = ig_user_id
        self.access_token = access_token
        self.base = f"{GRAPH_BASE}/{api_version}"
        self.timeout = timeout

    def _request(self, request: urllib.request.Request, operation: str) -> dict:
        request.add_header("Authorization", f"Bearer {self.access_token}")
        request.add_header("User-Agent", "digilab-instagram-publisher/1.0")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise InstagramAPIError(f"{operation}が失敗しました (HTTP {exc.code}): {detail}") from exc
        except urllib.error.URLError as exc:
            raise InstagramAPIError(f"{operation}で通信エラー: {exc.reason}") from exc
        except json.JSONDecodeError as exc:
            raise InstagramAPIError(f"{operation}の応答がJSONではありません") from exc

    def _post(self, path: str, params: dict) -> dict:
        url = f"{self.base}/{path}"
        body = urllib.parse.urlencode(params).encode("utf-8")
        request = urllib.request.Request(url, data=body, method="POST")
        return self._request(request, f"POST {path}")

    def _get(self, path: str, params: Optional[dict] = None) -> dict:
        query = urllib.parse.urlencode(params or {})
        url = f"{self.base}/{path}" + (f"?{query}" if query else "")
        return self._request(urllib.request.Request(url, method="GET"), f"GET {path}")

    def verify_credentials(self) -> dict:
        return self._get(self.ig_user_id, {"fields": "id,username"})

    def _create_image_container(
        self,
        image_url: str,
        caption: Optional[str] = None,
        alt_text: Optional[str] = None,
        is_carousel_item: bool = False,
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
        return str(creation_id)

    def _wait_until_ready(self, creation_id: str, attempts: int = 20, delay: int = 3) -> None:
        last_status: dict = {}
        for _ in range(attempts):
            last_status = self._get(creation_id, {"fields": "status_code"})
            code = last_status.get("status_code")
            if code == "FINISHED":
                return
            if code in {"ERROR", "EXPIRED"}:
                raise InstagramAPIError(f"コンテナ処理でエラー: {last_status}")
            time.sleep(delay)
        raise InstagramAPIError(f"コンテナ処理が時間内に完了しませんでした: {last_status}")

    def _publish(self, creation_id: str) -> str:
        result = self._post(f"{self.ig_user_id}/media_publish", {"creation_id": creation_id})
        media_id = result.get("id")
        if not media_id:
            raise InstagramAPIError(f"公開に失敗: {result}")
        return str(media_id)

    def publish_image(self, image_url: str, caption: str, alt_text: Optional[str] = None) -> str:
        creation_id = self._create_image_container(image_url, caption=caption, alt_text=alt_text)
        self._wait_until_ready(creation_id)
        return self._publish(creation_id)

    def publish_carousel(
        self, image_urls: List[str], caption: str, alt_text: Optional[str] = None,
    ) -> str:
        if not 2 <= len(image_urls) <= 10:
            raise InstagramAPIError("カルーセルは2〜10枚にしてください")
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
        self._wait_until_ready(str(creation_id))
        return self._publish(str(creation_id))
