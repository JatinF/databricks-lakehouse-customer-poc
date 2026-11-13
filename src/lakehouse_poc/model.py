"""Majority baseline versus one logistic regression. No search after the rule was frozen."""

from __future__ import annotations

from pathlib import Path

import mlflow
from sklearn.linear_model import LogisticRegression

from lakehouse_poc.decision import F1_MARGIN, FPR_CAP, MODEL_C, THRESHOLD, choose
from lakehouse_poc.spec import FEATURES, feature_rows
from lakehouse_poc.values import as_float, as_int


def refund_f1(truth: list[int], predicted: list[int]) -> float:
    tp = sum(1 for left, right in zip(truth, predicted, strict=True) if left == 1 and right == 1)
    fp = sum(1 for left, right in zip(truth, predicted, strict=True) if left == 0 and right == 1)
    fn = sum(1 for left, right in zip(truth, predicted, strict=True) if left == 1 and right == 0)
    if tp == 0:
        return 0.0
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    return 2 * precision * recall / (precision + recall)


def refund_fpr(truth: list[int], predicted: list[int]) -> float:
    negatives = sum(1 for value in truth if value == 0)
    if negatives == 0:
        return 0.0
    fp = sum(1 for left, right in zip(truth, predicted, strict=True) if left == 0 and right == 1)
    return fp / negatives


def _matrix(rows: list[dict[str, object]]) -> list[list[float]]:
    return [[as_float(row[name]) for name in FEATURES] for row in rows]


def evaluate(
    rows: list[dict[str, object]] | None = None,
    tracking_dir: Path | None = None,
) -> dict[str, object]:
    source = feature_rows() if rows is None else rows
    train = [row for row in source if not bool(row["holdout"])]
    holdout = [row for row in source if bool(row["holdout"])]
    train_y = [as_int(row["refund"]) for row in train]
    holdout_y = [as_int(row["refund"]) for row in holdout]
    majority = 1 if sum(train_y) * 2 >= len(train_y) else 0
    baseline_pred = [majority] * len(holdout_y)
    estimator = LogisticRegression(C=MODEL_C, solver="lbfgs", max_iter=500, random_state=0)
    estimator.fit(_matrix(train), train_y)
    probabilities = estimator.predict_proba(_matrix(holdout))[:, 1]
    model_pred = [1 if float(score) >= THRESHOLD else 0 for score in probabilities]
    baseline_f1 = refund_f1(holdout_y, baseline_pred)
    model_f1 = refund_f1(holdout_y, model_pred)
    model_fpr = refund_fpr(holdout_y, model_pred)
    recommendation = choose(model_f1, baseline_f1, model_fpr)
    if tracking_dir is not None:
        _log(tracking_dir, baseline_f1, model_f1, model_fpr, recommendation)
    return {
        "train_rows": len(train),
        "holdout_rows": len(holdout),
        "majority_label": majority,
        "majority_f1": baseline_f1,
        "logistic_f1": model_f1,
        "logistic_fpr": model_fpr,
        "threshold": THRESHOLD,
        "f1_margin": F1_MARGIN,
        "fpr_cap": FPR_CAP,
        "model_c": MODEL_C,
        "class_weight": estimator.get_params()["class_weight"],
        "recommendation": recommendation,
        "features": list(FEATURES),
    }


def _log(
    tracking_dir: Path,
    baseline_f1: float,
    model_f1: float,
    model_fpr: float,
    recommendation: str,
) -> None:
    tracking_dir.mkdir(parents=True, exist_ok=True)
    mlflow.set_tracking_uri(tracking_dir.resolve().as_uri())
    mlflow.set_experiment("paperlane-refund")
    with mlflow.start_run(run_name="majority"):
        mlflow.log_metric("refund_f1", baseline_f1)
        mlflow.set_tag("recommendation", recommendation)
    with mlflow.start_run(run_name="logistic"):
        mlflow.log_metric("refund_f1", model_f1)
        mlflow.log_metric("refund_fpr", model_fpr)
        mlflow.set_tag("recommendation", recommendation)
