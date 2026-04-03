#!/usr/bin/env python3
"""Evaluate 2 new skills: awesome-nano-banana prompt patterns + Hunyuan PromptEnhancer CoT."""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from generate import generate_image, load_api_key, TEST_SCENARIOS, PROJECT_DIR

# ────────────────────────────────────────────────────────
# Skill 4: awesome-nano-banana-pro-prompts style (10.5k stars)
#   Method: Extremely detailed narrative prompts drawn from community
#   patterns across 12,000+ curated examples. Very specific about
#   camera settings, materials, exact spatial layout, artistic references.
#   Tends to be longer and more "production-ready" than typical skill prompts.
# ────────────────────────────────────────────────────────

SKILL4_REWRITES = {
    "S1_avatar": (
        "A nostalgic 1990s American high school yearbook portrait photo of the person "
        "in this selfie. Head-and-shoulders crop, centered in frame, natural genuine smile "
        "with teeth showing. The subject wears a navy blue crew-neck sweater with a plaid "
        "flannel shirt collar peeking out underneath — a quintessential 90s preppy look. "
        "Behind them is the iconic yearbook laser beam backdrop: vivid neon beams of cyan, "
        "electric blue, and hot magenta radiating outward from behind the subject's head "
        "against a deep cobalt blue gradient. The lighting is classic school photo studio: "
        "dual umbrella flash from 45 degrees left and right, creating soft even illumination "
        "with gentle catch-lights in the eyes. Shot on Kodak Gold 200 film with a slight warm "
        "color shift, visible but subtle film grain, and the characteristic slightly desaturated "
        "reds of 90s school photography. The print has soft vignetting at corners as if scanned "
        "from a yearbook page. Square 1:1 format. The subject's facial features, bone structure, "
        "eye shape, and overall identity must be preserved exactly from the input selfie. "
        "No text, no name caption, no modern digital effects."
    ),
    "S2_edit": (
        "Edit this photograph with surgical precision:\n"
        "TARGET CHANGE: Replace only the upper-body garment (everything above the waist, "
        "below the neck) with a classic Type III indigo-dyed selvedge denim trucker jacket. "
        "The jacket specifics: medium-wash indigo with natural fading at stress points "
        "(elbows, chest pocket edges), two symmetrical chest flap pockets with antique brass "
        "snap buttons, exposed contrast-orange chain stitching along the yoke seams, a "
        "structured fold-down collar, and the jacket is buttoned up to the second-from-top "
        "button with the collar lying flat. The denim texture shows a visible twill weave "
        "with subtle slub-yarn irregularities.\n"
        "ABSOLUTE PRESERVATION: The subject's face, eyes, eyebrows, mouth, nose, facial "
        "expression (looking left), hair, glasses (thin-frame rectangular), skin tone and "
        "texture, both hands and their positions, the lower body (khaki chinos), the backpack "
        "with its visible shoulder straps, the wooden railing they're leaning against, the "
        "gravel path, green grass, the entire alpine lake, mountain range, snow-capped peaks, "
        "forested hillsides, overcast sky, and wooden dock in the background. Camera angle, "
        "focal length, depth of field, and color grading must remain identical.\n"
        "TRANSITION BLENDING: The collar area where the jacket meets the neck must show "
        "natural fabric-to-skin transition. Backpack straps must sit naturally on top of "
        "the denim shoulders. Shadows on the jacket must follow the existing overcast "
        "ambient lighting direction (diffuse from above). No hard shadow edges that weren't "
        "in the original image.\n"
        "Do not add any objects, text, or change the aspect ratio."
    ),
    "S3_poster": (
        'A print-ready, high-contrast Art Deco graphic design event poster at 3:4 portrait '
        'aspect ratio.\n'
        'COLOR PALETTE: Deep navy blue (#0d1b2a) background, metallic burnished gold (#b8860b) '
        'for accents and decorative elements, antique white (#faebd7) for primary text.\n'
        'TEXT CONTENT (must be rendered exactly as written, letter-perfect):\n'
        '  Line 1: "UC BERKELEY MUSIC SOCIETY" — positioned at the very top, antique white, '
        'bold geometric sans-serif (like Futura Bold), all-caps, tracking +50, largest header.\n'
        '  Line 2: "SPRING AUDITIONS" — dead center of the poster, metallic gold with a subtle '
        '3D embossed effect and drop shadow, dramatic display serif typography at 3x the size '
        'of Line 1, the dominant visual element.\n'
        '  Line 3: "Date: April 15th" — lower third, gold text on navy, clean sans-serif, '
        'medium size, centered.\n'
        '  Line 4: "Location: Sproul Hall Room 202" — directly below Line 3, same style.\n'
        '  Line 5: "Time: 6-9 PM" — directly below Line 4, same style.\n'
        'DECORATIVE ELEMENTS: Art Deco geometric border with stepped corners and fan motifs '
        'framing the entire poster. Between Lines 2 and 3, a symmetrical arrangement of gold '
        'silhouette musical instruments: a violin (left), treble clef (center), and trumpet '
        '(right), accented with scattered music notes and staff lines.\n'
        'COMPOSITION: Strict vertical symmetry. Clear visual hierarchy: title → headline → '
        'instruments → details. Generous margins. No photograph, pure graphic design.\n'
        'QUALITY: Print-resolution, no compression artifacts, no misspellings, no text warping.'
    ),
    "S4_character": (
        "A cinematic digital concept art painting, rendered in the visual language of Marvel "
        "Studios keyframe art and the detailed character design style of artists like Ryan "
        "Meinerding and Andy Park.\n"
        "CHARACTER — 'CYBER-KNIGHT': A tall, imposing figure (approximately 6'4\") with a "
        "heroic V-shaped torso silhouette. Every surface is covered in custom-fitted obsidian-"
        "black powered armor with a matte gunmetal finish and subtle metallic flake that catches "
        "light at extreme angles. The armor consists of overlapping segmented plates with "
        "smooth aerodynamic contours — chest piece, pauldrons, vambraces, cuisses, greaves — "
        "all connected by flexible black under-armor mesh visible at joints.\n"
        "SIGNATURE ELEMENT: Bioluminescent purple-violet energy veins trace circuit-board-like "
        "pathways across every major armor section. The veins are brightest at a triangular arc "
        "reactor-style core embedded in the center chest plate, dimming to a soft ambient glow "
        "at the extremities. The energy casts a faint purple reflection on nearby metal surfaces "
        "and wet ground.\n"
        "HELMET: Fully enclosed, angular and predatory, with swept-back aerodynamic fins. A "
        "narrow horizontal visor slit glows the same purple-violet. No visible mouth or eyes.\n"
        "CAPE: A floor-length cape made of a dark metallic smart-fabric, tattered and battle-"
        "damaged at the lower edge, caught mid-billow to the right by wind. The interior lining "
        "shows faint purple energy capillaries.\n"
        "POSE: Heroic wide power-stance, feet planted shoulder-width on rubble, weight centered, "
        "fists clenched at sides, chin tilted upward. Shoulders back, chest presented.\n"
        "CAMERA: Low angle (approximately 15° below eye level) looking upward to create an "
        "imposing, monumental feel. Focal length equivalent to 24mm wide-angle with slight "
        "barrel distortion for dramatic perspective.\n"
        "ENVIRONMENT: The ruined streets of a tech-noir New York City at blue-hour twilight. "
        "Shattered skyscrapers with exposed steel ribbing in the mid-ground. Flickering neon "
        "signs (OSCORP, STARK, CYBERNETICS) in the deep background. Cracked asphalt and "
        "concrete rubble underfoot. Rain-slicked surfaces reflecting the purple glow. Light "
        "rain with visible droplets in the foreground.\n"
        "LIGHTING: Dramatic cold-blue ambient fill from the twilight sky. Strong warm orange-"
        "amber accent light from distant fires camera-left. The energy veins provide purple "
        "radiosity bouncing off nearby surfaces. Strong backlight rim from a gap in storm "
        "clouds creating a divine halo effect around the character's silhouette.\n"
        "Aspect ratio 3:4 portrait. No text, no watermarks, no UI elements. The image is "
        "presented in a highly detailed digital concept art style with cinematic color grading."
    ),
}


def skill4_rewriter(scenario_id, scenario):
    return SKILL4_REWRITES[scenario_id]


# ────────────────────────────────────────────────────────
# Skill 5: Hunyuan PromptEnhancer Chain-of-Thought style (3.7k stars)
#   Method: Applies the CoT "总-分-总" (General-Detail-General) structure
#   from Hunyuan's system prompt:
#   1. Intent preservation (subject/action/style/layout/attributes/text)
#   2. 总-分-总 macro structure (overview → details → summary)
#   3. Objective and neutral tone
#   4. Primary-to-secondary element ordering
#   5. Strict spatial/importance logic
#   6. End with one-sentence style summary
# ────────────────────────────────────────────────────────

SKILL5_REWRITES = {
    "S1_avatar": (
        # 总: Overview
        "A classic 1990s American high school yearbook portrait photo, transforming the "
        "uploaded selfie while preserving the subject's identity. "
        # 分: Details (primary to secondary)
        "The subject is centered in a head-and-shoulders composition with a warm, natural "
        "smile. They wear a navy crew-neck sweater over a plaid button-up collar shirt. "
        "The background is the iconic 90s yearbook laser-beam gradient pattern — vivid cyan "
        "and magenta light rays radiating outward against a deep blue field. "
        "The lighting is soft dual-umbrella studio flash, producing even illumination with "
        "gentle catch-lights. A warm tungsten color cast permeates the image with visible "
        "Kodak Gold 200 film grain. "
        # 总: Style summary
        "The overall style is authentic 1990s school photography with a nostalgic, wholesome "
        "warmth. Square 1:1 aspect ratio."
    ),
    "S2_edit": (
        # 总: Overview
        "A local image edit that replaces only the upper-body clothing while keeping the "
        "entire rest of the photograph pixel-identical. "
        # 分: Details (primary to secondary)
        "The new garment is a classic mid-wash indigo denim trucker jacket with a fold-down "
        "collar, two chest flap pockets with brass snap buttons, and visible contrast orange "
        "stitching. The jacket is buttoned to the second-from-top button. "
        "All other elements remain unchanged: the subject's face, expression, hair, glasses, "
        "pose, hand positions, khaki trousers, backpack straps, and the complete background "
        "including the alpine lake, mountains, green hillside, wooden railing, gravel path, "
        "and overcast sky. "
        "The jacket's shadows follow the existing diffuse overcast lighting from above. The "
        "collar transitions seamlessly to the neck. Backpack straps rest naturally on top of "
        "the denim shoulders. "
        # 总: Style summary
        "The overall result is a seamless, photorealistic local garment replacement that is "
        "indistinguishable from an original photograph. Do not change the aspect ratio."
    ),
    "S3_poster": (
        # 总: Overview
        "A high-contrast Art Deco graphic design event poster for a university music "
        "audition event. "
        # 分: Details (primary to secondary)
        'The dominant headline "SPRING AUDITIONS" is rendered in large metallic gold display '
        'typography with a 3D embossed effect at the center of the poster. Above it, '
        '"UC BERKELEY MUSIC SOCIETY" appears in bold geometric sans-serif, antique white, '
        'all caps. Below the headline, gold silhouette musical instruments — a violin, '
        'treble clef, and trumpet — are arranged symmetrically with scattered music notes. '
        'In the lower third, event details are displayed in clean sans-serif gold text: '
        '"Date: April 15th", "Location: Sproul Hall Room 202", "Time: 6-9 PM" — each on '
        "its own line, centered and clearly legible. "
        "The color palette is deep navy background with burnished gold accents and cream "
        "white text. Art Deco geometric borders with stepped corners frame the poster. "
        "Strict vertical symmetry with clear top-to-bottom visual hierarchy. "
        # 总: Style summary
        "The overall style is a professional, print-ready Art Deco graphic design poster "
        "with elegant typography and clean layout. Aspect ratio 3:4 portrait."
    ),
    "S4_character": (
        # 总: Overview
        "Full-body concept art of an original Marvel-inspired superhero called 'Cyber-Knight', "
        "standing heroically in a ruined cyberpunk cityscape. "
        # 分: Details (primary to secondary)
        "The character wears sleek obsidian-black powered armor with a matte finish and "
        "interlocking segmented plates covering the chest, shoulders, arms, and legs. Glowing "
        "purple-violet energy veins trace circuit-like patterns across all major armor sections, "
        "emanating from a bright triangular core on the chest plate. The fully enclosed helmet "
        "has a narrow glowing purple visor slit with angular, predatory swept-back edges. "
        "A dark metallic-fiber cape, tattered at the hem, billows to the right in the wind. "
        "The character stands in a wide heroic power-stance with fists clenched, shot from a "
        "low angle looking upward for an imposing effect. "
        "The setting is the ruins of tech-noir New York City at twilight — shattered skyscrapers, "
        "flickering neon signs (OSCORP, CYBERNETICS), cracked asphalt with puddles reflecting "
        "purple glow, and light rain falling. Dramatic backlighting from storm clouds creates "
        "a rim light silhouette, with orange fire-glow from the left and purple energy radiosity "
        "from the armor. "
        # 总: Style summary
        "The overall style is highly detailed cinematic digital concept art with a deep indigo "
        "and purple color palette. Aspect ratio 3:4 portrait. No text, no watermark."
    ),
}


def skill5_rewriter(scenario_id, scenario):
    return SKILL5_REWRITES[scenario_id]


SKILLS = [
    ("opensource-4", "YouMind/awesome-nano-banana-prompts", skill4_rewriter),
    ("opensource-5", "Hunyuan-PromptEnhancer/CoT", skill5_rewriter),
]


async def main():
    api_key = load_api_key()
    if not api_key:
        print("ERROR: YUNWU_API_KEY not found.")
        sys.exit(1)

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
