# THE WORD brand portal

This repository **is** the brand system for THE WORD FOR ALL THE WORLD, published at
`https://brand.theword.world` via Cloudflare Pages. Read [`README.md`](README.md) for the full map.

## The rule that matters most

**`ai/` is generated. Never edit it by hand.** Its files are built from the visual guides plus
`ai-source/`. A hand edit is overwritten by the next build, and until then the site publishes a
standard that disagrees with the guide it claims to come from.

| To change | Edit |
| --- | --- |
| A color, token, law, typeface, Do/Don't rule, sub-brand rule | `brand/index.html` |
| Mission line, voice, vocabulary, banned words, audiences, proof policy | `brand/messaging/index.html` |
| An initiative's guide or document | `tools/gen_docs.py`, then rerun it |
| The audit rubric, agent rules, component specs, examples, the loader skill | `ai-source/` |
| Assets and their usage rules | `assets/` and `ai-source/asset-notes.json` |

## After any change

```bash
python3 tools/build_ai.py
python3 tools/brand_lint.py
```

Both must pass, and the regenerated files get committed with the change that caused them, never
separately. The GitHub Action runs both before deploying, so a broken AI layer never reaches
production.

## Working on branded output

Anything produced here is branded work and is held to the standard it publishes. Read
`ai/brand-system.md` before writing copy or building a page, and audit against `ai/audit.md` before
presenting it. The `/brand-audit` skill does this.

## Skills

`/brand-sync`, `/brand-release`, `/brand-audit`, `/brand-new-page`, `/brand-skills`. See
[`README.md`](README.md#skills) for what each one covers.

## House style

- No em dashes in prose written for this repository. Use a colon, a comma, or a period.
- Sentence case. Plain. Never hype. The guides are brand artifacts and read like it.
- Old versions of a guide move to `archive/` rather than being deleted, so an audit citing an older
  version can still be checked against it.
