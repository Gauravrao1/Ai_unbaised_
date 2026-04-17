from __future__ import annotations

from typing import Any, Dict, List

from app.core.config import get_settings


RISK_LEVELS = [
    (80, "high"),
    (50, "medium"),
    (0, "low"),
]


def _fallback_summary(report: Dict[str, Any]) -> str:
    privileged = report.get("privileged_group", "the advantaged group")
    unprivileged = report.get("unprivileged_group", "the affected group")
    dpd = float(report.get("metrics", {}).get("demographic_parity_difference", 0.0))
    eod = float(report.get("metrics", {}).get("equal_opportunity_difference", 0.0))
    risk = float(report.get("bias_risk_score", 0.0))

    return (
        f"{unprivileged} receives fewer positive predictions than {privileged}. "
        f"The demographic parity gap is {dpd:.2f} and the equal opportunity gap is {eod:.2f}. "
        f"Overall bias risk is {risk:.0f}/100, which means this model should be mitigated before production."
    )


def _fallback_actions(report: Dict[str, Any]) -> List[str]:
    suggestions = report.get("mitigation_suggestions") or []
    if suggestions:
        return list(suggestions)[:4]
    return [
        "Reweigh the training set so underrepresented groups contribute more fairly.",
        "Adjust classification thresholds to narrow the selection gap.",
        "Track fairness metrics after every retrain.",
    ]


def generate_explanation(report: Dict[str, Any]) -> Dict[str, Any]:
    settings = get_settings()
    summary = _fallback_summary(report)
    actions = _fallback_actions(report)
    title = "Fairness review"
    risk_level = "medium"

    for threshold, label in RISK_LEVELS:
        if float(report.get("bias_risk_score", 0.0)) >= threshold:
            risk_level = label
            break

    api_key = settings.gemini_api_key.strip()
    if api_key:
        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(settings.gemini_model_name)
            prompt = f"""
You are BiasLens AI, a fairness analyst for non-technical stakeholders.
Rewrite the following fairness report in simple, concise language.
Keep the output focused on what happened, why it matters, and what to do next.
Use the Indian context if helpful, but stay factual.

Report JSON:
{report}
"""
            response = model.generate_content(prompt)
            if getattr(response, "text", None):
                summary = response.text.strip()
                title = "AI fairness explanation"
        except Exception:
            pass

    return {
        "title": title,
        "summary": summary,
        "action_items": actions,
        "risk_level": risk_level,
    }

