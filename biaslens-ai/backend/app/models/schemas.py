from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    analysis_id: str
    filename: str
    model_filename: Optional[str] = None
    rows: int
    columns: List[str]
    detected_sensitive_columns: List[str]
    detected_target_column: Optional[str] = None
    preview: List[Dict[str, Any]]


class BiasAnalyzeRequest(BaseModel):
    analysis_id: str
    target_column: Optional[str] = None
    sensitive_column: Optional[str] = None


class MitigationRequest(BaseModel):
    analysis_id: str
    target_column: Optional[str] = None
    sensitive_column: Optional[str] = None
    strategy: str = Field(default="reweighing")


class ExplainRequest(BaseModel):
    analysis_id: str
    bias_report: Optional[Dict[str, Any]] = None


class BiasGroupMetrics(BaseModel):
    selection_rate: float
    true_positive_rate: float
    support: int


class BiasReport(BaseModel):
    analysis_id: str
    target_column: str
    sensitive_column: str
    privileged_group: str
    unprivileged_group: str
    fairness_score: float
    bias_risk_score: float
    metrics: Dict[str, float]
    group_metrics: Dict[str, BiasGroupMetrics]
    model_accuracy: float
    mitigation_suggestions: List[str]
    key_findings: List[str]
    dataset_preview: List[Dict[str, Any]]
    model_type: str
    source: str


class MitigationResponse(BaseModel):
    analysis_id: str
    strategy: str
    before: BiasReport
    after: BiasReport
    delta: Dict[str, float]
    recommendations: List[str]


class ExplainResponse(BaseModel):
    analysis_id: str
    title: str
    summary: str
    action_items: List[str]
    risk_level: str

