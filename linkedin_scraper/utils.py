"""
utils.py — Shared helpers: logging, human-like delays, smooth scrolling, safe clicks.
"""

import logging
import random
import time

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
)
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


# ---------------------------------------------------------------------------
# Logger
# ---------------------------------------------------------------------------

def setup_logger(name: str = "linkedin_scraper", level: int = logging.INFO) -> logging.Logger:
    """Return a pre-configured logger with a console handler."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)-8s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger


logger = setup_logger()


# ---------------------------------------------------------------------------
# Delays
# ---------------------------------------------------------------------------

def random_delay(min_seconds: float = 1.0, max_seconds: float = 3.0) -> None:
    """Sleep for a random duration to mimic human behaviour."""
    time.sleep(random.uniform(min_seconds, max_seconds))


def short_delay() -> None:
    """A brief pause (0.3–0.8 s) used between rapid UI interactions."""
    random_delay(0.3, 0.8)


# ---------------------------------------------------------------------------
# Scrolling
# ---------------------------------------------------------------------------

def smooth_scroll(driver: WebDriver, pixels: int = 600, steps: int = 6) -> None:
    """Scroll the page gradually instead of jumping to the bottom."""
    step_px = pixels // steps
    for _ in range(steps):
        driver.execute_script(f"window.scrollBy(0, {step_px});")
        time.sleep(random.uniform(0.15, 0.35))


def scroll_to_element(driver: WebDriver, element: WebElement) -> None:
    """Scroll an element into the viewport centre."""
    driver.execute_script(
        "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
        element,
    )
    short_delay()


def get_page_height(driver: WebDriver) -> int:
    """Return the current document scroll height."""
    return driver.execute_script("return document.body.scrollHeight")


# ---------------------------------------------------------------------------
# Safe click with JS fallback
# ---------------------------------------------------------------------------

def safe_click(driver: WebDriver, element: WebElement, retries: int = 3) -> bool:
    """
    Try to click an element. Falls back to JavaScript click on failure.
    Returns True if the click succeeded, False otherwise.
    """
    for attempt in range(retries):
        try:
            scroll_to_element(driver, element)
            element.click()
            return True
        except (ElementClickInterceptedException, StaleElementReferenceException):
            try:
                driver.execute_script("arguments[0].click();", element)
                return True
            except StaleElementReferenceException:
                if attempt == retries - 1:
                    return False
                short_delay()
    return False


# ---------------------------------------------------------------------------
# Network Blocking (CDP)
# ---------------------------------------------------------------------------

def apply_network_blocking(driver: WebDriver) -> None:
    """
    Apply CDP Network blocking rules to the current target (tab/window).
    Blocks images, videos, and other heavy media.
    """
    try:
        # Enable Network domain explicitly
        driver.execute_cdp_cmd("Network.enable", {})

        # Block heavy media files using specific patterns for LinkedIn CDNs
        driver.execute_cdp_cmd(
            "Network.setBlockedURLs",
            {
                "urls": [
                    # Block the main image delivery endpoints
                    "*media.licdn.com/dms/image*",
                    "*licdn.com/dms/image*",
                    "*licdn.com/dms/prop/image*",

                    # Block video blobs and streams
                    "*linkedin.com/sc/h/*", 
                    "*.mp4*", 
                    "*.avi*", "*.mov*", "*.mkv*", "*.wmv*",

                    # Block standard extensions just in case (with wildcards on both sides)
                    "*.jpg*", "*.jpeg*", "*.png*", "*.gif*", "*.webp*"
                ]
            }
        )
        
        # Inject CSS/JS to hide/remove video elements from DOM prevents them from trying to load
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                const style = document.createElement('style');
                style.type = 'text/css';
                style.innerHTML = 'video, .video-js, .media-player__player, .feed-shared-update-v2__content .linkedin-player { display: none !important; }';
                document.head.appendChild(style);
            """
        })
    except Exception as e:
        logger.warning(f"Failed to apply network blocking: {e}")
