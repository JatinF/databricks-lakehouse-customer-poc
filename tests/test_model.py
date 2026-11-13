from pathlib import Path

import mlflow
from mlflow.tracking import MlflowClient

from lakehouse_poc.decision import F1_MARGIN, FPR_CAP, MODEL_C, THRESHOLD, choose
from lakehouse_poc.model import evaluate
from lakehouse_poc.spec import FEATURES


def test_recommendation_uses_the_frozen_rule(tmp_path: Path) -> None:
    metrics = evaluate(tracking_dir=tmp_path)
    assert metrics["features"] == list(FEATURES)
    assert metrics["threshold"] == THRESHOLD
    assert metrics["model_c"] == MODEL_C
    assert metrics["class_weight"] is None
    assert metrics["f1_margin"] == F1_MARGIN
    assert metrics["fpr_cap"] == FPR_CAP
    assert metrics["train_rows"] == 180
    assert metrics["holdout_rows"] == 60
    assert metrics["majority_label"] == 0
    assert metrics["recommendation"] == choose(
        float(metrics["logistic_f1"]),
        float(metrics["majority_f1"]),
        float(metrics["logistic_fpr"]),
    )
    tracking_uri = tmp_path.resolve().as_uri()
    mlflow.set_tracking_uri(tracking_uri)
    client = MlflowClient(tracking_uri=tracking_uri)
    experiment = client.get_experiment_by_name("paperlane-refund")
    assert experiment is not None
    runs = client.search_runs([experiment.experiment_id])
    names = {run.info.run_name for run in runs}
    assert names == {"majority", "logistic"}
