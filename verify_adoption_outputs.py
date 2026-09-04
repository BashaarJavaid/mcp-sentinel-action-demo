"""Verify Phase 12 baseline Action output and its live-review budget."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, cast

RANK = {"informational": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("sarif", type=Path)
    parser.add_argument("findings", type=int)
    parser.add_argument("highest")
    parser.add_argument("matched", type=int)
    parser.add_argument("new", type=int)
    parser.add_argument("--additional-sarif", type=Path, action="append", default=[])
    args = parser.parse_args()

    payload = _load(args.sarif)
    run = payload["runs"][0]
    results = run.get("results", [])
    properties = run["invocations"][0]["properties"]
    baseline = properties["baseline"]
    assert run["tool"]["driver"]["version"] == "1.2.0"
    assert properties["analysisComplete"] is True
    assert len(results) == properties["findingCount"] == args.findings
    assert baseline["matched_finding_count"] == args.matched
    assert baseline["new_finding_count"] == args.new
    assert sum(item["baselineState"] == "unchanged" for item in results) == args.matched
    assert sum(item["baselineState"] == "new" for item in results) == args.new

    severities = [
        item["properties"]["severity"].lower()
        for item in results
        if item["properties"]["status"] != "suppressed"
        and item["properties"]["baselineMatched"] is not True
    ]
    highest = max(severities, key=RANK.__getitem__) if severities else "none"
    assert highest == args.highest

    reports = (payload, *(_load(path) for path in args.additional_sarif))
    cost = sum(
        report["runs"][0]["invocations"][0]["properties"]["gptReview"][
            "origin_cost_micro_usd"
        ]
        or 0
        for report in reports
    )
    assert cost <= 750_000
    print(
        f"verified {args.findings} findings ({args.matched} matched, "
        f"{args.new} new); live cost ${cost / 1_000_000:.6f}"
    )
    return 0


def _load(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    raise SystemExit(main())
