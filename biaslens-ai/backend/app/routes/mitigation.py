from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.schemas import BiasReport, MitigationRequest, MitigationResponse
from app.services.bias_engine import analyze_dataframe, build_bias_report
from app.services.file_service import load_analysis_metadata, load_dataframe, preview_dataframe
from app.services.mitigation import build_mitigation_suggestions, compare_before_after, train_weighted_model

router = APIRouter(tags=["mitigation"])


@router.post("/mitigate", response_model=MitigationResponse)
def mitigate_bias(request: MitigationRequest):
    metadata = load_analysis_metadata(request.analysis_id)
    csv_path = metadata.get("csv_path")
    if not csv_path:
        raise HTTPException(status_code=404, detail="Analysis not found. Upload a dataset first.")

    frame = load_dataframe(csv_path)
    before_analysis = analyze_dataframe(
        frame,
        target_column=request.target_column or metadata.get("detected_target_column"),
        sensitive_column=request.sensitive_column,
        model_path=metadata.get("model_path"),
    )
    before_report = BiasReport(
        analysis_id=request.analysis_id,
        target_column=before_analysis["target_column"],
        sensitive_column=before_analysis["sensitive_column"],
        privileged_group=before_analysis["privileged_group"],
        unprivileged_group=before_analysis["unprivileged_group"],
        fairness_score=before_analysis["fairness_score"],
        bias_risk_score=before_analysis["bias_risk_score"],
        metrics=before_analysis["metrics"],
        group_metrics=before_analysis["group_metrics"],
        model_accuracy=before_analysis["model_accuracy"],
        mitigation_suggestions=before_analysis["mitigation_suggestions"],
        key_findings=before_analysis["key_findings"],
        dataset_preview=preview_dataframe(frame),
        model_type=before_analysis["model_type"],
        source=before_analysis["source"],
    )

    target_column = request.target_column or metadata.get("detected_target_column")
    sensitive_column = request.sensitive_column or before_analysis["sensitive_column"]
    if target_column is None:
        raise HTTPException(status_code=400, detail="A binary target column is required for mitigation.")

    weighted_result = train_weighted_model(frame, target_column, sensitive_column)
    mitigated_analysis = build_bias_report(
        x_test_frame=weighted_result.x_test,
        y_true=weighted_result.y_test,
        y_pred=weighted_result.predictions,
        target_column=target_column,
        sensitive_column=sensitive_column,
        model_accuracy=weighted_result.accuracy,
        model_type=type(weighted_result.model.named_steps["classifier"]).__name__,
        source="reweighed-logistic-regression",
    )

    after_report = BiasReport(
        analysis_id=request.analysis_id,
        target_column=mitigated_analysis["target_column"],
        sensitive_column=mitigated_analysis["sensitive_column"],
        privileged_group=mitigated_analysis["privileged_group"],
        unprivileged_group=mitigated_analysis["unprivileged_group"],
        fairness_score=mitigated_analysis["fairness_score"],
        bias_risk_score=mitigated_analysis["bias_risk_score"],
        metrics=mitigated_analysis["metrics"],
        group_metrics=mitigated_analysis["group_metrics"],
        model_accuracy=mitigated_analysis["model_accuracy"],
        mitigation_suggestions=build_mitigation_suggestions(mitigated_analysis),
        key_findings=mitigated_analysis["key_findings"],
        dataset_preview=preview_dataframe(frame),
        model_type=mitigated_analysis["model_type"],
        source=mitigated_analysis["source"],
    )

    delta = compare_before_after(before_report.dict(), after_report.dict())
    return MitigationResponse(
        analysis_id=request.analysis_id,
        strategy=request.strategy,
        before=before_report,
        after=after_report,
        delta=delta,
        recommendations=weighted_result.recommendation_notes,
    )

