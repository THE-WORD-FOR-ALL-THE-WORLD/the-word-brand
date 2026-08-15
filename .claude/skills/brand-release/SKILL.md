---
name: brand-release
description: Make a governed change to THE WORD brand system end to end. Use when changing a color, token, typeface, law, rule, voice standard, banned word, audience, asset policy, initiative, or audit rubric, and when the user says "change the brand", "update the guide", "add a rule", "new brand version", "release the brand", or asks for anything that alters what the published standard says. Handles the edit, the version bump, the changelog entry, the AI rebuild, validation, and the commit.
---

# Release a brand change

Every change to this system is governed. The rule is written into the guides themselves: a
proposed edit in writing, approval by Joel Zimmer and Nathan Zimmer, a version bump, and a
changelog entry. No silent edits. This skill is that process, executed.

## 1. Classify the change

| Kind | Version move | Example |
| --- | --- | --- |
| Correction with no change in meaning | none | Fixing a typo, tightening a sentence |
| New rule, new token, new section, changed wording of a standard | patch, `4.4` to `4.5` | Adding a token, adding a banned word, restating a law |
| A standard reverses, a color changes value, a typeface is replaced | minor, `4.4` to `5.0` | Retiring a color, changing the primary ground |

The Brand Guide and the Messaging Guide version independently. A change to how things look moves
the Brand Guide. A change to what we say moves the Messaging Guide. A change that touches both
moves both.

If the change is a correction, skip to step 4.

## 2. Get it approved before editing

The guides say this system changes only with the approval of Joel Zimmer and Nathan Zimmer. Confirm
with the user that the change is approved before you edit a published standard. If it is not yet
approved, make the edit on a branch and say plainly that it is a proposal awaiting approval, not a
release.

## 3. Edit the visual guide, never the AI layer

The published `/ai` files are generated. Editing them directly is always wrong: the next build
overwrites the edit, and until then the guides and the AI layer disagree.

| Changing | Edit |
| --- | --- |
| A color, token, typeface, law, section, Do/Don't pair, or sub-brand rule | `brand/index.html` |
| The mission line, a pillar, vocabulary, a banned word, an audience, the message architecture, the proof policy | `brand/messaging/index.html` |
| An initiative's own brand guide or messaging document | `tools/gen_docs.py`, then rerun it |
| The audit rubric, agent operating rules, component specs, worked examples, the loader skill | the matching file in `ai-source/` |
| An asset, or an asset's usage rule | `assets/`, and `ai-source/asset-notes.json` |

Keep the guide's own register while editing it. The guides are themselves brand artifacts: the
prose is sentence case, plain, and unhyped, and every rule states what happens rather than what is
preferred.

## 4. Bump the version and record the change

For anything above a correction, in the same edit:

1. **Brand Guide.** Update `Brand Guide · Version X.Y` in the cover kicker and the `<title>`. Add a
   row to the `#changelog` table if an element changed against the old standard, and extend the
   revision trail sentence at the bottom with `· vX.Y <what changed>`.
2. **Messaging Guide.** Update `Messaging Guide · Version X.Y` in the kicker, the `<title>`, the
   meta row, and the companion line. Add a row to the governance changelog table with the version,
   the date, and the change.
3. **Both.** If a guide references the other's version, update that reference too.
4. `ai-source/overrides.json`: set `manifest.updated` to today's ISO date.

The version number in the guide is the number every audit report will cite. It is how anyone tells,
a year from now, which standard a piece of work was measured against. Getting it wrong is worse
than not bumping it.

## 5. Rebuild, validate, review

```bash
python3 tools/build_ai.py
python3 tools/brand_lint.py
python3 tools/build_ai.py --check
```

Then read the diff of `ai/brand-system.md` and `ai/tokens.json`. This is the actual review step:
the diff shows exactly what every AI tool in the world will start following. If it contains
something you did not intend, the extraction picked up more than the edit.

See [`brand-sync`](../brand-sync/SKILL.md) for what to do when the build or the lint fails.

## 6. Commit

One commit carrying the guide edit, the version bump, the changelog entry, and the regenerated AI
layer. Never split them: a commit where the guide says v4.5 and the manifest says v4.4 is a commit
where the site is lying about its own version.

Commit message: what changed and why, in the voice of the record.

```
Brand Guide v4.5: add <token> to the system tokens

<one or two sentences on what problem this solves>

Approved by Joel Zimmer and Nathan Zimmer.
```

Push to `main` only when the user asks. Cloudflare Pages publishes from `main` in about thirty
seconds, and the GitHub Action blocks the deploy if the build or the lint fails, so a broken AI
layer never reaches `brand.theword.world`.

## 7. Report

Tell the user:

- The new version numbers.
- What an agent will now see differently, in one or two sentences.
- The lint result, including any warnings.
- Whether it is pushed, or waiting.

## Retiring a standard

Old versions of a guide go to `archive/` rather than being deleted, so an audit report citing v4.3
can still be checked against v4.3. Copy the guide to `archive/<name>-v<version>.html` before
overwriting it with a minor-version change.
