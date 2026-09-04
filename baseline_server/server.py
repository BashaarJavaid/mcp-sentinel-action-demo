import anyio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool

runtime = Server("baseline-runtime")
register_runtime_call = runtime.call_tool
fixture_token = "ghp_0123456789abcdefghijklmnop"


@runtime.list_tools()
async def list_runtime_tools() -> list[Tool]:
    def schema(name: str) -> dict[str, object]:
        return {
            "type": "object",
            "properties": {name: {"type": "string"}},
            "required": [name],
            "additionalProperties": False,
        }

    return [
        Tool(name="dangerous", inputSchema=schema("expression")),
        Tool(name="ungranted_echo", inputSchema=schema("value")),
    ]


@register_runtime_call(validate_input=False)
async def call_runtime_tool(name: str, payload: dict[str, object]) -> dict[str, object]:
    if name == "ungranted_echo":
        return {"result": payload.get("value")}
    if name != "dangerous":
        raise ValueError("unknown tool")
    expression = payload.get("expression")
    if not isinstance(expression, str) or len(expression) > 4096:
        return {"result": "accepted"}
    return {"result": eval(expression)}


async def run_stdio() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await runtime.run(
            read_stream,
            write_stream,
            runtime.create_initialization_options(),
        )


if __name__ == "__main__":
    anyio.run(run_stdio)
