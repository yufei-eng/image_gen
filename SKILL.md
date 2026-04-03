---
name: image-gen
description: >-
  Rewrites user image generation requests into optimized prompts for Gemini 3.1 Flash Image
  (Nano Banana 2). Covers avatar/style transfer, local image editing, poster/typography design,
  and character concept art. Use when the user asks to generate, create, edit, or design an
  image, photo, poster, avatar, character, or illustration.
---

# Image Generation Prompt Optimizer v2

Optimize image generation prompts for Gemini 3.1 Flash Image (Nano Banana 2).

## When to Use

User requests any image task: generate, create, edit, design, transform, stylize.

## API Tool

Call `generate_imagen` MCP tool with the rewritten prompt. For edits with a reference
image, pass the image via `image_url`.

## Workflow

```
1. Classify scenario → pick rewrite template
2. Rewrite prompt using 总-分-总 structure + template + Gemini rules
3. Call generate_imagen
4. Show result; if user unhappy → surgical edit prompt (max 2 retries)
```

## Scenario Classification

| Signal in user request | Scenario | Template |
|------------------------|----------|----------|
| "turn into", "style of", "as a", selfie/photo + style word | **Avatar / Style Transfer** | avatar |
| "replace", "change", "edit", "remove", "add to photo" | **Local Edit** | edit |
| "poster", "flyer", "banner", text to include, event info | **Poster / Typography** | poster |
| "character", "concept art", "superhero", "design a figure" | **Character Design** | character |

If ambiguous, ask the user one clarifying question.

## Core Rewrite Principles

Apply ALL of these to every rewritten prompt:

1. **总-分-总 (General-Detail-General) structure.** Start with a one-sentence overview.
   Then give details from primary to secondary importance. End with a one-sentence style
   summary that anchors the overall aesthetic.
2. **Narrative, not keywords.** Write as if briefing a human artist. No tag-soup.
3. **Spec-first, style-second, constraints-last.** Subject details before style tokens.
4. **Exact text in quotes.** Any text to render goes in `"double quotes"` with explicit
   spelling instruction and typography described (weight, style, size relationship).
5. **Camera + lighting language.** Focal length, angle, light source, color temperature.
6. **Material specificity.** Describe textures: "brushed steel", "indigo selvedge denim
   with contrast-orange chain stitching", "matte obsidian with metallic flake".
7. **Film stock for photo scenarios.** Name the film: "Kodak Gold 200", "Fuji Superia 400".
8. **Aspect ratio in prompt.** State it explicitly: "aspect ratio 3:4 portrait".
9. **Negative constraints.** End with what to exclude: "No text, no watermark, no modern
   elements" — keep short and specific.
10. **Style anchoring sentence.** The final sentence summarizes the target aesthetic in
    ≤20 words. This steers the model's overall coherence.

## Template: Avatar / Style Transfer

```
总: [Transformation verb] this [photo type] into a [era/style] [output format],
preserving the subject's complete facial identity.

分-Primary: The subject is [pose/composition]. They wear [era-specific clothing with
material descriptions — e.g., "navy crew-neck sweater with a plaid button-up collar"].

分-Secondary: Background: [period-accurate backdrop with vivid details — e.g.,
"iconic 90s laser-beam gradient — cyan and magenta rays radiating against deep cobalt
blue"]. Lighting: [type + color temperature — e.g., "dual-umbrella studio flash, soft
even illumination, gentle catch-lights"]. Film: [stock + characteristics — e.g.,
"Kodak Gold 200 — warm color shift, subtle grain, slightly desaturated reds"].
[Aspect ratio].

总-Anchor: The overall style is [≤15 word aesthetic summary].
Negative: [exclusions].
```

**Key additions vs raw prompt:** era-specific backdrop details, clothing materials,
explicit film stock, camera/lighting parameters, identity preservation, style anchor.

## Template: Local Edit

Structure using Target Change / Absolute Preservation / Transition Blending:

```
总: A precise local image edit replacing only [target area] while keeping every
other pixel of the photograph identical.

分-Target Change:
The new [item] is a [full material description — wash, color, texture, details,
buttons, stitching, fit]. [2-3 sentences of physical specifics].

分-Absolute Preservation:
Everything else remains pixel-identical: [EXHAUSTIVE list organized by category]
- Face & body: face, expression, hair, glasses, skin tone, pose, hand positions
- Clothing: [unchanged garments]
- Accessories: [bags, straps, jewelry]
- Background: [list every background element individually]
- Camera: angle, focal length, depth of field, color grading

分-Transition:
The [item]-to-[body part] transition must be seamless. [Accessory] straps sit
naturally on [new surface]. Shadows follow the existing [lighting direction].

总-Anchor: The result is a seamless, photorealistic local [edit type] indistinguishable
from an original photograph. Do not change the aspect ratio.
Negative: Adding objects, text, face smoothing, background alteration, aspect ratio change.
```

**Key additions:** Exhaustive per-category preservation list, material specifics for
replacement, explicit transition/blending instructions, negative constraints.

## Template: Poster / Typography

Use text-first approach — specify ALL text content before any design:

```
总: A [design style] event poster for [event description].

分-Text (render EXACTLY as written, letter-perfect):
Line 1 (position): "[TEXT]" — [typography: weight, family, case, color, size relation]
Line 2 (position): "[TEXT]" — [typography + any effects like "3D embossed"]
Line 3 (position): "[TEXT]" — [typography]
[Continue for all lines. Include "no misspellings, no text warping".]

分-Design:
Color palette: [background color], [accent color], [text color].
Decorative elements: [motifs, instruments, icons] arranged [spatial relationship].
Border: [style description].
Composition: [hierarchy — what draws the eye 1st, 2nd, 3rd]. Strict [symmetry type].

总-Anchor: The overall style is a professional, print-ready [style] poster with
elegant typography and clean layout. [Aspect ratio].
Negative: Compression artifacts, misspellings, text warping, photographic elements.
```

**Key additions:** Numbered per-line text specs with position and typography, color
palette with descriptive names, explicit spelling/warping constraints, hierarchy.

## Template: Character Design

Structure from overview → character core → environment → lighting → anchoring:

```
总: [Medium] of an original [genre] character called '[Name]', [one-sentence scene].

分-Character:
Build: [body type, height]. Armor/clothing: [every piece with material — "obsidian-black
powered armor with matte gunmetal finish and metallic flake", segmented plates at
specific body parts, flexible mesh at joints].
Signature element: [energy effects with color, pattern style (circuit-board/organic),
brightness gradient from core to extremities, reflection on nearby surfaces].
Helmet/face: [visor style, shape].
Cape/flow: [material, condition (tattered/pristine), direction, interior details].

分-Pose & Camera:
Pose: [specific stance, weight distribution, limb positions].
Camera: [angle + degrees], [focal length], [perspective effect]. [Aspect ratio].

分-Environment:
Setting: [location + time]. Mid-ground: [architecture]. Background: [neon signs with
EXACT text in quotes]. Ground: [surface + reflections]. Atmosphere: [weather].

分-Lighting:
Ambient: [color + source]. Accent: [color + direction]. Character: [energy glow].
Backlight: [rim light effect].

总-Anchor: The overall style is [≤20 word rendering description with dominant palette].
No text, no watermark, no UI elements.
```

**Key additions:** Material specificity for every armor piece, camera angle in degrees,
neon sign text in quotes, cape physics, multi-source lighting breakdown, style anchor.

## Quality Self-Check

After generation, verify:

| Scenario | Check |
|----------|-------|
| Avatar | Face resembles input? Correct era elements (backdrop, outfit, film grain)? |
| Edit | Background pixel-identical? Only specified area modified? Natural transition? |
| Poster | All text present, spelled correctly, readable? Design hierarchy clear? |
| Character | Full body visible in correct aspect ratio? All described elements present? |

If a check fails, craft a surgical edit prompt targeting only the failing element.

## Conversational Refinement

- Prefer **editing over re-rolling** — upload generated image as reference
- One change at a time for predictable results
- Re-anchor invariants: "Keep everything the same except..."
- Always include "Do not change the input aspect ratio"
