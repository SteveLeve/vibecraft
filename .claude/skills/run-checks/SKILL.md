---
name: run-checks
description: Run the full VibeCraft quality check suite (ruff, mypy, pytest). Use before committing changes to mcp-server code.
disable-model-invocation: true
---

Run these three commands in sequence from the mcp-server directory and report results:

```bash
cd /home/steve-leve/projects/vibecraft/mcp-server

# 1. Lint
/home/steve-leve/.local/bin/uv run ruff check src/

# 2. Type check
/home/steve-leve/.local/bin/uv run mypy src/vibecraft --ignore-missing-imports

# 3. Tests
/home/steve-leve/.local/bin/uv run pytest -q
```

Report: ✅ All checks passed if all three succeed, or ❌ with the first failure output if any fail. Stop at the first failure — no need to run subsequent checks.
