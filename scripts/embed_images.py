#!/usr/bin/env python3
"""Embed all <img src="..."> in report.html as base64 data URIs."""
import base64, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
html_path = ROOT / "report.html"
html = html_path.read_text(encoding="utf-8")

def to_data_uri(match):
    src = match.group(1)
    img_path = ROOT / src
    if not img_path.exists():
        print(f"  WARN: {img_path} not found, skipping")
        return match.group(0)
    suffix = img_path.suffix.lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp"}.get(suffix.lstrip("."), "image/png")
    data = base64.b64encode(img_path.read_bytes()).decode()
    print(f"  embedded {src} ({len(data)//1024}KB)")
    return f'src="data:{mime};base64,{data}"'

html_out = re.sub(r'src="(test/results/[^"]+)"', to_data_uri, html)
html_path.write_text(html_out, encoding="utf-8")
print(f"\nDone. File size: {html_path.stat().st_size / 1024 / 1024:.1f} MB")
