import json
import random
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


ROOT_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT_DIR / "config" / "config.json"
TOPICS_PATH = ROOT_DIR / "config" / "topics.json"
OUTPUT_SCRIPTS_DIR = ROOT_DIR / "output" / "scripts"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def select_random_topic(topics_data: dict) -> tuple[str, str]:
    category = random.choice(list(topics_data.keys()))
    topic = random.choice(topics_data[category])
    return category, topic


def build_prompt(category: str, topic: str) -> str:
    return (
        "Write a high-energy, factually accurate 60-second educational script for a short vertical video. "
        f"Category: {category}. Topic: {topic}. "
        "Use simple language, one hook line, 4-6 body lines, and one CTA at the end. "
        "Return plain text only."
    )


def generate_ai_script(config: dict, category: str, topic: str) -> str:
    model = config["generation"]["model"]
    temperature = config["generation"]["temperature"]
    max_tokens = config["generation"]["max_tokens"]
    client = OpenAI()
    completion = client.responses.create(
        model=model,
        temperature=temperature,
        max_output_tokens=max_tokens,
        input=build_prompt(category, topic),
    )
    return completion.output_text.strip()


def fallback_script(category: str, topic: str) -> str:
    return (
        f"Did you know this about {topic}?\n"
        f"Today we explore a quick {category.replace('_', ' ')} concept in under 60 seconds.\n"
        "First, define the core idea in one sentence.\n"
        "Then connect it to a real-world example people recognize.\n"
        "Finally, explain why this matters for science and technology.\n"
        "Follow for your daily science short!"
    )


def save_script_record(category: str, topic: str, script_text: str) -> Path:
    OUTPUT_SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = OUTPUT_SCRIPTS_DIR / f"{timestamp}_{category}.json"
    payload = {
        "created_at_utc": timestamp,
        "category": category,
        "topic": topic,
        "script_text": script_text,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def run() -> Path:
    load_dotenv()
    config = load_json(CONFIG_PATH)
    topics = load_json(TOPICS_PATH)
    category, topic = select_random_topic(topics)
    try:
        script_text = generate_ai_script(config, category, topic)
    except Exception:
        script_text = fallback_script(category, topic)
    return save_script_record(category, topic, script_text)


if __name__ == "__main__":
    output_path = run()
    print(output_path)
