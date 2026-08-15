---
name: brand-audit
description: Audit any work against THE WORD brand system and return a versioned report. Use when the user asks to check, review, or audit something for brand compliance, when asked "is this on brand", when reviewing a page, post, deck, flyer, script, caption, email, or document, and before presenting any branded work produced in this repository.
---

# Audit work against the brand system

Two halves: a deterministic pass over anything in this repository, and a judgment pass against the
published rubric. Run both when the target is in the repo. Run the second alone when it is not.

## 1. Load the current standard

Working inside this repository, read the local files, which are the same bytes that are published:

- `ai/manifest.json` for the versions
- `ai/brand-system.md` for the standard
- `ai/tokens.json` for the values
- `ai/audit.md` for the rubric and the report template
- `ai/anti-patterns.md` when reviewing existing work
- The initiative's own guide under `letterhead/<slug>/` when an initiative is speaking

Working outside this repository, fetch `https://brand.theword.world/ai/manifest.json` and follow it.
If retrieval fails, the verdict is BLOCKED. Say which resource failed. Do not audit from memory and
call the result compliant.

## 2. Deterministic pass, for anything in this repo

```bash
python3 tools/brand_lint.py
```

This catches what a reading pass reliably misses: palette drift, improvised colors, text on Flame,
unapproved fonts, broken asset links, discovery gaps, manifest checksum mismatches, and navigation
that has fallen out of step. Fold its findings into the report as confirmed failures. It does not
replace the rubric: it cannot see whether the copy invents a statistic or whether the register
matches the speaker.

## 3. Judgment pass

Work `ai/audit.md` exactly as written. Gates first, in order, then the scored checks. Any gate
failure fails the audit no matter how the scored checks come out.

The gates are the checks most likely to be skipped, because each one requires actually looking:

- Did that number come from the official ministry record, or does it merely sound right?
- Is that photograph documentary, or was it generated, sourced, or staged?
- Is the prophecy quoted exactly, or has it been trimmed to fit?
- Does every initiative name carry the endorsement line?

Check them. Do not infer them.

## 4. Report

Use the template in `ai/audit.md` verbatim in structure. Open with the version line taken from the
manifest, which is a claim about which standard was applied, so make it true. Every `n/a` carries a
reason. Do not pad a clean audit.

If asked to fix rather than report, fix, then re-audit and show the new report. A fix that has not
been re-audited is a claim, not a result.

## Auditing this repository itself

To audit the portal as a whole rather than one page:

```bash
python3 tools/brand_lint.py
python3 tools/build_ai.py --check
```

Then read the pages. The portal is subject to its own standard, and the guides are brand artifacts
like anything else.
