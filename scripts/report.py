#!/usr/bin/env python3
"""Generate evaluation report comparing all test phases."""

import json
import os
from pathlib import Path
from datetime import datetime

PROJECT_DIR = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_DIR / "test" / "results"
REPORT_DIR = PROJECT_DIR / "report"


def load_scores(phase_dir: str) -> dict:
    """Load scores JSON from a phase directory."""
    scores_path = os.path.join(phase_dir, "scores.json")
    if os.path.exists(scores_path):
        with open(scores_path) as f:
            return json.load(f)
    return {}


def format_score_table(all_scores: dict) -> str:
    """Format a markdown comparison table from all phases' scores."""
    scenarios = ["S1_avatar", "S2_edit", "S3_poster", "S4_character"]
    scenario_labels = {
        "S1_avatar": "S1 Avatar",
        "S2_edit": "S2 Edit",
        "S3_poster": "S3 Poster",
        "S4_character": "S4 Character",
    }
    dimensions = ["prompt_adherence", "visual_quality", "aesthetics", "scenario_specific", "overall"]
    dim_labels = {
        "prompt_adherence": "Prompt Adherence",
        "visual_quality": "Visual Quality",
        "aesthetics": "Aesthetics",
        "scenario_specific": "Scenario-Specific",
        "overall": "Overall",
    }

    lines = []

    for sid in scenarios:
        lines.append(f"\n### {scenario_labels[sid]}\n")
        header = "| Phase | " + " | ".join(dim_labels[d] for d in dimensions) + " |"
        sep = "|-------|" + "|".join(["------:" for _ in dimensions]) + "|"
        lines.append(header)
        lines.append(sep)

        for phase_name, scores in all_scores.items():
            if sid in scores:
                s = scores[sid]
                vals = []
                for d in dimensions:
                    v = s.get(d, "-")
                    vals.append(str(v) if v != "-" else "-")
                lines.append(f"| {phase_name} | " + " | ".join(vals) + " |")

    return "\n".join(lines)


def compute_improvement(baseline_scores: dict, skill_scores: dict) -> dict:
    """Compute percentage improvement over baseline."""
    improvements = {}
    for sid in baseline_scores:
        if sid in skill_scores:
            b = baseline_scores[sid].get("overall", 0)
            s = skill_scores[sid].get("overall", 0)
            if b > 0:
                pct = ((s - b) / b) * 100
                improvements[sid] = {"baseline": b, "skill": s, "improvement_pct": round(pct, 1)}
    return improvements


def generate_report():
    """Generate the full evaluation report."""
    phases = {}
    phase_dirs = {
        "Baseline (Gemini Direct)": RESULTS_DIR / "baseline",
        "Competitor (Doubao)": RESULTS_DIR / "competitor",
        "OpenSource Skill 1": RESULTS_DIR / "opensource-1",
        "OpenSource Skill 2": RESULTS_DIR / "opensource-2",
        "OpenSource Skill 3": RESULTS_DIR / "opensource-3",
        "Custom Skill": RESULTS_DIR / "custom",
    }

    for name, dir_path in phase_dirs.items():
        scores = load_scores(str(dir_path))
        if scores:
            phases[name] = scores

    if not phases:
        print("No scores found in any phase directory.")
        return

    report_lines = [
        "# Image Gen Skill Evaluation Report",
        f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "\n## Evaluation Criteria (1-5 scale)",
        "- **Prompt Adherence**: How well the output matches the user's description",
        "- **Visual Quality**: Resolution, clarity, absence of artifacts",
        "- **Aesthetics**: Composition, color harmony, overall appeal",
        "- **Scenario-Specific**: S1=Style transfer | S2=Edit precision | S3=Text rendering | S4=Detail/creativity",
        "- **Overall**: Average of the four dimensions",
        "\n## Score Comparison",
        format_score_table(phases),
    ]

    baseline = phases.get("Baseline (Gemini Direct)", {})
    if baseline:
        report_lines.append("\n## Improvement Over Baseline\n")
        for phase_name, scores in phases.items():
            if phase_name == "Baseline (Gemini Direct)":
                continue
            improvements = compute_improvement(baseline, scores)
            if improvements:
                report_lines.append(f"### {phase_name}\n")
                report_lines.append("| Scenario | Baseline | This Phase | Improvement |")
                report_lines.append("|----------|--------:|----------:|-----------:|")
                for sid, imp in improvements.items():
                    report_lines.append(
                        f"| {sid} | {imp['baseline']} | {imp['skill']} | {imp['improvement_pct']:+.1f}% |"
                    )
                avg_imp = sum(i["improvement_pct"] for i in improvements.values()) / len(improvements)
                report_lines.append(f"\n**Average improvement: {avg_imp:+.1f}%**\n")

    notes_path = RESULTS_DIR / "evaluation-notes.md"
    if notes_path.exists():
        report_lines.append("\n## Qualitative Notes\n")
        report_lines.append(notes_path.read_text())

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / "evaluation-report.md"
    report_path.write_text("\n".join(report_lines))
    print(f"Report saved to {report_path}")


if __name__ == "__main__":
    generate_report()
