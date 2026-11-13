"""Pure silver and gold transforms. Spark output is compared with these rows."""

from __future__ import annotations

from lakehouse_poc.quality import split_events, split_orders
from lakehouse_poc.synthetic import (
    HOLDOUT_FROM,
    TENANT,
    clean_events,
    clean_orders,
    dirty_events,
    dirty_orders,
    inkwell_orders,
)
from lakehouse_poc.values import as_float, as_int

SILVER_COLUMNS = (
    "tenant_id",
    "order_id",
    "customer_id",
    "sku",
    "category",
    "quantity",
    "amount_cents",
    "discount_rate",
    "support_view",
    "wholesale",
    "new_customer",
    "channel",
    "currency",
    "sale_date",
    "ordered_at",
    "refund",
    "n",
)

FEATURES = (
    "discount_rate",
    "support_view",
    "wholesale",
    "quantity",
    "new_customer",
    "channel_web",
)


def silver_orders(rows: list[dict[str, object]] | None = None) -> list[dict[str, object]]:
    source = clean_orders() + dirty_orders() + inkwell_orders() if rows is None else rows
    kept, _rejected = split_orders(source)
    silver = []
    for row in kept:
        if str(row["tenant_id"]) != TENANT:
            continue
        silver.append({column: row[column] for column in SILVER_COLUMNS})
    return silver


def silver_events(rows: list[dict[str, object]] | None = None) -> list[dict[str, object]]:
    source = clean_events() + dirty_events() if rows is None else rows
    kept, _rejected = split_events(source)
    return [row for row in kept if str(row["tenant_id"]) == TENANT]


def gold_daily(orders: list[dict[str, object]] | None = None) -> list[dict[str, object]]:
    source = silver_orders() if orders is None else orders
    buckets: dict[tuple[str, str], dict[str, object]] = {}
    for row in source:
        key = (str(row["sale_date"]), str(row["category"]))
        bucket = buckets.get(key)
        if bucket is None:
            bucket = {
                "tenant_id": TENANT,
                "sale_date": key[0],
                "category": key[1],
                "orders": 0,
                "revenue_cents": 0,
                "refund_count": 0,
            }
            buckets[key] = bucket
        bucket["orders"] = as_int(bucket["orders"]) + 1
        bucket["revenue_cents"] = as_int(bucket["revenue_cents"]) + as_int(row["amount_cents"])
        if bool(row["refund"]):
            bucket["refund_count"] = as_int(bucket["refund_count"]) + 1
    return [buckets[key] for key in sorted(buckets)]


def feature_rows(orders: list[dict[str, object]] | None = None) -> list[dict[str, object]]:
    source = silver_orders() if orders is None else orders
    rows = []
    for row in source:
        rows.append(
            {
                "n": as_int(row["n"]),
                "order_id": str(row["order_id"]),
                "discount_rate": as_float(row["discount_rate"]),
                "support_view": 1 if bool(row["support_view"]) else 0,
                "wholesale": 1 if bool(row["wholesale"]) else 0,
                "quantity": as_int(row["quantity"]),
                "new_customer": 1 if bool(row["new_customer"]) else 0,
                "channel_web": 1 if str(row["channel"]) == "web" else 0,
                "refund": 1 if bool(row["refund"]) else 0,
                "holdout": as_int(row["n"]) >= HOLDOUT_FROM,
            }
        )
    return rows


def revenue_7d(gold: list[dict[str, object]], sale_date: str, category: str) -> int:
    """Sum of that category from six preceding dates through sale_date."""
    dates = sorted({str(row["sale_date"]) for row in gold})
    if sale_date not in dates:
        return 0
    end = dates.index(sale_date)
    window = set(dates[max(0, end - 6) : end + 1])
    total = 0
    for row in gold:
        if str(row["category"]) == category and str(row["sale_date"]) in window:
            total += as_int(row["revenue_cents"])
    return total
