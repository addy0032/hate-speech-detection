"""
feed_scraper.py — Scroll the target LinkedIn page feed and collect post URLs
from the last N days.
"""

import re
import time
from datetime import datetime, timedelta, timezone

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from linkedin_scraper.utils import (
    get_page_height,
    logger,
    random_delay,
    smooth_scroll,
)

# Regex that matches a standalone post URL (activity page).
POST_URL_PATTERN = re.compile(
    r"https://www\.linkedin\.com/feed/update/urn:li:activity:(\d+)"
)

# Mapping of LinkedIn's relative-time tokens to approximate timedelta values.
_TIME_UNITS = {
    "s":  timedelta(seconds=1),
    "m":  timedelta(minutes=1),
    "min": timedelta(minutes=1),
    "h":  timedelta(hours=1),
    "hr": timedelta(hours=1),
    "d":  timedelta(days=1),
    "w":  timedelta(weeks=1),
    "mo": timedelta(days=30),
    "yr": timedelta(days=365),
}


class FeedScraper:
    """Scroll a LinkedIn organisation / school page and collect recent post URLs."""

    def __init__(self, driver: WebDriver, max_days: int = 30) -> None:
        self.driver = driver
        self.max_days = max_days
        self.cutoff = datetime.now(timezone.utc) - timedelta(days=max_days)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def scrape_feed(self, url: str) -> list[dict]:
        """
        Navigate to *url*, scroll the feed, and return a list of
        ``{"post_url": ..., "estimated_time": ...}`` dicts whose posts
        are within the last ``max_days`` days.
        """
        # --- URL Normalization ---
        # Ensure we are on the 'Posts' tab with 'All' view for companies/schools
        if "linkedin.com/company/" in url or "linkedin.com/school/" in url:
            if "/posts" not in url:
                # User provided base page, append posts
                url = url.rstrip("/") + "/posts/?feedView=all"
            elif "feedView=" not in url:
                # User provided posts tab, ensure query param
                if "?" in url:
                     url += "&feedView=all"
                else:
                     url += "?feedView=all"
        elif "linkedin.com/in/" in url:
             if "recent-activity" not in url:
                 url = url.rstrip("/") + "/recent-activity/all/"
             elif "recent-activity/all" not in url:
                 # e.g. /recent-activity/shares/ -> force all? or leave as is?
                 # User asked for "recent-activity/all/" specifically.
                 if url.endswith("/recent-activity/") or url.endswith("/recent-activity"):
                     url = url.rstrip("/") + "/all/"
        
        logger.info(f"Navigating to feed: {url}")
        self.driver.get(url)
        random_delay(3, 5)

        # Wait for at least one feed item to appear.
        try:
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.feed-shared-update-v2, div.occludable-update")
                )
            )
        except Exception:
            logger.warning("Feed container not found — page may not have loaded.")

        collected: dict[str, dict] = {}   # activity_id → info dict
        old_streak = 0                    # consecutive "too-old" post counter
        max_old_streak = 5                # stop after this many consecutive old posts
        prev_height = 0
        no_change_count = 0

        while True:
            # --- Extract posts visible on the page ---
            posts = self._extract_posts()
            for post in posts:
                aid = post.get("activity_id")
                if aid and aid not in collected:
                    if post["is_recent"]:
                        collected[aid] = post
                        old_streak = 0
                        logger.info(
                            f"  ✅ Post {aid} — {post['time_text']} — collected "
                            f"({len(collected)} total)"
                        )
                    else:
                        old_streak += 1
                        logger.info(
                            f"  ⏭️  Post {aid} — {post['time_text']} — too old "
                            f"(streak {old_streak}/{max_old_streak})"
                        )

            # --- Check stop conditions ---
            if old_streak >= max_old_streak:
                logger.info("Reached old-post streak limit. Stopping scroll.")
                break

            # --- Scroll and wait for new content ---
            smooth_scroll(self.driver, pixels=900, steps=5)
            random_delay(1.5, 3.0)

            new_height = get_page_height(self.driver)
            if new_height == prev_height:
                no_change_count += 1
                if no_change_count >= 4:
                    logger.info("Page height unchanged after multiple scrolls. Stopping.")
                    break
            else:
                no_change_count = 0
            prev_height = new_height

        results = list(collected.values())
        logger.info(f"📋 Collected {len(results)} post(s) from the last {self.max_days} days.")
        return results

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _extract_posts(self) -> list[dict]:
        """Parse all visible feed update containers and return post metadata."""
        posts: list[dict] = []
        containers = self.driver.find_elements(
            By.CSS_SELECTOR, "div.feed-shared-update-v2"
        )

        for container in containers:
            try:
                info = self._parse_container(container)
                if info:
                    posts.append(info)
            except Exception:
                continue
        return posts

    def _parse_container(self, container) -> dict | None:
        """Extract URL and time info from a single feed update container."""
        # --- post URL ---
        link_elements = container.find_elements(
            By.CSS_SELECTOR,
            "a.app-aware-link[href*='feed/update/urn:li:activity']"
        )
        if not link_elements:
            # Fallback: look in the update's control menu or data attributes.
            data_urn = container.get_attribute("data-urn") or ""
            match = re.search(r"urn:li:activity:(\d+)", data_urn)
            if match:
                activity_id = match.group(1)
                post_url = f"https://www.linkedin.com/feed/update/urn:li:activity:{activity_id}/"
            else:
                return None
        else:
            href = link_elements[0].get_attribute("href") or ""
            match = POST_URL_PATTERN.search(href)
            if not match:
                return None
            activity_id = match.group(1)
            post_url = f"https://www.linkedin.com/feed/update/urn:li:activity:{activity_id}/"

        # --- timestamp text ---
        time_text = ""
        time_els = container.find_elements(
            By.CSS_SELECTOR,
            "span.update-components-actor__sub-description span[aria-hidden='true']"
        )
        if time_els:
            time_text = time_els[0].text.strip()

        is_recent = self._is_within_window(time_text)

        return {
            "activity_id": activity_id,
            "post_url": post_url,
            "time_text": time_text,
            "is_recent": is_recent,
        }

    def _is_within_window(self, time_text: str) -> bool:
        """
        Parse LinkedIn's relative-time string (e.g. '2d', '1w', '3mo')
        and return True if the post is within the cutoff window.
        If parsing fails, assume it is recent (safe to include).
        """
        if not time_text:
            return True

        # Normalise: "2d •" → "2d", "1 hr" → "1hr"
        cleaned = time_text.split("•")[0].strip().replace(" ", "")

        match = re.match(r"(\d+)(s|min|mo|yr|m|h|hr|d|w)", cleaned, re.IGNORECASE)
        if not match:
            return True  # can't parse → keep it

        value = int(match.group(1))
        unit_key = match.group(2).lower()
        delta = _TIME_UNITS.get(unit_key)
        if delta is None:
            return True

        estimated_time = datetime.now(timezone.utc) - (delta * value)
        return estimated_time >= self.cutoff
