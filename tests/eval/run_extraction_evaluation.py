#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import matplotlib.pyplot as plt


@dataclass
class Sample:
    tool: str
    chat_history: List[Dict[str, str]]
    current_message: str
    user_info: Dict[str, Any]
    ground_truth: Dict[str, Any]


def infer_tool_from_intent(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ["flashcard", "practice", "quiz", "question"]):
        return "flashcard_generator"
    if any(k in t for k in ["note", "outline", "summarize", "notes"]):
        return "note_maker"
    if any(k in t for k in ["explain", "why", "how"]):
        return "concept_explainer"
    return "concept_explainer"


def simulate_llm_parameters(tool: str, chat_history: List[Dict[str, str]], current_message: str, user_info: Dict[str, Any]) -> Dict[str, Any]:
    """Simulate parameter extraction using simple heuristics.
    Returns a flat param dict (already flattened from the JSON wrapper).
    """
    msg = current_message.strip()
    params: Dict[str, Any] = {}

    # Language default
    lang = user_info.get("preferred_language") or "en"

    if tool == "note_maker":
        source_text = msg if len(msg) >= 20 else (" ".join([msg] * 5))[:120]
        params.update({
            "source_text": source_text,
            "note_style": "outline" if "outline" in msg.lower() else "bullet",
            "target_length": "medium",
            "language": lang,
        })
    elif tool == "flashcard_generator":
        source_text = msg if len(msg) >= 20 else (" ".join([msg] * 5))[:150]
        diff = "easy"
        ml = (user_info.get("emotional_state") or "").lower()
        if any(k in msg.lower() for k in ["struggling", "stuck", "confused"]) or ml in ("confused",):
            diff = "easy"
        elif any(k in msg.lower() for k in ["challenge", "harder", "advanced", "tough"]):
            diff = "hard"
        elif "medium" in msg.lower():
            diff = "medium"
        params.update({
            "source_text": source_text,
            "card_style": "qa",
            "num_cards": 5,
            "difficulty": diff,
            "language": lang,
        })
    else:  # concept_explainer
        concept = msg
        # simple concept extraction: take first 4 words
        if "." in concept:
            concept = concept.split(".")[0]
        concept = concept.replace("Explain", "").replace("explain", "").strip()
        concept = concept.split(" at ")[0].strip()
        prior = "intermediate" if "intermediate" in msg.lower() else "basic"
        examples = 2 if "2" in msg or "two" in msg.lower() else 2
        params.update({
            "concept": concept if concept else msg,
            "prior_knowledge": prior,
            "explanation_style": "step_by_step",
            "examples_count": examples,
            "misconceptions": True,
            "include_quiz": ("question" in msg.lower() or "quiz" in msg.lower()),
            "language": lang,
        })

    return params


def load_dataset(path: str) -> List[Sample]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    samples: List[Sample] = []
    for i, item in enumerate(data):
        tool = item.get("tool") or infer_tool_from_intent(item.get("current_message", ""))
        samples.append(
            Sample(
                tool=tool,
                chat_history=item.get("chat_history", []),
                current_message=item.get("current_message", ""),
                user_info=item.get("user_info", {}),
                ground_truth=item.get("ground_truth", {}),
            )
        )
    return samples


def evaluate(samples: List[Sample]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Compute per-field precision/recall/accuracy.

    For each field with ground truth, we count:
      - correct: predicted == ground_truth
      - incorrect: predicted present but != ground_truth
      - missing: ground_truth present but predicted missing

    precision = correct / (correct + incorrect) if predicted any else 0
    recall = correct / (correct + missing)
    accuracy = correct / support
    """
    per_field = defaultdict(lambda: {"correct": 0, "incorrect": 0, "missing": 0, "support": 0})
    confusion_examples: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    for idx, s in enumerate(samples):
        pred = simulate_llm_parameters(s.tool, s.chat_history, s.current_message, s.user_info)
        gt = s.ground_truth or {}
        for field, gt_val in gt.items():
            per_field[field]["support"] += 1
            if field not in pred:
                per_field[field]["missing"] += 1
                if len(confusion_examples[field]) < 10:
                    confusion_examples[field].append({
                        "idx": idx,
                        "tool": s.tool,
                        "pred": None,
                        "gt": gt_val,
                        "msg": s.current_message[:120],
                    })
                continue
            if pred[field] == gt_val:
                per_field[field]["correct"] += 1
            else:
                per_field[field]["incorrect"] += 1
                if len(confusion_examples[field]) < 10:
                    confusion_examples[field].append({
                        "idx": idx,
                        "tool": s.tool,
                        "pred": pred[field],
                        "gt": gt_val,
                        "msg": s.current_message[:120],
                    })

    # compute metrics
    metrics = {"per_field": {}, "overall": {}}
    total_support = 0
    total_correct = 0
    for field, stats in per_field.items():
        support = stats["support"]
        correct = stats["correct"]
        incorrect = stats["incorrect"]
        missing = stats["missing"]
        total_support += support
        total_correct += correct
        precision = correct / (correct + incorrect) if (correct + incorrect) > 0 else 0.0
        recall = correct / (correct + missing) if (correct + missing) > 0 else 0.0
        accuracy = correct / support if support > 0 else 0.0
        metrics["per_field"][field] = {
            "support": support,
            "correct": correct,
            "incorrect": incorrect,
            "missing": missing,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "accuracy": round(accuracy, 4),
        }

    overall_accuracy = total_correct / total_support if total_support > 0 else 0.0
    metrics["overall"] = {
        "total_support": total_support,
        "total_correct": total_correct,
        "accuracy": round(overall_accuracy, 4),
    }

    return metrics, confusion_examples


def save_report(metrics: Dict[str, Any], confusion: Dict[str, List[Dict[str, Any]]], outdir: str) -> None:
    os.makedirs(outdir, exist_ok=True)
    # Save JSON
    with open(os.path.join(outdir, "report.json"), "w", encoding="utf-8") as f:
        json.dump({"metrics": metrics, "confusion": confusion}, f, indent=2, ensure_ascii=False)

    # Charts
    fields = list(metrics["per_field"].keys())
    accs = [metrics["per_field"][k]["accuracy"] for k in fields]

    plt.figure(figsize=(10, 4))
    plt.bar(fields, accs, color="#4e79a7")
    plt.ylim(0, 1)
    plt.ylabel("Accuracy")
    plt.title("Per-field Accuracy")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    acc_path = os.path.join(outdir, "accuracy.png")
    plt.savefig(acc_path)
    plt.close()

    # HTML report
    html = [
        "<html><head><meta charset='utf-8'><title>Parameter Extraction Evaluation</title></head><body>",
        "<h1>Parameter Extraction Evaluation</h1>",
        f"<p><strong>Overall accuracy:</strong> {metrics['overall']['accuracy']}</p>",
        "<h2>Per-field Metrics</h2>",
        "<table border='1' cellspacing='0' cellpadding='6'><tr><th>Field</th><th>Support</th><th>Correct</th><th>Incorrect</th><th>Missing</th><th>Precision</th><th>Recall</th><th>Accuracy</th></tr>",
    ]
    for k, st in metrics["per_field"].items():
        html.append(
            f"<tr><td>{k}</td><td>{st['support']}</td><td>{st['correct']}</td><td>{st['incorrect']}</td><td>{st['missing']}</td><td>{st['precision']}</td><td>{st['recall']}</td><td>{st['accuracy']}</td></tr>"
        )
    html.append("</table>")

    html.append("<h2>Accuracy Chart</h2>")
    html.append("<img src='accuracy.png' alt='Per-field Accuracy' style='max-width: 800px;'>")

    html.append("<h2>Confusion Examples</h2>")
    for field, examples in confusion.items():
        if not examples:
            continue
        html.append(f"<h3>{field}</h3>")
        html.append("<ul>")
        for ex in examples:
            html.append(
                f"<li><pre>{json.dumps(ex, ensure_ascii=False)}</pre></li>"
            )
        html.append("</ul>")

    html.append("</body></html>")
    with open(os.path.join(outdir, "report.html"), "w", encoding="utf-8") as f:
        f.write("\n".join(html))


def main():
    ap = argparse.ArgumentParser(description="Evaluate parameter extraction vs ground truth")
    ap.add_argument("--data", required=True, help="Path to JSON or CSV dataset (JSON expected)")
    ap.add_argument("--outdir", default="results", help="Output directory for reports")
    args = ap.parse_args()

    samples = load_dataset(args.data)
    metrics, confusion = evaluate(samples)
    save_report(metrics, confusion, args.outdir)

    print(f"Saved results to {os.path.join(args.outdir, 'report.json')} and {os.path.join(args.outdir, 'report.html')}")


if __name__ == "__main__":
    main()
