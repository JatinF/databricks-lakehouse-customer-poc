"""SQL text shared by Spark and the Databricks SQL notes.

A Databricks SQL warehouse was not used. Local runs send this text to Spark SQL.
"""

GOLD_DAY = """
SELECT
  sale_date,
  category,
  orders,
  revenue_cents,
  refund_count,
  SUM(revenue_cents) OVER (
    PARTITION BY category
    ORDER BY sale_date
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  ) AS revenue_7d_cents,
  RANK() OVER (
    PARTITION BY sale_date
    ORDER BY revenue_cents DESC
  ) AS category_rank
FROM gold_daily_category_revenue
WHERE sale_date = '2026-03-08'
ORDER BY category
""".strip()

NAIVE_DAY = """
SELECT
  sale_date,
  category,
  COUNT(*) AS orders,
  SUM(amount_cents) AS revenue_cents
FROM silver_orders
GROUP BY sale_date, category
HAVING sale_date = '2026-03-08'
ORDER BY category
""".strip()

PARTITION_DAY = """
SELECT sale_date, category, revenue_cents
FROM bench_partitioned
WHERE sale_date = '2026-03-08'
""".strip()

FULL_SCAN_DAY = """
SELECT sale_date, category, revenue_cents
FROM bench_unpartitioned
WHERE sale_date = '2026-03-08'
""".strip()
