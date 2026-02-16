import json
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Storage:
    def __init__(self, filename="youtube_comments.json"):
        self.filename = filename

    def load_data(self):
        if not os.path.exists(self.filename):
            return []
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def save_data(self, new_data):
        existing_data = self.load_data()
        
        # Simple deduplication based on comment_id if available, or just append
        # structure: list of video objects, or list of comments?
        # Requirement says:
        # [
        # {
        # "video_id": "...",
        # "video_url": "...",
        # "upload_date": "...",
        # "commentd_id": "...",
        # "comment": "...",
        # "author": "...",
        # "scraped_at": "ISO_TIMESTAMP"
        # }
        # ]
        
        # We need to check for duplicates based on comment_id
        existing_ids = {item.get('comment_id') for item in existing_data if item.get('comment_id')}
        
        added_count = 0
        for item in new_data:
            if item.get('comment_id') and item.get('comment_id') not in existing_ids:
                existing_data.append(item)
                existing_ids.add(item.get('comment_id'))
                added_count += 1
            elif not item.get('comment_id'):
                 # If no ID, append but warn? or just append
                 existing_data.append(item)
                 added_count += 1

        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Saved {added_count} new comments to {self.filename}")
