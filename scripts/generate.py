#!/usr/bin/env python3
"""Image generation script using Gemini 3.1 Flash Image via Compass LLM Proxy."""

import asyncio
import base64
import json
import os
import sys
from pathlib import Path
from datetime import datetime

from google import genai
from google.genai import types

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
CONFIG_PATHS = [
    PROJECT_DIR / "config.json",
    Path.home() / ".cursor" / "skills" / "image-gen" / "config.json",
    Path.home() / ".claude" / "skills" / "image-gen" / "config.json",
]

DEFAULT_IMAGE_MODEL = "gemini-3.1-flash-image-preview"

TEST_SCENARIOS = {
    "S1_avatar": {
        "name": "S1 Social - AI Avatar",
        "prompt": "Turn my selfie into a 90s high school yearbook photo",
        "reference_image": str(PROJECT_DIR / "test" / "samples" / "selfie.jpg"),
        "aspect_ratio": "1:1",
    },
    "S2_edit": {
        "name": "S2 Personal - Image Editing",
        "prompt": "I like this photo, but I would replace the upper-body with a denim jacket.",
        "reference_image": str(PROJECT_DIR / "test" / "samples" / "outfit.jpg"),
        "aspect_ratio": "1:1",
    },
    "S3_poster": {
        "name": "S3 Learning - Poster Design",
        "prompt": (
            "Create a high-contrast graphic design poster for 'UC Berkeley Music Society Spring Auditions'. "
            "Text to include: 'Date: April 15th', 'Location: Sproul Hall Room 202', 'Time: 6-9 PM'."
        ),
        "reference_image": None,
        "aspect_ratio": "3:4",
    },
    "S4_character": {
        "name": "S4 Character - Concept Art",
        "prompt": (
            "Full body concept art of a new Marvel-style superhero. A futuristic 'Cyber-Knight' "
            "wearing sleek obsidian armor with glowing purple energy veins. The character is "
            "standing in a heroic pose amidst the ruins of a tech-noir New York City."
        ),
        "reference_image": None,
        "aspect_ratio": "3:4",
    },
}


DEFAULT_BASE_URL = "http://beeai.test.shopee.io/inbeeai/compass-api/v1"


def load_config() -> dict:
    """Load compass_api config from config.json files, with env var overrides."""
    cfg: dict = {}
    for path in CONFIG_PATHS:
        if path.exists():
            try:
                with open(path) as f:
                    file_cfg = json.load(f)
                if "compass_api" in file_cfg:
                    cfg = file_cfg["compass_api"]
                    break
            except Exception:
                continue

    if os.environ.get("COMPASS_CLIENT_TOKEN"):
        cfg["client_token"] = os.environ["COMPASS_CLIENT_TOKEN"]
    if os.environ.get("COMPASS_BASE_URL"):
        cfg["base_url"] = os.environ["COMPASS_BASE_URL"]

    cfg.setdefault("base_url", DEFAULT_BASE_URL)
    cfg.setdefault("image_model", DEFAULT_IMAGE_MODEL)
    return cfg


def _build_client(compass_cfg: dict) -> genai.Client:
    """Build a Google GenAI client pointing at the Compass LLM Proxy."""
    return genai.Client(
        api_key=compass_cfg["client_token"],
        http_options=types.HttpOptions(
            base_url=compass_cfg["base_url"],
        ),
    )


_GENAI_CLIENT: genai.Client | None = None


def get_client() -> genai.Client:
    global _GENAI_CLIENT
    if _GENAI_CLIENT is None:
        cfg = load_config()
        if not cfg.get("client_token"):
            print(
                "ERROR: Compass API client_token not found.\n"
                "Options:\n"
                "  1. Set env var: export COMPASS_CLIENT_TOKEN='your_token'\n"
                "  2. Copy config.json.example to config.json and fill in client_token"
            )
            sys.exit(1)
        _GENAI_CLIENT = _build_client(cfg)
    return _GENAI_CLIENT


def get_model_name() -> str:
    cfg = load_config()
    return cfg.get("image_model", DEFAULT_IMAGE_MODEL)


async def generate_image(
    prompt: str,
    output_path: str,
    api_key: str = None,
    reference_image: str = None,
    style_suffix: str = None,
) -> dict:
    """Call Gemini 3.1 Flash Image via Compass LLM Proxy. Returns result dict."""
    client = get_client()
    model = get_model_name()

    parts: list[types.Part] = []

    if reference_image and os.path.exists(reference_image):
        with open(reference_image, "rb") as f:
            img_data = f.read()
        ext = os.path.splitext(reference_image)[1].lower()
        mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
        mime_type = mime_map.get(ext, "image/jpeg")
        parts.append(types.Part.from_bytes(data=img_data, mime_type=mime_type))

    full_prompt = f"{prompt}, {style_suffix}" if style_suffix else prompt
    parts.append(types.Part.from_text(text=full_prompt))

    try:
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=model,
            contents=[types.Content(role="user", parts=parts)],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )

        if not response.candidates:
            return {"success": False, "error": "No candidates in response"}

        image_data = None
        text_response = None
        for part in response.candidates[0].content.parts:
            if part.text:
                text_response = part.text
            if part.inline_data and part.inline_data.data:
                image_data = part.inline_data.data

        if not image_data:
            return {"success": False, "error": "No image data in response", "text": text_response}

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(image_data)

        return {"success": True, "output": output_path, "text": text_response}

    except Exception as e:
        return {"success": False, "error": str(e)}


async def run_baseline(output_dir: str = None):
    """Run all 4 test scenarios with raw prompts (no optimization)."""
    get_client()

    if output_dir is None:
        output_dir = str(PROJECT_DIR / "test" / "results" / "baseline")

    print(f"Model: {get_model_name()}")
    print(f"Compass base_url: {load_config().get('base_url', 'N/A')}")

    results = {}
    for scenario_id, scenario in TEST_SCENARIOS.items():
        print(f"\n{'='*60}")
        print(f"Generating: {scenario['name']}")
        print(f"Prompt: {scenario['prompt'][:80]}...")
        print(f"Reference: {scenario['reference_image'] or 'None'}")

        output_path = os.path.join(output_dir, f"{scenario_id}.png")
        result = await generate_image(
            prompt=scenario["prompt"],
            output_path=output_path,
            reference_image=scenario["reference_image"],
        )

        results[scenario_id] = {
            "scenario": scenario["name"],
            "prompt_used": scenario["prompt"],
            "reference_image": scenario["reference_image"],
            "output": output_path if result["success"] else None,
            "success": result["success"],
            "error": result.get("error"),
            "text_response": result.get("text"),
            "timestamp": datetime.now().isoformat(),
        }

        status = "OK" if result["success"] else f"FAILED: {result.get('error')}"
        print(f"Result: {status}")

    meta_path = os.path.join(output_dir, "generation-meta.json")
    with open(meta_path, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nMetadata saved to {meta_path}")
    return results


async def run_with_skill(prompt_rewriter, output_dir: str, label: str = "skill"):
    """Run scenarios with a prompt rewriter function.
    
    prompt_rewriter: callable(scenario_id, scenario_dict) -> rewritten_prompt_str
    """
    get_client()

    results = {}
    for scenario_id, scenario in TEST_SCENARIOS.items():
        rewritten = prompt_rewriter(scenario_id, scenario)
        print(f"\n{'='*60}")
        print(f"[{label}] {scenario['name']}")
        print(f"Original : {scenario['prompt'][:60]}...")
        print(f"Rewritten: {rewritten[:60]}...")

        output_path = os.path.join(output_dir, f"{scenario_id}.png")
        result = await generate_image(
            prompt=rewritten,
            output_path=output_path,
            reference_image=scenario["reference_image"],
        )

        results[scenario_id] = {
            "scenario": scenario["name"],
            "original_prompt": scenario["prompt"],
            "rewritten_prompt": rewritten,
            "reference_image": scenario["reference_image"],
            "output": output_path if result["success"] else None,
            "success": result["success"],
            "error": result.get("error"),
            "text_response": result.get("text"),
            "timestamp": datetime.now().isoformat(),
        }

        status = "OK" if result["success"] else f"FAILED: {result.get('error')}"
        print(f"Result: {status}")

    meta_path = os.path.join(output_dir, "generation-meta.json")
    with open(meta_path, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nMetadata saved to {meta_path}")
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Image Gen Skill - Test Runner")
    parser.add_argument("--mode", choices=["baseline"], default="baseline",
                        help="Test mode (baseline = raw prompts)")
    parser.add_argument("--output-dir", help="Override output directory")
    parser.add_argument("--scenario", help="Run single scenario (S1_avatar, S2_edit, S3_poster, S4_character)")
    args = parser.parse_args()

    if args.mode == "baseline":
        asyncio.run(run_baseline(args.output_dir))
