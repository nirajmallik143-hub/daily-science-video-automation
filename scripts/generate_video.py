import json
import random
from datetime import datetime, timezone
from pathlib import Path
from textwrap import wrap

from gtts import gTTS
from moviepy import (
    AudioClip,
    AudioFileClip,
    ColorClip,
    CompositeVideoClip,
    TextClip,
    VideoFileClip,
)
from PIL import Image, ImageDraw, ImageFont


ROOT_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT_DIR / "config" / "config.json"
OUTPUT_DIR = ROOT_DIR / "output"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_latest_script_record() -> tuple[Path, dict]:
    scripts_dir = OUTPUT_DIR / "scripts"
    script_files = sorted(scripts_dir.glob("*.json"))
    if not script_files:
        raise FileNotFoundError("No generated script found in output/scripts.")
    script_path = script_files[-1]
    return script_path, json.loads(script_path.read_text(encoding="utf-8"))


def _get_caption_lines(text: str, words_per_line: int) -> list[str]:
    words = text.split()
    chunks = [" ".join(words[i : i + words_per_line]) for i in range(0, len(words), words_per_line)]
    return chunks or [text]


def _pick_base_video(config: dict, duration: float):
    width = config["video"]["width"]
    height = config["video"]["height"]
    stock_dir = ROOT_DIR / config["paths"]["stock_footage_dir"]
    stock_files = list(stock_dir.glob("*.mp4")) if stock_dir.exists() else []

    if stock_files:
        clip = VideoFileClip(str(random.choice(stock_files)))
        final_duration = min(duration, clip.duration)
        clip = clip.with_duration(final_duration).resized((width, height))
        return clip, final_duration
    clip = ColorClip(size=(width, height), color=(8, 20, 35), duration=duration)
    return clip, duration


def _make_thumbnail(topic: str, output_dir: Path) -> Path:
    thumb_path = output_dir / "thumbnail.jpg"
    image = Image.new("RGB", (1080, 1920), color=(10, 17, 28))
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 88)
    except OSError:
        font = ImageFont.load_default()
    lines = "\n".join(wrap(topic.upper(), width=15))
    draw.multiline_text((80, 740), lines, fill=(255, 255, 255), font=font, spacing=20)
    image.save(thumb_path, format="JPEG", quality=92)
    return thumb_path


def run() -> dict:
    config = load_json(CONFIG_PATH)
    script_path, script_record = load_latest_script_record()
    text = script_record["script_text"]
    topic = script_record["topic"]

    run_stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = OUTPUT_DIR / "videos" / run_stamp
    run_dir.mkdir(parents=True, exist_ok=True)

    audio_path = run_dir / "voiceover.mp3"
    try:
        gTTS(text=text, lang=config["video"]["voice_language"]).save(str(audio_path))
    except Exception:
        approx_seconds = max(12, min(config["video"]["max_duration_seconds"], len(text.split()) // 2))
        fallback_audio = AudioClip(lambda t: 0.0, duration=approx_seconds, fps=44100)
        fallback_audio.write_audiofile(str(audio_path), fps=44100, logger=None)
    audio_clip = AudioFileClip(str(audio_path))
    duration = min(audio_clip.duration, float(config["video"]["max_duration_seconds"]))
    audio_clip = audio_clip.subclipped(0, duration)

    base_video, duration = _pick_base_video(config, duration)
    audio_clip = audio_clip.subclipped(0, duration)
    base_video = base_video.with_audio(audio_clip)
    caption_lines = _get_caption_lines(text, config["video"]["caption_words_per_line"])
    line_duration = max(duration / max(len(caption_lines), 1), 1.0)
    captions = []
    for index, line in enumerate(caption_lines):
        caption = (
            TextClip(
                text=line,
                font_size=config["video"]["font_size"],
                color="white",
                method="caption",
                size=(config["video"]["width"] - 120, None),
            )
            .with_start(index * line_duration)
            .with_duration(line_duration)
            .with_position(("center", "bottom"))
        )
        captions.append(caption)

    final = CompositeVideoClip([base_video, *captions]).with_duration(duration)
    video_path = run_dir / "video.mp4"
    final.write_videofile(
        str(video_path),
        fps=config["video"]["fps"],
        codec="libx264",
        audio_codec="aac",
        logger=None,
    )

    thumb_path = _make_thumbnail(topic, run_dir)
    payload = {
        "topic": topic,
        "category": script_record["category"],
        "video_path": str(video_path),
        "thumbnail_path": str(thumb_path),
        "script_path": str(script_path.resolve()),
    }
    metadata_path = run_dir / "metadata.json"
    metadata_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2))
