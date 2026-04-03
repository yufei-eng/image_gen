#!/usr/bin/env python3
"""Evaluate 3 open-source skills by applying their prompt rewriting methodology."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from generate import generate_image, load_api_key, TEST_SCENARIOS, PROJECT_DIR

# ────────────────────────────────────────────────────────
# Skill 1: harshkedia177/image-gen-plugin (nano-banana-prompting)
#   Method: Priority-ordered narrative prompts (Subject → Action → Setting
#   → Style → Camera → Constraints). JSON structured for complex scenes.
#   Text-first hack for text-heavy images. "Edit, don't re-roll" for edits.
# ────────────────────────────────────────────────────────

SKILL1_REWRITES = {
    "S1_avatar": (
        "Transform this selfie photograph into a nostalgic 1990s American high school "
        "yearbook portrait. The subject should be posed in a classic yearbook head-and-shoulders "
        "composition against a traditional laser-beam gradient backdrop in blue and purple tones. "
        "Warm soft studio flash lighting typical of 90s school photography. The subject wears a "
        "casual 90s outfit like a crew-neck sweater. Aspect ratio 1:1, photorealistic style with "
        "slight film grain reminiscent of Kodak Gold 200. No modern elements, no text overlays."
    ),
    "S2_edit": (
        "Edit this photograph: replace only the upper-body clothing with a classic indigo denim "
        "jacket with visible stitching and brass button details. Keep the subject's face, hair, "
        "expression, pose, lower body, and entire background completely unchanged. The denim "
        "jacket should fit naturally with realistic fabric folds and shadows that match the "
        "existing lighting direction. Ensure seamless blending at the collar and waistline "
        "transition areas. Do not change the input aspect ratio."
    ),
    "S3_poster": (
        'Generate an image: A high-contrast graphic design event poster. Bold geometric '
        'layout with a dark navy and gold color palette. Musical instruments (violin, trumpet, '
        'music notes) as decorative elements in the mid-section. '
        'Text to render precisely: "UC BERKELEY MUSIC SOCIETY" in bold sans-serif at the top, '
        '"SPRING AUDITIONS" in large display typography as the focal headline, '
        '"Date: April 15th" on its own line, '
        '"Location: Sproul Hall Room 202" on its own line, '
        '"Time: 6-9 PM" on its own line. '
        'All text must be spelled exactly as specified. Clean alignment, high legibility, '
        'no decorative distortion on text. Aspect ratio 3:4, print-ready poster design.'
    ),
    "S4_character": (
        "Full body concept art illustration of an original Marvel-inspired superhero called "
        "'Cyber-Knight'. Subject: A tall, imposing figure in sleek obsidian-black powered armor "
        "with intricate glowing purple-violet energy veins running across the chest plate, "
        "gauntlets, and greaves. The helmet features a narrow glowing visor. "
        "Pose: Standing in a confident heroic wide stance, fists slightly clenched, "
        "cape flowing to the right. "
        "Setting: Ruined tech-noir New York City at dusk — crumbling skyscrapers with flickering "
        "neon signs, debris on the ground, overcast sky with purple-tinged clouds. "
        "Style: Digital concept art, highly detailed, cinematic lighting with strong rim light "
        "from behind creating a silhouette edge glow. Dramatic low-angle shot. "
        "Aspect ratio 3:4. No text, no watermark."
    ),
}


def skill1_rewriter(scenario_id, scenario):
    return SKILL1_REWRITES[scenario_id]


# ────────────────────────────────────────────────────────
# Skill 2: openclaw/ivangdavila/image-generation
#   Method: Objective-First template (Goal → Subject+constraints → Style
#   → Exact text → Keep unchanged). Editing pattern: Change → Keep → Avoid.
#   Gemini-specific: split changes step-by-step, re-anchor invariants.
# ────────────────────────────────────────────────────────

SKILL2_REWRITES = {
    "S1_avatar": (
        "Goal: Transform a personal selfie into a retro school portrait.\n"
        "Subject: The person from the uploaded photo, head-and-shoulders framing, "
        "classic yearbook composition.\n"
        "Style: 1990s American high school yearbook photography, warm tungsten studio "
        "lighting, soft focus, traditional laser-pattern backdrop.\n"
        "Keep unchanged: The subject's facial features and identity must be preserved exactly.\n"
        "Avoid: Modern styling, harsh shadows, digital artifacts."
    ),
    "S2_edit": (
        "Edit request:\n"
        "- Change: Replace the upper-body garment with a medium-wash denim jacket, "
        "naturally fitted with visible button details and collar.\n"
        "- Keep: Person identity, face, expression, hair, lower body clothing, "
        "background scene, camera angle, lighting direction.\n"
        "- Avoid: Extra objects, text overlays, heavy color shift, changing aspect ratio."
    ),
    "S3_poster": (
        "Goal: Create an event announcement poster for a university music club.\n"
        "Subject: High-contrast graphic design poster with musical motifs "
        "(instruments, music notes, sound waves).\n"
        "Style: Bold modern graphic design, dark background with metallic gold accents, "
        "clean professional layout.\n"
        'Exact text: "UC BERKELEY MUSIC SOCIETY" as header, '
        '"SPRING AUDITIONS" as main headline, '
        '"Date: April 15th" as info line, '
        '"Location: Sproul Hall Room 202" as info line, '
        '"Time: 6-9 PM" as info line.\n'
        "Typography: Bold geometric sans-serif, all caps for header and headline, "
        "high contrast for legibility.\n"
        "Avoid: Decorative text distortion, misspellings, cluttered layout."
    ),
    "S4_character": (
        "Goal: Create original superhero concept art for a character portfolio.\n"
        "Subject: Full body view of 'Cyber-Knight' — a futuristic armored superhero, "
        "tall imposing build. Sleek obsidian-black armor with glowing purple energy veins "
        "tracing circuit-like patterns across chest, limbs, and helmet visor.\n"
        "Style: Marvel-inspired digital concept art, cinematic dramatic lighting, "
        "highly detailed rendering.\n"
        "Composition: Full body standing pose, heroic wide stance, low camera angle, "
        "slight upward perspective for imposing effect.\n"
        "Setting: Ruined tech-noir New York City — collapsed buildings, neon signage, "
        "rain-slicked debris, dark moody sky with purple atmospheric glow.\n"
        "Avoid: Text in image, watermarks, cartoonish proportions."
    ),
}


def skill2_rewriter(scenario_id, scenario):
    return SKILL2_REWRITES[scenario_id]


# ────────────────────────────────────────────────────────
# Skill 3: kousen/nano-banana-prompting (gist)
#   Method: Natural language narrative, as if briefing a human artist.
#   Camera language, lighting specifics, material/texture, color direction.
#   Text in quotation marks. Include purpose context.
#   Structure: Style/medium → specific subject → setting → action
#   → lighting → mood → camera → additional details → purpose.
# ────────────────────────────────────────────────────────

SKILL3_REWRITES = {
    "S1_avatar": (
        "A photorealistic 1990s high school yearbook portrait of the person in this selfie, "
        "captured in a classic head-and-shoulders composition with a retro laser-beam backdrop "
        "in vibrant blue and magenta. The subject wears a simple crew-neck sweater, hair neatly "
        "styled in a period-appropriate way. Shot with soft diffused studio flash lighting "
        "typical of 90s school photography studios, with slight warm color cast and natural "
        "film grain reminiscent of Kodak Gold. The mood is wholesome and nostalgic. "
        "Square 1:1 aspect ratio, styled for a social media profile picture."
    ),
    "S2_edit": (
        "Keep everything in this photograph exactly the same — the person's face, hair, "
        "expression, pose, the entire background and lower body — but replace only the "
        "upper-body clothing with a classic mid-wash denim jacket. The jacket should have "
        "visible brass buttons, contrast stitching, and a folded collar, fitted naturally "
        "to the subject's body with realistic fabric creases. The lighting on the new jacket "
        "should match the existing directional light in the scene, with consistent shadow "
        "placement. Seamless transition at the neckline and waist."
    ),
    "S3_poster": (
        'A bold, high-contrast graphic design poster for a university music event, styled for '
        'print at 3:4 aspect ratio. Dark navy background with gold and white metallic accents. '
        'Musical motifs — stylized violin, trumpet, and scattered music notes — as mid-section '
        'decorative elements. The text "UC BERKELEY MUSIC SOCIETY" appears in bold sans-serif '
        'at the top, "SPRING AUDITIONS" in large dramatic display typography as the central '
        'headline, with event details below: "Date: April 15th", "Location: Sproul Hall Room 202", '
        'and "Time: 6-9 PM" in clean, clearly legible type. Professional poster design with '
        'strong visual hierarchy and clean alignment. Created for a university student organization.'
    ),
    "S4_character": (
        "A cinematic digital concept art painting of an original Marvel-inspired superhero "
        "called 'Cyber-Knight', shown in a dramatic full-body standing pose with legs planted "
        "wide in a heroic stance. The character wears sleek obsidian-black powered armor with "
        "intricate glowing purple energy veins running like circuit traces across the chest plate, "
        "gauntlets, and leg guards. The helmet has a narrow glowing violet visor slit. "
        "A dark metallic cape billows behind. "
        "The scene is set in the ruins of a tech-noir New York City at twilight — shattered "
        "skyscrapers with flickering neon advertisements, rubble-strewn streets reflecting "
        "purple-tinged ambient light, rain mist in the air. "
        "Shot from a low angle looking upward for an imposing heroic effect, with dramatic "
        "backlighting creating a strong rim light silhouette. Rich purple and deep indigo "
        "color palette. Highly detailed, 3:4 portrait aspect ratio."
    ),
}


def skill3_rewriter(scenario_id, scenario):
    return SKILL3_REWRITES[scenario_id]


# ────────────────────────────────────────────────────────

SKILLS = [
    ("opensource-1", "harshkedia177/nano-banana-prompting", skill1_rewriter),
    ("opensource-2", "ivangdavila/image-generation", skill2_rewriter),
    ("opensource-3", "kousen/nano-banana-prompting", skill3_rewriter),
]


async def main():
    api_key = load_api_key()
    if not api_key:
        print("ERROR: YUNWU_API_KEY not found.")
        sys.exit(1)

    import json
    from datetime import datetime

    for dir_name, skill_name, rewriter in SKILLS:
        output_dir = str(PROJECT_DIR / "test" / "results" / dir_name)
        print(f"\n{'#'*70}")
        print(f"# Evaluating: {skill_name}")
        print(f"# Output: {output_dir}")
        print(f"{'#'*70}")

        results = {}
        for scenario_id, scenario in TEST_SCENARIOS.items():
            rewritten = rewriter(scenario_id, scenario)
            print(f"\n{'='*60}")
            print(f"[{skill_name}] {scenario['name']}")
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
                "skill": skill_name,
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
