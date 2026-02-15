# LinkedIn Scraper

A production-grade LinkedIn scraper using Python and Selenium. Scrapes posts from a target page (School/Company) within the last 14 days, extracts comments, and saves them to a JSON file.

## Features
- **Manual Login & Session Reuse**: Logs in once, saves cookies, and reuses them for future runs.
- **Smart Feed Scrolling**: Scrolls until posts are older than 14 days.
- **Comment Expansion**: Clicks "Load more comments" and "View more replies" to get full conversations.
- **Robustness**: Handles dynamic loading, stale elements, and random delays to mimic human behavior.
- **Data Persistence**: Appends new comments to `comments.json`, avoiding duplicates.

## Prerequisites

- Python 3.12+
- Chrome Browser installed

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Project Structure**:
   ```
   linkedin_scraper/
   ├── auth.py         # Login & Cookie management
   ├── feed_scraper.py # Feed scrolling logic
   ├── post_scraper.py # Individual post & comment scraping
   ├── storage.py      # JSON saving & deduplication
   ├── utils.py        # Helpers strings, delays, scrolling
   └── main.py         # Entry point
   ```

## Usage

Run the scraper:

```bash
python -m linkedin_scraper.main
```

### Options

- `--url`: Target LinkedIn page URL (default: BPIT School Page).
- `--days`: How many days back to scrape (default: 14).
- `--headless`: Run browser in background (not recommended for initial login).

Example:
```bash
python -m linkedin_scraper.main --url "https://www.linkedin.com/company/google/posts/" --days 7
```

## First Run (Important)

On the very first run, a browser window will open.
1. Use the browser window to **log in to LinkedIn manually**.
2. Once logged in and redirected to the feed, the script will detect the session, save cookies, and proceed automatically.
3. Future runs will skip login.

## Output

Data is saved to `comments.json`:

```json
[
  {
    "index": 1,
    "post_url": "https://www.linkedin.com/feed/update/...",
    "comment": "Great achievement!",
    "user_profile_url": "https://www.linkedin.com/in/...",
    "scraped_at": "2024-06-15T10:00:00"
  },
  ...
]
```

## Disclaimer

This tool is for educational purposes only. Scraping LinkedIn may violate their Terms of Service. Use responsibly.
