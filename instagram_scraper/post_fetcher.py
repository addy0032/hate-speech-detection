import instaloader
from datetime import datetime, timedelta, timezone
import time
import logging
import os

logger = logging.getLogger(__name__)

class PostFetcher:
    def __init__(self, session_user=None, session_file=None):
        self.L = instaloader.Instaloader()
        
        # Try to load session if provided, otherwise check for common session files or environment
        if session_user and session_file:
             try:
                 self.L.load_session_from_file(session_user, filename=session_file)
                 logger.info(f"Loaded session for {session_user}")
             except Exception as e:
                 logger.warning(f"Could not load session for {session_user}: {e}")
        else:
             # Fallback: check for 'session-speaking_smth' as in user example
             default_session = "session-speaking_smth"
             if os.path.exists(default_session):
                 try:
                     self.L.load_session_from_file("speaking_smth", filename=default_session)
                     logger.info(f"Loaded default session from {default_session}")
                 except Exception as e:
                     logger.warning(f"Could not load default session: {e}")
        
    def fetch_posts(self, username, days_back):
        """
        Fetches posts and comments from a user profile within the last N days.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
        
        try:
            profile = instaloader.Profile.from_username(self.L.context, username)
        except instaloader.ProfileNotExistsException:
            logger.error(f"Profile {username} does not exist.")
            return []
        except Exception as e:
             logger.error(f"Error loading profile {username}: {e}")
             return []

        posts_data = []
        
        logger.info(f"Fetching posts for {username} since {cutoff}...")
        
        for post in profile.get_posts():
            post_date = post.date_utc.replace(tzinfo=timezone.utc)
            
            if post_date < cutoff:
                break
                
            post_url = f"https://www.instagram.com/p/{post.shortcode}/"
            logger.info(f"Processing Post: {post_url}")
            
            comments_data = []
            try:
                for comment in post.get_comments():
                    comments_data.append({
                        "comment_id": str(comment.id),
                        "text": comment.text,
                        "author": comment.owner.username,
                        "created_at": comment.created_at_utc.replace(tzinfo=timezone.utc).isoformat(),
                        "likes": comment.likes_count
                    })
            except Exception as e:
                logger.error(f"Error fetching comments for post {post.shortcode}: {e}")

            posts_data.append({
                "post_url": post_url,
                "shortcode": post.shortcode,
                "caption": post.caption,
                "upload_date": post_date.isoformat(),
                "comments": comments_data,
                "comment_count": len(comments_data),
                "thumbnail_url": post.url 
            })
            
            time.sleep(2) # Avoid rate limiting
            
        logger.info(f"Fetched {len(posts_data)} posts from {username}")
        return posts_data
