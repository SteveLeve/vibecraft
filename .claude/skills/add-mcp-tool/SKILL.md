---
name: add-mcp-tool
description: Use when adding a new tool to the VibeCraft MCP server, creating a handler function, registering it in the tool registry, or defining a new tool schema.
---

# Add MCP Tool

## Overview

Adding a new MCP tool requires three coordinated steps: schema definition, handler implementation, and registry registration.

## Steps

### 1. Define Schema in `tool_schemas.py`

Add a `Tool` object to the list in `get_tool_schemas()`:

```python
# mcp-server/src/vibecraft/tool_schemas.py
Tool(
    name="my_new_tool",
    description="""One-line summary for the AI agent.

Detailed explanation of what this tool does.
Include key behaviors, constraints, and examples.

Example:
- my_new_tool action=do_thing param=value
""",
    inputSchema={
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "What to do (e.g., 'query', 'set', 'clear')",
            },
            "value": {
                "type": "string",
                "description": "Optional value",
            },
        },
        "required": ["action"],
    },
),
```

### 2. Create Handler Function

Create in an existing module (or new file in `tools/`):

```python
# mcp-server/src/vibecraft/tools/my_module.py
from typing import Dict, Any, List
from mcp.types import TextContent
import logging

logger = logging.getLogger(__name__)


async def handle_my_new_tool(
    arguments: Dict[str, Any],
    rcon,           # ClientBridge or RCONManager - use rcon.run_command(cmd)
    config,         # VibeCraftConfig instance
    logger_instance # logging.Logger
) -> List[TextContent]:
    """Handle my_new_tool."""
    action = arguments.get("action", "")

    if not action:
        return [TextContent(type="text", text="❌ action is required")]

    # Execute a command via the client bridge
    result = await rcon.run_command(f"/some command {action}")

    return [TextContent(type="text", text=f"✅ Done: {result}")]
```

### 3. Register in `tools/__init__.py`

Two options — use whichever fits the module pattern:

```python
# Option A: Direct assignment (most common pattern)
from . import my_module
TOOL_REGISTRY["my_new_tool"] = my_module.handle_my_new_tool

# Option B: Decorator (add inside the handler file)
from . import register_tool

@register_tool("my_new_tool")
async def handle_my_new_tool(arguments, rcon, config, logger_instance):
    ...
```

### 4. Test

```bash
cd mcp-server
# Run unit tests
uv run pytest -x -q -m "not integration"

# Verify server starts and lists tools (stdio mode)
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | uv run python -m src.vibecraft.server
```

### 5. Update Agent Docs

If the tool is agent-facing, add it to the appropriate section in `agent/AGENTS.md`:

```markdown
## MCP Tools
**My Category**: `my_new_tool` - brief description
```

## Quick Reference

| File | What to Change |
|------|---------------|
| `src/vibecraft/tool_schemas.py` | Add `Tool(name=..., description=..., inputSchema=...)` |
| `src/vibecraft/tools/<module>.py` | Add `async def handle_<tool_name>(arguments, rcon, config, logger_instance)` |
| `src/vibecraft/tools/__init__.py` | Add `TOOL_REGISTRY["tool_name"] = module.handle_tool_name` |
| `agent/AGENTS.md` | Add tool to MCP Tools section (if user-facing) |

## Common Mistakes

- **Missing from registry**: Handler defined but not added to `TOOL_REGISTRY` — tool won't appear in `tools/list`
- **Wrong return type**: Must return `List[TextContent]`, not a string
- **Sync handler**: Must be `async def` — sync functions break the server
- **Schema mismatch**: `inputSchema.required` must list only keys in `properties`
