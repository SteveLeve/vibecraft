# VibeCraft Copilot Instructions

VibeCraft is an AI-powered Minecraft WorldEdit MCP server. It exposes 46 MCP tools that allow AI clients (Claude) to build structures in Minecraft via a Fabric client mod (WebSocket) or RCON.

## Repository Structure

```
vibecraft/
├── mcp-server/src/vibecraft/   # Python MCP server
│   ├── server.py               # Entry point, tool dispatcher
│   ├── tool_schemas.py         # MCP tool definitions (all 46 tools)
│   ├── tools/__init__.py       # Tool registry (TOOL_REGISTRY dict)
│   ├── tools/*.py              # Handler implementations
│   ├── client_bridge.py        # WebSocket connection to Fabric mod
│   ├── rcon_manager.py         # Legacy RCON connection
│   ├── code_sandbox.py         # AST-safe Python executor for build()
│   └── data/                   # JSON data files (items, furniture, patterns)
├── agent/                      # Claude Code workspace for building in Minecraft
│   ├── AGENTS.md               # Agent system prompt
│   ├── .claude/skills/         # 7 building skill files
│   └── context/                # Reference guides (architectural styles, etc.)
└── client-mod/                 # Fabric mod source (Java)
```

## Commands

```bash
# Dependencies
cd mcp-server && uv sync

# Run tests
cd mcp-server && uv run pytest
cd mcp-server && uv run pytest tests/test_schematic_tools.py        # single file
cd mcp-server && uv run pytest -v --cov=src/vibecraft                # with coverage

# Type checking
cd mcp-server && uv run mypy src/

# Linting
cd mcp-server && uv run ruff check src/

# Run MCP server (stdio – used by Claude Code)
cd mcp-server && uv run python -m src.vibecraft.server

# Run MCP server (SSE/HTTP – for debugging, listens on :8765)
cd mcp-server && ./start-vibecraft.sh

# Minecraft server
docker compose up -d
docker compose logs -f minecraft
```

## Architecture

### Communication: Client Bridge vs RCON

**Primary (Client Bridge):** MCP server ↔ WebSocket ↔ Fabric client mod ↔ Minecraft server  
**Legacy (RCON):** MCP server ↔ RCON protocol ↔ Minecraft server (no client required)

The client bridge is preferred because it executes commands as the player (required for WorldEdit `//` commands). Configured via env vars: `VIBECRAFT_CLIENT_HOST` (default `127.0.0.1`), `VIBECRAFT_CLIENT_PORT` (default `8766`).

RCON is the fallback for headless/server-only environments. Configured via `VIBECRAFT_RCON_HOST/PORT/PASSWORD`.

### Adding a New MCP Tool

Always modify **three files**:

1. **`tool_schemas.py`** – Add a `Tool(name=..., description=..., inputSchema=...)` object to the schema list.
2. **`tools/<category>_tools.py`** – Implement the handler (see signature below).
3. **`tools/__init__.py`** – Import the handler and add it to `TOOL_REGISTRY["tool_name"] = handle_tool_name`.

**Handler signature (required):**
```python
async def handle_tool_name(
    arguments: Dict[str, Any],
    rcon: ClientBridge,
    config: VibeCraftConfig,
    logger: logging.Logger,
) -> List[TextContent]:
    ...
    return [TextContent(type="text", text="...")]
```

### `build()` Tool and code_sandbox.py

The `build` tool accepts either a `commands` list or a `code` string. When `code` is provided, `code_sandbox.py` executes it in a restricted Python environment:
- AST whitelist (no imports, no `eval`/`exec`, no attribute access to dunder names)
- Max 10,000 commands, 100,000 iterations, 50KB code size, 5s timeout
- Available builtins: `range`, `math`, `sum`, `min`, `max`, `abs`, `round`, `int`, `float`, `str`, `len`, `list`, `enumerate`, `zip`

The code must populate a `commands` list:
```python
commands = []
for x in range(10):
    commands.append(f"//set stone")
```

### WorldEdit Commands

- Send `//` commands directly via `rcon.execute_command(cmd)` — the client bridge handles player context automatically.
- Use comma-separated coordinates: `//pos1 100,64,200` (not space-separated).
- **Never** wrap WorldEdit commands with `execute as <player>` — that's handled internally.
- `prepare_worldedit_command()` in `core_tools.py` handles single-command wrapping when needed.

### Error Handling

Return errors as `TextContent` with an emoji prefix:
```python
return [TextContent(type="text", text="❌ Error: {message}")]
```
Or raise a `ValueError`/`RuntimeError` — `server.py`'s `call_tool()` catches exceptions and formats them as `"❌ Error: {str(e)}"`.

Block validation: use `validate_commands_blocks(commands)` before executing if user-supplied commands contain block names.

### Data Files

JSON files in `mcp-server/data/` are loaded on-demand:
- `minecraft_items_filtered.json` – item registry
- `minecraft_furniture_catalog.json` – 66+ furniture schematics
- `building_patterns_structured.json` – 50+ architectural patterns
- `building_templates.json`, `terrain_patterns_complete.json`, `minecraft_furniture_layouts.json`

## Key Configuration (env vars)

| Variable | Default | Notes |
|---|---|---|
| `VIBECRAFT_CLIENT_PORT` | `8766` | WebSocket port for Fabric mod |
| `VIBECRAFT_WORLDEDIT_MODE` | `off` | `auto` \| `force` \| `off` |
| `VIBECRAFT_WORLDEDIT_FALLBACK` | `warn` | `warn` \| `disable` \| `auto` |
| `VIBECRAFT_ENABLE_SAFETY_CHECKS` | `true` | Toggle command validation |
| `VIBECRAFT_RCON_PASSWORD` | `minecraft` | RCON password (legacy) |

## Testing Patterns

Tests use `pytest-asyncio` with `asyncio_mode = "auto"`. Use a `FakeConnection` stub (see `test_client_bridge.py`) to simulate WebSocket without a real Minecraft instance. Integration tests in `test_client_bridge_integration.py` require a live WebSocket server.

```python
@pytest.mark.asyncio
async def test_example():
    result = await handle_tool(arguments, rcon, config, logger)
    assert "stone" in result[0].text
```

## Agent vs MCP Server

The `agent/` folder is a separate Claude Code workspace for *using* VibeCraft to build in Minecraft — it's a client of the MCP server. The MCP server itself lives in `mcp-server/`. Don't mix concerns: agent skills/prompts live in `agent/`, server logic lives in `mcp-server/`.

To develop agent behavior (skills, system prompt), edit files in `agent/.claude/skills/` and `agent/AGENTS.md`, then run `claude` from the `agent/` directory to test.
