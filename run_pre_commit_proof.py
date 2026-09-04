"""Run the public v1.2.0 hook against clean, vulnerable, and suppressed cases."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="sentinel-pre-commit-proof-") as raw:
        temporary = Path(raw)
        cache = temporary / "cache"
        for name, expected in (("clean", 0), ("vulnerable", 1), ("suppressed", 0)):
            target = temporary / name
            fixture = "clean_server" if name == "clean" else "vulnerable_server"
            shutil.copytree(ROOT / fixture, target)
            if name == "suppressed":
                server = target / "server.py"
                server.write_text(
                    server.read_text(encoding="utf-8").replace(
                        'api_key = "ghp_0123456789abcdefghijklmnop"',
                        'api_key = "ghp_0123456789abcdefghijklmnop"  '
                        "# sentinel: ignore[SENT-005] reason=inert fixture token",
                    ),
                    encoding="utf-8",
                )
            (target / ".pre-commit-config.yaml").write_text(
                """\
minimum_pre_commit_version: 4.6.2
repos:
  - repo: https://github.com/BashaarJavaid/MCP-Sentinel
    rev: v1.2.0
    hooks:
      - id: mcp-sentinel
        args: [--rules, SENT-005]
        verbose: true
""",
                encoding="utf-8",
            )
            _run(("git", "init", "-q"), target)
            _run(("git", "config", "user.name", "MCP Sentinel Proof"), target)
            _run(("git", "config", "user.email", "proof@example.invalid"), target)
            _run(("git", "add", "."), target)
            _run(("git", "commit", "-qm", "fixture"), target)
            completed = _run(
                (
                    sys.executable,
                    "-m",
                    "pre_commit",
                    "run",
                    "--all-files",
                    "--show-diff-on-failure",
                ),
                target,
                env={**os.environ, "PRE_COMMIT_HOME": str(cache)},
                check=False,
            )
            output = completed.stdout + completed.stderr
            assert completed.returncode == expected, output
            if name == "suppressed":
                assert "Inline suppression:" in output
            print(f"{name}: exit {completed.returncode}")
    return 0


def _run(
    command: tuple[str, ...],
    cwd: Path,
    *,
    env: dict[str, str] | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command, cwd=cwd, env=env, check=check, text=True, capture_output=True
    )


if __name__ == "__main__":
    raise SystemExit(main())
