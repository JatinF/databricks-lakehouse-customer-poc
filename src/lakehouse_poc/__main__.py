"""CLI. `gates` prints the not-run table and does not dial."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from lakehouse_poc.dashboard import write_report
from lakehouse_poc.gates import report
from lakehouse_poc.study import run_study


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    command = args[0] if args else "gates"
    if command == "gates":
        print(json.dumps(report(), indent=2))
        return 0
    if command == "demo":
        out = Path(args[1]) if len(args) > 1 else Path("reports")
        summary = run_study()
        out.mkdir(parents=True, exist_ok=True)
        (out / "acceptance.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        write_report(out / "dashboard.html", summary)
        print(json.dumps({"recommendation": summary["recommendation"], "wrote": str(out)}))
        return 0
    print("usage: python -m lakehouse_poc [gates|demo]")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
