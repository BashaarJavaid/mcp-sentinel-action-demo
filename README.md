# MCP Sentinel Action Demo

Public Phase 8 proof for
[MCP Sentinel](https://github.com/BashaarJavaid/MCP-Sentinel).

The workflow scans paired clean and deliberately vulnerable Python MCP servers
with the composite Action's signed `v1` alias, which resolves to release
`v1.0.0` at commit `8e8868243872ac34990dda1d4751bbee8dc322d3`.

- The clean target must complete with no findings.
- The vulnerable target must upload all 11 `SENT-001` through `SENT-011`
  findings and fail at the `high` threshold.
- The workflow asserts that Action outputs match each validated SARIF 2.1.0
  report emitted by MCP Sentinel `1.0.0`.
- Both reports are retained as workflow artifacts for 90 days.

The token-like string in `vulnerable_server/server.py` is inert fixture data,
not a real credential.

The manual `adoption.yml` workflow proves Phase 12 against either exact
`v1.2.0` or the signed `v1` alias. Its dedicated `baseline_server` has one
static and four dynamic accepted findings: an unchanged scan passes with all
five visible, while adding one inert secret produces exactly one new failing
finding. The exact proof also installs the public pre-commit hook and exercises
clean, vulnerable, and inline-suppressed cases.
