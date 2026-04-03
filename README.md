# Image Gen Skill

Prompt optimization skill for Gemini 3.1 Flash Image (Nano Banana 2) that improves image generation quality in AI personal assistant scenarios.

## What It Does

Automatically rewrites user image requests into optimized prompts using scenario-specific templates:

| Scenario | Example | Technique |
|----------|---------|-----------|
| **Avatar / Style Transfer** | "Turn my selfie into a 90s yearbook photo" | Period-accurate details + identity preservation |
| **Local Image Edit** | "Replace my jacket with denim" | Change/Keep/Avoid pattern + blend instructions |
| **Poster / Typography** | "Create a concert poster with text..." | Text-first approach + per-line typography specs |
| **Character Design** | "Full body concept art of a superhero" | Material specificity + camera language |

## Results

Tested across 4 scenarios (5-point scale):

| Approach | Average Score |
|----------|--------------|
| Gemini Direct (no skill) | 4.38 |
| Best Open-Source Skill | 4.66 |
| **This Custom Skill** | **4.57** |

Best-in-class for avatar generation (4.75) and poster design (5.0/5).

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
├── SKILL.md              # The skill file (deploy this)
├── scripts/              # Test and evaluation scripts
├── test/results/         # Generated images and scores
└── report/               # Evaluation report
```

## Evaluation Report

See [report/evaluation-report.md](report/evaluation-report.md) for the full comparison including baseline, 3 open-source skills, and this custom skill.
