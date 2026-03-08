---
name: write-tests
description: Use when writing tests for new or modified VibeCraft MCP server tools, modules, or handlers. Covers test location, framework setup, async patterns, mocking, and integration test marking.
---

# Write Tests

## Setup

- **Test directory**: `mcp-server/tests/`
- **Framework**: pytest + pytest-asyncio (`asyncio_mode = "auto"` in pyproject.toml)
- **Run tests**: `cd mcp-server && uv run pytest -x -q -m "not integration"`
- **`sys.path`**: `conftest.py` automatically adds `src/` — import as `from vibecraft.X import Y`

## Test Patterns

### Unit Test (mock the connection)

```python
# tests/test_my_tool.py
import pytest
from vibecraft.tools.my_module import handle_my_new_tool
from vibecraft.config import VibeCraftConfig
import logging

logger = logging.getLogger(__name__)


class FakeRcon:
    """Mock rcon/client for unit tests."""
    def __init__(self, response="OK"):
        self.last_command = None
        self._response = response

    async def run_command(self, cmd: str) -> str:
        self.last_command = cmd
        return self._response


async def test_my_tool_success():
    fake_rcon = FakeRcon(response="done")
    config = VibeCraftConfig()

    result = await handle_my_new_tool(
        arguments={"action": "query"},
        rcon=fake_rcon,
        config=config,
        logger_instance=logger,
    )

    assert len(result) == 1
    assert "✅" in result[0].text
    assert fake_rcon.last_command is not None


async def test_my_tool_missing_action():
    result = await handle_my_new_tool(
        arguments={},
        rcon=FakeRcon(),
        config=VibeCraftConfig(),
        logger_instance=logger,
    )
    assert "❌" in result[0].text
```

### WebSocket Mock (for ClientBridge tests)

The existing `test_client_bridge.py` has a `FakeConnection` class that simulates WebSocket. Reuse it:

```python
from tests.test_client_bridge import FakeConnection, make_client

def test_with_fake_websocket():
    fake = FakeConnection(preloaded=[
        '{"type": "result", "id": "1", "success": true, "data": "OK"}'
    ])
    client = make_client(fake)
    # use client as rcon...
```

### Integration Test (requires live server)

Mark with `@pytest.mark.integration` — these are skipped in normal runs:

```python
import pytest

@pytest.mark.integration
async def test_my_tool_live():
    """Requires Minecraft + mod running."""
    from vibecraft.client_bridge import ClientBridge
    from vibecraft.config import VibeCraftConfig
    config = VibeCraftConfig()
    client = ClientBridge(config)
    result = await handle_my_new_tool(
        arguments={"action": "query"},
        rcon=client,
        config=config,
        logger_instance=logging.getLogger(__name__),
    )
    assert result
```

## Run Commands

```bash
cd mcp-server

# Unit tests only (default)
uv run pytest -x -q -m "not integration"

# All tests including integration (requires live server)
uv run pytest -x -q

# Specific file
uv run pytest tests/test_my_tool.py -v

# With coverage report
uv run pytest --cov=src/vibecraft --cov-report=html -m "not integration"
```

## What to Test

For each new tool handler, cover:
- Happy path with expected input
- Missing required argument → returns `❌` error TextContent
- Command is sent with correct format (check `fake_rcon.last_command`)
- Edge cases specific to the tool (empty string, boundary values)

## Quick Reference

| Fixture / Class | File | Purpose |
|----------------|------|---------|
| `FakeConnection` | `tests/test_client_bridge.py` | Mock WebSocket for ClientBridge |
| `make_client(fake)` | `tests/test_client_bridge.py` | Build ClientBridge with fake connection |
| `VibeCraftConfig()` | `vibecraft.config` | Default config (uses env vars) |
| `asyncio_mode = "auto"` | `pyproject.toml` | No `@pytest.mark.asyncio` needed |

## Common Mistakes

- **Forgetting async**: All handlers are `async def` — test functions must also be `async def`
- **Adding `@pytest.mark.asyncio`**: Not needed — `asyncio_mode = "auto"` handles it
- **Importing from wrong path**: Use `from vibecraft.X import Y` (not `from src.vibecraft...`)
- **Running integration tests locally**: Use `-m "not integration"` to skip them
