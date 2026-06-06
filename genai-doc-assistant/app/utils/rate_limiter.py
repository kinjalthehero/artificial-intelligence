"""
Per-IP Rate Limiter
====================
Protects the Gemini API from abuse by limiting requests per IP address.

Why per-IP (not global)?
- A global limiter would let one abusive user block everyone else
- Per-IP ensures each visitor gets a fair share of the API quota
- Legitimate users are unaffected even if someone else is spamming

Algorithm: Sliding Window
- Tracks timestamps of recent requests per IP in a deque (double-ended queue)
- When a new request arrives, removes timestamps older than the window (1 hour)
- If the remaining count exceeds the limit, returns HTTP 429 (Too Many Requests)
- Includes a Retry-After header telling the client when to try again

IP Detection:
- Behind reverse proxies (Render, AWS ALB), the real client IP is in the
  X-Forwarded-For header. We extract the first IP from that header.
- Falls back to request.client.host for direct connections.

Memory cleanup runs every 10 minutes to remove stale IP entries.
"""

import time
from collections import deque

from fastapi import HTTPException, Request

from app.core.logging_config import get_logger

logger = get_logger(__name__)


def get_client_ip(request: Request) -> str:
    """Extract the real client IP address.

    Behind reverse proxies (Render, Nginx, AWS ALB), the actual client IP is in
    the X-Forwarded-For header as a comma-separated list. The first entry is
    the original client IP.
    """
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class IPRateLimiter:
    def __init__(self) -> None:
        # {category:ip -> deque of timestamps} — tracks when each IP made requests
        self._buckets: dict[str, deque] = {}
        self._last_cleanup = time.time()

    def check(self, category: str, ip: str, max_calls: int, window_seconds: int) -> None:
        """Check if the IP is within its rate limit. Raises HTTP 429 if exceeded.

        Args:
            category: "chat" or "upload" — different limits for different endpoints
            ip: Client IP address
            max_calls: Maximum allowed requests in the window (e.g., 30)
            window_seconds: Time window in seconds (e.g., 3600 = 1 hour)
        """
        now = time.time()

        # Periodically clean up stale entries to prevent memory growth
        if now - self._last_cleanup > 600:  # Every 10 minutes
            self._cleanup(now, window_seconds)

        key = f"{category}:{ip}"
        if key not in self._buckets:
            self._buckets[key] = deque()

        timestamps = self._buckets[key]

        # Remove timestamps outside the sliding window
        while timestamps and now - timestamps[0] > window_seconds:
            timestamps.popleft()

        # Check if limit exceeded
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

        # Record this request's timestamp
        timestamps.append(now)

    def _cleanup(self, now: float, window_seconds: int) -> None:
        """Remove IP entries that haven't been seen within the time window."""
        stale_keys = [
            key for key, ts in self._buckets.items()
            if not ts or now - ts[-1] > window_seconds
        ]
        for key in stale_keys:
            del self._buckets[key]
        self._last_cleanup = now


# Singleton instance used by all API routers
ip_rate_limiter = IPRateLimiter()
