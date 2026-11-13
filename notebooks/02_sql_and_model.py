# Databricks notebook source
# SQL text for a Databricks SQL warehouse. The warehouse was not used.

# COMMAND ----------
from lakehouse_poc.spec import feature_rows, gold_daily, revenue_7d
from lakehouse_poc.sqltext import GOLD_DAY

gold = gold_daily()
march_8 = [row for row in gold if row["sale_date"] == "2026-03-08"]
assert len(march_8) == 2
for row in march_8:
    assert revenue_7d(gold, "2026-03-08", str(row["category"])) >= int(row["revenue_cents"])
assert "revenue_7d_cents" in GOLD_DAY
assert sum(1 for row in feature_rows() if row["holdout"]) == 60
