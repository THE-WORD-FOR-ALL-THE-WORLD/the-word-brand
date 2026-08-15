---
name: brand-sync
description: Regenerate and validate the machine-readable AI layer at /ai after any change to the visual brand guides, the assets, or the hand-authored ai-source files. Use whenever brand/index.html, brand/messaging/index.html, assets/, letterhead/, documents/, or ai-source/ has been edited, when tokens.json or manifest.json look stale, when the build or lint fails, or when the user says "sync the brand", "rebuild the AI layer", or "the AI files are out of date".
---

# Sync the AI layer

The published files under `/ai` are generated. This skill regenerates them from the visual guides
and proves they are consistent before anything ships.

## Run it

```bash
python3 tools/build_ai.py     # regenerate ai/, skills/, llms.txt, sitemap.xml, _headers
python3 tools/brand_lint.py   # prove the pages, the AI layer, and delivery still agree
```

Both must succeed. Then commit the regenerated files together with whatever change triggered the
sync, never in a separate "rebuild" commit: a commit where the guides and the AI layer disagree is
a commit where the site lied about being canonical.

## What flows where

| You edited | What changes automatically |
| --- | --- |
| A color, token, law, typeface, or Do/Don't card in `brand/index.html` | `tokens.json`, `brand-system.md`, `anti-patterns.md`, `components.json`, `manifest.json` |
| Vocabulary, banned words, audiences, or the mission line in `brand/messaging/index.html` | `brand-system.md`, `anti-patterns.md`, `manifest.json` |
| Files in `assets/` | `assets.json` |
| A new initiative under `letterhead/` or `documents/` | `manifest.json`, `llms.txt`, `sitemap.xml`, `brand-system.md` |
| Anything in `ai-source/` | The file it feeds, unchanged in body |

Nothing in `ai-source/` is ever overwritten. That is the whole point of the split: the guides own
the mechanical facts, `ai-source/` owns everything an agent needs that no visual page states.

## When the build fails

`build_ai.py` raises `SourceError` when a pattern it depends on stops matching in a guide. This is
deliberate. A silent fallback would publish a stale standard under a "canonical" label.

1. Read the error. It names the guide and what it was looking for.
2. Open that guide and find what the markup now looks like.
3. Update the matching extractor in `tools/brandsource.py`.
4. Rebuild and confirm the value in `ai/` matches what the guide actually says.

Never work around a `SourceError` by hardcoding the value in `ai-source/overrides.json` unless the
value genuinely belongs only to machines. An override that duplicates a guide fact is the stale
copy this architecture exists to prevent.

## When the lint reports something

Errors block. Warnings are informational and worth reading anyway.

| Code | Meaning | Usual fix |
| --- | --- | --- |
| L1 | A guide no longer parses | Update `tools/brandsource.py` |
| L2 | A hand-authored input is missing | Restore it from git history |
| L3 | A page sets a token to a different value than the guide | Fix the page, or fix the guide and rebuild |
| L4 | An improvised color appears | Remove it, or record it with a reason in `ai-source/overrides.json` under `lint.allowedColors` |
| L5 | Text sits directly on Flame | Move the text to Ember, Midnight, or a scrim |
| L6 | An unapproved font family appears | Replace with DM Serif Display, DM Serif Text, or DM Sans |
| L7 | A page points at an asset that does not exist | Fix the path or publish the asset |
| L8 | Something is published but not discoverable | Rerun `build_ai.py` |
| L9 | A manifest checksum does not match the file | Rerun `build_ai.py` |
| L10 | A page's navigation differs from the rest of the portal | Copy the chrome from an existing page |
| L11 | The published and installable copies of the skill differ | Rerun `build_ai.py` |

## Verify before you finish

Report the actual output of both commands. If `build_ai.py --check` still reports stale files after
a build, something wrote to `ai/` outside the generator, and that needs saying rather than
rebuilding over.

Related: [`brand-release`](../brand-release/SKILL.md) for a versioned change,
[`brand-skills`](../brand-skills/SKILL.md) for changing how these skills work.
