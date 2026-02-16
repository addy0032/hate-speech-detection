import threading
import uuid
import time
from typing import Dict
from linkedin_scraper.main import init_driver
from linkedin_scraper.post_scraper import PostScraper
from linkedin_scraper.feed_scraper import FeedScraper
from linkedin_scraper.classifier import CommentClassifier
from linkedin_scraper.storage import Storage
from linkedin_scraper.auth import LinkedInAuth
from linkedin_scraper.utils import logger
from .models import ScrapeStatus, ScrapeResult

# In-memory storage for task status (replace with proper DB in production)
tasks: Dict[str, ScrapeStatus] = {}

def run_scraper_task(task_id: str, urls: list[str], days: int = 30):
    task = tasks[task_id]
    task.status = "processing"
    task.progress.append(f"Initializing driver (Days limit: {days})...")
    
    driver = None
    try:
        driver = init_driver(headless=False) # Or True if configured
        
        # Auth
        task.progress.append("Authenticating...")
        auth = LinkedInAuth(driver)
        if not auth.authenticate():
            raise Exception("Authentication failed")
            
        post_scraper = PostScraper(driver)
        # We can reuse the existing storage logic or build results in memory.
        # For now, let's build results in memory to return to frontend, 
        # but also use the existing Storage to persist to JSON as a backup/cache.
        storage = Storage() 
        results = []

        classifier = CommentClassifier()
        if not classifier.client:
             task.progress.append("Warning: Classifier not initialized (check API key).")

        # Expand feed URLs
        feed_scraper = FeedScraper(driver, max_days=days)
        final_urls = []
        
        for url in urls:
            if "linkedin.com/school/" in url or "linkedin.com/company/" in url or "linkedin.com/in/" in url:
                task.progress.append(f"Scraping feed: {url}")
                try:
                    posts = feed_scraper.scrape_feed(url)
                    found_urls = [p["post_url"] for p in posts]
                    task.progress.append(f"Found {len(found_urls)} posts.")
                    final_urls.extend(found_urls)
                except Exception as e:
                     logger.error(f"Error scraping feed {url}: {e}")
                     task.progress.append(f"Error scraping feed: {e}")
            else:
                final_urls.append(url)
        
        # Deduplicate
        final_urls = list(dict.fromkeys(final_urls))
        total_urls = len(final_urls)
        
        if total_urls == 0:
            task.progress.append("No posts found to scrape.")
            task.status = "completed"
            return

        for i, url in enumerate(final_urls, 1):
            task.progress.append(f"Scraping post {i}/{total_urls}: {url}")
            comments = post_scraper.scrape_post(url)
            
            # Classification
            if comments and classifier.client:
                task.progress.append(f"Classifying {len(comments)} comments...")
                for comment in comments:
                    text = comment.get("comment", "")
                    if text:
                        comment["label"] = classifier.classify(text)
                    else:
                        comment["label"] = "safe"

            # Save to local JSON storage
            storage.add_comments(comments)
            storage.save()

            results.append(ScrapeResult(
                post_url=url,
                comment_count=len(comments),
                comments=comments
            ))
            
            task.progress.append(f"Finished post {i}")
            time.sleep(2) # rate limit buffer

        task.results = results
        task.status = "completed"
        task.progress.append("All tasks completed successfully.")

    except Exception as e:
        logger.exception(f"Task failed: {e}")
        task.status = "failed"
        task.error = str(e)
        task.progress.append(f"Error: {str(e)}")
    finally:
        if driver:
            driver.quit()

def start_scraping(urls: list[str], days: int = 30) -> str:
    task_id = str(uuid.uuid4())
    tasks[task_id] = ScrapeStatus(task_id=task_id, status="pending")
    
    thread = threading.Thread(target=run_scraper_task, args=(task_id, urls, days))
    thread.daemon = True
    thread.start()
    
    return task_id


import json
import os

def load_existing_comments() -> ScrapeStatus:
    file_path = "comments.json"
    if not os.path.exists(file_path):
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if not data:
            return None

        # Group by post_url
        grouped = {}
        for comment in data:
            url = comment.get("post_url")
            if not url:
                continue
            if url not in grouped:
                grouped[url] = []
            grouped[url].append(comment)
        
        results = []
        for url, comments in grouped.items():
            results.append(ScrapeResult(
                post_url=url,
                comment_count=len(comments),
                comments=comments
            ))
            
        task_id = "existing_data"
        status = ScrapeStatus(
            task_id=task_id,
            status="completed",
            progress=["Loaded from existing comments.json"],
            results=results
        )
        tasks[task_id] = status
        return status
        
    except Exception as e:
        logger.error(f"Failed to load existing comments: {e}")
        return None

def get_task_status(task_id: str) -> ScrapeStatus:
    return tasks.get(task_id)
