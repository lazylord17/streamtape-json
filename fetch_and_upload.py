import os
import requests
import json
from base64 import b64encode

# --- Streamtape credentials ---
API_USERNAME = os.environ["STREAMTAPE_USERNAME"]
API_PASSWORD = os.environ["STREAMTAPE_PASSWORD"]

# --- GitHub details ---
GITHUB_REPO = "lazylord17/streamtape-json"
GITHUB_FILE_PATH = "streamtape_videos.json"  # path in repo
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]

# --- Fetch root folder from Streamtape ---
def fetch_root_folder():
    url = "https://api.streamtape.com/file/listfolder"
    params = {
        "login": API_USERNAME,
        "key": API_PASSWORD
    }
    response = requests.get(url, params=params, timeout=20)
    data = response.json()

    if data.get("status") != 200:
        raise Exception(f"Streamtape API error: {data.get('msg')}")

    # Only root folder
    result = data.get("result", {})
    folders = result.get("folders", [])
    files = result.get("files", [])
    return {"folders": folders, "files": files}

# --- Update GitHub file ---
def update_github_file(content: dict):
    # Check if file exists and get its SHA
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    sha = None
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        sha = response.json()["sha"]

    # Convert content to base64
    encoded_content = b64encode(json.dumps(content, indent=2).encode()).decode()

    payload = {
        "message": "Update Streamtape videos JSON",
        "content": encoded_content,
    }
    if sha:
        payload["sha"] = sha

    r = requests.put(url, headers=headers, json=payload)
    if r.status_code in [200, 201]:
        print("GitHub file updated successfully!")
    else:
        print("Failed to update GitHub file:", r.json())

if __name__ == "__main__":
    print("Fetching root folder from Streamtape...")
    data = fetch_root_folder()
    print(f"Fetched {len(data['files'])} files and {len(data['folders'])} folders.")

    print("Updating GitHub repo...")
    update_github_file(data)