# Agent instructions

This repository is the canonical brand system for THE WORD FOR ALL THE WORLD, published at
`https://brand.theword.world`.

## Before creating or reviewing branded work

Retrieve the manifest and follow what it names:

    https://brand.theword.world/ai/manifest.json

Working inside this repository, read the local copies instead. They are the same bytes:
`ai/manifest.json`, `ai/brand-system.md`, `ai/tokens.json`, `ai/audit.md`.

Do not use cached or remembered brand standards when the current manifest is accessible. Run the
audit at `ai/audit.md` before presenting anything, and state the brand-system version you used.

## Before changing anything in this repository

**`ai/` is generated output. Never edit it directly.** Change the source instead:

- Visual standards: `brand/index.html`
- Verbal standards: `brand/messaging/index.html`
- Initiative guides and documents: `tools/gen_docs.py`
- Audit rubric, agent rules, component specs, examples, the installable skill: `ai-source/`

Then run both, and commit the regenerated files with the change that caused them:

```bash
python3 tools/build_ai.py
python3 tools/brand_lint.py
```

Every change to a published standard needs a version bump and a changelog entry. The governance
rule is written into the guides themselves: no silent edits.

See [`README.md`](README.md) for the full map and [`CLAUDE.md`](CLAUDE.md) for the short version.
