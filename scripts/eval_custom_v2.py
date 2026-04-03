#!/usr/bin/env python3
"""Evaluate Custom Skill v2 on 4 scenarios — applies the 总-分-总 fused methodology."""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from generate import generate_image, load_api_key, TEST_SCENARIOS, PROJECT_DIR

OUTPUT_DIR = str(PROJECT_DIR / "test" / "results" / "custom-v2")

CUSTOM_V2_PROMPTS = {
    "S1_avatar": (
        # 总: Overview
        "Transform this selfie into a classic 1990s American high school yearbook portrait "
        "photo, preserving the subject's complete facial identity — face shape, glasses, hair, "
        "skin tone must match exactly. "
        # 分-Primary: Subject
        "The subject is centered in a head-and-shoulders composition with a warm, natural smile "
        "and a slight head tilt. They wear a navy blue crew-neck sweater layered over a plaid "
        "flannel button-up shirt — the collar and top button visible above the sweater neckline "
        "in a quintessential 90s prep style. "
        # 分-Secondary: Backdrop + film
        "Background: the iconic 90s yearbook laser-beam gradient — vivid neon beams of cyan "
        "and hot magenta radiating outward from behind the subject's head against a deep cobalt "
        "blue field, slightly blurred to keep the portrait sharp. "
        "Lighting: dual-umbrella studio flash at 45° angles, producing soft even illumination "
        "with gentle catch-lights in the eyes and soft shadows under the chin. "
        "Film stock: Kodak Gold 200 — warm color shift toward amber, subtle film grain texture, "
        "slightly desaturated reds, soft vignetting at corners as if scanned from a printed yearbook page. "
        "Aspect ratio 1:1 square. "
        # 总-Anchor
        "The overall style is authentic 1990s school photography with nostalgic warmth and film charm. "
        "No text overlays, no name captions, no modern digital effects."
    ),
    "S2_edit": (
        # 总: Overview
        "A precise local image edit: replace ONLY the upper-body garment with a denim trucker "
        "jacket while keeping every other pixel of the photograph identical. "
        # 分-Target Change
        "The new jacket is a classic Levi's Type III indigo denim trucker jacket in a medium-wash "
        "with natural fading at stress points (elbows, chest pocket edges, collar crease). "
        "It has two symmetrical chest flap pockets with antique brass snap buttons, "
        "visible contrast-orange chain stitching along the yoke seams, "
        "a structured fold-down collar buttoned to the second-from-top button, "
        "and a natural twill weave with slub-yarn irregularities. The jacket fits comfortably "
        "over the subject's frame. "
        # 分-Preservation
        "Absolute preservation (pixel-identical): "
        "Face: expression (looking left), eyes, mouth, nose, jawline, skin tone. "
        "Hair: style, color, all strands. Glasses: exact frame shape and lens reflections. "
        "Hands: both hand positions exactly as they are. "
        "Lower body: khaki chinos, shoes. "
        "Accessories: backpack — straps must sit naturally over the denim jacket shoulders. "
        "Background: wooden railing/bench the subject leans against, gravel path, green grass "
        "in foreground, alpine lake with still water reflection, snow-capped mountain peaks, "
        "forested green hillside, autumn-colored trees at water's edge, overcast sky. "
        "Camera: exact same angle, focal length, depth of field, color grading. "
        # 分-Transition
        "Blending: collar-to-neck transition seamless with natural fabric-to-skin edge. "
        "Backpack straps drape naturally over denim shoulders with correct shadow underneath. "
        "Jacket shadows match existing diffuse overcast lighting from above — no new hard shadows. "
        # 总-Anchor
        "The result is a seamless photorealistic garment replacement indistinguishable from "
        "the original photograph. Do not change the aspect ratio. "
        "No face smoothing, no added objects, no text, no background alterations."
    ),
    "S3_poster": (
        # 总: Overview
        "A high-contrast Art Deco graphic design event poster for UC Berkeley Music Society "
        "Spring Auditions. "
        # 分-Text first (exact spelling)
        "EXACT TEXT TO RENDER (letter-perfect, no misspellings, no text warping): "
        'Line 1 (top center): "UC BERKELEY MUSIC SOCIETY" — antique white (#faebd7), '
        "bold geometric sans-serif, all caps, wide letter-spacing, largest size. "
        'Line 2 (center, hero text): "SPRING AUDITIONS" — metallic burnished gold with 3D '
        "embossed bevel effect and drop shadow, dramatic display serif or slab-serif, 3× size "
        "of Line 1, visual center of gravity of the poster. "
        'Line 3 (lower third): "Date: April 15th" — gold on navy, clean sans-serif, centered. '
        'Line 4 (below Line 3): "Location: Sproul Hall Room 202" — same style. '
        'Line 5 (below Line 4): "Time: 6-9 PM" — same style. '
        "All five lines must be rendered exactly as written above with zero spelling errors. "
        # 分-Design
        "Color palette: deep navy blue background, metallic burnished gold accents, antique white/cream text. "
        "Decorative elements: Art Deco geometric border with stepped corners and fan motifs framing "
        "the entire poster. Between Lines 2 and 3: symmetrical gold silhouette violin (left), "
        "treble clef (center), trumpet (right), with scattered music notes and staff line fragments as accents. "
        "Composition: strict vertical symmetry. Visual hierarchy: SPRING AUDITIONS (hero) draws the eye first, "
        "then UC BERKELEY MUSIC SOCIETY (header), then instruments, then event details. "
        "Generous margins. 3:4 portrait orientation. "
        # 总-Anchor
        "The overall style is a professional, print-ready Art Deco poster with elegant metallic "
        "typography and clean geometric layout. "
        "No photographs, no compression artifacts, no decorative distortion on text characters."
    ),
    "S4_character": (
        # 总: Overview
        "Full-body concept art of an original Marvel-inspired superhero called 'Cyber-Knight', "
        "standing as a lone sentinel in the rain-soaked ruins of a cyberpunk city. "
        # 分-Character
        "Build: tall imposing figure with a heroic V-shaped torso. "
        "Armor: obsidian-black powered armor with a matte gunmetal finish and metallic flake — "
        "overlapping segmented plates cover chest, pauldrons, vambraces, cuisses, and greaves, "
        "connected by flexible black under-armor mesh visible at joints. "
        "Energy: bioluminescent purple-violet veins trace circuit-board pathways across all "
        "armor sections, brightest at a triangular arc reactor core on the chest plate, "
        "dimming toward extremities, casting faint purple reflections on nearby wet surfaces. "
        "Helmet: fully enclosed, angular and predatory, with swept-back aerodynamic fins and "
        "a narrow horizontal purple visor slit. "
        "Cape: floor-length dark metallic smart-fabric, battle-damaged with a tattered lower "
        "edge, billowing to the right in wind, interior showing faint purple energy capillaries. "
        # 分-Pose & Camera
        "Pose: wide heroic power-stance, feet shoulder-width apart on broken concrete rubble, "
        "fists clenched at sides, chin tilted upward, shoulders back, chest presented. "
        "Camera: low angle approximately 15° below eye level for an imposing monumental feel, "
        "24mm wide-angle lens with slight barrel distortion. Aspect ratio 3:4 portrait. "
        # 分-Environment
        'Setting: ruined tech-noir New York City at blue-hour twilight. '
        "Mid-ground: shattered skyscrapers with exposed steel ribbing and broken glass. "
        'Background: flickering neon signs reading "OSCORP" and "CYBERNETICS" in pink and cyan. '
        "Ground: cracked asphalt and concrete rubble, rain-slicked puddles reflecting the purple "
        "glow from the armor. Atmosphere: steady light rain with visible foreground droplets. "
        # 分-Lighting
        "Ambient: cold blue fill from the twilight sky. "
        "Accent: warm orange-amber fire-glow from wreckage on the left. "
        "Character: purple radiosity from the armor's energy veins. "
        "Backlight: strong rim light from a gap in the storm clouds, creating a divine halo "
        "silhouette around the helmet and shoulders. "
        # 总-Anchor
        "The overall style is highly detailed cinematic digital concept art with a deep indigo, "
        "black, and purple palette, in the tradition of Marvel concept artists. "
        "No text overlays, no watermarks, no UI elements."
    ),
}


async def main():
    api_key = load_api_key()
    if not api_key:
        print("ERROR: YUNWU_API_KEY not found.")
        sys.exit(1)

    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    print(f"Custom Skill v2 Evaluation — Output: {OUTPUT_DIR}\n")

    results = {}
    for scenario_id, scenario in TEST_SCENARIOS.items():
        prompt = CUSTOM_V2_PROMPTS[scenario_id]
        print(f"{'='*60}")
        print(f"[Custom v2] {scenario['name']}")
        print(f"Prompt: {prompt[:100]}...")

        output_path = f"{OUTPUT_DIR}/{scenario_id}.png"
        result = await generate_image(
            prompt=prompt,
            output_path=output_path,
            api_key=api_key,
            reference_image=scenario["reference_image"],
        )

        results[scenario_id] = {
            "scenario": scenario["name"],
            "original_prompt": scenario["prompt"],
            "rewritten_prompt": prompt,
            "output": output_path if result["success"] else None,
            "success": result["success"],
            "error": result.get("error"),
            "timestamp": datetime.now().isoformat(),
        }

        status = "OK" if result["success"] else f"FAILED: {result.get('error')}"
        print(f"Result: {status}\n")
        await asyncio.sleep(5)

    with open(f"{OUTPUT_DIR}/generation-meta.json", "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Metadata saved to {OUTPUT_DIR}/generation-meta.json")


if __name__ == "__main__":
    asyncio.run(main())
