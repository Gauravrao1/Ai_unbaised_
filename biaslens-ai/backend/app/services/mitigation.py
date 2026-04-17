from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from app.services.bias_engine import encode_target_series


@dataclass
class MitigationResult:
    model: Pipeline
    accuracy: float
    predictions: np.ndarray
    x_test: pd.DataFrame
    y_test: pd.Series
    sensitive_test: pd.Series
    recommendation_notes: List[str]


def build_preprocessor(frame: pd.DataFrame) -> ColumnTransformer:
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


def compute_reweighing_weights(frame: pd.DataFrame, target_column: str, sensitive_column: str) -> pd.Series:
    target = encode_target_series(frame[target_column])
    sensitive = frame[sensitive_column].astype(str).fillna("Unknown")

    joint = pd.crosstab(sensitive, target, normalize=True)
    sensitive_probs = sensitive.value_counts(normalize=True)
    target_probs = target.value_counts(normalize=True)

    weights = []
    for sensitive_value, target_value in zip(sensitive, target):
        joint_probability = joint.loc[sensitive_value, target_value] if target_value in joint.columns else 0.0
        if joint_probability == 0:
            weights.append(1.0)
            continue
        weights.append(float((sensitive_probs[sensitive_value] * target_probs[target_value]) / joint_probability))

    return pd.Series(weights, index=frame.index)


def train_weighted_model(
    frame: pd.DataFrame,
    target_column: str,
    sensitive_column: str,
) -> MitigationResult:
    features = frame.drop(columns=[target_column]).copy()
    target = encode_target_series(frame[target_column])
    x_train, x_test, y_train, y_test, frame_train, frame_test = train_test_split(
        features,
        target,
        frame[[sensitive_column]],
        test_size=0.25,
        random_state=42,
        stratify=target if target.nunique() > 1 else None,
    )

    preprocessor = build_preprocessor(x_train)
    classifier = LogisticRegression(max_iter=1000)
    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier),
        ]
    )

    sample_weights = compute_reweighing_weights(frame_train.join(y_train.rename(target_column)), target_column, sensitive_column)
    pipeline.fit(x_train, y_train, classifier__sample_weight=sample_weights)
    predictions = pipeline.predict(x_test)
    accuracy = accuracy_score(y_test, predictions)

    return MitigationResult(
        model=pipeline,
        accuracy=accuracy,
        predictions=predictions,
        x_test=x_test,
        y_test=y_test,
        sensitive_test=frame_test[sensitive_column].astype(str).fillna("Unknown"),
        recommendation_notes=[
            "Reweighing reduced the influence of imbalanced protected groups during training.",
            "Next step: tune decision thresholds for the most affected group.",
        ],
    )


def compare_before_after(
    original_report: Dict[str, object],
    mitigated_report: Dict[str, object],
) -> Dict[str, float]:
    before_risk = float(original_report.get("bias_risk_score", 0.0))
    after_risk = float(mitigated_report.get("bias_risk_score", 0.0))
    before_fairness = float(original_report.get("fairness_score", 0.0))
    after_fairness = float(mitigated_report.get("fairness_score", 0.0))

    return {
        "bias_risk_reduction": round(before_risk - after_risk, 2),
        "fairness_gain": round(after_fairness - before_fairness, 2),
        "risk_improvement_pct": round(((before_risk - after_risk) / before_risk) * 100, 2) if before_risk else 0.0,
    }


def build_mitigation_suggestions(report: Dict[str, object]) -> List[str]:
    metrics = report.get("metrics", {})
    disparate_impact = float(metrics.get("disparate_impact", 1.0))
    suggestions = [
        "Reweighing: rebalance training samples so underrepresented groups have stronger influence.",
        "Threshold adjustment: lower or raise decision thresholds for the disadvantaged group.",
        "Fairness constraints: enforce equal opportunity or demographic parity during model training.",
    ]

    if disparate_impact < 0.8:
        suggestions.insert(0, "Urgent: the selection rate gap is large enough to trigger fairness intervention.")

    return suggestions

