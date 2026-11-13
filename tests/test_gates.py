import socket

import pytest

from lakehouse_poc.catalog import (
    LETA,
    OMAR,
    PRUE,
    allow,
    column_allowed,
    principal_from_token,
    visible_rows,
)
from lakehouse_poc.gates import FlowError, classify, ensure_local, report
from lakehouse_poc.synthetic import OTHER_TENANT, TENANT, inkwell_orders, order_record


def test_remote_targets_are_blocked_without_dialing(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("dialed")

    monkeypatch.setattr(socket, "socket", boom)
    host = "https://adb-900.cloud.databricks.net"
    with pytest.raises(FlowError) as caught:
        ensure_local(host, allow_remote=False)
    assert "adb-900" not in str(caught.value)
    assert "databricks" not in str(caught.value)
    table = report(
        {
            "DATABRICKS_HOST": "",
            "KAFKA_BOOTSTRAP": "",
            "CLOUD_URI": "s3://syn-paperlane-landing/orders",
            "MLFLOW_TRACKING_URI": "",
        },
        allow_remote=False,
    )
    assert table["databricks_workspace"] == "not-run"
    assert table["kafka_broker"] == "not-run"
    assert table["cloud_storage"] == "blocked"
    assert table["unity_catalog"] == "not-run"
    assert table["lakeflow_service"] == "not-run"
    assert table["sql_warehouse"] == "not-run"
    assert table["mlflow"] == "local-file"
    assert table["deployment"] == "NO-GO"
    assert classify("localhost:9092", allow_remote=False) == "local"
    assert classify(r"F:\agy\landing", allow_remote=False) == "local"


def test_grants_hide_bronze_and_other_tenants() -> None:
    assert principal_from_token("lab-leta") == LETA
    assert principal_from_token("lab-nope") is None
    assert allow(LETA, "SELECT", "paperlane.gold.daily_category_revenue")
    assert not allow(LETA, "SELECT", "paperlane.bronze.orders")
    assert not column_allowed(LETA, "paperlane.bronze.orders", "email")
    assert allow(OMAR, "MODIFY", "paperlane.gold")
    assert not allow(LETA, "MODIFY", "paperlane.gold")
    rows = [order_record(1), *inkwell_orders()]
    status, visible = visible_rows(OMAR, "paperlane.bronze.orders", rows)
    assert status == "ok"
    assert {str(row["tenant_id"]) for row in visible} == {TENANT}
    denied, hidden = visible_rows(PRUE, "paperlane.gold.daily_category_revenue", rows)
    assert denied == "denied"
    assert hidden == []
    assert PRUE.tenant_id == OTHER_TENANT
