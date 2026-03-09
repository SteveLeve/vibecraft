---
name: mini-game-systems
description: Designs and builds Minecraft mini-game systems, adventure maps, and lobby areas using VibeCraft MCP tools. Use when creating game arenas, scoreboards, win/lose conditions, lobby hubs, portal networks, team systems, checkpoints, or player progression mechanics. Combines command blocks, redstone, and procedural building.
---

# Mini-Game Systems

## Design Pattern: Game State Machine

All mini-games follow the same state flow:

```
LOBBY → COUNTDOWN → PLAYING → END → RESET → LOBBY
```

Each state transition is triggered by a command block chain. Build each phase independently.

---

## Lobby Area

### Layout Principles
- Central open space (players mill around)
- Visible signs/titles showing game name and player count
- NPC (armor stand) at each portal/game entrance
- Waiting area with safe spawns, adventure mode

```python
build(commands=[
    # Lobby spawn point marker
    '/summon armor_stand 0 63 0 {CustomName:\'{"text":"lobby_spawn"}\',Invisible:1b,NoGravity:1b,Marker:1b}',

    # Welcome title broadcast (repeating, checks for new joins)
    '/setblock 0 60 0 repeating_command_block{Command:"title @a[tag=!welcomed] title {\\"text\\":\\"Welcome!\\",\\"color\\":\\"gold\\"}",auto:1b}',
    '/setblock 1 60 0 chain_command_block[facing=east]{Command:"tag @a add welcomed",auto:1b}',

    # Lock lobby players to adventure mode
    '/setblock 2 60 0 repeating_command_block{Command:"gamemode adventure @a[tag=lobby]",auto:1b}',
])
```

### Portal to Game
```python
build(commands=[
    # Nether portal frame
    '/fill -2 64 10 2 69 10 obsidian',
    '/fill -1 65 10 1 68 10 nether_portal[axis=x]',

    # Pressure plate in front
    '/setblock 0 64 9 stone',
    '/setblock 0 65 9 stone_pressure_plate',
    # Trigger: teleport to game arena and tag as "playing"
    '/setblock 0 63 9 command_block[facing=up]{Command:"tp @a[distance=..2,tag=lobby] 100 65 200",auto:0b}',
    '/setblock 0 62 9 chain_command_block[facing=down]{Command:"tag @a[distance=..5] add playing",auto:1b}',
    '/setblock 0 61 9 chain_command_block[facing=down]{Command:"tag @a[tag=playing] remove lobby",auto:1b}',
])
```

---

## Scoreboard System

### Setup (run once at world load)

```python
build(commands=[
    # Create objectives (run these via build() or manually in chat)
    '/scoreboard objectives add kills playerKillCount',
    '/scoreboard objectives add deaths deathCount',
    '/scoreboard objectives add timer dummy',
    '/scoreboard objectives add score dummy',

    # Display kills on sidebar
    '/scoreboard objectives setdisplay sidebar kills',

    # Display score in tab list
    '/scoreboard objectives setdisplay list score',
])
```

### In-Game Score Display

```python
build(commands=[
    # Actionbar shows current score (repeating)
    '/setblock 0 60 5 repeating_command_block{Command:"title @a[tag=playing] actionbar [{\\"text\\":\\"Score: \\"},{\\"score\\":{\\"name\\":\\"@p\\",\\"objective\\":\\"score\\"}}]",auto:1b}',
])
```

---

## Team System

```python
build(commands=[
    # Create teams
    '/team add red',
    '/team add blue',
    '/team modify red color red',
    '/team modify blue color blue',
    '/team modify red friendlyFire false',
    '/team modify blue friendlyFire false',

    # Auto-assign players evenly (simplified: tag first half red, rest blue)
    '/team join red @a[tag=playing,limit=4,sort=nearest]',
    '/team join blue @a[tag=playing,team=!red]',
])
```

---

## Arena Reset

Critical for repeatable games. Store the original state as fill commands:

```python
# Define arena bounds
AX1, AY1, AZ1 = 90, 63, 90
AX2, AY2, AZ2 = 110, 80, 110

build(commands=[
    # 1. Clear entire arena volume
    f'/fill {AX1} {AY1} {AZ1} {AX2} {AY2} {AZ2} air',
    # 2. Restore floor
    f'/fill {AX1} {AY1} {AZ1} {AX2} {AY1} {AZ2} stone',
    # 3. Restore walls (north, south, east, west)
    f'/fill {AX1} {AY1} {AZ1} {AX2} {AY2} {AZ1} stone_bricks',
    f'/fill {AX1} {AY1} {AZ2} {AX2} {AY2} {AZ2} stone_bricks',
    f'/fill {AX1} {AY1} {AZ1} {AX1} {AY2} {AZ2} stone_bricks',
    f'/fill {AX2} {AY1} {AZ1} {AX2} {AY2} {AZ2} stone_bricks',
    # 4. Reset scoreboard
    '/scoreboard players reset * kills',
    '/scoreboard players reset * timer',
    '/scoreboard players reset * score',
])
```

---

## Win/Lose Detection

### Score-based win
```python
build(commands=[
    # Check every tick if any player reached 10 kills
    '/setblock 0 60 10 repeating_command_block{Command:"execute as @a[scores={kills=10..}] run tag @s add winner",auto:1b}',
    '/setblock 1 60 10 chain_command_block[facing=east]{Command:"execute if entity @a[tag=winner] run title @a title {\\"text\\":\\"Game Over!\\",\\"color\\":\\"gold\\"}",auto:1b}',
    '/setblock 2 60 10 chain_command_block[facing=east]{Command:"execute if entity @a[tag=winner] run tellraw @a [{\\"text\\":\\"Winner: \\"},{\\"selector\\":\\"@a[tag=winner]\\"}]",auto:1b}',
    '/setblock 3 60 10 chain_command_block[facing=east]{Command:"execute if entity @a[tag=winner] run tp @a 0 65 0",auto:1b}',
])
```

### Time-based game end
```python
build(commands=[
    # Countdown: 1200 ticks = 60 seconds
    '/setblock 0 60 15 repeating_command_block{Command:"scoreboard players add @a[tag=playing,limit=1] timer 1",auto:1b}',
    '/setblock 1 60 15 chain_command_block[facing=east]{Command:"execute if score @a timer matches 1200.. run title @a title {\\"text\\":\\"TIME!\\",\\"color\\":\\"red\\"}",auto:1b}',
    '/setblock 2 60 15 chain_command_block[facing=east]{Command:"execute if score @a timer matches 1200.. run tp @a 0 65 0",auto:1b}',
])
```

### Last-player-standing
```python
build(commands=[
    # Tag dead players as spectators
    '/setblock 0 60 20 repeating_command_block{Command:"gamemode spectator @a[tag=dead,gamemode=survival]",auto:1b}',
    # Win when only one survivor
    '/setblock 1 60 20 chain_command_block[facing=east]{Command:"execute if entity @a[gamemode=survival,limit=1] run tag @a[gamemode=survival] add winner",auto:1b}',
])
```

---

## Adventure Map Patterns

### Checkpoint System
```python
build(code="""
commands = []

# 5 checkpoints along a path
checkpoints = [
    (100, 65, 200),
    (150, 70, 250),
    (200, 65, 300),
    (250, 80, 350),
    (300, 65, 400),
]

for i, (cx, cy, cz) in enumerate(checkpoints):
    # Pressure plate
    commands.append(f'/setblock {cx} {cy} {cz} stone')
    commands.append(f'/setblock {cx} {cy+1} {cz} stone_pressure_plate')
    # Command block below: record checkpoint number to scoreboard
    commands.append(f'/setblock {cx} {cy-1} {cz} command_block[facing=up]{{Command:"scoreboard players set @a[distance=..2] checkpoint {i}",auto:0b}}')
    # Tellraw confirmation
    commands.append(f'/setblock {cx-1} {cy-1} {cz} chain_command_block[facing=east]{{Command:"tellraw @a[distance=..3] {{\\"text\\":\\"Checkpoint {i+1} reached!\\",\\"color\\":\\"green\\"}}",auto:1b}}')
""")
```

### NPC Dialogue (armor stand + trigger)
```python
build(commands=[
    # Armor stand NPC
    '/summon armor_stand 10 64 10 {CustomName:\'{"text":"Village Elder"}\',CustomNameVisible:1b,NoGravity:1b}',

    # Repeating: trigger dialogue when player nearby
    '/setblock 10 60 10 repeating_command_block{Command:"execute as @a[distance=..3,tag=!spoke_elder] at @s run tellraw @s {\\"text\\":\\"The dungeon lies to the north...\\",\\"color\\":\\"yellow\\"}",auto:1b}',
    '/setblock 11 60 10 chain_command_block[facing=east]{Command:"tag @a[distance=..3] add spoke_elder",auto:1b}',
])
```

### Locked Door (requires key item / advancement)
```python
build(commands=[
    # Door blocks
    '/fill 50 64 100 50 66 100 iron_door',

    # Repeating check: open door if player has specific score (quest complete)
    '/setblock 50 60 100 repeating_command_block{Command:"execute as @a[scores={quest1=1..},distance=..5] run setblock 50 64 100 air",auto:1b}',
    '/setblock 51 60 100 chain_command_block[facing=east]{Command:"execute as @a[scores={quest1=1..},distance=..5] run setblock 50 65 100 air",auto:1b}',
    '/setblock 52 60 100 chain_command_block[facing=east]{Command:"execute as @a[scores={quest1=1..},distance=..5] run setblock 50 66 100 air",auto:1b}',
])
```

---

## Lobby Hub: Multi-Game Portal Room

```python
build(code="""
commands = []

# Central hub: circular room with portals around the edge
cx, cy, cz = 0, 64, 0
hub_radius = 15
games = [
    ("Spleef", 0, 100, 65, 0),
    ("PvP Arena", 90, 200, 65, 0),
    ("Parkour", 180, 300, 65, 0),
    ("Maze", 270, 400, 65, 0),
]

# Hub floor
for x in range(cx - hub_radius, cx + hub_radius + 1):
    for z in range(cz - hub_radius, cz + hub_radius + 1):
        if ((x-cx)**2 + (z-cz)**2)**0.5 <= hub_radius:
            commands.append(f'/setblock {x} {cy} {z} quartz_block')

# Portal pillars at compass points
import_angles = [0, 90, 180, 270]
for i, (name, angle_deg, dest_x, dest_y, dest_z) in enumerate(games):
    angle = radians(angle_deg)
    px = int(cx + cos(angle) * (hub_radius - 2))
    pz = int(cz + sin(angle) * (hub_radius - 2))

    # Pillar
    for dy in range(5):
        commands.append(f'/setblock {px} {cy + dy} {pz} end_stone_bricks')

    # Sign label
    commands.append(f'/setblock {px} {cy + 5} {pz} oak_sign{{Text1:\\'{{\\"text\\":\\"{name}\\"}}\\',Text2:\\'{{\\"text\\":\\"Step to enter\\"}}\\' }}')

    # Pressure plate trigger
    commands.append(f'/setblock {px} {cy + 1} {pz} oak_pressure_plate')
    commands.append(f'/setblock {px} {cy - 1} {pz} command_block[facing=up]{{Command:"tp @a[distance=..2] {dest_x} {dest_y} {dest_z}",auto:0b}}')
""")
```

---

## Tips

- **Tick timing:** 20 ticks = 1 second. Use `scoreboard players add @a timer 1` in repeating block to count seconds.
- **Test selectors first** by running commands in chat before wiring to command blocks.
- **Name your command blocks** with `CustomName` — makes debugging much easier.
- **Conditional chains** fail silently — use `TrackOutput:1b` on chain blocks during testing.
- **Always reset tags** at game end: `tag @a remove playing`, `tag @a remove winner`, `tag @a remove dead`.
