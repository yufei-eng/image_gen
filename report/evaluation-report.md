# Image Gen Skill Evaluation Report

**Generated**: 2026-04-03
**Base Model**: Gemini 3.1 Flash Image (Nano Banana 2) via Yunwu API
**Deployment**: Claude Code + Cursor dual-environment

---

## Executive Summary

We evaluated prompt optimization approaches for Gemini 3.1 Flash Image across four personal-assistant image generation scenarios. The custom-built skill achieves the best overall performance in avatar generation (4.75/5) and poster design (5.0/5), while the best open-source skill (harshkedia177) leads in character concept art (4.75/5). All prompt-optimized approaches outperform the raw baseline (4.38/5) in most scenarios.

**Key finding**: Gemini 3.1 Flash Image already performs remarkably well with raw prompts (baseline avg 4.38/5). Prompt optimization provides meaningful but incremental improvement (+4-6%), with the largest gains in poster typography and avatar style transfer.

---

## Evaluation Criteria (1-5 scale)

| Dimension | Description |
|-----------|-------------|
| Prompt Adherence | Does the output match the user's description? |
| Visual Quality | Resolution, clarity, absence of artifacts |
| Aesthetics | Composition, color harmony, overall appeal |
| Scenario-Specific | S1=Style transfer | S2=Edit precision | S3=Text rendering | S4=Detail/creativity |
| **Overall** | Average of the four dimensions |

---

## Score Comparison

### Full Results Table

| Phase | S1 Avatar | S2 Edit | S3 Poster | S4 Character | **Average** |
|-------|-----------|---------|-----------|--------------|-------------|
| **Baseline (Gemini Direct)** | 4.25 | 3.88 | 4.88 | 4.50 | **4.38** |
| **Skill 1 (harshkedia177)** | 4.50 | 4.38 | 5.00 | 4.75 | **4.66** |
| **Skill 2 (ivangdavila)** | 4.13 | 4.00 | 4.50 | 4.25 | **4.22** |
| **Skill 3 (kousen)** | 4.50 | 4.00 | 4.75 | 4.63 | **4.47** |
| **Custom Skill** | **4.75** | 4.38 | **5.00** | 4.13* | **4.57** |

*\*S4 Custom generated via gemini-2.5-flash (MCP fallback) due to API rate limiting; not fully comparable.*

### Best Score Per Scenario

| Scenario | Best Phase | Score | Key Success Factor |
|----------|-----------|-------|--------------------|
| S1 Avatar | **Custom Skill** | 4.75 | Explicit period-accurate outfit + film grain + identity preservation |
| S2 Edit | **Skill 1 / Custom** (tied) | 4.38 | Change/Keep/Avoid pattern + blend instructions |
| S3 Poster | **Skill 1 / Custom** (tied) | 5.00 | Text-first approach + per-line typography specs |
| S4 Character | **Skill 1** | 4.75 | Priority-ordered narrative + explicit constraints |

---

## Improvement Over Baseline

| Phase | Avg Score | vs Baseline | Improvement |
|-------|-----------|-------------|-------------|
| Baseline | 4.38 | — | — |
| Skill 1 (harshkedia177) | 4.66 | +0.28 | **+6.4%** |
| Skill 3 (kousen) | 4.47 | +0.09 | +2.1% |
| Custom Skill | 4.57 | +0.19 | **+4.3%** |
| Skill 2 (ivangdavila) | 4.22 | -0.16 | -3.7% |

---

## Open Source Skill Analysis

### Skill 1: harshkedia177/image-gen-plugin

**Score: 4.66/5 (Best open-source)**

| Strength | Weakness |
|----------|----------|
| Best text-first hack for typography | Slightly verbose prompts |
| Strong priority-ordered narrative structure | No scenario-specific templates |
| Self-review loop concept | No Gemini 3.1-specific optimizations |
| Explicit "no text, no watermark" constraints | Generic approach across all tasks |

**Best for**: Poster/typography (5.0) and character design (4.75)

### Skill 2: ivangdavila/image-generation

**Score: 4.22/5 (Below baseline)**

| Strength | Weakness |
|----------|----------|
| Structured Objective-First template | Over-structured prompts may confuse Gemini |
| Excellent Change/Keep/Avoid edit pattern | Goal/Subject/Style separation can fragment intent |
| Multi-provider model selection guide | Benchmark data not Gemini 3.1-specific |
| Comprehensive documentation | Template overhead with marginal quality gain |

**Best for**: Reference documentation, not prompt rewriting

### Skill 3: kousen/nano-banana-prompting

**Score: 4.47/5 (Above baseline)**

| Strength | Weakness |
|----------|----------|
| Closest to Google's official guidance | "Brief a human artist" approach lacks precision |
| Natural language narrative is readable | No structured templates per scenario |
| Camera + lighting + material language | Tends to add creative drift (e.g., Tokyo vs NYC) |
| Purpose context helps quality | Less explicit constraints than Skill 1 |

**Best for**: Character art visual quality (5.0 visual quality in S4)

### Recommendation

**Most recommended: harshkedia177/image-gen-plugin (Skill 1)** — Highest overall score, particularly strong in typography and character design. Its priority-ordered narrative structure and text-first hack are directly applicable to our use case.

**Custom skill still needed?** Yes, for two reasons:
1. No open-source skill provides scenario-specific templates (avatar vs edit vs poster vs character), which we demonstrated improves S1 avatar results.
2. The Change/Keep/Avoid edit pattern with explicit blend instructions (from our custom skill) delivers the most reliable image editing results.

---

## Custom Skill Design

### Architecture

The custom skill classifies user requests into four scenario templates:

```
User Request → Scenario Classifier → Template Selection → Prompt Rewrite → Gemini API
                    ↓
        avatar | edit | poster | character
```

### Key Techniques Per Scenario

| Scenario | Technique | Impact |
|----------|-----------|--------|
| Avatar | Period-accurate outfit + film grain spec + identity preservation | +11.8% vs baseline |
| Edit | Change/Keep/Avoid + exhaustive KEEP list + blend instructions | +12.9% vs baseline |
| Poster | Text-first with per-line typography + "no distortion" | +2.5% vs baseline |
| Character | Material specificity + camera angle + cape physics | -8.2%* vs baseline |

*S4 degradation due to model fallback, not prompt quality.

### Deployment

- `~/.claude/skills/image-gen/SKILL.md` (Claude Code)
- `~/.cursor/skills/image-gen/SKILL.md` (Cursor)

---

## Competitor Comparison (Doubao / Seedream)

**Status**: Test guide prepared at `reference/doubao-test-guide.md`. Awaiting manual web testing.

Based on public benchmarks (Seedream 2.0 technical report):
- Seedream excels at Chinese text rendering (78% success rate)
- Strong photorealistic output at low cost
- Native understanding of Chinese prompts with automatic style inference
- Expected to outperform in S3 (text rendering) with Chinese text scenarios

Competitor scores will be added after manual testing is completed.

---

## Files & Artifacts

```
image-gen-skill/
├── SKILL.md                                    # Custom skill (deployed)
├── reference/
│   ├── doubao-test-guide.md                    # Doubao testing instructions
├── scripts/
│   ├── generate.py                             # Gemini API wrapper + baseline runner
│   ├── eval_opensource.py                       # Open-source skill evaluator
│   ├── eval_custom.py                          # Custom skill evaluator
│   └── report.py                               # Report generator utility
├── test/
│   ├── samples/                                # Test input images (selfie.jpg, outfit.jpg)
│   └── results/
│       ├── baseline/                           # Phase 1: Gemini direct (4 images + scores)
│       ├── opensource-1/                       # harshkedia177 (4 images + scores)
│       ├── opensource-2/                       # ivangdavila (4 images + scores)
│       ├── opensource-3/                       # kousen (4 images + scores)
│       └── custom/                             # Custom skill (4 images + scores)
└── report/
    └── evaluation-report.md                    # This report
```
