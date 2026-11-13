"""Order and event checks. The first failing rule wins."""

from __future__ import annotations

from lakehouse_poc.values import as_int

AS_OF = "2026-03-09T00:00:00Z"
VALID_CURRENCY = frozenset({"USD"})


def order_reject_reason(row: dict[str, object]) -> str | None:
    amount = as_int(row["amount_cents"])
    if amount < 0:
        return "negative_amount"
    if str(row.get("customer_id", "")) == "":
        return "missing_customer"
    if str(row["ordered_at"]) >= AS_OF:
        return "future_timestamp"
    if str(row["currency"]) not in VALID_CURRENCY:
        return "unknown_currency"
    return None


def split_orders(
    rows: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[tuple[str, dict[str, object]]]]:
    kept: list[dict[str, object]] = []
    rejected: list[tuple[str, dict[str, object]]] = []
    for row in rows:
        reason = order_reject_reason(row)
        if reason is None:
            kept.append(row)
        else:
            rejected.append((reason, row))
    return kept, rejected


def split_events(
    rows: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[tuple[str, dict[str, object]]]]:
    seen: set[str] = set()
    kept: list[dict[str, object]] = []
    rejected: list[tuple[str, dict[str, object]]] = []
    ordered = sorted(rows, key=lambda item: (str(item["event_id"]), as_int(item["offset"])))
    for row in ordered:
        event_id = str(row["event_id"])
        if event_id in seen:
            rejected.append(("duplicate_event", row))
            continue
        seen.add(event_id)
        kept.append(row)
    return kept, rejected


def reason_counts(rejected: list[tuple[str, dict[str, object]]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for reason, _row in rejected:
        counts[reason] = counts.get(reason, 0) + 1
    return counts
