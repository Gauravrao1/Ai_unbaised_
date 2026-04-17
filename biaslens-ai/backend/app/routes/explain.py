from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.schemas import ExplainRequest, ExplainResponse
from app.services.explanation import generate_explanation
from app.services.file_service import load_analysis_metadata
from app.services.bias_engine import analyze_dataframe
from app.services.file_service import load_dataframe

router = APIRouter(tags=["explain"])


@router.post("/explain", response_model=ExplainResponse)
def explain_bias(request: ExplainRequest):
    if request.bias_report is None:
        metadata = load_analysis_metadata(request.analysis_id)
        csv_path = metadata.get("csv_path")
        if not csv_path:
            raise HTTPException(status_code=404, detail="Analysis not found. Upload a dataset first.")
        frame = load_dataframe(csv_path)
        report = analyze_dataframe(
            frame,
            target_column=metadata.get("detected_target_column"),
            sensitive_column=None,
            model_path=metadata.get("model_path"),
        )
    else:
        report = request.bias_report

    explanation = generate_explanation(report)
    return ExplainResponse(
        analysis_id=request.analysis_id,
        title=explanation["title"],
        summary=explanation["summary"],
        action_items=explanation["action_items"],
        risk_level=explanation["risk_level"],
    )

