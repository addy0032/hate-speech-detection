from .channel_fetcher import ChannelFetcher
from .comment_fetcher import CommentFetcher
from linkedin_scraper.storage import Storage # Use shared storage
import logging

logger = logging.getLogger(__name__)

def scrape_channel(channel_url, days, callback=None):
    """
    Orchestrates the scraping of a YouTube channel.
    Args:
        channel_url: The URL of the YouTube channel.
        days: How many days back to look for videos.
        callback: Optional function to call with progress updates (str).
    Returns:
        List of dictionaries containing video info and comments.
    """
    if callback: callback(f"Initializing YouTube scraper for {channel_url}...")
    
    channel_fetcher = ChannelFetcher()
    comment_fetcher = CommentFetcher()
    storage = Storage()
    
    # 1. Fetch Videos
    if callback: callback("Fetching videos from channel...")
    videos = channel_fetcher.fetch_videos(channel_url, days)
    
    if not videos:
        if callback: callback("No videos found in the specified period.")
        return []
    
    if callback: callback(f"Found {len(videos)} videos. Starting comment extraction...")
    
    results = []
    
    for i, video in enumerate(videos, 1):
        video_title = video.get('title', 'Unknown Title')
        if callback: callback(f"Scraping video {i}/{len(videos)}: {video_title}")
        
        # 2. Fetch Comments
        comments = comment_fetcher.fetch_comments(video.get('video_id'))
        
        # Transform comments to standard format immediately
        transformed_comments = []
        for c in comments:
            transformed_comments.append({
                "comment_id": c.get('comment_id'), # Keep original ID if needed internally
                "urn": c.get('comment_id'), # Standard key
                "comment": c.get('text'),   # Standard key
                "author_name": c.get('author'), # Standard key
                "timestamp": c.get('time'),
                "votes": c.get('votes'),
                "photo": c.get('photo'),
                "label": "unknown" # Default label
            })
        
        video_data = {
            'video_id': video.get('video_id'),
            'post_url': video.get('video_url'), # Map to post_url for consistency
            'title': video.get('title'),
            'upload_date': video.get('upload_date'),
            'comments': transformed_comments, # Use transformed comments
            'comment_count': len(transformed_comments),
            'thumbnails': video.get('thumbnails')
        }
        
        results.append(video_data)
        
    # 3. Store incrementally using shared Storage
        storage = Storage() # Defaults to comments.json
        
        comments_to_save = []
        for c in transformed_comments:
            comments_to_save.append({
                "post_url": video.get('video_url'),
                "comment": c.get('comment'),
                "urn": c.get('urn'),
                "author_name": c.get('author_name'),
                "label": c.get('label'),
                "scraped_at": datetime.now().isoformat()
            })
            
        if comments_to_save:
            storage.add_comments(comments_to_save)
            storage.save()
            
    if callback: callback("YouTube scraping completed.")
    return results

from datetime import datetime
