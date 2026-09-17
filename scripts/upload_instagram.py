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

    token = os.getenv("META_ACCESS_TOKEN")
    page_id = os.getenv("INSTAGRAM_PAGE_ID")
    if not token or not page_id:
        raise ValueError("META_ACCESS_TOKEN and INSTAGRAM_PAGE_ID are required.")

    caption = config["platform_templates"]["instagram"]["caption_template"].format(topic=topic)
    base_url = f"https://graph.facebook.com/v20.0/{page_id}"

    create_resp = requests.post(
        f"{base_url}/media",
        data={
            "media_type": "REELS",
            "video_url": metadata["video_path"],
            "caption": caption,
            "access_token": token,
        },
        timeout=60,
    )
    create_resp.raise_for_status()
    creation_id = create_resp.json()["id"]

    publish_resp = requests.post(
        f"{base_url}/media_publish",
        data={"creation_id": creation_id, "access_token": token},
        timeout=60,
    )
    publish_resp.raise_for_status()
    result = publish_resp.json()

    return {
        "platform": "instagram",
        "creation_id": creation_id,
        "post_id": result.get("id"),
        "status": "uploaded",
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
