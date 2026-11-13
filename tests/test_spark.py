import os
import shutil
from pathlib import Path

import pytest

from lakehouse_poc.spark_job import (
    frame_from_rows,
    java_ready,
    merge_orders,
    read_delta,
    silver_from_bronze,
    stream_json_to_delta,
    write_delta,
    write_json_rows,
)
from lakehouse_poc.spec import gold_daily, silver_orders
from lakehouse_poc.sqltext import GOLD_DAY, NAIVE_DAY
from lakehouse_poc.synthetic import clean_orders, corrected_order_10, inkwell_orders, order_record

ROOT = Path(__file__).resolve().parents[1]


def _ensure_java() -> None:
    from lakehouse_poc.spark_job import prepare_windows_hadoop

    prepare_windows_hadoop()
    if shutil.which("java") or java_ready():
        return
    homes = sorted((ROOT / ".jdk").glob("jdk-*"))
    if not homes:
        pytest.skip("Java is absent and the Lakeflow service was not used as a substitute")
    os.environ["JAVA_HOME"] = str(homes[0])
    os.environ["PATH"] = str(homes[0] / "bin") + os.pathsep + os.environ.get("PATH", "")


@pytest.fixture(scope="module")
def spark():
    _ensure_java()
    if not java_ready():
        pytest.skip("Java is absent and the Lakeflow service was not used as a substitute")
    from lakehouse_poc.spark_job import build_session

    session = build_session()
    yield session
    session.stop()


def test_delta_merge_schema_and_silver_match(spark, tmp_path: Path) -> None:
    first = clean_orders()[:180]
    path = tmp_path / "orders"
    write_delta(frame_from_rows(spark, first), path)
    updates = [corrected_order_10()]
    for row in clean_orders()[180:]:
        copied = dict(row)
        copied["gift_wrap"] = True
        updates.append(copied)
    merge_orders(spark, path, updates)
    stored = read_delta(spark, path)
    assert len(stored) == 240
    by_id = {row["order_id"]: row for row in stored}
    assert by_id["SYN-ORD-0010"]["amount_cents"] == 100
    assert by_id["SYN-ORD-0001"]["gift_wrap"] is None
    assert by_id["SYN-ORD-0240"]["gift_wrap"] is True
    assert len([row for row in stored if row["order_id"] == "SYN-ORD-0001"]) == 1
    from delta.tables import DeltaTable

    operations = {
        row.operation
        for row in DeltaTable.forPath(spark, path.resolve().as_posix()).history().collect()
    }
    assert "MERGE" in operations
    assert "WRITE" in operations


def test_spark_gold_matches_the_pure_spec_and_sql(spark) -> None:
    bronze = clean_orders() + inkwell_orders()
    silver = silver_from_bronze(frame_from_rows(spark, bronze))
    got = [row.asDict() for row in silver.collect()]
    assert len(got) == 240
    assert all("email" not in row for row in got)
    expected = {
        (row["sale_date"], row["category"]): int(row["revenue_cents"]) for row in gold_daily()
    }
    silver.createOrReplaceTempView("silver_orders")
    from lakehouse_poc.spark_job import gold_from_silver

    gold_from_silver(silver).createOrReplaceTempView("gold_daily_category_revenue")
    ranked = {row["category"]: int(row["revenue_cents"]) for row in spark.sql(GOLD_DAY).collect()}
    naive = {row["category"]: int(row["revenue_cents"]) for row in spark.sql(NAIVE_DAY).collect()}
    march_8 = {key[1]: value for key, value in expected.items() if key[0] == "2026-03-08"}
    assert ranked == march_8
    assert naive == march_8
    pure_ids = {row["order_id"] for row in silver_orders()}
    assert "SYN-ORD-M01" not in pure_ids


def test_available_now_stream_appends_the_second_batch(spark, tmp_path: Path) -> None:
    landing = tmp_path / "landing"
    first = clean_orders()[:180]
    write_json_rows(first, landing)
    schema = frame_from_rows(spark, first).schema
    dest = tmp_path / "bronze"
    checkpoint = tmp_path / "checkpoint"
    stream_json_to_delta(spark, landing, dest, checkpoint, schema)
    assert spark.read.format("delta").load(dest.resolve().as_posix()).count() == 180
    second = clean_orders()[180:]
    write_json_rows(second, landing)
    stream_json_to_delta(spark, landing, dest, checkpoint, schema)
    assert spark.read.format("delta").load(dest.resolve().as_posix()).count() == 240
    assert order_record(240)["order_id"] == "SYN-ORD-0240"
