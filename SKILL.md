---
name: image-gen
description: >-
  Rewrites user image generation requests into optimized prompts for Gemini 3.1 Flash Image
  (Nano Banana 2). Covers four key scenarios: avatar/style transfer, local image editing,
  poster/typography design, and character concept art. Use when the user asks to generate,
  create, edit, or design an image, photo, poster, avatar, character, or illustration.
---

# Image Generation Prompt Optimizer

Optimize image generation prompts for Gemini 3.1 Flash Image (Nano Banana 2) across
four core personal-assistant scenarios.

## When to Use

User requests any image task: generate, create, edit, design, transform, stylize.

## API Tool

Call `generate_imagen` MCP tool with the rewritten prompt. For edits with a reference
image, pass the image via `image_url`.

## Workflow

```
1. Classify scenario → pick rewrite template
2. Rewrite prompt using template + Gemini rules
3. Call generate_imagen
4. Show result; if user unhappy → patch prompt, regenerate (max 2 retries)
```

## Scenario Classification

| Signal in user request | Scenario | Template |
|------------------------|----------|----------|
| "turn into", "style of", "as a", selfie/photo + style word | **Avatar / Style Transfer** | avatar |
| "replace", "change", "edit", "remove", "add to photo" | **Local Edit** | edit |
| "poster", "flyer", "banner", text to include, event info | **Poster / Typography** | poster |
| "character", "concept art", "superhero", "design a figure" | **Character Design** | character |

If ambiguous, ask the user one clarifying question.

## Rewrite Rules (All Scenarios)

These Gemini-specific rules apply to every rewritten prompt:

1. **Narrative, not keywords.** Write as if briefing a human artist. No tag-soup.
2. **Spec-first, style-second, constraints-last.** Subject details before style tokens.
3. **Exact text in quotes.** Any text to render goes in `"double quotes"` with spelling
   specified and font style described (e.g., "bold sans-serif, all caps").
4. **Explicit preservation.** For edits, state what must NOT change before what should.
5. **Camera + lighting language.** Use cinematic terms: focal length, angle, light source.
6. **Material specificity.** Describe textures: "brushed steel", "indigo selvedge denim",
   "matte obsidian with metallic flake".
7. **Aspect ratio in prompt.** State it explicitly: "aspect ratio 3:4 portrait".
8. **No contradictions.** One dominant style per prompt.

## Template: Avatar / Style Transfer

Rewrite the user's request following this structure:

```
[Transformation verb] this [photo type] into a [era/style] [output format].
The subject: [head-and-shoulders/full body], [specific pose/composition].
Background: [period-accurate backdrop with details].
Outfit: [era-specific clothing with material descriptions].
Photography: [lighting type], [color cast], [film stock/grain], [lens feel].
Preserve: The subject's facial features and identity exactly.
Aspect ratio: [ratio]. No modern elements, no text overlays.
```

**Key additions to user prompt:** era-specific backdrop, outfit, lighting/film grain,
explicit identity preservation, aspect ratio.

## Template: Local Edit

Structure using the Change / Keep / Avoid pattern with strong preservation anchoring:

```
Edit this photograph:
- CHANGE: [exactly what to modify, with material/texture/color details]
- KEEP UNCHANGED: [exhaustive list — face, hair, expression, pose, lower body,
  background scene, lighting direction, camera angle, color grading]
- BLEND: [transition details — collar area, waistline, shadow continuity]
- AVOID: Extra objects, text overlays, color shift, aspect ratio change.
Do not change the input aspect ratio.
```

**Key additions:** Explicit KEEP list (the longer the better for edits), material detail
for the replacement item, transition/blend instructions, "do not change aspect ratio".

## Template: Poster / Typography

Use the text-first approach — specify all text first, then design around it:

```
Generate an image: [design style] event poster.
Layout: [orientation], [color palette with specific hex-adjacent descriptions].
EXACT TEXT TO RENDER:
- "[Line 1]" — [position], [typography: weight, style, size relationship]
- "[Line 2]" — [position], [typography]
- "[Line 3]" — [position], [typography]
[Continue for all text lines]
All text must be spelled exactly as written above. High legibility, no decorative
distortion on text characters.
Visual elements: [decorative motifs, instruments, icons, patterns].
Composition: [hierarchy — what draws the eye first, second, third].
Aspect ratio: [ratio]. Professional print-ready quality.
```

**Key additions:** Text-first with exact spelling, per-line typography specs, explicit
"no distortion" constraint, visual hierarchy description.

## Template: Character Design

Structure from subject core outward, with cinematic production language:

```
[Medium/style] of an original [genre] character called '[Name]'.
FIGURE: [body type, build], [detailed armor/clothing with materials —
  "sleek obsidian-black powered armor", "brushed titanium gauntlets"].
DETAILS: [energy effects, accessories, weapons — with glow colors, patterns].
HELMET/FACE: [visor style, expression if visible].
POSE: [specific stance — "heroic wide stance, fists clenched, weight on front foot"].
[Camera direction — "low angle looking upward for imposing effect"].
CAPE/FLOW: [fabric behavior — "tattered cape billowing right"].
SETTING: [specific location with named city elements, time of day, weather].
ATMOSPHERE: [lighting — "dramatic backlight creating rim glow", color palette].
Style: [rendering quality — "highly detailed digital concept art, cinematic"].
Aspect ratio: [ratio, usually 3:4 portrait for full body]. No text, no watermark.
```

**Key additions:** Material specificity for every armor piece, camera angle, cape physics,
environmental details with real-world anchors, explicit "no text" for concept art.

## Quality Self-Check

After generation, verify against these criteria before showing the user:

| Scenario | Check |
|----------|-------|
| Avatar | Face resembles input? Style is correct era? |
| Edit | Background unchanged? Only specified area modified? |
| Poster | All text present and spelled correctly? Readable? |
| Character | Full body visible? All described elements present? |

If a check fails, craft a surgical edit prompt (change only the failing element)
and regenerate once. Show both options to the user.

## Conversational Refinement

When the user requests changes to a generated image:
- Prefer **editing over re-rolling** — upload the generated image as reference
- Make one change at a time for predictable results
- Re-anchor invariants: "Keep everything the same except..."
- Always include "Do not change the input aspect ratio"
