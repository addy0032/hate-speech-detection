from itertools import islice
from youtube_comment_downloader import *
import logging

logger = logging.getLogger(__name__)

class CommentFetcher:
    def __init__(self):
        self.downloader = YoutubeCommentDownloader()

    def fetch_comments(self, video_id, max_comments=None):
        """
        Fetches comments for a given video ID.
        """
        url = f"https://www.youtube.com/watch?v={video_id}"
        comments_found = []
        
        try:
            generator = self.downloader.get_comments_from_url(url, sort_by=SORT_BY_POPULAR)
            
            if max_comments:
                generator = islice(generator, max_comments)
                
            for comment in generator:
                comments_found.append({
                    'comment_id': comment.get('cid'),
                    'text': comment.get('text'),
                    'author': comment.get('author'),
                    'time': comment.get('time'),
                    'votes': comment.get('votes'),
                    'photo': comment.get('photo'),
                    'heart': comment.get('heart'),
                    'reply': comment.get('reply', False)
                })
                
        except Exception as e:
            logger.error(f"Error fetching comments for video {video_id}: {e}")
            
        return comments_found
