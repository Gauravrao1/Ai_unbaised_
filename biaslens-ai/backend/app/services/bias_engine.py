from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

try:
    from fairlearn.metrics import (
        MetricFrame,
        demographic_parity_difference,
        equal_opportunity_difference,
        selection_rate,
        true_positive_rate,
    )
except Exception as exc:  # pragma: no cover
    raise RuntimeError("fairlearn is required for BiasLens AI") from exc

try:
    from aif360.sklearn.metrics import statistical_parity_difference as aif360_statistical_parity_difference
except Exception:  # pragma: no cover
    aif360_statistical_parity_difference = None


SENSITIVE_PATTERNS = [
    "gender",
    "sex",
    "female",
    "male",
    "caste",
    "category",
    "age",
    "income",
    "race",
    "ethnicity",
    "religion",
    "disability",
    "tribe",
    "community",
    "sc",
    "st",
    "obc",
    "minority",
]

TARGET_PATTERNS = [
    "target",
    "label",
    "selected",
    "selection",
    "approved",
    "decision",
    "outcome",
    "hired",
    "hire",
    "loan_approved",
    "result",
]


@dataclass
class ModelBundle:
    model: Pipeline
    accuracy: float
    predictions: np.ndarray
    feature_columns: List[str]
    model_type: str


def _safe_string(value: Any) -> str:
    return str(value).strip().lower()


def detect_sensitive_columns(frame: pd.DataFrame) -> List[str]:
    candidates: List[str] = []
    for column in frame.columns:
        lowered = _safe_string(column)
        if any(pattern in lowered for pattern in SENSITIVE_PATTERNS):
            candidates.append(column)
            continue
        series = frame[column].dropna()
        if series.empty:
            continue
        unique_values = {str(item).strip().lower() for item in series.unique()[:20]}
        if {"male", "female"}.issubset(unique_values) or {"m", "f"}.issubset(unique_values):
            candidates.append(column)
            continue
        caste_tokens = {"general", "obc", "sc", "st", "ews"}
        if len(unique_values) <= 10 and len(unique_values.intersection(caste_tokens)) >= 2:
            candidates.append(column)
    return list(dict.fromkeys(candidates))


def detect_target_column(frame: pd.DataFrame) -> Optional[str]:
    for column in frame.columns:
        lowered = _safe_string(column)
        if any(pattern in lowered for pattern in TARGET_PATTERNS):
            return column

    for column in frame.columns:
        if frame[column].nunique(dropna=True) == 2:
            return column

    return None


def encode_target_series(series: pd.Series) -> pd.Series:
    if series.dtype.kind in {"i", "u", "f"}:
        return pd.Series((series > series.median()).astype(int), index=series.index)

    normalized = series.astype(str).str.strip().str.lower()
    positive_tokens = {"1", "true", "yes", "selected", "approved", "hire", "hired", "pass", "qualified"}
    encoded = normalized.isin(positive_tokens).astype(int)
    if encoded.nunique() == 1 and series.nunique(dropna=True) == 2:
        mapping = {value: index for index, value in enumerate(normalized.unique())}
        return normalized.map(mapping).astype(int)
    return encoded


def _build_preprocessor(frame: pd.DataFrame) -> ColumnTransformer:
    numeric_features = frame.select_dtypes(include=[np.number, "bool"]).columns.tolist()
    categorical_features = [column for column in frame.columns if column not in numeric_features]

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_features),
            ("categorical", categorical_pipeline, categorical_features),
        ],
        remainder="drop",
    )


def _train_baseline_model(frame: pd.DataFrame, target_column: str) -> Tuple[Pipeline, float, np.ndarray, pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    features = frame.drop(columns=[target_column])
    target = encode_target_series(frame[target_column])

    x_train, x_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=0.25,
        random_state=42,
        stratify=target if target.nunique() > 1 else None,
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", _build_preprocessor(x_train)),
            ("classifier", LogisticRegression(max_iter=1000)),
        ]
    )
    pipeline.fit(x_train, y_train)
    predictions = pipeline.predict(x_test)
    accuracy = accuracy_score(y_test, predictions)
    return pipeline, accuracy, predictions, x_test, y_test, x_train, y_train


def _try_model_prediction(frame: pd.DataFrame, target_column: str, model_path: Optional[str]) -> Optional[ModelBundle]:
    if not model_path:
        return None

    try:
        import joblib

        model = joblib.load(model_path)
        features = frame.drop(columns=[target_column])
        target = encode_target_series(frame[target_column])
        x_train, x_test, y_train, y_test = train_test_split(
            features,
            target,
            test_size=0.25,
            random_state=42,
            stratify=target if target.nunique() > 1 else None,
        )
        predictions = model.predict(x_test)
        accuracy = accuracy_score(y_test, predictions)
        return ModelBundle(
            model=model,
            accuracy=accuracy,
            predictions=predictions,
            feature_columns=list(features.columns),
            model_type=type(model).__name__,
        )
    except Exception:
        return None


def _metric_dict(y_true: pd.Series, y_pred: np.ndarray, sensitive_values: pd.Series) -> Dict[str, float]:
    try:
        dpd = float(demographic_parity_difference(y_true, y_pred, sensitive_features=sensitive_values))
    except Exception:
        dpd = 0.0
    try:
        eod = float(equal_opportunity_difference(y_true, y_pred, sensitive_features=sensitive_values))
    except Exception:
        eod = 0.0
    try:
        group_selection_rates = MetricFrame(
            metrics={"selection_rate": selection_rate},
            y_true=y_true,
            y_pred=y_pred,
            sensitive_features=sensitive_values,
        ).by_group["selection_rate"]
        max_rate = float(group_selection_rates.max())
        min_rate = float(group_selection_rates.min())
        di = round((min_rate / max_rate), 4) if max_rate else 1.0
    except Exception:
        di = 1.0

    if aif360_statistical_parity_difference is not None:
        try:
            statistical_parity = float(aif360_statistical_parity_difference(y_true, y_pred, sensitive_features=sensitive_values))
        except Exception:
            statistical_parity = dpd
    else:
        statistical_parity = dpd

    return {
        "demographic_parity_difference": round(dpd, 4),
        "equal_opportunity_difference": round(eod, 4),
        "disparate_impact": round(di, 4),
        "statistical_parity_difference": round(statistical_parity, 4),
    }


def _risk_score(metrics: Dict[str, float]) -> Tuple[float, float]:
    dpd = abs(metrics.get("demographic_parity_difference", 0.0))
    eod = abs(metrics.get("equal_opportunity_difference", 0.0))
    spd = abs(metrics.get("statistical_parity_difference", 0.0))
    di = metrics.get("disparate_impact", 1.0)

    normalized_gap = min(1.0, dpd / 0.25) * 0.35 + min(1.0, eod / 0.25) * 0.3 + min(1.0, spd / 0.25) * 0.15 + min(1.0, abs(1 - di) / 0.5) * 0.2
    bias_risk_score = round(min(100.0, normalized_gap * 100), 2)
    fairness_score = round(max(0.0, 100.0 - bias_risk_score), 2)
    return fairness_score, bias_risk_score


def _group_metrics(y_true: pd.Series, y_pred: np.ndarray, sensitive_values: pd.Series) -> Dict[str, Dict[str, float]]:
    frame = MetricFrame(
        metrics={
            "selection_rate": selection_rate,
            "true_positive_rate": true_positive_rate,
        },
        y_true=y_true,
        y_pred=y_pred,
        sensitive_features=sensitive_values,
    )

    group_support = sensitive_values.astype(str).value_counts().to_dict()
    grouped = {}
    for group, values in frame.by_group.iterrows():
        group_name = str(group)
        grouped[group_name] = {
            "selection_rate": round(float(values["selection_rate"]), 4),
            "true_positive_rate": round(float(values["true_positive_rate"]), 4),
            "support": int(group_support.get(group_name, 0)),
        }
    return grouped


def _pick_groups(group_metrics: Dict[str, Dict[str, float]]) -> Tuple[str, str]:
    ranked = sorted(group_metrics.items(), key=lambda item: item[1]["selection_rate"])
    unprivileged_group = ranked[0][0]
    privileged_group = ranked[-1][0]
    return privileged_group, unprivileged_group


def _suggestions(metrics: Dict[str, float], sensitive_column: str) -> List[str]:
    suggestions = [
        f"Reweigh samples for {sensitive_column} before retraining.",
        "Compare group-specific thresholds instead of one global cutoff.",
        "Apply fairness constraints such as equal opportunity or demographic parity.",
        "Check whether the training data underrepresents one protected group.",
    ]
    if metrics.get("disparate_impact", 1.0) < 0.8:
        suggestions.insert(0, "The disparate impact ratio is below the 0.8 rule of thumb, so mitigation is recommended immediately.")
    return suggestions


def _find_key_findings(metrics: Dict[str, float], privileged_group: str, unprivileged_group: str) -> List[str]:
    dpd = metrics.get("demographic_parity_difference", 0.0)
    eod = metrics.get("equal_opportunity_difference", 0.0)
    di = metrics.get("disparate_impact", 1.0)
    return [
        f"{unprivileged_group} is treated worse than {privileged_group} on selection rate by {abs(dpd):.2f}.",
        f"Equal opportunity gap is {abs(eod):.2f}, which signals unequal true positive rates.",
        f"Disparate impact is {di:.2f}; values under 0.80 are usually a fairness red flag.",
    ]


def build_bias_report(
    x_test_frame: pd.DataFrame,
    y_true: pd.Series,
    y_pred: np.ndarray,
    target_column: str,
    sensitive_column: str,
    model_accuracy: float,
    model_type: str,
    source: str,
) -> Dict[str, Any]:
    sensitive_values = x_test_frame[sensitive_column].astype(str).fillna("Unknown")
    metrics = _metric_dict(y_true, y_pred, sensitive_values)
    fairness_score, bias_risk_score = _risk_score(metrics)
    group_metrics = _group_metrics(y_true, y_pred, sensitive_values)
    privileged_group, unprivileged_group = _pick_groups(group_metrics)

    return {
        "target_column": target_column,
        "sensitive_column": sensitive_column,
        "privileged_group": privileged_group,
        "unprivileged_group": unprivileged_group,
        "fairness_score": fairness_score,
        "bias_risk_score": bias_risk_score,
        "metrics": metrics,
        "group_metrics": group_metrics,
        "model_accuracy": round(float(model_accuracy), 4),
        "mitigation_suggestions": _suggestions(metrics, sensitive_column),
        "key_findings": _find_key_findings(metrics, privileged_group, unprivileged_group),
        "model_type": model_type,
        "source": source,
    }


def analyze_dataframe(
    frame: pd.DataFrame,
    target_column: Optional[str] = None,
    sensitive_column: Optional[str] = None,
    model_path: Optional[str] = None,
) -> Dict[str, Any]:
    detected_target = target_column or detect_target_column(frame)
    if detected_target is None:
        raise ValueError("Unable to detect a binary target column.")

    detected_sensitive_candidates = detect_sensitive_columns(frame)
    detected_sensitive = sensitive_column or (detected_sensitive_candidates[0] if detected_sensitive_candidates else None)
    if detected_sensitive is None:
        raise ValueError("Unable to detect a sensitive column.")

    model_bundle = _try_model_prediction(frame, detected_target, model_path)
    if model_bundle is None:
        model, accuracy, predictions, x_test, y_test, _, _ = _train_baseline_model(frame, detected_target)
        model_type = type(model.named_steps["classifier"]).__name__
        x_test_frame = x_test
        y_test_series = y_test
    else:
        model = model_bundle.model
        accuracy = model_bundle.accuracy
        predictions = model_bundle.predictions
        model_type = model_bundle.model_type
        features = frame.drop(columns=[detected_target])
        target_series = encode_target_series(frame[detected_target])
        _, x_test_frame, _, y_test_series = train_test_split(
            features,
            target_series,
            test_size=0.25,
            random_state=42,
            stratify=target_series if target_series.nunique() > 1 else None,
        )

    return build_bias_report(
        x_test_frame=x_test_frame,
        y_true=y_test_series,
        y_pred=predictions,
        target_column=detected_target,
        sensitive_column=detected_sensitive,
        model_accuracy=accuracy,
        model_type=model_type,
        source="uploaded-model" if model_bundle else "baseline-logistic-regression",
    )


def describe_sensitive_columns(frame: pd.DataFrame) -> List[Dict[str, Any]]:
    candidates = []
    for column in detect_sensitive_columns(frame):
        unique_count = int(frame[column].nunique(dropna=True))
        examples = [str(value) for value in frame[column].dropna().unique()[:5]]
        candidates.append({"column": column, "unique_values": unique_count, "examples": examples})
    return candidates

