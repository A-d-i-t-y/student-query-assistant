"""
cache.py — Simple in-process response cache using a dictionary.

Prevents redundant API calls for identical questions within the same session.
"""

from typing import Optional


class ResponseCache:
    """
    Lightweight dictionary-backed cache for AI responses.

    Keys   : normalised query strings
    Values : assistant response strings
    """

    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    @staticmethod
    def _normalise(query: str) -> str:
        """Lowercase and strip whitespace to improve cache hit rate."""
        return query.lower().strip()

    def get(self, query: str) -> Optional[str]:
        """Return a cached response or None if not found."""
        return self._store.get(self._normalise(query))

    def set(self, query: str, response: str) -> None:
        """Store a response for the given query."""
        self._store[self._normalise(query)] = response

    def clear(self) -> None:
        """Clear all cached entries."""
        self._store.clear()

    def __len__(self) -> int:
        return len(self._store)
