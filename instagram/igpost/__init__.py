"""Instagram投稿自動化パッケージ。"""

from .igclient import InstagramAPIError, InstagramClient
from .post import DELETE, Post, PostError, load_posts

__all__ = [
    "DELETE",
    "InstagramAPIError",
    "InstagramClient",
    "Post",
    "PostError",
    "load_posts",
]
