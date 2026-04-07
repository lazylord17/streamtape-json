import os
import requests
import json
import base64
import time

USERNAME = os.getenv("STREAMTAPE_USERNAME")
PASSWORD = os.getenv("STREAMTAPE_PASSWORD")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPO")  # lazylord17/streamtape-json
BRANCH = "main"  # replace with your default branch

API_URL = f"https://api.streamtape.com/file/listfolder?login={USERNAME}&key={PASSWORD}"
GITHUB_API = f"https://api.github.com/repos/{REPO}/contents/streamtape_videos.json"
LOCAL_JSON = "/tmp/streamtape_videos.json"

def fetch_videos():
    retries = 0
    while retries < 10:
        try:
            r = requests.get(API_URL, timeout=20)
            if r.status_code == 429:
                print("Rate limit hit, waiting 5 sec...")
                time.sleep(5)
                retries += 1
                continue
            r.raise_for_status()
            data = r.json()
            if data.get("status") == 200:
                return data["result"]
            else:
                print("API returned error:", data)
                return {}
        except Exception as e:
            print("Fetch error:", e)
            time.sleep(5)
            retries += 1
    raise Exception("Failed to fetch Streamtape videos after retries")

def save_local_json(data):
    with open(LOCAL_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def upload_to_github():
    with open(LOCAL_JSON, "r", encoding="utf-8") as f:
        content = f.read()

    content_b64 = base64.b64encode(content.encode()).decode()

    # Check if file exists on GitHub
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(GITHUB_API + f"?ref={BRANCH}", headers=headers)
    if r.status_code == 200:
        sha = r.json().get("sha")
    else:
        sha = None

    payload = {
        "message": "Update Streamtape videos JSON",
        "content": content_b64,
        "branch": BRANCH,
    }
    if sha:
        payload["sha"] = sha

    r = requests.put(GITHUB_API, headers=headers, json=payload)
    if r.status_code in [200, 201]:
        print("✅ Uploaded JSON successfully")
    else:
        print("❌ Failed to upload JSON:", r.status_code, r.text)

if __name__ == "__main__":
    print("Fetching Streamtape root folder...")
    videos = fetch_videos()
    save_local_json(videos)
    upload_to_github()
