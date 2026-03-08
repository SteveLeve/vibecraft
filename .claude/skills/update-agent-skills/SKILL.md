---
name: update-agent-skills
description: Use when modifying the VibeCraft building agent's behavior, adding new building capabilities, editing agent skills or the system prompt, or teaching the agent new workflows.
---

# Update Agent Skills

## File Map

| What | Where |
|------|-------|
| Agent system prompt | `agent/AGENTS.md` |
| Building skills | `agent/.claude/skills/<skill-name>/SKILL.md` |
| Reference guides | `agent/context/*.md` |

## Workflow

### 1. Decide: AGENTS.md vs Skill File?

- **`AGENTS.md`**: Critical rules, must-always-follow constraints, tool selection guidance. Changes here affect every single agent response.
- **Skill file**: Specific workflows (how to build a house, how to use WorldEdit). Skills are loaded on demand when the task matches.
- **`agent/context/`**: Read-only reference (block lists, coordinate guides). Agent reads these when needed but they aren't auto-loaded.

### 2. Edit the Right File

**Editing `agent/AGENTS.md`:**
- Use for rules that must never be violated (floor height rule, coordinate formats)
- Keep critical rules near the top — the agent reads top-down
- Use `WRONG/CORRECT` examples for rules with common mistakes

**Creating/editing a skill:**
```
agent/.claude/skills/
  my-new-skill/
    SKILL.md          # Required
    reference.md      # Optional: heavy reference material (100+ lines)
```

Every skill needs YAML frontmatter — this is what controls auto-triggering:
```yaml
---
name: my-new-skill
description: Use when [specific task the agent is asked to do]
---
```

**Description best practices:**
- Start with "Use when..." — describes WHEN to load, not WHAT the skill does
- Be specific: "Use when building multi-story structures with interior rooms" beats "Use when building"
- Include synonyms the user might say: "house, cottage, cabin, home"
- Keep under 500 characters

### 3. Test in the Agent

```bash
cd agent
claude  # Start Claude Code as the building agent
```

Then ask it to do the task the skill covers. Observe:
- Did the skill auto-trigger? (check if it was loaded)
- Did the agent follow the workflow correctly?
- Were there gaps or misunderstandings in the skill content?

### 4. Iterate

Refine the skill based on what you observed:
- **Skill didn't trigger**: Make the description more specific to the trigger phrase
- **Agent ignored a step**: Add emphasis (bold, move to top, add `WRONG/CORRECT` example)
- **Agent got confused**: Simplify — remove ambiguity, add concrete examples

## Context Files (`agent/context/`)

Context files are reference material the agent can read when needed:
- They are NOT auto-loaded — the agent must explicitly `Read` them
- Use for large reference tables (all block names, coordinate systems)
- Link to them from AGENTS.md or skills: "See `context/blocks.md` for block names"
- Don't put workflow instructions here — put those in skills

## Quick Reference

```bash
# Test agent with a specific task
cd agent && claude

# View current skills
ls agent/.claude/skills/

# Check skill frontmatter format
head -5 agent/.claude/skills/using-worldedit/SKILL.md
```

## Common Mistakes

- **No frontmatter**: Skill won't auto-trigger without `name` and `description` in YAML block
- **Description summarizes content**: Description should say WHEN to use, not WHAT the skill does — if it summarizes, the agent may follow the description instead of reading the skill body
- **Critical rules in skill, not AGENTS.md**: Rules that must always apply belong in AGENTS.md, not in an optional skill
- **Context files as instructions**: `agent/context/` is reference-only — workflows go in skills
