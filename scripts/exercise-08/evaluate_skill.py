#!/usr/bin/env python3
"""
Skill Effectiveness Evaluator for Exercise 08.

Runs your SAST skill against a known-vulnerable codebase WITH and WITHOUT
the skill loaded, then uses an LLM judge to score both outputs on defined
criteria. Produces a side-by-side benchmark showing whether the skill
actually improves results.

Uses your existing AWS Bedrock session — no Claude Code or API keys needed.

Usage:
    python evaluate_skill.py
    python evaluate_skill.py --skill-only     # skip baseline, just evaluate the skill
    python evaluate_skill.py --model <id>     # override the model (default: sonnet)
"""

import argparse
import json
import os
import sys
import time

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from dotenv import load_dotenv
from fetch_url_tool import FetchURLTool
from langchain_aws import ChatBedrockConverse

load_dotenv()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_PATH = os.path.join(SCRIPT_DIR, "repo")
SKILLS_DIR = os.path.join(SCRIPT_DIR, "skills")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "skill-eval-results")

DEFAULT_MODEL = "us.anthropic.claude-sonnet-4-6-v1:0"

# ─────────────────────────────────────────────────────────────────────────────
# Eval cases — each targets a specific capability the skill should improve
# ─────────────────────────────────────────────────────────────────────────────
EVAL_CASES = [
    {
        "id": "idor",
        "name": "IDOR / Missing Ownership Checks",
        "prompt": (
            "Analyze the Django views in ./taskManager/views.py for Insecure "
            "Direct Object Reference vulnerabilities. Identify views that fetch "
            "objects by user-supplied ID without verifying the requesting user "
            "owns or has access to that object."
        ),
        "criteria": [
            "Identifies specific IDOR-vulnerable views by name and file location",
            "Explains the ownership gap (what check is missing)",
            "Provides a realistic attacker exploit scenario",
            "Recommends a specific fix (e.g., filter queryset by request.user)",
            "Distinguishes between views that already have protections vs those that don't",
        ],
    },
    {
        "id": "missing_auth",
        "name": "Missing Authentication",
        "prompt": (
            "Review the Django application in ./taskManager/ for views that "
            "should require authentication but don't. Check for missing "
            "@login_required decorators or LoginRequiredMixin."
        ),
        "criteria": [
            "Lists specific views/endpoints missing authentication",
            "Correctly identifies which views are intentionally public (login, register)",
            "Notes whether there is global auth middleware or per-view enforcement",
            "Cites file paths and function/class names",
            "Assesses severity based on what the unprotected view exposes",
        ],
    },
    {
        "id": "parameter_tampering",
        "name": "Parameter Tampering / Client Trust",
        "prompt": (
            "Look for parameter tampering vulnerabilities in ./taskManager/. "
            "Find places where the application trusts client-supplied input to "
            "determine resource ownership or make access control decisions "
            "instead of using the server-side session."
        ),
        "criteria": [
            "Finds at least one instance where client input controls ownership assignment",
            "Explains why trusting POST/GET data for user identity is dangerous",
            "Recommends using request.user or session-derived identity",
            "Identifies the specific form fields or parameters being trusted",
            "Demonstrates understanding of the difference between authn and authz",
        ],
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# LLM Judge prompt — this is what scores the outputs
# ─────────────────────────────────────────────────────────────────────────────
JUDGE_SYSTEM_PROMPT = """You are an expert security engineering evaluator.
You will be given the output of a SAST analysis agent and a list of evaluation
criteria. Score each criterion on whether the output satisfies it.

For each criterion, respond with:
- "pass" if the output clearly satisfies it
- "partial" if it partially addresses it but is incomplete or vague
- "fail" if the output does not address it at all

Be strict but fair. Cite specific evidence from the output for each judgment."""

JUDGE_USER_TEMPLATE = """## Evaluation Criteria
{criteria}

## Agent Output to Evaluate
```
{output}
```

## Instructions
Score each criterion. Respond in this exact JSON format:
```json
{{
  "scores": [
    {{
      "criterion": "the criterion text",
      "verdict": "pass | partial | fail",
      "evidence": "brief quote or explanation from the output"
    }}
  ],
  "overall_quality": "A 1-2 sentence qualitative assessment of the output"
}}
```"""


# ─────────────────────────────────────────────────────────────────────────────
# Core functions
# ─────────────────────────────────────────────────────────────────────────────
def create_analysis_agent(model_id: str, use_skills: bool):
    """Create a DeepAgent configured for SAST analysis."""
    llm = ChatBedrockConverse(model_id=model_id, temperature=0.2)
    backend = FilesystemBackend(root_dir=REPO_PATH, virtual_mode=False)

    system_prompt = (
        "You are a security engineer analyzing a Python/Django codebase for "
        "access control vulnerabilities. Be specific — cite file paths, function "
        "names, and line numbers. Explain how each issue could be exploited."
    )

    return create_deep_agent(
        model=llm,
        tools=[FetchURLTool()],
        backend=backend,
        system_prompt=system_prompt,
        skills=[SKILLS_DIR] if use_skills else [],
        debug=False,
    )


def run_agent(agent, prompt: str) -> dict:
    """Run agent on a prompt, return output and metadata."""
    start = time.time()
    final_output = ""
    tool_calls = []

    try:
        for event in agent.stream(
            {"messages": [{"role": "user", "content": prompt}]}
        ):
            for key, value in event.items():
                if "Middleware" in key:
                    continue
                if isinstance(value, dict) and "messages" in value:
                    for msg in value["messages"]:
                        if hasattr(msg, "tool_calls") and msg.tool_calls:
                            for tc in msg.tool_calls:
                                tool_calls.append(tc["name"])
                        elif hasattr(msg, "content") and msg.content:
                            final_output = msg.content
    except Exception as e:
        final_output = final_output or f"[ERROR] {type(e).__name__}: {str(e)[:500]}"

    return {
        "output": final_output,
        "duration_seconds": round(time.time() - start, 1),
        "tool_calls": tool_calls,
    }


def judge_output(model_id: str, output: str, criteria: list[str]) -> dict:
    """Use an LLM to evaluate agent output against criteria."""
    llm = ChatBedrockConverse(model_id=model_id, temperature=0.0)

    criteria_text = "\n".join(f"{i+1}. {c}" for i, c in enumerate(criteria))
    user_msg = JUDGE_USER_TEMPLATE.format(criteria=criteria_text, output=output)

    response = llm.invoke([
        {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
        {"role": "user", "content": user_msg},
    ])

    content = response.content if hasattr(response, "content") else str(response)

    # Extract JSON from response
    try:
        json_start = content.index("{")
        json_end = content.rindex("}") + 1
        return json.loads(content[json_start:json_end])
    except (ValueError, json.JSONDecodeError):
        return {
            "scores": [{"criterion": c, "verdict": "error", "evidence": "Judge failed to produce valid JSON"} for c in criteria],
            "overall_quality": "Evaluation error — could not parse judge response",
            "_raw_response": content,
        }


def score_to_points(verdict: str) -> float:
    return {"pass": 1.0, "partial": 0.5, "fail": 0.0}.get(verdict, 0.0)


def print_header(text: str, char: str = "="):
    width = 70
    print(f"\n{char * width}")
    print(f"  {text}")
    print(f"{char * width}")


def print_grades(grades: dict, label: str):
    """Print grading results for one run."""
    scores = grades.get("scores", [])
    total = sum(score_to_points(s["verdict"]) for s in scores)
    max_score = len(scores)

    print(f"\n  [{label}] Score: {total}/{max_score} ({total/max_score*100:.0f}%)")
    for s in scores:
        icon = {"pass": "+", "partial": "~", "fail": "-"}.get(s["verdict"], "?")
        print(f"    [{icon}] {s['verdict'].upper():7s} | {s['criterion']}")
        if s.get("evidence"):
            evidence = s["evidence"][:100]
            print(f"              → {evidence}")

    quality = grades.get("overall_quality", "")
    if quality:
        print(f"\n    Quality: {quality}")


# ─────────────────────────────────────────────────────────────────────────────
# Main evaluation loop
# ─────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Evaluate skill effectiveness")
    parser.add_argument("--skill-only", action="store_true", help="Skip baseline run")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Bedrock model ID")
    parser.add_argument("--eval", type=str, help="Run a single eval by ID (e.g., idor)")
    args = parser.parse_args()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print_header("SKILL EFFECTIVENESS EVALUATOR")
    print(f"  Skill:    broken-access-control")
    print(f"  Model:    {args.model}")
    print(f"  Target:   {REPO_PATH}")
    print(f"  Baseline: {'skipped' if args.skill_only else 'enabled'}")

    cases = EVAL_CASES
    if args.eval:
        cases = [c for c in EVAL_CASES if c["id"] == args.eval]
        if not cases:
            print(f"\n  ERROR: No eval with id '{args.eval}'. Available: {[c['id'] for c in EVAL_CASES]}")
            sys.exit(1)

    results = []

    for case in cases:
        print_header(f"EVAL: {case['name']}", char="─")
        print(f"  Prompt: {case['prompt'][:80]}...")

        # --- Run WITH skill ---
        print(f"\n  Running WITH skill...")
        agent_with = create_analysis_agent(args.model, use_skills=True)
        run_with = run_agent(agent_with, case["prompt"])
        print(f"  Done ({run_with['duration_seconds']}s, {len(run_with['tool_calls'])} tool calls)")

        # --- Run WITHOUT skill (baseline) ---
        run_without = None
        if not args.skill_only:
            print(f"\n  Running WITHOUT skill (baseline)...")
            agent_without = create_analysis_agent(args.model, use_skills=False)
            run_without = run_agent(agent_without, case["prompt"])
            print(f"  Done ({run_without['duration_seconds']}s, {len(run_without['tool_calls'])} tool calls)")

        # --- LLM Judge ---
        print(f"\n  Judging outputs...")
        grades_with = judge_output(args.model, run_with["output"], case["criteria"])
        print_grades(grades_with, "WITH SKILL")

        grades_without = None
        if run_without:
            grades_without = judge_output(args.model, run_without["output"], case["criteria"])
            print_grades(grades_without, "BASELINE")

        # --- Save results ---
        eval_dir = os.path.join(OUTPUT_DIR, case["id"])
        os.makedirs(eval_dir, exist_ok=True)

        with open(os.path.join(eval_dir, "with_skill_output.txt"), "w") as f:
            f.write(run_with["output"])
        with open(os.path.join(eval_dir, "with_skill_grades.json"), "w") as f:
            json.dump(grades_with, f, indent=2)

        if run_without:
            with open(os.path.join(eval_dir, "baseline_output.txt"), "w") as f:
                f.write(run_without["output"])
            with open(os.path.join(eval_dir, "baseline_grades.json"), "w") as f:
                json.dump(grades_without, f, indent=2)

        results.append({
            "eval_id": case["id"],
            "eval_name": case["name"],
            "with_skill": {
                "score": sum(score_to_points(s["verdict"]) for s in grades_with.get("scores", [])),
                "max": len(case["criteria"]),
                "duration": run_with["duration_seconds"],
            },
            "baseline": {
                "score": sum(score_to_points(s["verdict"]) for s in grades_without.get("scores", [])) if grades_without else None,
                "max": len(case["criteria"]),
                "duration": run_without["duration_seconds"] if run_without else None,
            } if not args.skill_only else None,
        })

    # ─────────────────────────────────────────────────────────────────────────
    # Summary
    # ─────────────────────────────────────────────────────────────────────────
    print_header("BENCHMARK SUMMARY")

    total_with = sum(r["with_skill"]["score"] for r in results)
    total_max = sum(r["with_skill"]["max"] for r in results)
    avg_time_with = sum(r["with_skill"]["duration"] for r in results) / len(results)

    print(f"\n  WITH SKILL:    {total_with}/{total_max} ({total_with/total_max*100:.0f}%)")
    print(f"  Avg duration:  {avg_time_with:.1f}s")

    if not args.skill_only:
        total_without = sum(r["baseline"]["score"] for r in results if r["baseline"])
        avg_time_without = sum(r["baseline"]["duration"] for r in results if r["baseline"]) / len(results)
        delta = total_with - total_without

        print(f"\n  BASELINE:      {total_without}/{total_max} ({total_without/total_max*100:.0f}%)")
        print(f"  Avg duration:  {avg_time_without:.1f}s")
        print(f"\n  DELTA:         {'+' if delta >= 0 else ''}{delta} points")
        print(f"  Time overhead: {avg_time_with - avg_time_without:+.1f}s")

        if delta > 0:
            print(f"\n  VERDICT: Skill IMPROVES results (+{delta/total_max*100:.0f}% effectiveness)")
        elif delta == 0:
            print(f"\n  VERDICT: Skill has NO MEASURABLE EFFECT on these evals")
        else:
            print(f"\n  VERDICT: Skill DEGRADES results ({delta/total_max*100:.0f}% worse)")

    # Save benchmark
    benchmark = {
        "skill": "broken-access-control",
        "model": args.model,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "results": results,
        "summary": {
            "with_skill_pct": total_with / total_max * 100,
            "baseline_pct": (total_without / total_max * 100) if not args.skill_only else None,
        },
    }
    benchmark_path = os.path.join(OUTPUT_DIR, "benchmark.json")
    with open(benchmark_path, "w") as f:
        json.dump(benchmark, f, indent=2)

    print(f"\n  Results saved to: {OUTPUT_DIR}/")
    print()


if __name__ == "__main__":
    main()
