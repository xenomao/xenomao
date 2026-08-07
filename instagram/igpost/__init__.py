"""DigiLab Beauty — Instagram 自動投稿ライブラリ。

FABLE5 が生成した画像とキャプション(投稿スペック)を読み込み、
Instagram Graph API 経由でフィード投稿する仕組みを提供する。
"""

from .post import Post, PostError, load_posts
from .igclient import InstagramClient, InstagramAPIError

__all__ = [
    "Post",
    "PostError",
    "load_posts",
    "InstagramClient",
    "InstagramAPIError",
]
