"""Measure the pure study and, when Java is present, local Spark SQL."""

from __future__ import annotations

import json
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Any

from lakehouse_poc.spark_job import java_ready
from lakehouse_poc.study import run_study


def hardware() -> dict[str, Any]:
    script = (
        "$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1 "
        "Name, NumberOfCores, NumberOfLogicalProcessors; "
        "$os = Get-CimInstance Win32_OperatingSystem | Select-Object "
        "FreePhysicalMemory, TotalVisibleMemorySize; "
        "[pscustomobject]@{name=$cpu.Name; cores=$cpu.NumberOfCores; "
        "logical=$cpu.NumberOfLogicalProcessors; free_kb=[int64]$os.FreePhysicalMemory; "
        "total_kb=[int64]$os.TotalVisibleMemorySize} | ConvertTo-Json -Compress"
    )
    completed = subprocess.run(
        ["powershell", "-NoProfile", "-Command", script],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    return {
        "processor": payload["name"],
        "cores": payload["cores"],
        "logical_processors": payload["logical"],
        "free_physical_memory_kb": payload["free_kb"],
        "total_visible_memory_kb": payload["total_kb"],
        "python": platform.python_version(),
        "system": platform.system(),
    }


def spark_section(root: Path) -> dict[str, Any]:
    if not (shutil.which("java") or java_ready()):
        return {"status": "not-run", "reason": "java_absent", "sql_warehouse": "not-run"}
    from lakehouse_poc.spark_job import build_session, time_queries

    session = build_session()
    try:
        timings = time_queries(session, root / "spark-bench")
        timings["status"] = "ran"
        timings["spark"] = session.version
        return timings
    finally:
        session.stop()


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    summary = run_study(tracking_dir=root / "mlruns")
    summary["hardware"] = hardware()
    summary["spark_sql"] = spark_section(root / "warehouse")
    out = root / "benchmarks" / "latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "recommendation": summary["recommendation"],
                "logistic_f1": summary["logistic_f1"],
                "spark": summary["spark_sql"].get("status"),
            }
        )
    )


if __name__ == "__main__":
    main()
