"""Lakeflow pipeline source.

The Lakeflow service was not started. Local tests parse this file and run the
same transform functions under Spark. `spark` is bound by the pipeline runtime.
"""

from pyspark import pipelines as dp

from lakehouse_poc.spark_job import bronze_orders_stream, gold_from_silver, silver_from_bronze


@dp.table(name="bronze_orders")
def bronze_orders():
    return bronze_orders_stream(spark, "landing/orders")  # noqa: F821


@dp.expect("kept_amount", "amount_cents >= 0")
@dp.materialized_view(name="silver_orders")
def silver_orders():
    return silver_from_bronze(spark.table("bronze_orders"))  # noqa: F821


@dp.materialized_view(name="gold_daily_category_revenue")
def gold_daily_category_revenue():
    return gold_from_silver(spark.table("silver_orders"))  # noqa: F821
