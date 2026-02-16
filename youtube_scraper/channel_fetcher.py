import yt_dlp
from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger(__name__)

class ChannelFetcher:
    def __init__(self):
        self.ydl_opts = {
            'quiet': True,
            'extract_flat': True,  # Only get metadata, don't download
            'force_generic_extractor': False,
        }

    def fetch_videos(self, channel_url_or_user, days_back):
        """
        Fetches videos from a YouTube channel within the last N days.
        """
        # Calculate the cutoff date
        cutoff_date = datetime.now() - timedelta(days=days_back)
        videos_found = []

        # Adjust URL if it's just a username
        if not channel_url_or_user.startswith("http"):
            if channel_url_or_user.startswith("@"):
                 url = f"https://www.youtube.com/{channel_url_or_user}/videos"
            else:
                 url = f"https://www.youtube.com/user/{channel_url_or_user}/videos"
        else:
            url = channel_url_or_user
            if not url.endswith("/videos"):
                url = f"{url}/videos"

        logger.info(f"Fetching videos from {url} since {cutoff_date.date()}")

        # 1. Fetch the list of videos (flat)
        logger.info(f"Fetching video list from {url}...")
        
        flat_opts = self.ydl_opts.copy()
        flat_opts['extract_flat'] = True
        
        video_entries = []
        with yt_dlp.YoutubeDL(flat_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                if 'entries' in info:
                    video_entries = list(info['entries']) # generator to list to iterate safe if needed
            except Exception as e:
                logger.error(f"Error fetching channel list: {e}")
                return []

        if not video_entries:
            logger.warning("No entries found for channel.")
            return []

        logger.info(f"Found {len(video_entries)} potential videos. checking dates...")

        # 2. Iterate and fetch details for each to check date
        # We need a new ydl instance for detailed extraction
        detail_opts = {
            'quiet': True,
            'extract_flat': False,
            'force_generic_extractor': False,
            'skip_download': True, # Important: don't download video
        }

        consecutive_old_videos = 0
        THRESHOLD_OLD = 3 # Stop after seeing 3 videos older than cutoff to be safe against slight disorder
        
        with yt_dlp.YoutubeDL(detail_opts) as ydl:
            for i, entry in enumerate(video_entries):
                if not entry: continue
                
                video_id = entry.get('id')
                video_url = entry.get('url') or f"https://www.youtube.com/watch?v={video_id}"
                
                try:
                    # Fetch details
                    # logger.debug(f"Checking video {i+1}: {video_url}")
                    vid_info = ydl.extract_info(video_url, download=False)
                    
                    upload_date_str = vid_info.get('upload_date')
                    if not upload_date_str:
                        logger.warning(f"No upload date for {video_url}, skipping.")
                        continue
                        
                    upload_date = datetime.strptime(upload_date_str, '%Y%m%d')
                    
                    if upload_date >= cutoff_date:
                        video_data = {
                            'video_id': vid_info.get('id'),
                            'video_url': video_url,
                            'title': vid_info.get('title'),
                            'upload_date': upload_date.isoformat(),
                            'thumbnails': vid_info.get('thumbnails'),
                            'channel_id': vid_info.get('channel_id'),
                            'channel_url': vid_info.get('channel_url'),
                            'uploader': vid_info.get('uploader'),
                        }
                        videos_found.append(video_data)
                        consecutive_old_videos = 0 # Reset counter
                    else:
                        consecutive_old_videos += 1
                        if consecutive_old_videos >= THRESHOLD_OLD:
                            logger.info(f"Stopped fetching after finding {THRESHOLD_OLD} older videos.")
                            break
                            
                except Exception as e:
                    logger.error(f"Error fetching details for {video_url}: {e}")
                    continue

        logger.info(f"Found {len(videos_found)} videos uploaded in the last {days_back} days.")
        return videos_found
