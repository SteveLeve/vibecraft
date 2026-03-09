---
name: command-blocks
description: Places and configures command blocks in Minecraft using VibeCraft MCP tools. Use when adding game logic, scoreboards, player effects, teleportation triggers, NPC dialogue, or any automation that requires command blocks rather than redstone alone.
---

# Command Blocks

## Block Types

| Block ID | Behavior | Use For |
|----------|----------|---------|
| `command_block` | Impulse — runs once per redstone signal | One-shot triggers, doors, events |
| `repeating_command_block` | Runs every game tick while powered | Timers, continuous checks, polling |
| `chain_command_block` | Runs when the block it faces from fires | Sequential command chains |

**Block states:** `[facing=north\|south\|east\|west\|up\|down, conditional=true\|false]`
- `conditional=true` — only runs if the previous block in chain succeeded

## Placement via VibeCraft

Command blocks require NBT to set their command. Use `/setblock` with escaped curly braces in f-strings:

```python
build(commands=[
    # Impulse, always active (auto:1b), facing east
    '/setblock 100 64 200 command_block[facing=east]{Command:"say Game starting!",auto:1b}',

    # Repeating, always active — runs every tick
    '/setblock 100 64 201 repeating_command_block[facing=east]{Command:"scoreboard players add @a timer 1",auto:1b}',

    # Chain, conditional — runs only if previous succeeded
    '/setblock 101 64 201 chain_command_block[facing=east,conditional=true]{Command:"say Timer incremented",auto:1b}',
])
```

**NBT fields:**
- `Command:"..."` — the command to run (no leading `/`)
- `auto:1b` — always active, no redstone needed
- `CustomName:'{"text":"Name"}'` — label shown in GUI
- `TrackOutput:0b` — disable last output display (cleaner)

**Important:** Escape `{` and `}` as `{{` and `}}` when inside Python f-strings.

## Core Game Commands (1.21 syntax)

### /execute
```
execute as <selector> at @s run <command>
execute if score <target> <obj> matches <range> run <command>
execute if block <x> <y> <z> <block> run <command>
execute as @a[gamemode=survival,distance=..10] at @s run effect give @s speed 1 10 1
```

### /scoreboard
```
# Setup (run once, usually via build() or manually)
scoreboard objectives add kills playerKillCount
scoreboard objectives add timer dummy
scoreboard objectives setdisplay sidebar kills

# In command blocks
scoreboard players add @a timer 1
scoreboard players set @a[tag=dead] timer 0
scoreboard players operation @a score += @a bonus
execute if score @p timer matches 200.. run say Time's up!
```

### /tellraw — Rich text to players
```
tellraw @a {"text":"Welcome!","color":"gold","bold":true}
tellraw @a [{"text":"Kills: ","color":"white"},{"score":{"name":"@p","objective":"kills"}}]
tellraw @a {"text":"Click here","clickEvent":{"action":"run_command","value":"/join"}}
```

### /effect
```
effect give @a speed 30 2 true      # 30s, level 3, hide particles
effect give @a[tag=lobby] saturation 99999 1 true
effect clear @a                      # Remove all effects
```

### /tp and /teleport
```
tp @a 100 64 200                    # Teleport all players to coords
tp @a[tag=team_red] 50 64 50        # Teleport tagged players
tp @p @e[type=armor_stand,name=spawn_point]  # Teleport to named entity
```

### /tag
```
tag @a add lobby
tag @a[score_kills_min=10] add winner
tag @e[tag=winner] remove lobby
```

### /gamemode
```
gamemode adventure @a               # Lock breaking/placing
gamemode survival @a[tag=playing]
gamemode spectator @a[tag=dead]
```

### /fill — Arena reset
```
fill 80 63 80 120 80 120 air        # Clear arena
fill 80 63 80 120 63 120 stone      # Reset floor
```

## Selector Arguments

```
@a                         # All players
@a[tag=playing]            # Tagged players
@a[distance=..10]          # Within 10 blocks of command block
@a[scores={kills=5..}]     # Score ≥ 5
@a[scores={timer=..0}]     # Timer ≤ 0
@a[gamemode=survival]
@e[type=armor_stand,name=lobby_spawn]
@r                         # Random player
@p                         # Nearest player
```

## Command Block Chains

Run sequential commands by chaining `chain_command_block` blocks facing each other:

```python
build(commands=[
    # Block 1 (impulse trigger — activated by button/pressure plate)
    '/setblock 100 64 200 command_block[facing=east]{Command:"gamemode adventure @a",auto:0b}',
    # Block 2 (chain — runs after block 1)
    '/setblock 101 64 200 chain_command_block[facing=east]{Command:"tp @a 0 64 0",auto:1b}',
    # Block 3 (chain — runs after block 2)
    '/setblock 102 64 200 chain_command_block[facing=east]{Command:"title @a title \\"Game Start\\"",auto:1b}',
    # Block 4 (chain — runs after block 3)
    '/setblock 103 64 200 chain_command_block[facing=east]{Command:"playsound minecraft:entity.player.levelup master @a",auto:1b}',
])
```

## Title / Subtitle Display

```
title @a title {"text":"GAME OVER","color":"red","bold":true}
title @a subtitle {"text":"You were eliminated","color":"gray"}
title @a actionbar {"text":"Kills: 3","color":"yellow"}
title @a times 10 40 10            # Fade in (ticks), stay, fade out
```

## Armor Stand NPCs

Armor stands as invisible markers or visible "NPCs":

```python
build(commands=[
    # Invisible marker at a point (used as named teleport target)
    '/summon armor_stand 0 63 0 {CustomName:\'{"text":"spawn_point"}\',Invisible:1b,NoGravity:1b,Marker:1b}',
    # Visible NPC with name tag
    '/summon armor_stand 10 64 10 {CustomName:\'{"text":"Shop Keeper"}\',CustomNameVisible:1b,NoGravity:1b,Small:0b}',
])
```

## Common Patterns

### Pressure plate trigger
```python
build(commands=[
    '/setblock 0 64 0 stone',
    '/setblock 0 65 0 stone_pressure_plate',
    '/setblock 0 63 0 command_block[facing=up]{Command:"tp @a[distance=..2] 100 65 100",auto:0b}',
])
```

### Timer countdown (repeating → chain)
```python
build(commands=[
    # Count up every tick
    '/setblock 0 64 0 repeating_command_block{Command:"scoreboard players add @a timer 1",auto:1b}',
    # Check if time limit reached (200 ticks = 10 seconds)
    '/setblock 1 64 0 chain_command_block[facing=east]{Command:"execute if score @a timer matches 200.. run function vibecraft:end_game",auto:1b}',
])
```
