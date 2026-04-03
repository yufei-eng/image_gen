#!/usr/bin/env python3
"""Evaluate custom skill by applying its prompt rewriting templates."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from generate import generate_image, load_api_key, TEST_SCENARIOS, PROJECT_DIR

# Custom skill rewrites — applying all templates from SKILL.md

CUSTOM_REWRITES = {
    # Avatar / Style Transfer template
    "S1_avatar": (
        "Transform this selfie into a 1990s American high school yearbook portrait. "
        "The subject: head-and-shoulders framing, centered classic yearbook composition, "
        "natural friendly smile. "
        "Background: traditional multi-colored laser-beam gradient backdrop in cyan, blue, "
        "and magenta — the iconic 90s school photo pattern. "
        "Outfit: navy crew-neck sweater layered over a plaid button-up collar shirt, "
        "period-accurate preppy style with visible collar points. "
        "Photography: soft diffused studio flash from two front umbrella lights, warm "
        "tungsten color cast, natural skin tones, slight film grain reminiscent of "
        "Kodak Gold 200 shot on a point-and-shoot camera. The image should feel like "
        "a slightly faded genuine yearbook photo scanned from a printed page. "
        "Preserve: The subject's facial features, bone structure, and identity exactly "
        "as they appear in the input selfie. "
        "Aspect ratio 1:1 square. No modern elements, no text overlays, no watermark."
    ),

    # Local Edit template (Change / Keep / Avoid)
    "S2_edit": (
        "Edit this photograph:\n"
        "- CHANGE: Replace only the upper-body garment with a classic mid-wash indigo "
        "selvedge denim jacket. The jacket has a folded collar, two chest flap pockets "
        "with brass snap buttons, contrast orange stitching along seams, and natural "
        "fabric creasing at the elbows and chest. It is buttoned up to the second-to-top button.\n"
        "- KEEP UNCHANGED: The subject's face, facial expression, hair and hairstyle, "
        "glasses, skin tone, body pose (leaning against wooden railing), hand positions, "
        "lower body (khaki trousers), backpack straps on shoulders, the entire background "
        "scene (alpine lake, mountains, green hillside, wooden dock, gravel path), "
        "original lighting direction (overcast daylight from above-left), original color "
        "grading and white balance, camera angle and focal length.\n"
        "- BLEND: Ensure seamless transition at the neckline where jacket collar meets "
        "skin/hair. Jacket shadows must match the existing soft overcast lighting — no "
        "harsh shadows that weren't in the original. Backpack straps should rest naturally "
        "over the denim jacket shoulders.\n"
        "- AVOID: Adding any new objects, text overlays, changing the background, altering "
        "facial features, shifting the color temperature, or cropping differently.\n"
        "Do not change the input aspect ratio."
    ),

    # Poster / Typography template (text-first approach)
    "S3_poster": (
        "Generate an image: A high-contrast Art Deco-inspired graphic design event poster.\n"
        "Layout: 3:4 portrait orientation. Color palette: deep navy (#1a1a3e) background "
        "with metallic gold (#c5a55a) accents and cream white (#f5f0e1) text.\n"
        "EXACT TEXT TO RENDER:\n"
        '- "UC BERKELEY MUSIC SOCIETY" — top of poster, bold geometric sans-serif, all caps, '
        "cream white, largest header size.\n"
        '- "SPRING AUDITIONS" — center of poster, dramatic oversized display typography, '
        "metallic gold with slight 3D emboss effect, the visual focal point.\n"
        '- "Date: April 15th" — lower third, clean sans-serif, gold on navy, medium size.\n'
        '- "Location: Sproul Hall Room 202" — below date line, same style, medium size.\n'
        '- "Time: 6-9 PM" — below location line, same style, medium size.\n'
        "All text must be spelled exactly as written above. High contrast for legibility, "
        "absolutely no decorative distortion or warping on text characters.\n"
        "Visual elements: Art Deco geometric patterns framing the text. Gold silhouettes "
        "of musical instruments (violin, trumpet, treble clef, music notes) arranged "
        "symmetrically in the mid-section between the headline and event details.\n"
        "Composition: Eye flow top→center headline→instruments→details. Clean margins, "
        "balanced symmetry. Professional print-ready poster quality."
    ),

    # Character Design template
    "S4_character": (
        "Highly detailed digital concept art painting of an original Marvel-inspired "
        "superhero called 'Cyber-Knight'.\n"
        "FIGURE: Tall, imposing muscular build, standing 6'4\". Wearing sleek obsidian-black "
        "powered armor with a matte finish and subtle metallic flake. The armor consists of "
        "interlocking plates with smooth aerodynamic contours.\n"
        "DETAILS: Glowing purple-violet energy veins trace circuit-board-like patterns "
        "across the chest plate, along the forearms and gauntlets, down the thigh guards "
        "and greaves. The veins pulse with a soft inner light that casts a faint purple "
        "ambient glow on nearby surfaces. A triangular energy core on the chest plate "
        "glows brighter than the veins.\n"
        "HELMET: Fully enclosed with a narrow horizontal visor slit that glows the same "
        "purple-violet. Angular, predatory silhouette with swept-back edges.\n"
        "POSE: Heroic wide power stance, legs planted shoulder-width apart, fists slightly "
        "clenched at the sides, weight centered. Chin tilted slightly upward in defiance. "
        "Shot from a low angle looking upward for an imposing, larger-than-life effect.\n"
        "CAPE: A dark metallic-fiber cape, tattered at the lower edge from battle damage, "
        "caught mid-billow to the right by wind. The interior lining has faint purple "
        "energy traces.\n"
        "SETTING: The ruins of a tech-noir New York City at twilight. Shattered skyscrapers "
        "with exposed steel frames, flickering neon signs in the background (OSCORP, SHIELD, "
        "CYBERNETICS), rubble and cracked asphalt underfoot, puddles reflecting the purple "
        "glow. Light rain falling.\n"
        "ATMOSPHERE: Dramatic backlighting from a break in storm clouds, creating a strong "
        "rim light silhouette along the armor edges. Deep indigo and purple color palette "
        "with orange-amber accent from distant fires. Cinematic depth of field with "
        "slightly blurred background.\n"
        "Aspect ratio 3:4 portrait orientation. No text in the image, no watermark."
    ),
}


def custom_rewriter(scenario_id, scenario):
    return CUSTOM_REWRITES[scenario_id]


async def main():
    api_key = load_api_key()
    if not api_key:
        print("ERROR: YUNWU_API_KEY not found.")
        sys.exit(1)

    import json
    from datetime import datetime

    output_dir = str(PROJECT_DIR / "test" / "results" / "custom")
    print(f"\n{'#'*70}")
    print(f"# Evaluating: Custom Skill (image-gen-skill)")
    print(f"# Output: {output_dir}")
    print(f"{'#'*70}")

    results = {}
    for scenario_id, scenario in TEST_SCENARIOS.items():
        rewritten = custom_rewriter(scenario_id, scenario)
        print(f"\n{'='*60}")
        print(f"[Custom Skill] {scenario['name']}")
        print(f"Original:  {scenario['prompt'][:70]}...")
        print(f"Rewritten: {rewritten[:70]}...")

        output_path = f"{output_dir}/{scenario_id}.png"
        result = await generate_image(
            prompt=rewritten,
            output_path=output_path,
            api_key=api_key,
            reference_image=scenario["reference_image"],
        )

        results[scenario_id] = {
            "scenario": scenario["name"],
            "skill": "Custom (image-gen-skill)",
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

    meta_path = f"{output_dir}/generation-meta.json"
    Path(meta_path).parent.mkdir(parents=True, exist_ok=True)
    with open(meta_path, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nMetadata saved to {meta_path}")


if __name__ == "__main__":
    asyncio.run(main())
