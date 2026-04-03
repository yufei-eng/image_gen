#!/usr/bin/env python3
"""Image generation via Gemini 3.1 Flash Image through Compass LLM Proxy."""

import json
import os
import sys
import time
import uuid

from google import genai
from google.genai import types

COMPASS_BASE_URL = "http://beeai.test.shopee.io/inbeeai/compass-api/v1"
IMAGE_MODEL = "gemini-3.1-flash-image-preview"

CONFIG_PATHS = [
    os.path.expanduser("~/.claude/skills/image-gen/config.json"),
    os.path.expanduser("~/.cursor/skills/image-gen/config.json"),
]


def _load_client_token() -> str:
    """Resolve client token: env var > config.json files."""
    token = os.environ.get("COMPASS_CLIENT_TOKEN", "")
    if token:
        return token
    for path in CONFIG_PATHS:
        if os.path.exists(path):
            try:
                with open(path) as f:
                    cfg = json.load(f)
                token = cfg.get("compass_api", {}).get("client_token", "")
                if token:
                    return token
            except Exception:
                continue
    return ""


_token = _load_client_token()
if not _token:
    print(
        "ERROR: Compass API client_token not found.\n"
        "Set env var COMPASS_CLIENT_TOKEN, or create ~/.claude/skills/image-gen/config.json:\n"
        '  {"compass_api": {"client_token": "YOUR_TOKEN"}}'
    )
    sys.exit(1)

client = genai.Client(
    api_key=_token,
    http_options=types.HttpOptions(base_url=COMPASS_BASE_URL),
)


def main():
    if len(sys.argv) < 2:
        print("Usage: main.py <prompt> [image_path]")
        sys.exit(1)

    prompt = sys.argv[1]
    image_path = sys.argv[2] if len(sys.argv) > 2 else None

    parts: list[types.Part] = []

    if image_path and os.path.exists(image_path):
        with open(image_path, "rb") as f:
            img_data = f.read()
        ext = os.path.splitext(image_path)[1].lower()
        mime_map = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
        }
        mime_type = mime_map.get(ext, "image/jpeg")
        parts.append(types.Part.from_bytes(data=img_data, mime_type=mime_type))
        print(f"Reference image loaded: {image_path}")

    parts.append(types.Part.from_text(text=prompt))

    print(f"Calling {IMAGE_MODEL} via Compass LLM Proxy...")

    try:
        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=[types.Content(role="user", parts=parts)],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )
    except Exception as e:
        print(f"API call failed: {e}")
        sys.exit(1)

    if not response.candidates:
        print("No candidates returned from API")
        sys.exit(1)

    text_content = ""
    saved_images = []

    for part in response.candidates[0].content.parts:
        if part.text:
            text_content += part.text
        if part.inline_data and part.inline_data.data:
            mime = part.inline_data.mime_type or "image/png"
            ext_map = {"image/png": ".png", "image/webp": ".webp", "image/gif": ".gif"}
            ext = ext_map.get(mime, ".jpg")
            filename = f"generated_{int(time.time())}_{uuid.uuid4().hex[:6]}{ext}"
            with open(filename, "wb") as f:
                f.write(part.inline_data.data)
            size_kb = len(part.inline_data.data) / 1024
            saved_images.append(filename)
            print(f"Image saved: {os.path.abspath(filename)} ({size_kb:.1f} KB)")

    if text_content:
        print(f"Model notes: {text_content}")

    if not saved_images:
        print("No image generated.")
        sys.exit(1)

    print(f"Done. Generated {len(saved_images)} image(s).")


if __name__ == "__main__":
    main()
