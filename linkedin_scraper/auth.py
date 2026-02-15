"""
auth.py — LinkedIn authentication: manual login, cookie persistence, session validation.
"""

import json
import os
import time
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from linkedin_scraper.utils import logger, random_delay

LOGIN_URL = "https://www.linkedin.com/login"
FEED_URL = "https://www.linkedin.com/feed/"
DEFAULT_COOKIE_PATH = "cookies.json"


class LinkedInAuth:
    """Handles LinkedIn login, cookie save / load, and session validation."""

    def __init__(self, driver: WebDriver, cookie_path: str = DEFAULT_COOKIE_PATH) -> None:
        self.driver = driver
        self.cookie_path = Path(cookie_path)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def authenticate(self) -> bool:
        """
        Main entry point.
        1. Try to restore a previous session from cookies.
        2. If that fails, prompt for manual login.
        Returns True on success.
        """
        if self.cookie_path.exists():
            logger.info("Found saved cookies — attempting session restore …")
            if self._load_cookies():
                logger.info("✅ Session restored successfully.")
                return True
            logger.warning("Saved session expired/invalid. Falling back to manual login.")

        return self._manual_login()

    # ------------------------------------------------------------------
    # Manual login
    # ------------------------------------------------------------------

    def _manual_login(self) -> bool:
        """Open the login page and wait for the user to log in manually."""
        self.driver.get(LOGIN_URL)
        logger.info("🔑 Please log in to LinkedIn manually in the browser …")
        logger.info("   Waiting for you to reach the feed page …")

        try:
            # Wait up to 5 minutes for the user to finish logging in.
            WebDriverWait(self.driver, 300).until(
                EC.url_contains("/feed")
            )
        except Exception:
            logger.error("Login timed out (5 min). Aborting.")
            return False

        random_delay(2, 4)  # let the page settle
        self._save_cookies()
        logger.info("✅ Login successful — cookies saved.")
        return True

    # ------------------------------------------------------------------
    # Cookie helpers
    # ------------------------------------------------------------------

    def _save_cookies(self) -> None:
        cookies = self.driver.get_cookies()
        with open(self.cookie_path, "w", encoding="utf-8") as fh:
            json.dump(cookies, fh, indent=2)
        logger.info(f"Saved {len(cookies)} cookies to {self.cookie_path}")

    def _load_cookies(self) -> bool:
        """Load cookies and validate the resulting session."""
        try:
            with open(self.cookie_path, "r", encoding="utf-8") as fh:
                cookies = json.load(fh)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning(f"Could not read cookie file: {exc}")
            return False

        # Navigate to LinkedIn first (cookies require a matching domain).
        self.driver.get("https://www.linkedin.com/")
        random_delay(1, 2)

        for cookie in cookies:
            # Selenium rejects cookies with certain keys.
            for key in ("sameSite", "expiry"):
                cookie.pop(key, None)
            try:
                self.driver.add_cookie(cookie)
            except Exception:
                pass  # skip problematic cookies

        return self._validate_session()

    def _validate_session(self) -> bool:
        """Navigate to the feed and check we are authenticated."""
        self.driver.get(FEED_URL)
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.feed-shared-update-v2, .scaffold-layout__main")
                )
            )
            return True
        except Exception:
            return False
