# MCP Sentinel Action Demo

Public Phase 4 proof for
[MCP Sentinel](https://github.com/BashaarJavaid/MCP-Sentinel).

The workflow scans paired clean and deliberately vulnerable Python MCP servers
with the composite Action pinned to implementation commit
`3528d040b4da7cc37ca50ce59bbd79afb3a3c16c`.

- The clean target must complete with no findings.
- The vulnerable target must upload SARIF and fail at the `high` threshold.
- The workflow asserts that Action outputs match each validated SARIF report.
- Both reports are retained as workflow artifacts for 90 days.

The token-like string in `vulnerable_server/server.py` is inert fixture data,
not a real credential.
