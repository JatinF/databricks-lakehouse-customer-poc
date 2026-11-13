"""Fixed Paperlane orders and events. No random generator."""

from __future__ import annotations

from lakehouse_poc.values import as_dict, as_int

DATASET_ID = "paperlane-v1-fixed-18"
ORG = "SYN-ORG-PAPERLANE"
TENANT = "SYN-TENANT-PAPERLANE"
OTHER_TENANT = "SYN-TENANT-INKWELL"
NOTICE = "SYNTHETIC_POC_NOT_A_DEPLOYMENT"
ORDERS_PER_DAY = 30
ORDER_COUNT = 240
HOLDOUT_FROM = 181
FORCE_REFUND = frozenset({4, 14, 24})
FORCE_KEEP = frozenset({15, 45})
TOPIC_ORDERS = "paperlane.orders.v1"
TOPIC_EVENTS = "paperlane.events.v1"

# Hand count from the rule below, checked again in tests.
# Multiples of 15 in 1..240, except wholesale 165, minus FORCE_KEEP, plus FORCE_REFUND.
EXPECTED_REFUNDS = 16
EXPECTED_HOLDOUT_REFUNDS = 4


def sale_date(n: int) -> str:
    day = 1 + (n - 1) // ORDERS_PER_DAY
    return f"2026-03-{day:02d}"


def order_record(n: int, tenant: str = TENANT) -> dict[str, object]:
    """One clean order. Discount, support, and wholesale follow fixed moduli."""
    quantity = (n % 4) + 1
    unit_cents = 1200 if n % 2 == 0 else 800
    discounted = n % 5 == 0
    gross = quantity * unit_cents
    net = (gross * 3 // 4) if discounted else gross
    support = n % 3 == 0
    wholesale = n % 11 == 0
    pattern = discounted and support and not wholesale
    refund = pattern
    if n in FORCE_REFUND:
        refund = True
    if n in FORCE_KEEP:
        refund = False
    customer_number = ((n - 1) % 40) + 1
    sku = "SYN-SKU-CARD" if n % 2 == 0 else "SYN-SKU-INK"
    return {
        "n": n,
        "tenant_id": tenant,
        "order_id": f"SYN-ORD-{n:04d}",
        "customer_id": f"SYN-CUS-{customer_number:03d}",
        "email": f"cus{customer_number:03d}@synthetic.example",
        "sku": sku,
        "category": "cards" if sku == "SYN-SKU-CARD" else "ink",
        "quantity": quantity,
        "amount_cents": net,
        "discount_rate": 0.25 if discounted else 0.0,
        "support_view": support,
        "wholesale": wholesale,
        "new_customer": customer_number <= 8,
        "channel": "web" if n % 2 == 0 else "store",
        "currency": "USD",
        "sale_date": sale_date(n),
        "ordered_at": f"{sale_date(n)}T12:00:00Z",
        "refund": refund,
    }


def clean_orders() -> list[dict[str, object]]:
    return [order_record(n) for n in range(1, ORDER_COUNT + 1)]


def inkwell_orders() -> list[dict[str, object]]:
    rows = []
    for n in (1, 2, 3):
        row = order_record(n, tenant=OTHER_TENANT)
        row["order_id"] = f"SYN-ORD-M{n:02d}"
        row["email"] = f"ink{n:03d}@synthetic.example"
        rows.append(row)
    return rows


def _shell(order_id: str) -> dict[str, object]:
    row = order_record(1)
    row["order_id"] = order_id
    row["n"] = 0
    return row


def dirty_orders() -> list[dict[str, object]]:
    """Eight rows. Each breaks one quality rule and would otherwise be valid."""
    rows: list[dict[str, object]] = []
    for order_id, kind in (
        ("SYN-ORD-D01", "negative_amount"),
        ("SYN-ORD-D02", "negative_amount"),
        ("SYN-ORD-D03", "missing_customer"),
        ("SYN-ORD-D04", "missing_customer"),
        ("SYN-ORD-D05", "future_timestamp"),
        ("SYN-ORD-D06", "future_timestamp"),
        ("SYN-ORD-D07", "unknown_currency"),
        ("SYN-ORD-D08", "unknown_currency"),
    ):
        row = _shell(order_id)
        if kind == "negative_amount":
            row["amount_cents"] = -500
        elif kind == "missing_customer":
            row["customer_id"] = ""
        elif kind == "future_timestamp":
            row["ordered_at"] = "2026-04-01T00:00:00Z"
            row["sale_date"] = "2026-04-01"
        else:
            row["currency"] = "XXX"
        rows.append(row)
    return rows


def events_for(order: dict[str, object]) -> list[dict[str, object]]:
    n = as_int(order["n"])
    sale = str(order["sale_date"])
    rows: list[dict[str, object]] = []
    seq = 1
    if n % 4 == 0:
        rows.append(_event(order, seq, "product_view", sale))
        seq += 1
    if bool(order["support_view"]):
        rows.append(_event(order, seq, "support_view", sale))
        seq += 1
    rows.append(_event(order, seq, "purchase", sale))
    return rows


def _event(order: dict[str, object], seq: int, kind: str, sale: str) -> dict[str, object]:
    n = as_int(order["n"])
    return {
        "tenant_id": order["tenant_id"],
        "event_id": f"SYN-EVT-{n:04d}-{seq}",
        "order_id": order["order_id"],
        "kind": kind,
        "sale_date": sale,
        "observed_at": f"{sale}T11:{seq:02d}:00Z",
        "offset": seq,
    }


def clean_events() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for order in clean_orders():
        rows.extend(events_for(order))
    return rows


def dirty_events() -> list[dict[str, object]]:
    """Two ids, each written twice. The second copy is the quality failure."""
    rows = []
    for event_id, offset in (
        ("SYN-EVT-DUP-0001", 1),
        ("SYN-EVT-DUP-0001", 2),
        ("SYN-EVT-DUP-0002", 1),
        ("SYN-EVT-DUP-0002", 2),
    ):
        rows.append(
            {
                "tenant_id": TENANT,
                "event_id": event_id,
                "order_id": "SYN-ORD-0001",
                "kind": "product_view",
                "sale_date": "2026-03-01",
                "observed_at": "2026-03-01T11:00:00Z",
                "offset": offset,
            }
        )
    return rows


def kafka_capture(rows: list[dict[str, object]], topic: str) -> list[dict[str, object]]:
    """Captured topic export. A broker was not started."""
    return [
        {"topic": topic, "partition": 0, "offset": index, "value": row}
        for index, row in enumerate(rows)
    ]


def unwrap_capture(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    ordered = sorted(rows, key=lambda item: (as_int(item["partition"]), as_int(item["offset"])))
    return [as_dict(item["value"]) for item in ordered]


def corrected_order_10() -> dict[str, object]:
    """Batch-2 correction used only by the MERGE proof. Amount becomes 100 cents."""
    row = order_record(10)
    row["amount_cents"] = 100
    row["gift_wrap"] = False
    return row
