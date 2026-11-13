"""Acceptance summary for the pure path. Spark timings are added by the benchmark."""

from __future__ import annotations

from pathlib import Path

from lakehouse_poc.catalog import LINEAGE
from lakehouse_poc.model import evaluate
from lakehouse_poc.quality import reason_counts, split_events, split_orders
from lakehouse_poc.spec import gold_daily, silver_events, silver_orders
from lakehouse_poc.synthetic import (
    DATASET_ID,
    EXPECTED_HOLDOUT_REFUNDS,
    EXPECTED_REFUNDS,
    NOTICE,
    ORG,
    clean_events,
    clean_orders,
    dirty_events,
    dirty_orders,
    inkwell_orders,
)
from lakehouse_poc.values import as_int


def run_study(tracking_dir: Path | None = None) -> dict[str, object]:
    _order_kept, order_rejected = split_orders(clean_orders() + dirty_orders() + inkwell_orders())
    _event_kept, event_rejected = split_events(clean_events() + dirty_events())
    reasons = reason_counts(order_rejected + event_rejected)
    silver = silver_orders()
    silver_ids = {str(row["order_id"]) for row in silver}
    gold = gold_daily(silver)
    refunds = sum(1 for row in silver if bool(row["refund"]))
    holdout_refunds = sum(
        1 for row in silver if bool(row["refund"]) and as_int(row["n"]) >= 181
    )
    metrics = evaluate(tracking_dir=tracking_dir)
    return {
        "dataset_id": DATASET_ID,
        "organization": ORG,
        "notice": NOTICE,
        "orders_clean": len(clean_orders()),
        "orders_dirty": len(dirty_orders()),
        "inkwell_orders": len(inkwell_orders()),
        "dq_failures": len(order_rejected) + len(event_rejected),
        "dq_by_reason": reasons,
        "silver_orders": len(silver),
        "silver_events": len(silver_events()),
        "inkwell_in_silver": sum(
            1 for row in inkwell_orders() if str(row["order_id"]) in silver_ids
        ),
        "gold_rows": len(gold),
        "refund_count": refunds,
        "expected_refunds": EXPECTED_REFUNDS,
        "holdout_refunds": holdout_refunds,
        "expected_holdout_refunds": EXPECTED_HOLDOUT_REFUNDS,
        "majority_f1": metrics["majority_f1"],
        "logistic_f1": metrics["logistic_f1"],
        "logistic_fpr": metrics["logistic_fpr"],
        "recommendation": metrics["recommendation"],
        "lineage": [list(pair) for pair in LINEAGE],
        "tokens": 0,
        "price": "none",
        "databricks_workspace": "not-run",
        "kafka_broker": "not-run",
        "cloud_storage": "local-files",
        "unity_catalog": "not-run",
        "lakeflow_service": "not-run",
        "sql_warehouse": "not-run",
    }
