# ADR 0001: Local Spark stands in for Databricks

## Status

Accepted for this reference. Production remains NO-GO.

## Context

The POC needs PySpark, Delta, streaming, SQL, and a Lakeflow-shaped pipeline. This workstation has no Databricks CLI, no workspace, and originally no Java. Installing a portable JDK runs Spark locally. It does not create a Databricks runtime.

## Decision

Execute Delta `MERGE`, schema evolution, `availableNow`, and Spark SQL on local Spark. Keep the Lakeflow file, the asset bundle, and the Unity Catalog SQL as source that was not deployed. Block non-local hosts.

## Consequences

A green test can show medallion behavior and a query time on this CPU. It cannot show Photon, Unity Catalog enforcement, or a Lakeflow update. Those stay not-run.
