"""
post_scraper.py — Scrapes a single LinkedIn post: opens in new tab,
expands all comments/replies, and extracts text.
"""

import os
import sys
import time
from typing import List, Dict

# Ensure project root is in path so `linkedin_scraper` package is importable
# This allows running this file directly for debugging
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from linkedin_scraper.utils import (
    logger,
    safe_click,
    short_delay,
    apply_network_blocking,
)


class PostScraper:
    """Handles scraping of a single LinkedIn post."""

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver

    def scrape_post(self, post_url: str) -> List[Dict[str, str]]:
        """
        Open the post URL in a new tab, expand all comments, and return
        extracted data.
        """
        logger.info(f"Processing post: {post_url}")
        
        # Open in a new tab to preserve the feed state in the main tab.
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[-1])
        
        # Apply network blocking to the new tab
        apply_network_blocking(self.driver)
        
        try:
            self.driver.get(post_url)
            # time.sleep(3) -> Optimized to wait for content
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "article, .feed-shared-update-v2"))
                )
            except TimeoutException:
                 logger.warning(f"Timeout waiting for post content: {post_url}")
            
            # 1. Expand comments
            self._expand_comments()
            
            # 2. Extract data
            comments = self._extract_comments(post_url)
            logger.info(f"  -> Extracted {len(comments)} comment(s).")
            return comments

        except Exception as e:
            logger.error(f"Error scraping post {post_url}: {e}")
            return []
            
        finally:
            # Always close the tab and switch back
            if len(self.driver.window_handles) > 1:
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
            short_delay()

    def _expand_comments(self) -> None:
        """
        Continuously find and click 'Load more comments', 'View more replies',
        or 'see more' buttons until none remain.
        """
        # Selectors for various "expand" buttons
        current_buttons_selectors = [
            "button.comments-comments-list__load-more-comments-button",
            "button.comments-comment-item__show-more-button",
            "button.feed-shared-inline-show-more-text__see-more-less-toggle",
            "span.artdeco-button__text" 
        ]

        max_clicks = 150
        clicks = 0
        consecutive_no_clicks = 0
        
        while clicks < max_clicks:
            clicked_any = False
            
            for selector in current_buttons_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for el in elements:
                    if not el.is_displayed():
                        continue
                        
                    if "artdeco-button__text" in selector:
                        text = el.text.lower()
                        # Strict filtering to avoid infinite loops on "Reply" buttons
                        if "load more comments" not in text and "previous replies" not in text:
                            continue

                    try:
                        if safe_click(self.driver, el):
                            clicked_any = True
                            clicks += 1
                            short_delay()
                    except Exception:
                        pass
            
            if not clicked_any:
                consecutive_no_clicks += 1
                if consecutive_no_clicks >= 3:
                     break

                self.driver.execute_script("window.scrollBy(0, 300);")
                time.sleep(1)
                
                # Double check after scroll
                found_new = False
                for selector in current_buttons_selectors:
                    if self.driver.find_elements(By.CSS_SELECTOR, selector):
                        found_new = True
                        break
                if not found_new:
                    break
            else:
                consecutive_no_clicks = 0
                time.sleep(1.5)

        if clicks >= max_clicks:
            logger.warning("  ⚠️ Reached max click limit for comments expansion.")

    def _extract_comments(self, post_url: str) -> List[Dict[str, str]]:
        """Parse the DOM for comment containers using robust selectors."""
        results = []
        
        # 1. Identify comment entities
        # Use a broad selector for the article container
        comment_elements = self.driver.find_elements(By.CSS_SELECTOR, "article.comments-comment-entity")
        logger.info(f"    Found {len(comment_elements)} comment candidates in DOM.")

        for el in comment_elements:
            try:
                # Scroll into view to ensure text rendering
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
                
                # --- Text Extraction ---
                text = ""
                # Try specific content span first
                try:
                    text_node = el.find_element(By.CSS_SELECTOR, ".comments-comment-item__main-content")
                    text = text_node.text.strip()
                    # Fallback to textContent if .text is empty (hidden/off-screen)
                    if not text:
                         text = text_node.get_attribute("textContent").strip()
                except NoSuchElementException:
                    pass
                
                # Fallback: look for generic text body
                if not text:
                    try:
                         text_node = el.find_element(By.CSS_SELECTOR, "div.update-components-text")
                         text = text_node.text.strip()
                    except NoSuchElementException:
                        pass
                
                if not text:
                    continue # Skip if absolutely no text found

                # --- Author Extraction ---
                author_name = "Unknown"
                profile_url = ""
                
                # Check for "comment-meta" (structure in user HTML) or "post-meta" (older)
                meta_selectors = [
                    ".comments-comment-meta__actor",
                    ".comments-post-meta__actor"
                ]
                
                for meta_sel in meta_selectors:
                    try:
                        actor_node = el.find_element(By.CSS_SELECTOR, meta_sel)
                        
                        # Link
                        try:
                            link_el = actor_node.find_element(By.TAG_NAME, "a")
                            profile_url = link_el.get_attribute("href").split("?")[0]
                        except NoSuchElementException:
                            pass
                            
                        # Name
                        try:
                            # Try definition title or name span
                            name_el = actor_node.find_element(By.CSS_SELECTOR, ".comments-comment-meta__description-title, span.comments-post-meta__name-text")
                            author_name = name_el.text.strip()
                        except NoSuchElementException:
                             # Fallback: just get all text from the actor block
                             author_name = actor_node.text.split("\n")[0].strip()
                        
                        if author_name and author_name != "Unknown":
                            break
                    except NoSuchElementException:
                        continue
                
                # Clean up author name (remove "Status is online" etc if leaked)
                author_name = author_name.split("•")[0].strip()

                # Extract URN/ID
                urn = el.get_attribute("data-id") or el.get_attribute("data-urn") or ""

                results.append({
                    "post_url": post_url,
                    "urn": urn,
                    "comment": text,
                    "user_profile_url": profile_url,
                    "author_name": author_name
                })
                    
            except StaleElementReferenceException:
                continue
            except Exception as e:
                logger.warning(f"Error extracting single comment: {e}")
                
        return results

if __name__ == "__main__":
    # Simple self-test enabling run of just this file
    pass
