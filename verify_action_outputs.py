"""Verify that composite Action outputs describe the emitted SARIF."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, cast

RANK = {
    "informational": 0,
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("sarif", type=Path)
    parser.add_argument("findings_count", type=int)
    parser.add_argument("highest_severity")
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()

    payload = cast(
        dict[str, Any], json.loads(args.sarif.read_text(encoding="utf-8"))
    )
    run = payload["runs"][0]
    results = run.get("results", [])
    invocation = run["invocations"][0]
    assert len(results) == args.findings_count
    assert invocation["properties"]["findingCount"] == args.findings_count
    if args.require_complete:
        assert invocation["properties"]["analysisComplete"] is True

    severities = [
        result["properties"]["severity"].lower()
        for result in results
        if result["properties"]["status"] != "suppressed"
    ]
    highest = max(severities, key=RANK.__getitem__) if severities else "none"
    assert highest == args.highest_severity
    print(
        f"verified {args.findings_count} result(s); highest severity: {highest}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
