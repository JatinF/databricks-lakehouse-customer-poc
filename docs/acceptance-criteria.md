# Acceptance criteria

Dataset `paperlane-v1-fixed-18`. Notice `SYNTHETIC_POC_NOT_A_DEPLOYMENT`.

| Check | Pass condition |
| --- | --- |
| Raw retain | Bronze input includes 240 clean orders, 8 dirty orders, 3 Inkwell orders, and 4 dirty event copies |
| Quarantine | 10 data-quality failures: negative amount 2, missing customer 2, future timestamp 2, unknown currency 2, duplicate event 2 |
| Silver | 240 Paperlane orders, no email column, Inkwell order ids absent |
| Hand revenue | 1 March 2026 category revenue equals the sum of order amounts 1 through 30 |
| Refund count | 16 refunds, 4 of them in the holdout `n >= 181` |
| MERGE | Order 10 becomes 100 cents, the table holds 240 orders, `gift_wrap` arrives on the new rows |
| Stream | `availableNow` loads 180 rows, then 240 after the second file drop |
| Grants | Leta can select gold and cannot select bronze. Omar can modify gold. Prue is denied |
| SQL | The 8 March revenue from `GOLD_DAY` matches the pure gold rows. The committed bench records both layouts. Partitioned is not treated as faster unless its p50 is lower |
| Model | Recommendation equals `choose(logistic_f1, majority_f1, logistic_fpr)` with margin 0.05 and false-positive cap 0.20 |
| Gates | Empty Databricks, Kafka, and cloud settings stay not-run or local-file. A remote host raises `remote_blocked` and the message omits the host |
| Cost | Tokens 0. Price none |
| Services | Workspace, Unity Catalog, Lakeflow, and the SQL warehouse stay not-run |

Spark checks run when Java is on the machine or on the GitHub-hosted runner. They are not replaced by a claim that Lakeflow ran.
