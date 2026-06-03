import time
from collections import deque

from fastapi import HTTPException, Request

from app.core.logging_config import get_logger

logger = get_logger(__name__)


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class IPRateLimiter:
    def __init__(self) -> None:
        self._buckets: dict[str, dict[str, deque]] = {}
        self._last_cleanup = time.time()

    def check(self, category: str, ip: str, max_calls: int, window_seconds: int) -> None:
        now = time.time()

        if now - self._last_cleanup > 600:
            self._cleanup(now, window_seconds)

        key = f"{category}:{ip}"
        if key not in self._buckets:
            self._buckets[key] = deque()

        timestamps = self._buckets[key]

        while timestamps and now - timestamps[0] > window_seconds:
            timestamps.popleft()

        if len(timestamps) >= max_calls:
            retry_after = int(window_seconds - (now - timestamps[0])) + 1
            logger.warning(
                "rate_limit_exceeded",
                category=category,
                ip=ip,
                retry_after=retry_after,
            )
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. You can make {max_calls} {category} requests per hour. "
                       f"Please try again in {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)},
            )

        timestamps.append(now)

    def _cleanup(self, now: float, window_seconds: int) -> None:
        stale_keys = [
            key for key, ts in self._buckets.items()
            if not ts or now - ts[-1] > window_seconds
        ]
        for key in stale_keys:
            del self._buckets[key]
        self._last_cleanup = now


ip_rate_limiter = IPRateLimiter()
