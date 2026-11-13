# Databricks notebook source
# Paperlane walkthrough. Synthetic data. The Lakeflow service is not started here.

# COMMAND ----------
from lakehouse_poc.study import run_study

report = run_study()
print(report["notice"])
print(report["silver_orders"])
print(report["dq_failures"])
print(report["recommendation"])

# COMMAND ----------
from lakehouse_poc.catalog import LETA, OMAR, PRUE, allow

assert allow(LETA, "SELECT", "paperlane.gold.daily_category_revenue")
assert not allow(LETA, "SELECT", "paperlane.bronze.orders")
assert allow(OMAR, "SELECT", "paperlane.bronze.orders")
assert not allow(PRUE, "SELECT", "paperlane.gold.daily_category_revenue")
assert not allow(LETA, "MODIFY", "paperlane.gold")
assert allow(OMAR, "MODIFY", "paperlane.gold")
