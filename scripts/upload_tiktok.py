import json
import os
from pathlib import Path

import requests


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


def run() -> dict:
    config = load_json(CONFIG_PATH)
    metadata = load_json(latest_metadata_path())
    topic = metadata["topic"]
    caption = config["platform_templates"]["tiktok"]["caption_template"].format(topic=topic)

    client_key = os.getenv("TIKTOK_CLIENT_ID")
    client_secret = os.getenv("TIKTOK_CLIENT_SECRET")
    access_token = os.getenv("TIKTOK_ACCESS_TOKEN")
    video_url = os.getenv("TIKTOK_VIDEO_URL")
    if not client_key or not client_secret or not access_token:
        raise ValueError("TIKTOK_CLIENT_ID, TIKTOK_CLIENT_SECRET and TIKTOK_ACCESS_TOKEN are required.")
    if not video_url:
        raise ValueError("TIKTOK_VIDEO_URL is required and must be a publicly accessible video URL.")

    auth_header = "Bearer " + access_token
    response = requests.post(
        "https://open.tiktokapis.com/v2/post/publish/video/init/",
        headers={"Authorization": auth_header, "Content-Type": "application/json"},
        json={
            "source_info": {"source": "PULL_FROM_URL", "video_url": video_url},
            "post_info": {"title": caption[:150]},
        },
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    publish_id = (
        data.get("data", {}).get("publish_id")
        or data.get("data", {}).get("task_id")
        or data.get("publish_id")
    )

    return {"platform": "tiktok", "publish_id": publish_id, "status": "uploaded"}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
