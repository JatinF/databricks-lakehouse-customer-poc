import ast
from pathlib import Path

from lakehouse_poc.catalog import GRANTS, LINEAGE
from lakehouse_poc.dashboard import render
from lakehouse_poc.decision import choose
from lakehouse_poc.quality import order_reject_reason, reason_counts, split_events, split_orders
from lakehouse_poc.spec import gold_daily, revenue_7d, silver_orders
from lakehouse_poc.study import run_study
from lakehouse_poc.synthetic import (
    EXPECTED_HOLDOUT_REFUNDS,
    EXPECTED_REFUNDS,
    TOPIC_ORDERS,
    clean_orders,
    dirty_events,
    dirty_orders,
    kafka_capture,
    order_record,
    unwrap_capture,
)

ROOT = Path(__file__).resolve().parents[1]


def test_hand_checked_orders_and_refund_count() -> None:
    fourth = order_record(4)
    fifteenth = order_record(15)
    tenth = order_record(10)
    assert fourth["quantity"] == 1
    assert fourth["amount_cents"] == 1200
    assert fourth["refund"] is True
    assert fifteenth["amount_cents"] == 2400
    assert fifteenth["refund"] is False
    assert fifteenth["support_view"] is True
    assert tenth["amount_cents"] == 2700
    assert sum(1 for row in clean_orders() if row["refund"]) == EXPECTED_REFUNDS
    holdout = [row for row in clean_orders() if int(row["n"]) >= 181 and row["refund"]]
    assert len(holdout) == EXPECTED_HOLDOUT_REFUNDS
    assert "email" not in silver_orders()[0]


def test_quality_reasons_and_tenant_filter() -> None:
    _kept, rejected = split_orders(clean_orders() + dirty_orders())
    _events, event_rejected = split_events(dirty_events())
    reasons = reason_counts(rejected + event_rejected)
    assert reasons == {
        "negative_amount": 2,
        "missing_customer": 2,
        "future_timestamp": 2,
        "unknown_currency": 2,
        "duplicate_event": 2,
    }
    assert order_reject_reason(order_record(1)) is None
    assert all(row["tenant_id"] == "SYN-TENANT-PAPERLANE" for row in silver_orders())
    assert len(silver_orders()) == 240


def test_gold_window_and_study_rule() -> None:
    gold = gold_daily()
    march_1 = [row for row in gold if row["sale_date"] == "2026-03-01"]
    assert sum(int(row["orders"]) for row in march_1) == 30
    hand = sum(int(order_record(n)["amount_cents"]) for n in range(1, 31))
    assert sum(int(row["revenue_cents"]) for row in march_1) == hand
    for row in gold:
        if row["sale_date"] == "2026-03-08":
            assert revenue_7d(gold, "2026-03-08", str(row["category"])) >= int(row["revenue_cents"])
    study = run_study()
    assert study["dq_failures"] == 10
    assert study["inkwell_in_silver"] == 0
    assert study["refund_count"] == EXPECTED_REFUNDS
    assert study["recommendation"] == choose(
        float(study["logistic_f1"]),
        float(study["majority_f1"]),
        float(study["logistic_fpr"]),
    )
    assert {tuple(pair) for pair in study["lineage"]} == set(LINEAGE)
    page = render(study)
    assert "Data-quality failures" in page
    assert str(study["dq_failures"]) in page
    assert "SYNTHETIC_POC_NOT_A_DEPLOYMENT" in page
    assert "Local Spark SQL" not in page
    spark_page = render(
        {
            **study,
            "spark_sql": {
                "status": "ran",
                "rows": 40000,
                "repeats": 40,
                "engine": "spark-sql-local",
                "sql_warehouse": "not-run",
                "partitioned": {"p50": 0.44},
                "unpartitioned": {"p50": 0.39},
            },
        }
    )
    assert "Partitioned p50 0.44 s" in spark_page
    assert "SQL warehouse not-run" in spark_page


def test_kafka_capture_orders_by_offset() -> None:
    rows = clean_orders()[:5]
    captured = list(reversed(kafka_capture(rows, TOPIC_ORDERS)))
    restored = unwrap_capture(captured)
    assert [row["order_id"] for row in restored] == [row["order_id"] for row in rows]
    assert captured[0]["topic"] == TOPIC_ORDERS


def test_declared_pipeline_and_catalog_sql() -> None:
    pipeline = (ROOT / "pipelines" / "paperlane_medallion.py").read_text(encoding="utf-8")
    ast.parse(pipeline)
    assert '@dp.table(name="bronze_orders")' in pipeline
    assert '@dp.materialized_view(name="silver_orders")' in pipeline
    assert '@dp.materialized_view(name="gold_daily_category_revenue")' in pipeline
    assert "amount_cents >= 0" in pipeline
    sql = (ROOT / "resources" / "unity_catalog.sql").read_text(encoding="utf-8")
    for _role, privilege, securable in GRANTS:
        assert privilege in sql
        assert securable in sql
    for child, parent in LINEAGE:
        assert child in sql
        assert parent in sql
    bundle = (ROOT / "resources" / "databricks.yml").read_text(encoding="utf-8")
    assert "paperlane_medallion" in bundle
    assert "was not run" in bundle
