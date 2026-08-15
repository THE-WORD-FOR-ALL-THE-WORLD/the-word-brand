---
name: brand-skills
description: Create, edit, review, or retire the skills in this repository, including the installable the-word-brand loader skill published at /ai/SKILL.md. Use when the user asks to add a skill, change what a skill does, fix a skill that is not triggering, review the skills, install the brand skill somewhere else, or asks how the skills in this project fit together.
---

# Manage the skills in this project

Two kinds of skill live here, and they are governed differently.

| Kind | Lives in | Audience | Edited |
| --- | --- | --- | --- |
| **Maintenance skills** | `.claude/skills/<name>/SKILL.md` | Whoever is working inside this repository | Directly |
| **The loader skill** | `ai-source/skill.md` | Every AI tool in the world | Through the build, which publishes it to `ai/SKILL.md` and `skills/the-word-brand/SKILL.md` |

## The inventory

| Skill | Does |
| --- | --- |
| `brand-sync` | Regenerates and validates the AI layer after any change |
| `brand-release` | Makes a governed, versioned change to the standard end to end |
| `brand-audit` | Audits work against the current system and returns a versioned report |
| `brand-new-page` | Adds a page, guide, or initiative with correct chrome and wiring |
| `brand-skills` | This one. Manages the skills themselves. |
| `the-word-brand` | The installable loader. Teaches any agent to retrieve and obey the live system. |

Keep this table current. A skill that is not listed here is a skill nobody knows exists.

## The one rule that governs the loader skill

**The loader skill contains no brand standards.** Not the palette, not the laws, not the voice
rules. It teaches an agent where to retrieve the current system and how to use it, and nothing else.

Everything an installed copy states is frozen the moment someone installs it. A skill that carries
the palette becomes a stale palette on somebody's laptop the first time a color changes, and that
copy will be trusted because it looks official. The whole architecture exists to prevent exactly
that.

The "Quick orientation" section is the deliberate exception: five lines, enough for an agent to
recognize it is in the right territory, explicitly labeled as not enough to work from. If that
section starts growing, cut it back.

Editing the loader:

```bash
$EDITOR ai-source/skill.md
python3 tools/build_ai.py     # publishes it to ai/ and skills/
python3 tools/brand_lint.py   # L11 confirms the two copies are identical
```

Never edit `ai/SKILL.md` or `skills/the-word-brand/SKILL.md`. Both are generated, and the next
build overwrites them.

## Adding a maintenance skill

1. Create `.claude/skills/<name>/SKILL.md` with frontmatter:

   ```yaml
   ---
   name: <kebab-case, matching the folder>
   description: <what it does, then when to use it, including the words a user would actually say>
   ---
   ```

2. **Write the description for retrieval, not for reading.** It is the only thing seen when deciding
   whether to load the skill. Name the triggering situations and the phrases a user would type. A
   description that reads well but names no trigger will never fire.

3. **Write the body for doing, not for explaining.** Commands to run, in order. What each output
   means. What to do when it fails. Tables over paragraphs. If a step cannot be verified, say how to
   report that honestly rather than assuming success.

4. **Link related skills** with a relative path, as the existing skills do. Skills that do not
   reference each other get used in isolation and drift apart.

5. Add it to the inventory table above and to the skills table in `README.md`.

## Reviewing a skill

Check each of these:

- Does the description name real triggers, in the user's words?
- Does the body duplicate a brand fact that lives in the guides? Delete it and link instead.
- Does every command in it actually run? Run them.
- Does it tell the reader what to do when a step fails, or does it assume success?
- Does it cross-link the skills that come before and after it in a real workflow?

## A skill is not triggering

Almost always the description, not the body. Rewrite it to lead with what the skill does, then
enumerate the situations and the literal phrases that should invoke it. Test with the phrasing the
user actually used, not the phrasing you would have chosen.

## Retiring a skill

Delete the folder, remove it from both inventory tables, and remove every cross-link pointing at
it. A dangling link from another skill is worse than the skill's absence, because it sends a reader
somewhere that no longer exists.

## Installing the loader skill elsewhere

For another repository or another tool, copy `skills/the-word-brand/` into that project's skills
directory, or point the tool at `https://brand.theword.world/ai/SKILL.md`. See
[`skills/README.md`](../../../skills/README.md) for the per-tool instructions, and keep that file
current when a tool's install path changes.

For a repository that only needs agents to obey the brand, no install is required: copy the
`AGENTS.md` snippet from [`README.md`](../../../README.md). Four lines pointing at the manifest is
enough for any agent with web access.
