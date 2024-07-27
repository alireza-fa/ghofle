from functools import lru_cache

from django.conf import settings

from .base import Redis


@lru_cache
def get_redis_connection() -> Redis:
    return Redis(
        host=getattr(settings, "REDIS_HOST_DEBUG", "localhost") if settings.DEBUG else getattr(settings, "REDIS_HOST", "localhost"),
        port=getattr(settings, "REDIS_PORT", 6379),
        password=getattr(settings, "REDIS_PASSWORD", None)
    )
