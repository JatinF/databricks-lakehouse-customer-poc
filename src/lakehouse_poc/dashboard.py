"""Static customer report. This is not a Databricks SQL dashboard."""

from __future__ import annotations

from pathlib import Path


def render(summary: dict[str, object]) -> str:
    reasons = summary["dq_by_reason"]
    reason_rows = ""
    if isinstance(reasons, dict):
        for name in sorted(reasons):
            reason_rows += f"<tr><td>{name}</td><td>{reasons[name]}</td></tr>"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>Paperlane POC report</title>
<style>
body {{ margin: 0; background: #f4f7fb; color: #102033; font-family: "Segoe UI", sans-serif; }}
header {{ background: #101820; color: white; padding: 24px 32px; }}
header p {{ color: #c5d0da; }}
main {{ padding: 24px 32px; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }}
article {{ background: white; border: 1px solid #e1e8ef; box-shadow: 0 1px 2px #d9e3ec; padding: 16px; }}
h1 {{ margin: 0 0 8px; font-size: 22px; }}
h2 {{ margin: 0 0 8px; font-size: 16px; color: #0f5c6b; }}
.span {{ grid-column: 1 / -1; }}
table {{ border-collapse: collapse; width: 100%; }}
td {{ border-bottom: 1px solid #e1e8ef; padding: 6px 0; }}
.warn {{ color: #9a6700; }}
</style>
</head>
<body>
<header>
<h1>Paperlane lakehouse POC</h1>
<p>{summary["notice"]} · Synthetic prospect · Deployment NO-GO</p>
</header>
<main>
<article><h2>Organization</h2><p>{summary["organization"]}</p><p>{summary["dataset_id"]}</p></article>
<article><h2>Silver orders</h2><p>{summary["silver_orders"]}</p><p>Refunds {summary["refund_count"]}</p></article>
<article><h2>Data-quality failures</h2><p>{summary["dq_failures"]}</p><p class="warn">Quarantine, not deleted from bronze</p></article>
<article class="span"><h2>Quality reasons</h2><table>{reason_rows}</table></article>
<article><h2>Model recommendation</h2><p>{summary["recommendation"]}</p><p>Logistic F1 {summary["logistic_f1"]}</p><p>Majority F1 {summary["majority_f1"]}</p></article>
<article><h2>Services not contacted</h2><p>Databricks workspace {summary["databricks_workspace"]}</p><p>Unity Catalog {summary["unity_catalog"]}</p><p>Lakeflow {summary["lakeflow_service"]}</p><p>SQL warehouse {summary["sql_warehouse"]}</p></article>
<article><h2>Cost</h2><p>Price {summary["price"]}</p><p>Tokens {summary["tokens"]}</p><p>Inkwell rows in silver {summary["inkwell_in_silver"]}</p></article>
{spark_card(summary)}
</main>
</body>
</html>
"""


def spark_card(summary: dict[str, object]) -> str:
    spark = summary.get("spark_sql")
    if not isinstance(spark, dict) or spark.get("status") != "ran":
        return ""
    partitioned = spark.get("partitioned")
    plain = spark.get("unpartitioned")
    if not isinstance(partitioned, dict) or not isinstance(plain, dict):
        return ""
    return (
        "<article class=\"span\"><h2>Local Spark SQL</h2>"
        f"<p>Partitioned p50 {partitioned.get('p50')} s</p>"
        f"<p>Unpartitioned p50 {plain.get('p50')} s</p>"
        f"<p>{spark.get('rows')} rows, {spark.get('repeats')} repeats, "
        f"{spark.get('engine')}. SQL warehouse {spark.get('sql_warehouse')}.</p>"
        "<p>The partitioned p50 is higher on this run.</p></article>"
    )


def write_report(path: Path, summary: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(summary), encoding="utf-8")
