import json
import logging
import os
import time
from hashlib import sha1
from pathlib import Path

from dotenv import load_dotenv
import requests

import generate_script
import generate_video
import upload_instagram
import upload_tiktok
import upload_youtube


ROOT_DIR = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT_DIR / "output" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def _env_enabled(name: str) -> bool:
    return os.getenv(name, "true").strip().lower() in {"true", "1", "yes", "on"}


def setup_logging() -> None:
    log_path = LOG_DIR / "pipeline.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[logging.FileHandler(log_path), logging.StreamHandler()],
    )


def safe_run(label: str, fn):
    try:
        result = fn()
        if isinstance(result, Path):
            result = str(result)
        logging.info("%s success: %s", label, result)
        return {"status": "success", "result": result}
    except Exception as exc:
        logging.exception("%s failed", label)
        return {"status": "failed", "error": str(exc)}


def upload_video_to_cloudinary(video_path: str) -> str | None:
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")
    if not cloud_name or not api_key or not api_secret:
        return None

    timestamp = int(time.time())
    signature_raw = f"timestamp={timestamp}{api_secret}"
    signature = sha1(signature_raw.encode("utf-8")).hexdigest()
    with open(video_path, "rb") as video_file:
        response = requests.post(
            f"https://api.cloudinary.com/v1_1/{cloud_name}/video/upload",
            data={"api_key": api_key, "timestamp": timestamp, "signature": signature},
            files={"file": video_file},
            timeout=120,
        )
    response.raise_for_status()
    return response.json().get("secure_url")


def run_pipeline() -> dict:
    load_dotenv()
    setup_logging()
    logging.info("Starting daily science video automation pipeline.")

    results = {
        "script": safe_run("script_generation", generate_script.run),
        "video": None,
        "uploads": {},
    }

    if results["script"]["status"] == "success":
        results["video"] = safe_run("video_generation", generate_video.run)
        if results["video"]["status"] == "success":
            video_result = results["video"]["result"]
            generated_video_url = upload_video_to_cloudinary(video_result["video_path"])
            if generated_video_url:
                os.environ.setdefault("INSTAGRAM_VIDEO_URL", generated_video_url)
                os.environ.setdefault("TIKTOK_VIDEO_URL", generated_video_url)
                video_result["public_video_url"] = generated_video_url
            if _env_enabled("ENABLE_YOUTUBE"):
                results["uploads"]["youtube"] = safe_run("upload_youtube", upload_youtube.run)
            if _env_enabled("ENABLE_INSTAGRAM"):
                results["uploads"]["instagram"] = safe_run("upload_instagram", upload_instagram.run)
            if _env_enabled("ENABLE_TIKTOK"):
                results["uploads"]["tiktok"] = safe_run("upload_tiktok", upload_tiktok.run)

    summary_path = ROOT_DIR / "output" / "last_run.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    failed_stages = []
    if results["script"]["status"] != "success":
        failed_stages.append("script_generation")
    if results["video"] and results["video"]["status"] != "success":
        failed_stages.append("video_generation")
    failed_uploads = [k for k, v in results["uploads"].items() if v["status"] != "success"]
    failed_stages.extend([f"upload_{name}" for name in failed_uploads])
    if failed_stages:
        logging.warning("Pipeline completed with failures: %s", ", ".join(failed_stages))
    else:
        logging.info("Pipeline completed successfully.")
    return results


if __name__ == "__main__":
    pipeline_results = run_pipeline()
    print(json.dumps(pipeline_results, indent=2))
    failure_exists = (
        pipeline_results["script"]["status"] != "success"
        or (pipeline_results["video"] and pipeline_results["video"]["status"] != "success")
        or any(result["status"] != "success" for result in pipeline_results["uploads"].values())
    )
    raise SystemExit(1 if failure_exists else 0)
