# Installable skills

## `the-word-brand`

A thin loader. It teaches an AI tool to retrieve THE WORD brand system from
`https://brand.theword.world/ai/manifest.json` and to audit its work against the current rubric
before presenting it.

It deliberately contains almost no brand rules. Rules live at the URL, so they can change without
anyone reinstalling anything. An installed copy that carried the palette would become a stale
palette the first time a color changed.

`SKILL.md` here is **generated** from [`../ai-source/skill.md`](../ai-source/skill.md). Edit that
file and run `python3 tools/build_ai.py`. Editing this copy directly does nothing: the next build
overwrites it, and `tools/brand_lint.py` fails on the mismatch in the meantime.

## Installing it

**Claude Code, one project.** Copy the folder into the project:

```bash
mkdir -p .claude/skills
curl -sL https://raw.githubusercontent.com/nathan-zimmer/the-word-brand/main/skills/the-word-brand/SKILL.md \
  -o .claude/skills/the-word-brand/SKILL.md
```

**Claude Code, everywhere.** Same file, at `~/.claude/skills/the-word-brand/SKILL.md`.

**Codex, and other tools that read `AGENTS.md`.** No install needed. Put this in the repository's
`AGENTS.md`:

```markdown
All branded work must use the current THE WORD Brand System.

Before creating or reviewing branded work, retrieve:
https://brand.theword.world/ai/manifest.json

Follow the skill and audit resources declared by that manifest. Do not use cached
standards when the current manifest is accessible. State the brand-system version
you used in your audit report.
```

**Any assistant with web access, no install.** Paste this at the top of the conversation:

```
Before beginning, retrieve https://brand.theword.world/ai/manifest.json. Follow the
current brand system and skill identified in that manifest. When finished, audit the
result using the current audit standard and state which brand-system version you used.
```

**Anything with a Markdown skill format.** `SKILL.md` is plain Markdown with YAML frontmatter. Most
tools that accept skills accept this file unchanged. If a tool needs a different shape, convert the
file rather than rewriting the workflow, and keep the retrieval-first behavior intact.

## Checking that it worked

Ask the tool: *"What version of THE WORD brand system are you working from, and what is the hex
value of Ember?"*

A working install fetches the manifest and answers with the current version and `#C13A24`. A tool
that answers from memory, hedges, or gives a version without having fetched anything has not
loaded the skill.
