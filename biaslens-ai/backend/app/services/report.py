from __future__ import annotations

from typing import Any, Dict


def build_downloadable_report(analysis: Dict[str, Any], explanation: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "product": "BiasLens AI",
        "summary": {
            "fairness_score": analysis.get("fairness_score"),
            "bias_risk_score": analysis.get("bias_risk_score"),
            "model_accuracy": analysis.get("model_accuracy"),
            "privileged_group": analysis.get("privileged_group"),
            "unprivileged_group": analysis.get("unprivileged_group"),
        },
        "analysis": analysis,
        "explanation": explanation,
    }

