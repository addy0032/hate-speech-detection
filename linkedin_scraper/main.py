"""
main.py — Orchestrator for the LinkedIn Scraper.
"""

import argparse
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Ensure project root is in path so `linkedin_scraper` package is importable
# This allows running `python linkedin_scraper/main.py` or just `main.py`
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

from linkedin_scraper.auth import LinkedInAuth
from linkedin_scraper.classifier import CommentClassifier
from linkedin_scraper.feed_scraper import FeedScraper
from linkedin_scraper.post_scraper import PostScraper
from linkedin_scraper.storage import Storage
from linkedin_scraper.utils import logger, random_delay, apply_network_blocking


# Default target (can be overridden via CLI)
DEFAULT_TARGET_URL = "https://www.linkedin.com/school/bhagwan-parshuram-institute-of-technology/posts/?feedView=all"


def init_driver(headless: bool = False) -> webdriver.Chrome:
    """Initialize Chrome driver with anti-detection options."""
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    
    # Anti-detection & stability
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,800")
    
    # Exclude automation switches
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Disable cache to allow blocking to work effectively
    options.add_argument("--disable-application-cache")
    
    # Speed up: don't wait for all resources (images/styles) to finish loading
    options.page_load_strategy = 'eager'

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Execute CDP command to mask webdriver
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                  get: () => undefined
                })
            """
        },
    )

    # Enable Network blocking
    apply_network_blocking(driver)

    return driver


def main():
    parser = argparse.ArgumentParser(description="LinkedIn Scraper")
    parser.add_argument("--url", type=str, default=DEFAULT_TARGET_URL, help="Target LinkedIn Page URL")
    parser.add_argument("--days", type=int, default=30, help="Max days age for posts")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    args = parser.parse_args()

    logger.info("🚀 Starting LinkedIn Scraper ...")
    driver = init_driver(headless=args.headless)

    try:
        # 1. Login / Auth
        auth = LinkedInAuth(driver)
        if not auth.authenticate():
            logger.error("Authentication failed. Exiting.")
            return

        # 2. Feed Scraping
        feed_scraper = FeedScraper(driver, max_days=args.days)
        posts = feed_scraper.scrape_feed(args.url)
        
        if not posts:
            logger.info("No recent posts found. Exiting.")
            return

        # 3. Post Scraping
        post_scraper = PostScraper(driver)
        storage = Storage()
        
        logger.info(f"Processing {len(posts)} posts ...")
        for i, post in enumerate(posts, 1):
            url = post["post_url"]
            logger.info(f"[{i}/{len(posts)}] Scraping post: {url}")
            
            comments = post_scraper.scrape_post(url)
            if comments:
                new_count = storage.add_comments(comments)
                storage.save()
                logger.info(f"   -> Added {new_count} new comments (Total stored: {storage.total})")
            else:
                logger.info("   -> No comments extracted.")
            
            # Pause between posts
            random_delay(2, 4)

        logger.info("✨ Scraping complete!")

        # 4. Batch Classification (Phase 2)
        logger.info("🤖 Starting Batch Classification Phase...")
        
        # Reload storage to ensure we have latest data
        # (Though self.data is already in memory, good practice if modified externally)
        
        # Find pending comments (unknown, pending, or empty string labels)
        pending_comments = [
            c for c in storage.data 
            if not c.get("label") or c.get("label") in ["unknown", "pending", ""]
        ]
        
        if pending_comments:
            logger.info(f"🔍 Found {len(pending_comments)} comments pending classification.")
            classifier = CommentClassifier()
            
            if classifier.client:
                processed_count = 0
                errors = 0
                total_pending = len(pending_comments)
                
                logger.info(f"   Using model: openai/gpt-oss-120b (via Groq)")
                
                for i, comment in enumerate(pending_comments, 1):
                    text = comment.get("comment", "")
                    if not text:
                        comment["label"] = "safe" # Empty is safe
                        processed_count += 1
                        continue

                    # Classify
                    label = classifier.classify(text)
                    comment["label"] = label
                    
                    if not label or label == "unknown" or label == "error":
                        logger.warning(f"   ⚠️  Failed to classify comment {i}: '{text[:20]}...' -> '{label}'")
                        errors += 1
                    else:
                        processed_count += 1
                        
                    # Save periodically
                    if i % 5 == 0:
                        storage.save()
                        logger.info(f"   Classified {i}/{total_pending} comments...")

                storage.save()
                logger.info(f"✅ Batch classification complete! Processed: {processed_count}. Errors: {errors}.")
            else:
                logger.warning("⚠️  Skipping classification — Groq client not available. Check API Key.")
        else:
             logger.info("✨ All comments are already classified.")

    except KeyboardInterrupt:
        logger.info("Interrupted by user. Closing ...")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
