import json
import os
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


ROOT_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT_DIR / "config" / "config.json"
OUTPUT_DIR = ROOT_DIR / "output" / "videos"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def latest_metadata_path() -> Path:
    run_dirs = sorted([d for d in OUTPUT_DIR.glob("*") if d.is_dir()])
    if not run_dirs:
        raise FileNotFoundError("No generated video run found in output/videos.")
    return run_dirs[-1] / "metadata.json"


def build_youtube_client():
    creds = Credentials(
        token=None,
        refresh_token=os.getenv("YOUTUBE_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("YOUTUBE_CLIENT_ID"),
        client_secret=os.getenv("YOUTUBE_CLIENT_SECRET"),
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )
    return build("youtube", "v3", credentials=creds)


def run() -> dict:
    config = load_json(CONFIG_PATH)
    metadata = load_json(latest_metadata_path())
    topic = metadata["topic"]
    template = config["platform_templates"]["youtube"]

    body = {
        "snippet": {
            "title": template["title_template"].format(topic=topic),
            "description": template["description_template"].format(topic=topic),
            "tags": template["tags"],
            "categoryId": template["categoryId"],
        },
        "status": {
            "privacyStatus": template["privacyStatus"],
            "selfDeclaredMadeForKids": False,
        },
    }

    youtube = build_youtube_client()
    media = MediaFileUpload(metadata["video_path"], resumable=False)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = request.execute()
    video_id = response.get("id")
    if video_id and metadata.get("thumbnail_path"):
        thumb_media = MediaFileUpload(metadata["thumbnail_path"], resumable=False)
        youtube.thumbnails().set(videoId=video_id, media_body=thumb_media).execute()

    return {"platform": "youtube", "video_id": video_id, "status": "uploaded"}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
