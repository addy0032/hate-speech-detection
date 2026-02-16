from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import ScrapeRequest, ScrapeStatus, ScrapeResult
from .service import run_scraper_task, get_task_status, tasks, start_scraping, load_existing_comments, start_youtube_scraping
import csv
import io
from fastapi.responses import StreamingResponse

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/scrape", response_model=ScrapeStatus)
async def scrape(request: ScrapeRequest):
    if not request.urls:
        raise HTTPException(status_code=400, detail="No URLs provided")
    
    task_id = start_scraping(request.urls, request.days)
    return tasks[task_id]

@app.post("/scrape/youtube", response_model=ScrapeStatus)
async def scrape_youtube(request: ScrapeRequest):
    if not request.urls:
        raise HTTPException(status_code=400, detail="No channel URL provided")
        
    # Take the first URL as the channel
    task_id = start_youtube_scraping(request.urls[0], request.days)
    return tasks[task_id]

@app.get("/load-existing", response_model=ScrapeStatus)
async def load_existing():
    status = load_existing_comments()
    if not status:
        raise HTTPException(status_code=404, detail="No existing data found")
    return status

@app.get("/status/{task_id}", response_model=ScrapeStatus)
async def get_status(task_id: str):
    status = get_task_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    return status

@app.get("/export/{task_id}")
async def export_csv(task_id: str):
    status = get_task_status(task_id)
    if not status or status.status != "completed" or not status.results:
        raise HTTPException(status_code=404, detail="Task not ready or not found")

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Post URL", "Comment", "Label", "Author Name", "User Profile URL"])

    for result in status.results:
        if isinstance(result, ScrapeResult): # Validate type for safety
             for comment in result.comments:
                writer.writerow([
                    result.post_url,
                    comment.get("comment", ""),
                    comment.get("label", ""),
                    comment.get("author_name", "Unknown"),
                    comment.get("user_profile_url", "")
                ])
        elif isinstance(result, dict):
             # Handle if it was stored as dict
             pass 

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=comments_{task_id}.csv"}
    )

@app.get("/")
def read_root():
    return {"message": "LinkedIn Scraper API is running"}
