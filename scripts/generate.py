#!/usr/bin/env python3
"""Image generation script using Gemini 3.1 Flash Image (Nano Banana 2) via Yunwu API."""

import asyncio
import base64
import json
import os
import sys
from pathlib import Path
from datetime import datetime

import httpx

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
CONFIG_PATHS = [
    Path.home() / ".claude" / "skills" / "video-gen" / "config.json",
    Path.home() / ".cursor" / "skills" / "video-gen" / "config.json",
    PROJECT_DIR / "config.json",
]

GEMINI_IMAGE_URL = "https://yunwu.ai/v1beta/models/gemini-3.1-flash-image-preview:generateContent"

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


def load_api_key() -> str:
    for path in CONFIG_PATHS:
        if path.exists():
            try:
                with open(path) as f:
                    cfg = json.load(f)
                key = cfg.get("YUNWU_API_KEY", "")
                if key:
                    return key
            except Exception:
                continue
    return os.getenv("YUNWU_API_KEY", "")


async def generate_image(
    prompt: str,
    output_path: str,
    api_key: str,
    reference_image: str = None,
    style_suffix: str = None,
) -> dict:
    """Call Gemini 3.1 Flash Image API. Returns result dict."""
    parts = []

    if reference_image and os.path.exists(reference_image):
        with open(reference_image, "rb") as f:
            img_data = f.read()
        ext = os.path.splitext(reference_image)[1].lower()
        mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
        mime_type = mime_map.get(ext, "image/jpeg")
        parts.append({
            "inlineData": {
                "mimeType": mime_type,
                "data": base64.b64encode(img_data).decode("utf-8"),
            }
        })

    full_prompt = f"{prompt}, {style_suffix}" if style_suffix else prompt
    parts.append({"text": full_prompt})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE", "TEXT"],
            "responseMimeType": "text/plain",
        },
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                GEMINI_IMAGE_URL,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": api_key,
                },
            )
            resp.raise_for_status()
            result = resp.json()

        candidates = result.get("candidates", [])
        if not candidates:
            return {"success": False, "error": "No candidates in response"}

        resp_parts = candidates[0].get("content", {}).get("parts", [])
        image_b64 = None
        text_response = None
        for part in resp_parts:
            if "inlineData" in part:
                image_b64 = part["inlineData"].get("data")
            if "text" in part:
                text_response = part["text"]

        if not image_b64:
            return {"success": False, "error": "No image data in response", "text": text_response}

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(base64.b64decode(image_b64))

        return {"success": True, "output": output_path, "text": text_response}

    except Exception as e:
        return {"success": False, "error": str(e)}


async def run_baseline(output_dir: str = None):
    """Run all 4 test scenarios with raw prompts (no optimization)."""
    api_key = load_api_key()
    if not api_key:
        print("ERROR: YUNWU_API_KEY not found. Set it in config.json or environment.")
        sys.exit(1)

    if output_dir is None:
        output_dir = str(PROJECT_DIR / "test" / "results" / "baseline")

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
            api_key=api_key,
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
    api_key = load_api_key()
    if not api_key:
        print("ERROR: YUNWU_API_KEY not found.")
        sys.exit(1)

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
            api_key=api_key,
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
