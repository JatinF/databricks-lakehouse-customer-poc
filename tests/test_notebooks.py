from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _cells(path: Path) -> list[str]:
    chunks: list[list[str]] = [[]]
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# Databricks notebook source"):
            continue
        if line.startswith("# COMMAND ----------"):
            chunks.append([])
            continue
        chunks[-1].append(line)
    return ["\n".join(chunk) for chunk in chunks if chunk and "".join(chunk).strip()]


def test_notebooks_execute_the_pure_path() -> None:
    first: dict[str, object] = {}
    for cell in _cells(ROOT / "notebooks" / "01_medallion.py"):
        exec(cell, first, first)
    report = first["report"]
    assert isinstance(report, dict)
    assert report["dq_failures"] == 10
    assert report["inkwell_in_silver"] == 0
    assert report["databricks_workspace"] == "not-run"
    second: dict[str, object] = {}
    for cell in _cells(ROOT / "notebooks" / "02_sql_and_model.py"):
        exec(cell, second, second)
