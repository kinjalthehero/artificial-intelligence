import asyncio
import time
from collections import deque

from app.core.logging_config import get_logger

logger = get_logger(__name__)


class RateLimiter:
    def __init__(self, max_calls: int = 14, window_seconds: int = 60) -> None:
        self._timestamps: deque = deque()
        self._max = max_calls
        self._window = window_seconds
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            now = time.time()
            while self._timestamps and now - self._timestamps[0] > self._window:
                self._timestamps.popleft()

            if len(self._timestamps) >= self._max:
                oldest = self._timestamps[0]
                wait = self._window - (now - oldest) + 0.1
                logger.warning("rate_limit_waiting", wait_seconds=round(wait, 1))
                await asyncio.sleep(wait)
                now = time.time()
                while self._timestamps and now - self._timestamps[0] > self._window:
                    self._timestamps.popleft()

            self._timestamps.append(time.time())

    @property
    def remaining(self) -> int:
        now = time.time()
        active = sum(1 for t in self._timestamps if now - t <= self._window)
        return max(0, self._max - active)


rate_limiter = RateLimiter()
