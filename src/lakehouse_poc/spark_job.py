"""PySpark and Delta path. Skipped when Java is absent. Databricks is not called."""

from __future__ import annotations

import json
import math
import os
import shutil
import tempfile
import time
from pathlib import Path
from typing import Any

from lakehouse_poc.quality import AS_OF
from lakehouse_poc.spec import SILVER_COLUMNS
from lakehouse_poc.sqltext import FULL_SCAN_DAY, GOLD_DAY, NAIVE_DAY, PARTITION_DAY
from lakehouse_poc.synthetic import TENANT

BENCH_ROWS = 40000
BENCH_REPEATS = 40


def java_ready() -> bool:
    if shutil.which("java"):
        return True
    home = Path(os.environ.get("JAVA_HOME", ""))
    return home.is_dir() and (home / "bin" / "java.exe").is_file()


def prepare_windows_hadoop() -> None:
    """Point Spark at a local winutils.exe. The binary is not committed."""
    if os.name != "nt":
        return
    home = Path(__file__).resolve().parents[2] / ".hadoop"
    if (home / "bin" / "winutils.exe").is_file():
        os.environ["HADOOP_HOME"] = str(home)
        os.environ["hadoop.home.dir"] = str(home)


def build_session() -> Any:
    import sys

    prepare_windows_hadoop()
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
    from delta import configure_spark_with_delta_pip
    from pyspark.sql import SparkSession

    builder = (
        SparkSession.builder.master("local[1]")
        .appName("paperlane-poc")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
        .config("spark.sql.shuffle.partitions", "1")
        .config("spark.sql.execution.arrow.pyspark.enabled", "false")
        .config("spark.ui.enabled", "false")
        .config("spark.driver.host", "127.0.0.1")
    )
    return configure_spark_with_delta_pip(builder).getOrCreate()


def _jsonable(row: dict[str, Any]) -> dict[str, Any]:
    converted: dict[str, Any] = {}
    for key, value in row.items():
        if value is None or isinstance(value, str | int | float | bool):
            converted[key] = value
        else:
            converted[key] = str(value)
    return converted


def write_json_rows(rows: list[dict[str, Any]], dest: Path) -> Path:
    """Land one JSON-lines file. Spark reads it in the JVM."""
    dest.mkdir(parents=True, exist_ok=True)
    target = dest / f"part-{len(list(dest.glob('part-*.json'))):04d}.json"
    lines = [json.dumps(_jsonable(row), separators=(",", ":")) for row in rows]
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target


def frame_from_rows(spark: Any, rows: list[dict[str, Any]]) -> Any:
    """Build a DataFrame from a JSON landing file.

    ``SparkSession.createDataFrame`` crashes the Python worker on this Windows
    host. The file read stays in the JVM, which is also how bronze is landed.
    """
    if not rows:
        raise ValueError("frame_from_rows needs at least one row")
    landing = Path(tempfile.mkdtemp(prefix="paperlane-rows-"))
    target = write_json_rows(rows, landing)
    return spark.read.option("samplingRatio", "1.0").json(target.resolve().as_posix())


def _frame(spark: Any, rows: list[dict[str, Any]]) -> Any:
    return frame_from_rows(spark, rows)


def write_delta(
    frame: Any,
    path: Path,
    mode: str = "overwrite",
    partition: str | None = None,
) -> None:
    writer = frame.write.format("delta").mode(mode)
    if partition:
        writer = writer.partitionBy(partition)
    writer.save(path.resolve().as_posix())


def merge_orders(spark: Any, path: Path, updates: list[dict[str, object]]) -> None:
    from delta.tables import DeltaTable

    source = _frame(spark, updates)
    (
        DeltaTable.forPath(spark, path.resolve().as_posix())
        .alias("target")
        .merge(source.alias("source"), "target.order_id = source.order_id")
        .withSchemaEvolution()
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )


def stream_json_to_delta(
    spark: Any,
    source: Path,
    dest: Path,
    checkpoint: Path,
    schema: Any,
) -> None:
    query = (
        spark.readStream.schema(schema)
        .json(source.resolve().as_posix())
        .writeStream.format("delta")
        .outputMode("append")
        .option("checkpointLocation", checkpoint.resolve().as_posix())
        .trigger(availableNow=True)
        .start(dest.resolve().as_posix())
    )
    query.awaitTermination()


def silver_from_bronze(frame: Any) -> Any:
    from pyspark.sql import functions as F

    kept = frame.filter(
        (F.col("amount_cents") >= 0)
        & (F.col("customer_id") != "")
        & (F.col("ordered_at") < AS_OF)
        & (F.col("currency") == "USD")
        & (F.col("tenant_id") == TENANT)
    )
    return kept.select(*SILVER_COLUMNS)


def gold_from_silver(frame: Any) -> Any:
    from pyspark.sql import functions as F

    return (
        frame.groupBy("tenant_id", "sale_date", "category")
        .agg(
            F.count("*").alias("orders"),
            F.sum("amount_cents").alias("revenue_cents"),
            F.sum(F.col("refund").cast("int")).alias("refund_count"),
        )
        .orderBy("sale_date", "category")
    )


def bronze_orders_stream(spark: Any, landing: str) -> Any:
    """Streaming read used by the Lakeflow source. Tests call stream_json_to_delta."""
    return spark.readStream.format("json").load(landing)


def read_delta(spark: Any, path: Path) -> list[dict[str, object]]:
    frame = spark.read.format("delta").load(path.resolve().as_posix())
    return [row.asDict() for row in frame.collect()]


def register_gold(spark: Any, orders: list[dict[str, object]]) -> None:
    silver = silver_from_bronze(_frame(spark, orders))
    silver.createOrReplaceTempView("silver_orders")
    gold_from_silver(silver).createOrReplaceTempView("gold_daily_category_revenue")


def query(spark: Any, sql: str) -> list[dict[str, object]]:
    return [row.asDict() for row in spark.sql(sql).collect()]


def _bench_frame(spark: Any) -> Any:
    rows = [
        {
            "sale_date": f"2026-03-{(index % 8) + 1:02d}",
            "category": "cards" if index % 2 == 0 else "ink",
            "revenue_cents": (index % 50) + 1,
        }
        for index in range(BENCH_ROWS)
    ]
    return _frame(spark, rows)


def time_queries(spark: Any, root: Path) -> dict[str, object]:
    """Compare one date on a partitioned Delta table with a full unpartitioned scan."""
    frame = _bench_frame(spark).cache()
    frame.count()
    partitioned = root / "bench_partitioned"
    plain = root / "bench_unpartitioned"
    write_delta(frame, partitioned, partition="sale_date")
    write_delta(frame, plain)
    spark.read.format("delta").load(partitioned.resolve().as_posix()).createOrReplaceTempView(
        "bench_partitioned"
    )
    spark.read.format("delta").load(plain.resolve().as_posix()).createOrReplaceTempView(
        "bench_unpartitioned"
    )
    spark.sql(PARTITION_DAY).count()
    spark.sql(FULL_SCAN_DAY).count()
    return {
        "rows": BENCH_ROWS,
        "repeats": BENCH_REPEATS,
        "partitioned": _samples(spark, PARTITION_DAY),
        "unpartitioned": _samples(spark, FULL_SCAN_DAY),
        "engine": "spark-sql-local",
        "sql_warehouse": "not-run",
    }


def _samples(spark: Any, sql: str) -> dict[str, float]:
    samples: list[float] = []
    for _ in range(BENCH_REPEATS):
        started = time.perf_counter()
        spark.sql(sql).collect()
        samples.append(time.perf_counter() - started)
    return {
        "min": min(samples),
        "p50": nearest_rank(samples, 0.50),
        "p95": nearest_rank(samples, 0.95),
        "max": max(samples),
    }


def nearest_rank(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = math.ceil(fraction * len(ordered)) - 1
    return ordered[max(0, index)]


def gold_sql_rows(spark: Any) -> list[dict[str, object]]:
    return query(spark, GOLD_DAY)


def naive_sql_rows(spark: Any) -> list[dict[str, object]]:
    return query(spark, NAIVE_DAY)
