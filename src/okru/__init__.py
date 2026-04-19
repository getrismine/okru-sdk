"""Python SDK для API ok.ru.

Публичная поверхность:

    from okru import Client, OAuthClient, authorization_url
    from okru.errors import OkApiError, OkRateLimitError
    from okru.models import User, Group, FeedItem
"""

from okru.auth import OAuthClient, OAuthToken, authorization_url
from okru.client import Client
from okru.errors import (
    OkApiError,
    OkAuthError,
    OkError,
    OkInvalidAccessTokenError,
    OkInvalidSessionError,
    OkParamError,
    OkPermissionDeniedError,
    OkRateLimitError,
    OkTransportError,
)
from okru.http import RetryPolicy, Transport
from okru.models import FeedItem, Group, User

__version__ = "0.1.0"

__all__ = [
    "Client",
    "FeedItem",
    "Group",
    "OAuthClient",
    "OAuthToken",
    "OkApiError",
    "OkAuthError",
    "OkError",
    "OkInvalidAccessTokenError",
    "OkInvalidSessionError",
    "OkParamError",
    "OkPermissionDeniedError",
    "OkRateLimitError",
    "OkTransportError",
    "RetryPolicy",
    "Transport",
    "User",
    "__version__",
    "authorization_url",
]
