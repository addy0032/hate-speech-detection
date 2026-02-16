import requests
import time
import json
import sys

def test_youtube_api():
    base_url = "http://localhost:8000"
    
    # Check if server is running
    try:
        requests.get(base_url)
    except requests.exceptions.ConnectionError:
        print("Error: Backend server is not running on port 8000.")
        sys.exit(1)

    print("Testing YouTube Scrape API...")
    
    # Channel to test
    channel_url = "https://www.youtube.com/@AsianSensation" 
    
    payload = {
        "urls": [channel_url],
        "days": 60 
    }
    
    try:
        # 1. Start Scrape
        print(f"Starting scrape for {channel_url}...")
        response = requests.post(f"{base_url}/scrape/youtube", json=payload)
        response.raise_for_status()
        task_data = response.json()
        task_id = task_data["task_id"]
        print(f"Task started with ID: {task_id}")
        
        # 2. Poll Status
        while True:
            status_response = requests.get(f"{base_url}/status/{task_id}")
            status_response.raise_for_status()
            status_data = status_response.json()
            status = status_data["status"]
            
            print(f"Status: {status} - Last progress: {status_data['progress'][-1] if status_data['progress'] else 'None'}")
            
            if status in ["completed", "failed"]:
                if status == "completed":
                    results = status_data.get("results", [])
                    print(f"Success! Found {len(results)} videos in response.")
                    if results:
                        print(f"First video: {results[0].get('post_url')}")
                        print(f"Comments: {results[0].get('comment_count')}")
                        if results[0].get('comments'):
                            first_comment = results[0]['comments'][0]
                            print(f"Sample Comment Keys: {first_comment.keys()}")
                            print(f"Sample Comment Label: {first_comment.get('label')}")
                            if 'comment' in first_comment and 'author_name' in first_comment:
                                print("Keys validation passed.")
                            else:
                                print("Keys validation FAILED.")
                        
                else:
                    print(f"Task failed: {status_data.get('error')}")
                break
            
            time.sleep(2)
            
    except Exception as e:
        print(f"Test failed with exception: {e}")

if __name__ == "__main__":
    test_youtube_api()
