#!/usr/bin/env python3
"""Round 2 evaluation: 3 new ClawHub-derived skills on 4 scenarios."""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from generate import generate_image, load_api_key, TEST_SCENARIOS, PROJECT_DIR

# ────────────────────────────────────────────────────────
# Skill A: Image Cog (CellCog) methodology
# Core: Descriptive narrative + explicit style/lighting/mood/composition
# Source: openclaw/skills/nitishgargiitd/image-cog
# ────────────────────────────────────────────────────────

SKILL_A_REWRITES = {
    "S1_avatar": (
        "Transform this selfie into a nostalgic 1990s American high school yearbook portrait. "
        "Style: Photorealistic school photography with Kodak Gold 200 film grain and warm color grading. "
        "Lighting: Classic dual-umbrella studio flash, soft and even, with gentle catch-lights in the eyes. "
        "Mood: Wholesome, nostalgic, authentic 90s school photo warmth. "
        "Composition: Head-and-shoulders, centered, 1:1 square format. "
        "The subject wears a navy crew-neck sweater with a plaid flannel collar peeking out — quintessential 90s prep. "
        "Background: Iconic 90s yearbook laser-beam gradient in cyan and magenta against deep blue. "
        "No modern elements, no text overlays, no name caption. Preserve facial identity exactly from input."
    ),
    "S2_edit": (
        "Edit this photograph: replace ONLY the upper-body clothing with a classic indigo denim trucker jacket. "
        "Style: Photorealistic, seamless local edit indistinguishable from the original photograph. "
        "Lighting: Match the existing overcast ambient lighting exactly — diffuse from above, soft shadows. "
        "Mood: Natural, casual outdoor feel unchanged from original. "
        "The jacket has two chest flap pockets with brass snap buttons, visible contrast stitching, "
        "and a fold-down collar buttoned to the second-from-top button. "
        "PRESERVE EXACTLY: face, expression, hair, glasses, skin tone, hand positions, lower body (khaki chinos), "
        "backpack straps, wooden railing, gravel path, alpine lake, mountains, sky, and all background elements. "
        "Backpack straps must sit naturally on the denim shoulders. Do not change the aspect ratio."
    ),
    "S3_poster": (
        'Create a professional event poster with high-contrast graphic design. '
        'Style: Art Deco inspired, elegant, print-ready quality. '
        'Mood: Prestigious, artistic, inviting — a university music event. '
        'Composition: 3:4 portrait, strict vertical symmetry, clear visual hierarchy. '
        'Color palette: Deep navy background with burnished gold accents and antique white text. '
        'Text to render EXACTLY (letter-perfect, no misspellings): '
        '"UC BERKELEY MUSIC SOCIETY" — top, bold geometric sans-serif, all caps, white. '
        '"SPRING AUDITIONS" — center, large metallic gold display typography with 3D embossed effect. '
        '"Date: April 15th" — lower section, gold on navy. '
        '"Location: Sproul Hall Room 202" — below date, same style. '
        '"Time: 6-9 PM" — below location, same style. '
        'Decorative elements: Art Deco geometric border with stepped corners, gold silhouette violin (left), '
        'treble clef (center), trumpet (right) between headline and details, scattered music notes. '
        'No photograph, pure graphic design.'
    ),
    "S4_character": (
        "Full body concept art of an original Marvel-inspired superhero 'Cyber-Knight'. "
        "Style: Digital concept art in the tradition of Ryan Meinerding and Andy Park — highly detailed, cinematic. "
        "Lighting: Dramatic cold-blue ambient fill from twilight sky, warm orange accent from distant fires camera-left, "
        "purple radiosity from armor energy veins, strong backlight rim from storm clouds creating a halo silhouette. "
        "Mood: Imposing, heroic, monumental — a lone sentinel amid destruction. "
        "Composition: Low angle (~15° below eye level), 24mm wide-angle, 3:4 portrait format. "
        "Character: Tall imposing figure in obsidian-black powered armor with matte gunmetal finish. "
        "Glowing purple-violet energy veins trace circuit-board pathways across all armor sections, "
        "brightest at a triangular arc reactor chest core. Fully enclosed angular helmet with narrow purple visor. "
        "Floor-length dark metallic cape, tattered at edges, billowing right. "
        "Pose: Wide heroic power-stance, fists clenched, chin tilted up, shoulders back. "
        "Setting: Ruined tech-noir NYC at twilight — shattered skyscrapers, OSCORP/CYBERNETICS neon signs, "
        "cracked wet asphalt reflecting purple glow, light rain with visible foreground droplets. "
        "No text, no watermarks."
    ),
}


# ────────────────────────────────────────────────────────
# Skill B: YouMind Community Patterns (12K+ curated prompts)
# Core: Ultra-detailed structured prompts with sections for
# Scene/Subject/Environment/Lighting/Camera/Negative, exact camera parameters
# Source: YouMind-OpenLab/awesome-nano-banana-pro-prompts (10.5K stars)
# ────────────────────────────────────────────────────────

SKILL_B_REWRITES = {
    "S1_avatar": (
        "### Scene\n"
        "1990s American high school yearbook portrait photo, transforming the uploaded selfie.\n\n"
        "### Subject\n"
        "* Gender/age/identity: preserve exactly from input selfie\n"
        "* Hair, glasses, facial structure: unchanged from input\n"
        "* Expression: warm, natural smile with teeth showing\n"
        "* Clothing: navy blue crew-neck sweater with a plaid button-up shirt collar peeking out\n"
        "* Pose: head-and-shoulders, centered, slight head tilt\n\n"
        "### Environment\n"
        "* Background: iconic 90s yearbook laser-beam backdrop — vivid neon beams of cyan, "
        "electric blue, and hot magenta radiating outward from behind the subject against deep cobalt blue gradient\n\n"
        "### Lighting\n"
        "* Source: dual umbrella flash at 45° left and right\n"
        "* Quality: soft, even illumination with gentle catch-lights in eyes\n"
        "* White balance (K): 4800 (warm tungsten shift)\n\n"
        "### Camera\n"
        "* Film stock: Kodak Gold 200 — warm color shift, subtle film grain, slightly desaturated reds\n"
        "* Focal length: 85mm portrait lens\n"
        "* Aperture: f/5.6 (moderate depth of field)\n"
        "* Aspect ratio: 1:1 square\n"
        "* Soft vignetting at corners as if scanned from yearbook page\n\n"
        "### Negative\n"
        "* Modern digital effects, text overlays, name captions, beauty filters, CGI look"
    ),
    "S2_edit": (
        "### Task\n"
        "Local image edit — replace ONLY the upper-body garment.\n\n"
        "### Target Change\n"
        "* New garment: classic Type III indigo denim trucker jacket\n"
        "* Wash: medium indigo with natural fading at stress points (elbows, chest pocket edges)\n"
        "* Details: two symmetrical chest flap pockets with antique brass snap buttons, "
        "exposed contrast-orange chain stitching along yoke seams, structured fold-down collar, "
        "buttoned to second-from-top button, visible twill weave with slub-yarn irregularities\n\n"
        "### Absolute Preservation\n"
        "* Face, eyes, mouth, nose, facial expression (looking left), hair, glasses, skin tone\n"
        "* Both hands and their exact positions\n"
        "* Lower body: khaki chinos\n"
        "* Backpack with visible shoulder straps\n"
        "* Wooden railing subject leans against, gravel path, green grass\n"
        "* Entire alpine lake, mountain range, snow-capped peaks, forested hillsides, overcast sky\n"
        "* Camera angle, focal length, depth of field, color grading — all identical\n\n"
        "### Transition Blending\n"
        "* Collar-to-neck: natural fabric-to-skin transition\n"
        "* Backpack straps: sit naturally on denim shoulders\n"
        "* Shadows: follow existing overcast ambient lighting (diffuse from above)\n"
        "* No hard shadow edges not in original\n\n"
        "### Negative\n"
        "* Adding objects, text, aspect ratio change, face smoothing, background alteration"
    ),
    "S3_poster": (
        "### Scene\n"
        "Print-ready high-contrast Art Deco event poster, 3:4 portrait.\n\n"
        "### Color Palette\n"
        "* Background: deep navy blue (#0d1b2a)\n"
        "* Accents: metallic burnished gold (#b8860b)\n"
        "* Primary text: antique white (#faebd7)\n\n"
        "### Text Content (render EXACTLY as written)\n"
        '* Line 1 (top): "UC BERKELEY MUSIC SOCIETY" — antique white, bold geometric sans-serif, all-caps, tracking +50, largest header\n'
        '* Line 2 (center): "SPRING AUDITIONS" — metallic gold, 3D embossed effect + drop shadow, dramatic display serif, 3x size of Line 1\n'
        '* Line 3 (lower third): "Date: April 15th" — gold text, clean sans-serif, centered\n'
        '* Line 4: "Location: Sproul Hall Room 202" — same style below Line 3\n'
        '* Line 5: "Time: 6-9 PM" — same style below Line 4\n\n'
        "### Decorative Elements\n"
        "* Art Deco geometric border with stepped corners and fan motifs framing entire poster\n"
        "* Between Lines 2-3: symmetrical gold silhouette violin (left), treble clef (center), trumpet (right)\n"
        "* Scattered music notes and staff lines as accents\n\n"
        "### Composition\n"
        "* Strict vertical symmetry\n"
        "* Hierarchy: title → headline → instruments → details\n"
        "* Generous margins, no photograph, pure graphic design\n\n"
        "### Negative\n"
        "* Compression artifacts, misspellings, text warping, photographic elements"
    ),
    "S4_character": (
        "### Scene\n"
        "Full-body concept art, original Marvel-inspired superhero 'Cyber-Knight' in ruined cyberpunk cityscape.\n\n"
        "### Character\n"
        "* Build: tall imposing figure (~6'4\"), heroic V-shaped torso\n"
        "* Armor: obsidian-black powered armor, matte gunmetal finish with metallic flake, "
        "overlapping segmented plates (chest piece, pauldrons, vambraces, cuisses, greaves) "
        "connected by flexible black under-armor mesh at joints\n"
        "* Energy veins: bioluminescent purple-violet circuit-board pathways across all armor sections, "
        "brightest at triangular arc reactor chest core, dimming at extremities, casting faint purple reflection\n"
        "* Helmet: fully enclosed, angular, predatory, swept-back aerodynamic fins, narrow horizontal purple visor\n"
        "* Cape: floor-length dark metallic smart-fabric, battle-damaged tattered lower edge, "
        "billowing right, interior shows faint purple energy capillaries\n\n"
        "### Pose\n"
        "* Heroic wide power-stance, feet shoulder-width on rubble, weight centered\n"
        "* Fists clenched at sides, chin tilted upward, shoulders back, chest presented\n\n"
        "### Camera\n"
        "* Angle: low (~15° below eye level), imposing monumental feel\n"
        "* Focal length: 24mm wide-angle, slight barrel distortion\n"
        "* Aspect ratio: 3:4 portrait\n\n"
        "### Environment\n"
        "* Setting: ruined tech-noir NYC at blue-hour twilight\n"
        "* Mid-ground: shattered skyscrapers with exposed steel ribbing\n"
        "* Background: flickering neon signs (OSCORP, CYBERNETICS)\n"
        "* Ground: cracked asphalt and concrete rubble, rain-slicked puddles reflecting purple glow\n"
        "* Atmosphere: light rain with visible foreground droplets\n\n"
        "### Lighting\n"
        "* Ambient: cold-blue fill from twilight sky\n"
        "* Accent: warm orange-amber from distant fires (camera-left)\n"
        "* Radiosity: purple bounce from energy veins\n"
        "* Backlight: strong rim from gap in storm clouds, divine halo silhouette effect\n\n"
        "### Negative\n"
        "* Text, watermarks, UI elements, anime style, landscape orientation"
    ),
}


# ────────────────────────────────────────────────────────
# Skill C: Hunyuan PromptEnhancer CoT (总-分-总)
# Core: General-Detail-General structure, primary-to-secondary ordering,
# end with one-sentence style summary for style anchoring
# Source: Hunyuan-PromptEnhancer/PromptEnhancer (3.7K stars)
# ────────────────────────────────────────────────────────

SKILL_C_REWRITES = {
    "S1_avatar": (
        # 总: Overview
        "A classic 1990s American high school yearbook portrait photo, transforming the "
        "uploaded selfie while preserving the subject's complete facial identity. "
        # 分: Primary details
        "The subject is centered in a head-and-shoulders composition with a warm, natural "
        "smile. They wear a navy crew-neck sweater layered over a plaid button-up collar shirt — "
        "the quintessential 90s preppy yearbook look. "
        # 分: Secondary details
        "The background is the iconic 90s yearbook laser-beam gradient pattern — vivid cyan "
        "and magenta light rays radiating outward against a deep cobalt blue field. "
        "The lighting is soft dual-umbrella studio flash producing even illumination with "
        "gentle catch-lights in the eyes. A warm tungsten color cast and visible Kodak Gold 200 "
        "film grain permeate the image. Soft vignetting at corners as if scanned from a yearbook page. "
        # 总: Style summary
        "The overall style is authentic 1990s school photography with a nostalgic, wholesome "
        "warmth — square 1:1 format, no text, no modern elements."
    ),
    "S2_edit": (
        # 总: Overview
        "A precise local image edit replacing only the upper-body clothing with a denim trucker "
        "jacket while keeping every other pixel of the photograph identical. "
        # 分: Primary — the change
        "The new garment is a classic mid-wash indigo denim trucker jacket with a structured "
        "fold-down collar, two chest flap pockets with brass snap buttons, visible contrast "
        "orange stitching along the yoke seams, and the jacket buttoned to the second-from-top "
        "button. The denim texture shows a natural twill weave with subtle fading at stress points. "
        # 分: Secondary — preservation
        "Everything else remains pixel-identical: the subject's face, expression, hair, glasses, "
        "skin tone, pose (seated, leaning against wooden bench, looking left), hand positions, "
        "khaki trousers, backpack with visible shoulder straps resting naturally on the denim "
        "shoulders, and the complete background — alpine lake, snow-capped mountains, green hillside, "
        "wooden railing, gravel path, overcast sky. The jacket's shadows follow the existing diffuse "
        "overcast lighting from above, and the collar transitions seamlessly to the neck. "
        # 总: Style summary
        "The result is a seamless, photorealistic local garment replacement indistinguishable "
        "from an original photograph. Do not change the aspect ratio."
    ),
    "S3_poster": (
        # 总: Overview
        "A high-contrast Art Deco graphic design event poster for a university music audition event. "
        # 分: Primary — text
        'The dominant headline "SPRING AUDITIONS" is rendered in large metallic gold display '
        'typography with a 3D embossed effect at the poster center. Above it, '
        '"UC BERKELEY MUSIC SOCIETY" appears in bold geometric sans-serif, antique white, all caps. '
        'Below the headline, event details are displayed in clean sans-serif gold text: '
        '"Date: April 15th", "Location: Sproul Hall Room 202", "Time: 6-9 PM" — each on '
        "its own centered line, clearly legible. "
        # 分: Secondary — decorative
        "Between the headline and details, gold silhouette musical instruments — a violin (left), "
        "treble clef (center), and trumpet (right) — are arranged symmetrically with scattered "
        "music notes. Art Deco geometric borders with stepped corners and fan motifs frame the poster. "
        "The color palette is deep navy background with burnished gold accents and cream white text. "
        "Strict vertical symmetry with clear top-to-bottom visual hierarchy. "
        # 总: Style summary
        "The overall style is a professional, print-ready Art Deco graphic design poster "
        "with elegant typography and clean layout — 3:4 portrait, no photograph, no misspellings."
    ),
    "S4_character": (
        # 总: Overview
        "Full-body concept art of an original Marvel-inspired superhero called 'Cyber-Knight', "
        "standing heroically in a ruined cyberpunk cityscape. "
        # 分: Primary — character
        "The character wears sleek obsidian-black powered armor with a matte finish and "
        "interlocking segmented plates covering chest, shoulders, arms, and legs. Glowing "
        "purple-violet energy veins trace circuit-like patterns across all armor sections, "
        "emanating from a bright triangular core on the chest plate. The fully enclosed helmet "
        "has a narrow glowing purple visor with angular, predatory swept-back edges. "
        "A dark metallic-fiber cape, tattered at the hem, billows to the right in wind. "
        "The character stands in a wide heroic power-stance with fists clenched, shot from a "
        "low angle looking upward for an imposing effect. "
        # 分: Secondary — environment
        "The setting is the ruins of tech-noir New York City at twilight — shattered skyscrapers "
        "with exposed steel ribbing, flickering neon signs (OSCORP, CYBERNETICS), cracked asphalt "
        "with puddles reflecting purple glow, and light rain falling. Dramatic cold-blue ambient "
        "fill from the sky, warm orange fire-glow from the left, purple energy radiosity from "
        "the armor, and strong backlight rim from storm clouds creating a silhouette halo. "
        # 总: Style summary
        "The overall style is highly detailed cinematic digital concept art with a deep indigo "
        "and purple palette — 3:4 portrait, no text, no watermark."
    ),
}


def skill_a_rewriter(scenario_id, scenario):
    return SKILL_A_REWRITES[scenario_id]


def skill_b_rewriter(scenario_id, scenario):
    return SKILL_B_REWRITES[scenario_id]


def skill_c_rewriter(scenario_id, scenario):
    return SKILL_C_REWRITES[scenario_id]


SKILLS = [
    ("r2-skill-a", "Image Cog (CellCog) Method", skill_a_rewriter),
    ("r2-skill-b", "YouMind Community Patterns", skill_b_rewriter),
    ("r2-skill-c", "Hunyuan CoT 总-分-总", skill_c_rewriter),
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
            print(f"Rewritten: {rewritten[:80]}...")

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

            await asyncio.sleep(3)

        meta_path = f"{output_dir}/generation-meta.json"
        Path(meta_path).parent.mkdir(parents=True, exist_ok=True)
        with open(meta_path, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nMetadata saved to {meta_path}")


if __name__ == "__main__":
    asyncio.run(main())
