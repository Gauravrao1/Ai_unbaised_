from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.schemas import BiasAnalyzeRequest, BiasReport
from app.services.bias_engine import analyze_dataframe
from app.services.file_service import load_analysis_metadata, load_dataframe, preview_dataframe

router = APIRouter(tags=["bias"])


@router.post("/analyze-bias", response_model=BiasReport)
def analyze_bias(request: BiasAnalyzeRequest):
    metadata = load_analysis_metadata(request.analysis_id)
    csv_path = metadata.get("csv_path")
    model_path = metadata.get("model_path")
    if not csv_path:
        raise HTTPException(status_code=404, detail="Analysis not found. Upload a dataset first.")

    frame = load_dataframe(csv_path)
    analysis = analyze_dataframe(
        frame,
        target_column=request.target_column or metadata.get("detected_target_column"),
        sensitive_column=request.sensitive_column,
        model_path=model_path,
    )

    return BiasReport(
        analysis_id=request.analysis_id,
        target_column=analysis["target_column"],
        sensitive_column=analysis["sensitive_column"],
        privileged_group=analysis["privileged_group"],
        unprivileged_group=analysis["unprivileged_group"],
        fairness_score=analysis["fairness_score"],
        bias_risk_score=analysis["bias_risk_score"],
        metrics=analysis["metrics"],
        group_metrics=analysis["group_metrics"],
        model_accuracy=analysis["model_accuracy"],
        mitigation_suggestions=analysis["mitigation_suggestions"],
        key_findings=analysis["key_findings"],
        dataset_preview=preview_dataframe(frame),
        model_type=analysis["model_type"],
        source=analysis["source"],
    )

