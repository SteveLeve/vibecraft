---
name: debug-connection
description: Use when VibeCraft tools return errors, connections fail, player is not found, WorldEdit commands don't execute, or the WebSocket/SSE connection between Minecraft client and MCP server is broken.
---

# Debug Connection

## Diagnostic Checklist

Work through these in order — each step eliminates a category of failure.

### Step 1: Is Minecraft running?

The Fabric client mod runs inside the Minecraft game client, not the server.
- Minecraft must be **open** and in a **loaded world**
- The mod only activates when you're in-game (not on the main menu)

### Step 2: Is the client mod loaded?

In the Minecraft chat, run:
```
/vibecraft status
```
- `✅ VibeCraft active` → mod is loaded and running
- Command not found → mod not installed or wrong Minecraft version
- Check mod jar: `client-mod/build/release/vibecraft-client-0.1.0-mc<version>.jar`

### Step 3: Is AI control enabled?

```
/vibecraft allow
```
Run this in-game to allow the MCP server to send commands. Required every session (or configure auto-allow in mod settings).

### Step 4: Is the MCP server running?

```bash
# Check if SSE server is up
curl -N http://127.0.0.1:8765/sse

# Or check for the process
pgrep -f "vibecraft.server" || pgrep -f "server_http"
```

Start if not running:
```bash
cd mcp-server && ./start-vibecraft.sh
```

### Step 5: Port check

| Component | Protocol | Default Port |
|-----------|----------|-------------|
| MCP server (SSE) | HTTP/SSE | `8765` |
| Client mod bridge | WebSocket | `8766` |

- MCP server config: `VIBECRAFT_CLIENT_PORT=8766` (must match mod's port)
- Mod config: check `config/vibecraft-client.json` in your Minecraft folder

### Step 6: WorldEdit mode

```bash
# Check current mode (default: auto)
echo $VIBECRAFT_WORLDEDIT_MODE

# Force WorldEdit on
export VIBECRAFT_WORLDEDIT_MODE=force
```

Modes: `auto` (detect), `force` (require), `off` (disable)

## Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `Connection refused 8766` | Client mod not running or AI not allowed | Run `/vibecraft allow` in-game |
| `Player not found` | No player in world / wrong player name | Enter a world, check `get_player_position` |
| `WorldEdit not available` | WorldEdit mod not installed | Install WorldEdit for Fabric |
| `WebSocket timeout` | Minecraft paused or frozen | Unpause the game |
| `401 Unauthorized` | Token mismatch | Check `VIBECRAFT_CLIENT_TOKEN` env var |
| `tools/list empty` | MCP server not registered | Add to Claude Code MCP config |

## Check Server Logs

```bash
# MCP server logs (if running in SSE mode)
tail -f mcp-server/logs/vibecraft.log

# Minecraft logs
tail -f ~/.minecraft/logs/latest.log | grep -i vibecraft
```

## Full Stack Restart

When in doubt:
```bash
# 1. Kill existing server
pkill -f "vibecraft.server" || pkill -f "server_http"

# 2. Restart MCP server
cd mcp-server && ./start-vibecraft.sh &

# 3. In Minecraft: quit to menu and re-enter world, then /vibecraft allow
```
