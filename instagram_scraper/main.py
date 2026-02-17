from .post_fetcher import PostFetcher
from linkedin_scraper.storage import Storage
from linkedin_scraper.classifier import CommentClassifier
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def scrape_instagram_profile(username, days, session_user=None, session_file=None, callback=None):
    """
    Orchestrates the scraping of an Instagram profile.
    """
    if callback: callback(f"Initializing Instagram scraper for {username}...")
    
    fetcher = PostFetcher(session_user=session_user, session_file=session_file)
    storage = Storage()
    classifier = CommentClassifier()
    
    if not classifier.client:
         if callback: callback("Warning: Classifier not initialized (check API key).")
    
    # 1. Fetch Posts
    if callback: callback("Fetching posts from profile...")
    posts = fetcher.fetch_posts(username, days)
    
    if not posts:
        if callback: callback("No posts found in the specified period.")
        return []
    
    if callback: callback(f"Found {len(posts)} posts. Processing comments...")
    
    results = []
    
    for i, post in enumerate(posts, 1):
        if callback: callback(f"Processing post {i}/{len(posts)}: {post.get('shortcode')}")
        
        comments = post.get('comments', [])
        transformed_comments = []
        
        if callback and comments: callback(f"Classifying {len(comments)} comments...")

        for c in comments:
            text = c.get('text', '')
            label = "unknown"
            if text and classifier.client:
                label = classifier.classify(text)
            elif not text:
                label = "safe"
            
            transformed_comments.append({
                "comment_id": c.get('comment_id'),
                "urn": c.get('comment_id'), # Use ID as URN
                "comment": text,
                "author_name": c.get('author'),
                "timestamp": c.get('created_at'),
                "likes": c.get('likes'),
                "label": label
            })
            
        post_data = {
            "post_url": post.get('post_url'),
            "caption": post.get('caption'),
            "upload_date": post.get('upload_date'),
            "comments": transformed_comments,
            "comment_count": len(transformed_comments),
            "thumbnail_url": post.get('thumbnail_url')
        }
        
        results.append(post_data)
        
        # Store incrementally
        comments_to_save = []
        for c in transformed_comments:
            comments_to_save.append({
                "post_url": post.get('post_url'),
                "comment": c.get('comment'),
                "urn": c.get('urn'),
                "author_name": c.get('author_name'),
                "label": c.get('label'),
                "scraped_at": datetime.now().isoformat()
            })
            
        if comments_to_save:
            storage.add_comments(comments_to_save)
            storage.save()
            
    if callback: callback("Instagram scraping completed.")
    return results
