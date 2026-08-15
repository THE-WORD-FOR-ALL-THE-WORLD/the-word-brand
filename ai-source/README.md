# ai-source: the hand-authored half of the AI layer

Everything an AI agent reads lives at `https://brand.theword.world/ai/`. Those published
files are built from two sources:

| Source | What it holds | Who writes it |
| --- | --- | --- |
| `brand/index.html`, `brand/messaging/index.html`, `assets/`, `letterhead/`, `documents/` | Versions, colors, tokens, laws, typefaces, sub-brands, do/don't rules, vocabulary, banned words, audiences, asset inventory | The visual guides. Edit them, run the build, and the AI layer follows automatically. |
| **`ai-source/` (this folder)** | Everything an agent needs that no visual page states: the audit rubric, agent operating rules, component specs, worked examples, retrieval instructions | You, by hand. **The build never overwrites these files.** |

That is the whole contract. Change a hex in the Brand Guide and `/ai/tokens.json` follows on
the next build. Change how agents should behave and you edit this folder, where no generator
can touch it.

## The files

| File | Becomes | Notes |
| --- | --- | --- |
| `overrides.json` | manifest fields, token overrides | Values here win over anything parsed from the guides. Use it for a deliberate exception, and say why in `_why`. |
| `agent-rules.md` | the "How an agent uses this system" section of `/ai/brand-system.md` | Rules that govern AI work specifically. Not brand law, agent law. |
| `audit.md` | `/ai/audit.md` | The audit rubric, copied through verbatim with a version header stamped on top. |
| `anti-patterns.md` | the authored half of `/ai/anti-patterns.md` | The generated half is built from the Brand Guide's DON'T cards and the Messaging Guide's banned-word lists. Do not restate those here. |
| `approved-examples.md` | `/ai/approved-examples.md` | Worked, on-brand output an agent can pattern-match against. |
| `components.json` | `/ai/components.json` | Component specs written against **token names**, never raw hex. The build resolves names to current values, so a palette change updates every component spec. |
| `asset-notes.json` | usage notes merged into `/ai/assets.json` | Keyed by file path. Files with no note still publish, they just carry no guidance. |
| `skill.md` | `/ai/SKILL.md` and `skills/the-word-brand/SKILL.md` | The installable thin-loader skill. One source, two published copies. |

## Editing rules

1. **Never put brand facts here that a guide already states.** If a value can be read from the
   visual guides, it belongs there. Duplicating it here creates the exact stale copy this whole
   architecture exists to prevent.
2. **Write for a machine reader.** Plain Markdown and JSON. No decoration, no tables that only
   make sense visually, no "see the diagram above."
3. **Every override needs a `_why`.** A year from now, an unexplained override is indistinguishable
   from a mistake.
4. After editing anything here, run `python3 tools/build_ai.py` and commit both this folder and
   the regenerated `ai/` folder together.

See [`../README.md`](../README.md) for the full system map.
