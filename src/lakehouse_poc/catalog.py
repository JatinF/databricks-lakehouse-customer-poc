"""Local stand-in for Unity Catalog grants. The catalog service was not contacted."""

from __future__ import annotations

import secrets
from dataclasses import dataclass

from lakehouse_poc.synthetic import OTHER_TENANT, TENANT

LINEAGE = (
    ("silver_orders", "bronze_orders"),
    ("silver_events", "bronze_events"),
    ("gold_daily_category_revenue", "silver_orders"),
    ("gold_order_features", "silver_orders"),
    ("gold_order_features", "silver_events"),
)

# Privilege, securable. Analysts read gold. Engineers also read bronze and silver.
GRANTS = (
    ("analyst", "USE CATALOG", "paperlane"),
    ("analyst", "USE SCHEMA", "paperlane.gold"),
    ("analyst", "SELECT", "paperlane.gold.daily_category_revenue"),
    ("analyst", "SELECT", "paperlane.gold.order_features"),
    ("engineer", "USE CATALOG", "paperlane"),
    ("engineer", "USE SCHEMA", "paperlane.bronze"),
    ("engineer", "USE SCHEMA", "paperlane.silver"),
    ("engineer", "USE SCHEMA", "paperlane.gold"),
    ("engineer", "SELECT", "paperlane.bronze.orders"),
    ("engineer", "SELECT", "paperlane.bronze.events"),
    ("engineer", "SELECT", "paperlane.silver.orders"),
    ("engineer", "SELECT", "paperlane.silver.events"),
    ("engineer", "SELECT", "paperlane.gold.daily_category_revenue"),
    ("engineer", "SELECT", "paperlane.gold.order_features"),
    ("engineer", "MODIFY", "paperlane.gold"),
)

PII_COLUMNS = frozenset({"email"})


@dataclass(frozen=True)
class Principal:
    principal_id: str
    token: str
    role: str
    tenant_id: str


LETA = Principal("SYN-USER-LETA", "lab-leta", "analyst", TENANT)
OMAR = Principal("SYN-USER-OMAR", "lab-omar", "engineer", TENANT)
PRUE = Principal("SYN-USER-PRUE", "lab-prue", "analyst", OTHER_TENANT)
PRINCIPALS = (LETA, OMAR, PRUE)


def principal_from_token(token: str) -> Principal | None:
    for person in PRINCIPALS:
        if len(token) == len(person.token) and secrets.compare_digest(token, person.token):
            return person
    return None


def allow(principal: Principal, privilege: str, securable: str) -> bool:
    if principal.tenant_id != TENANT:
        return False
    return (principal.role, privilege, securable) in GRANTS


def column_allowed(principal: Principal, securable: str, column: str) -> bool:
    if column in PII_COLUMNS and principal.role != "engineer":
        return False
    return allow(principal, "SELECT", securable)


def visible_rows(
    principal: Principal,
    securable: str,
    rows: list[dict[str, object]],
) -> tuple[str, list[dict[str, object]]]:
    """Deny when the grant is missing. Otherwise keep the principal's tenant."""
    if not allow(principal, "SELECT", securable):
        return "denied", []
    kept = [row for row in rows if str(row.get("tenant_id", "")) == principal.tenant_id]
    return "ok", kept
