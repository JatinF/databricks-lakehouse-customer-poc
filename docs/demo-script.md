# Demo script

Twelve to fourteen minutes. Audience: the Paperlane prospect's analyst and engineer. Every figure below is in `benchmarks/latest.json`. Do not replace them with a warehouse claim.

## 0:00 Open

Say the notice `SYNTHETIC_POC_NOT_A_DEPLOYMENT` before any chart. Paperlane is synthetic. The deployment decision is NO-GO. This laptop is not a Databricks workspace.

Show the header of [dashboard.html](dashboard.html).

## 1:00 Problem

Refund review is a spreadsheet. Orders and events arrive as files: a captured topic and a directory. The ask was a medallion layout, a daily category figure, and a refund score that is allowed to lose to a majority baseline.

Name the three principals. Leta is the Paperlane analyst. Omar is the Paperlane engineer. Prue is an Inkwell analyst and is the cross-tenant stop.

## 2:30 Medallion

Walk [diagrams/medallion.svg](diagrams/medallion.svg). Bronze keeps the raw files. Silver drops the email and the bad rows. Gold is daily category revenue and the model features. Inkwell orders never enter silver.

## 4:30 Quality

Ten failures, two of each reason: negative amount, missing customer, future timestamp, unknown currency, duplicate event. Silver holds 240 orders and 382 events. Gold has 16 daily rows. Refunds are 16, and 4 of those are in the holdout `n >= 181`.

## 6:30 Delta

The merge proof is separate from the model. The first write is orders 1 through 180. The second batch sets order 10 to 100 cents, adds `gift_wrap`, and inserts orders 181 through 240. After the merge the table has 240 orders, order 10 is 100 cents, order 1 has no gift wrap, and order 240 has gift wrap. History contains `WRITE` and `MERGE`.

The stream proof drops a second JSON file and `availableNow` moves the count from 180 to 240. No broker was started.

## 8:30 Access

Leta can select gold and cannot select bronze. Omar can modify gold. Prue cannot select Paperlane gold. The SQL file in `resources/unity_catalog.sql` was not applied. The check is the in-process enforcer.

## 9:30 SQL

Show the timing table in the README. Same predicate, `sale_date = 2026-03-08`, 40,000 rows, 40 repeats.

Partitioned p50 is 0.4407844999950612 seconds. Unpartitioned p50 is 0.397024899997632 seconds. Say that the partitioned layout was slower on this machine. Do not call it a Photon or warehouse result.

## 11:30 Model

Two MLflow runs, `majority` and `logistic`, in a local file store. Both refund F1 scores are 0.0. The logistic false-positive rate is 0.0 because every holdout prediction is the negative class. The frozen rule returns `majority`. Say that the threshold stayed at 0.5.

## 13:00 Close

Read the not-run line: workspace, Unity Catalog service, Lakeflow service, SQL warehouse, Kafka broker, cloud bucket. Price none. Tokens 0. Stop on NO-GO. Do not offer a deployment date.
