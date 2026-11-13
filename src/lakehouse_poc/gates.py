"""Gate table. Unset targets stay not-run. This module does not open a socket."""

from __future__ import annotations

import os
from collections.abc import Mapping

from lakehouse_poc.synthetic import ORG

LOCAL_HOSTS = frozenset({"localhost", "127.0.0.1", "::1"})


class FlowError(Exception):
    pass


def _host(value: str) -> str:
    text = value.strip()
    for prefix in ("https://", "http://"):
        if text.startswith(prefix):
            rest = text[len(prefix) :]
            return rest.split("/", 1)[0].split(":", 1)[0]
    if "://" in text:
        return "remote"
    if ":" in text and not text[1:2].startswith(":\\") and "/" not in text.split(":", 1)[0]:
        return text.split(":", 1)[0]
    return ""


def classify(value: str, allow_remote: bool) -> str:
    text = value.strip()
    if text == "":
        return "not-run"
    lowered = text.lower()
    if len(text) >= 3 and text[1] == ":" and text[2] in "\\/":
        return "local"
    if lowered.startswith(("s3://", "abfss://", "gs://", "wasbs://")):
        return "remote" if allow_remote else "blocked"
    host = _host(text).lower()
    if host in LOCAL_HOSTS or lowered.startswith("file:"):
        return "local"
    if host == "" and "://" not in lowered:
        return "local"
    return "remote" if allow_remote else "blocked"


def ensure_local(value: str, allow_remote: bool) -> str:
    kind = classify(value, allow_remote=allow_remote)
    if kind == "blocked":
        raise FlowError("remote_blocked")
    return kind


def report(
    env: Mapping[str, str] | None = None,
    allow_remote: bool | None = None,
) -> dict[str, str]:
    source = os.environ if env is None else env
    if allow_remote is None:
        allow_remote = source.get("LAKEHOUSE_ALLOW_REMOTE", "") == "1"
    mlflow_uri = source.get("MLFLOW_TRACKING_URI", "")
    mlflow_state = "local-file" if mlflow_uri.strip() == "" else classify(mlflow_uri, allow_remote)
    return {
        "organization": ORG,
        "notice": "SYNTHETIC_POC_NOT_A_DEPLOYMENT",
        "databricks_workspace": classify(source.get("DATABRICKS_HOST", ""), allow_remote),
        "kafka_broker": classify(source.get("KAFKA_BOOTSTRAP", ""), allow_remote),
        "cloud_storage": classify(source.get("CLOUD_URI", ""), allow_remote),
        "unity_catalog": "not-run",
        "lakeflow_service": "not-run",
        "sql_warehouse": "not-run",
        "mlflow": mlflow_state,
        "deployment": "NO-GO",
    }
