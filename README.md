# Image Gen Skill

Prompt optimization skill for Gemini 3.1 Flash Image (Nano Banana 2) that significantly improves image generation quality in AI personal assistant scenarios.

## What It Does

Automatically rewrites user image requests into optimized prompts using a fused **总-分-总 (General-Detail-General)** methodology:

| Scenario | Example | Technique |
|----------|---------|-----------|
| **Avatar / Style Transfer** | "Turn my selfie into a 90s yearbook photo" | Period-accurate details + film stock + identity preservation + style anchoring |
| **Local Image Edit** | "Replace my jacket with denim" | Per-category preservation list + material specifics + transition blending |
| **Poster / Typography** | "Create a concert poster with text..." | Text-first hack + per-line numbered specs + no-misspelling constraint |
| **Character Design** | "Full body concept art of a superhero" | Material specificity + multi-source lighting + camera language + neon text in quotes |
| **Product / Object** | "Product shot of sneakers on marble" | Object material + staging + commercial lighting setup |
| **General Scene** *(fallback)* | "A sunset", "cute panda", "logo design"... | Universal 总-分-总 with subject/environment/style/mood sections |

## Results

Tested across 4 scenarios (5-point scale):

| Approach | S1 Avatar | S2 Edit | S3 Poster | S4 Character | **Average** |
|----------|-----------|---------|-----------|--------------|-------------|
| Gemini Direct (no skill) | 4.25 | 3.88 | 4.88 | 4.50 | 4.38 |
| Doubao (Competitor) | 3.88 | 4.75 | 3.75 | 4.25 | 4.16 |
| Best Open-Source Skill | 4.63 | 4.63 | 5.00 | 4.63 | 4.72 |
| **This Custom Skill v2** | **5.00** | **4.75** | **5.00** | **4.88** | **4.91** |

**+12% vs Gemini Direct** · **+18% vs Doubao** · **+4% vs Best Open-Source**

## Core Methodology

Custom Skill v2 fuses 6 prompt engineering approaches:

1. **总-分-总 structure** (from Hunyuan CoT) — overview → primary-to-secondary details → style anchoring sentence
2. **Text-First Hack + line numbering** (from YouMind community) — specify all text before design for 100% text accuracy
3. **Per-category preservation lists** (from Doubao's editing strength) — exhaustive Face→Hair→Glasses→Background itemization
4. **Material/lighting/film language** (from Image Cog + Skill 1) — "Kodak Gold 200", "indigo selvedge denim", "matte gunmetal with metallic flake"
5. **Negative constraints** — short exclusion list at prompt end
6. **Style anchoring** — final ≤20-word sentence steering overall aesthetic coherence

## Installation

### Claude Code
```bash
mkdir -p ~/.claude/skills/image-gen
cp SKILL.md ~/.claude/skills/image-gen/SKILL.md
```

### Cursor
```bash
mkdir -p ~/.cursor/skills/image-gen
cp SKILL.md ~/.cursor/skills/image-gen/SKILL.md
```

## Requirements

- Gemini API access (via `generate_imagen` MCP tool or direct API)
- `GEMINI_API_KEY` or `YUNWU_API_KEY` environment variable

## Project Structure

```
├── SKILL.md                    # The skill file (deploy this)
├── report.html                 # Interactive 8-slide evaluation report
├── scripts/
│   ├── generate.py             # Core image generation API client
│   ├── eval_round2.py          # Round 2: Image Cog / YouMind / Hunyuan CoT
│   └── eval_custom_v2.py       # Custom Skill v2 evaluation
├── test/
│   ├── samples/                # Test input images (selfie, outfit)
│   └── results/
│       ├── baseline/           # Gemini direct (no skill)
│       ├── competitor/         # Doubao / Seedream
│       ├── r2-skill-a/         # Round 2: Image Cog method
│       ├── r2-skill-b/         # Round 2: YouMind method
│       ├── r2-skill-c/         # Round 2: Hunyuan CoT method
│       ├── custom-v2/          # Custom Skill v2 (best — current)
│       ├── custom/             # [Archive] v1 custom skill (4.57)
│       └── opensource-*/       # [Archive] Round 1 open-source skills
└── reference/                  # Doubao prompt patterns, test guide
```

## Evaluation Report

Open `report.html` in a browser to view the interactive comparison report with side-by-side image comparisons and qualitative analysis for all 4 scenarios.
