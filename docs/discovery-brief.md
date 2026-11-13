# Discovery brief

Paperlane is a synthetic specialty retailer, organization `SYN-ORG-PAPERLANE`. This brief is a prepared POC, not minutes from a customer meeting and not a signed statement of work.

## Problem

Refund review is a spreadsheet. Orders and site events arrive as files: a captured Kafka topic and a directory that stands in for object storage. The prospect wants a medallion layout, a daily category revenue figure an analyst can read, and a refund score that is allowed to lose to a simple baseline.

## Users

| Principal | Role | Tenant |
| --- | --- | --- |
| `SYN-USER-LETA` | Analyst | `SYN-TENANT-PAPERLANE` |
| `SYN-USER-OMAR` | Engineer | `SYN-TENANT-PAPERLANE` |
| `SYN-USER-PRUE` | Analyst | `SYN-TENANT-INKWELL` |

Inkwell exists so a cross-tenant read can be refused. It is not a second customer implementation.

## In scope for the reference

- Synthetic orders, events, and a fixed set of bad rows.
- Bronze retain, silver quarantine, gold daily revenue and features.
- Delta `MERGE`, a new column, and a streaming append with `availableNow`.
- A Lakeflow source file and a local run of the same transforms.
- Grant checks and a Unity Catalog SQL file that was not applied.
- Spark SQL for the day query, timed on local Spark when Java is present.
- One logistic regression compared with a majority baseline under a frozen rule.
- MLflow file-store runs.

## Out of scope

A Databricks workspace, Unity Catalog service, Lakeflow service, SQL warehouse, Kafka broker, cloud bucket, Photon, and any production deployment. Those stay not-run. The deployment decision is NO-GO.

## Success

The acceptance checklist in `docs/acceptance-criteria.md` passes, including the rule that the refund model is kept only when it clears the margin and the false-positive cap. Beating the baseline is not required.
