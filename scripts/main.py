import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

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


def run_pipeline() -> dict:
    load_dotenv()
    setup_logging()
    logging.info("Starting daily science video automation pipeline.")

    results = {
        "script": safe_run("script_generation", generate_script.run),
        "video": None,
        "uploads": {},
    }

    if results["script"]["status"] != "success":
        return results

    results["video"] = safe_run("video_generation", generate_video.run)
    if results["video"]["status"] != "success":
        return results

    if _env_enabled("ENABLE_YOUTUBE"):
        results["uploads"]["youtube"] = safe_run("upload_youtube", upload_youtube.run)
    if _env_enabled("ENABLE_INSTAGRAM"):
        results["uploads"]["instagram"] = safe_run("upload_instagram", upload_instagram.run)
    if _env_enabled("ENABLE_TIKTOK"):
        results["uploads"]["tiktok"] = safe_run("upload_tiktok", upload_tiktok.run)

    summary_path = ROOT_DIR / "output" / "last_run.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    failed_uploads = [k for k, v in results["uploads"].items() if v["status"] != "success"]
    if failed_uploads:
        logging.warning("Pipeline completed with failed uploads: %s", ", ".join(failed_uploads))
    else:
        logging.info("Pipeline completed successfully.")
    return results


if __name__ == "__main__":
    print(json.dumps(run_pipeline(), indent=2))
