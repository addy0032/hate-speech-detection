"""
storage.py — JSON persistence layer: deduplication, auto-indexing, append-only.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from linkedin_scraper.utils import logger

DEFAULT_OUTPUT = "comments.json"


class Storage:
    """Stores scraped comments in a JSON file with dedup and auto-incrementing index."""

    def __init__(self, filepath: str = DEFAULT_OUTPUT) -> None:
        self.filepath = Path(filepath)
        self.data: list[dict] = []
        self._seen: set[tuple[str, str]] = set()  # (post_url, comment_text)
        self._load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_comments(self, comments: list[dict]) -> int:
        """
        Add a batch of comment dicts. Each dict should contain at least:
          - post_url
          - comment
        Optional keys: user_profile_url, urn
        """
        added = 0
        for item in comments:
            urn = item.get("urn")
            post_url = item.get("post_url", "")
            text = item.get("comment", "")
            
            # Primary key: URN. Fallback: (post_url, text)
            if urn:
                key = urn
            else:
                key = (post_url, text)
            
            if key in self._seen or (not urn and not text):
                continue
                
            self._seen.add(key)

            entry = {
                "index": self._next_index(),
                "urn": urn,
                "post_url": post_url,
                "comment": text,
                "user_profile_url": item.get("user_profile_url", ""),
                "author_name": item.get("author_name", ""),
                "label": item.get("label", "unknown"),
                "scraped_at": datetime.now(timezone.utc).isoformat(),
            }
            self.data.append(entry)
            added += 1

        return added

    def save(self) -> None:
        """Persist current data to disk."""
        with open(self.filepath, "w", encoding="utf-8") as fh:
            json.dump(self.data, fh, indent=2, ensure_ascii=False)
        logger.info(f"💾 Saved {len(self.data)} comment(s) to {self.filepath}")

    @property
    def total(self) -> int:
        return len(self.data)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _load(self) -> None:
        """Load existing JSON data from disk (if any)."""
        if not self.filepath.exists():
            return
        try:
            with open(self.filepath, "r", encoding="utf-8") as fh:
                self.data = json.load(fh)
            for entry in self.data:
                urn = entry.get("urn")
                if urn:
                    self._seen.add(urn)
                else:
                    # Fallback for old data without URN
                    key = (entry.get("post_url", ""), entry.get("comment", ""))
                    self._seen.add(key)
                    
            logger.info(f"Loaded {len(self.data)} existing comment(s) from {self.filepath}")
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning(f"Could not load {self.filepath}: {exc}")
            self.data = []

    def _next_index(self) -> int:
        if not self.data:
            return 1
        return max(entry.get("index", 0) for entry in self.data) + 1
