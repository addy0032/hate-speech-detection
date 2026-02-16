from pydantic import BaseModel
from typing import List, Optional

class ScrapeRequest(BaseModel):
    urls: List[str]
    days: int = 30

class ScrapeResult(BaseModel):
    post_url: str
    comment_count: int
    comments: List[dict]

class ScrapeStatus(BaseModel):
    task_id: str
    status: str  # "pending", "processing", "completed", "failed"
    progress: List[str] = []
    error: Optional[str] = None
    results: Optional[List[ScrapeResult]] = None
