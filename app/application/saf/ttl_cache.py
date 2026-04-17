"""Simple TTL cache used for SAF use-cases (Phase 5).
"""
from __future__ import annotations

import time
from typing import Any, Dict

class TTLCache:
    def __init__(self, ttl_seconds: int = 120) -> None:
        self.ttl = ttl_seconds
        self._data: Dict[str, Any] = {}
        self._ts: Dict[str, float] = {}

    def get(self, key: str):
        if key not in self._data:
            return None
        if (time.time() - self._ts.get(key, 0)) > self.ttl:
            self._data.pop(key, None)
            self._ts.pop(key, None)
            return None
        return self._data[key]

    def set(self, key: str, value: Any):
        self._data[key] = value
        self._ts[key] = time.time()

__all__ = ["TTLCache"]
