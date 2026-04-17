"""Lightweight thread-safe TTL cache for small in-process datasets.

Infrastructure layer implementation. Not suitable for very high write
concurrency (uses coarse lock) but fine for admin/UI caching.
"""
from __future__ import annotations
import time
import threading
from typing import Generic, TypeVar, Optional, Dict, Tuple

K = TypeVar("K")
V = TypeVar("V")

class TTLCache(Generic[K, V]):
    def __init__(self, default_ttl: float = 30.0, max_items: int = 1024) -> None:
        self._default_ttl = float(default_ttl)
        self._max_items = max_items
        self._data: Dict[K, Tuple[float, V]] = {}
        self._lock = threading.Lock()

    def set(self, key: K, value: V, ttl: Optional[float] = None) -> None:
        exp = time.time() + (ttl if ttl is not None else self._default_ttl)
        with self._lock:
            if len(self._data) >= self._max_items:
                # Simple eviction: drop oldest
                oldest_key = min(self._data.items(), key=lambda kv: kv[1][0])[0]
                self._data.pop(oldest_key, None)
            self._data[key] = (exp, value)

    def get(self, key: K) -> Optional[V]:
        with self._lock:
            item = self._data.get(key)
            if not item:
                return None
            exp, val = item
            if exp < time.time():
                self._data.pop(key, None)
                return None
            return val

    def pop(self, key: K) -> None:
        with self._lock:
            self._data.pop(key, None)

    def stats(self) -> dict:
        with self._lock:
            live = {k: v for k, v in self._data.items() if v[0] >= time.time()}
            expired = len(self._data) - len(live)
            return {
                "size": len(live),
                "expired_purged": expired,
                "default_ttl": self._default_ttl,
                "max_items": self._max_items,
            }

__all__ = ["TTLCache"]
