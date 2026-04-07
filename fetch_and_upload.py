import os
import requests
import json
import base64
import time

# Environment variables
USERNAME = os.getenv("STREAMTAPE_USERNAME")
PASSWORD = os.getenv("STREAMTAPE_PASSWORD")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPO")  # e.g., lazylord17/streamtape-json

API_URL = f"https://api.streamtape.com/file/listfolder?login={USERNAME}&key={PASSWORD}"
GITHUB_API = f"https://api.github.com/repos/{REPO}/contents/streamtape_videos.json"
LOCAL_JSON = "/tmp/streamtape_videos.json"

MAX_RETRIES = 5

def fetch_videos():
    retries = 0
    while retries < MAX_RETRIES:
        try:
            response = requests.get(API_URL, timeout=20)
            if response.status_code == 429:  # rate limit
                print("Rate limit hit, waiting 5 sec...")
                time.sleep(5)
                retries += 1
                continue
            response.raise_for_status()
            data = response.json()
            if data.get("status") == 200:
                return data["result"]
            else:
                print("API error:", data)
                return {}
        except Exception as e:
            print("Error fetching videos:", e)
            time.sleep(5)
            retries += 1
    raise Exception("Max retries exceeded fetching Streamtape videos")

def save_local_json(data):
    with open(LOCAL_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def upload_to_github():
    with open(LOCAL_JSON, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Encode in base64
    content_b64 = base64.b64encode(content.encode("utf-8")).decode("utf-8")

    # Check if file exists on GitHub
    r = requests.get(GITHUB_API, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    sha = r.json().get("sha") if r.status_code == 200 else None

    payload = {
        "message": "Update Streamtape videos JSON",
        "content": content_b64,
        "branch": "main",
    }
    if sha:
        payload["sha"] = sha

    r = requests.put(
        GITHUB_API,
        headers={"Authorization": f"token {GITHUB_TOKEN}"},
        json=payload
    )
    if r.status_code in [200, 201]:
        print("Uploaded JSON to GitHub successfully")
    else:
        print("Failed to upload JSON:", r.status_code, r.text)

if __name__ == "__main__":
    print("Fetching all Streamtape videos...")
    result = fetch_videos()
    save_local_json(result)
    upload_to_github()
