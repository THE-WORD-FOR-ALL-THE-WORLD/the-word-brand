---
name: brand-new-page
description: Add a new page, guide, initiative, or document to the brand portal with the correct chrome, registration, and discovery wiring. Use when the user asks to add a page, add a guide, add an initiative, add a document, create a new section of brand.theword.world, or says a new front door needs its own brand guide or messaging document.
---

# Add a page to the portal

Every page in this portal is a published standard. Adding one means wiring it into the chrome, the
navigation, the AI layer, and discovery, all of which are checked by the linter.

## Decide what you are adding

| Adding | Where it goes | How to build it |
| --- | --- | --- |
| A new initiative (a fourth front door) | `letterhead/<slug>/` and `documents/<slug>/` | Add it to `tools/gen_docs.py` and rerun that script |
| A new document for an existing initiative | the same folders | `tools/gen_docs.py` |
| A new top-level guide, such as a Photography Guide | `<name>/index.html` | Hand-authored, copying an existing guide's chrome |
| A new machine-readable resource for agents | `ai-source/`, then `tools/build_ai.py` | Never hand-write a file into `ai/` |

## Adding an initiative

Initiative pages are generated so all three stay identical in structure. Edit
`tools/gen_docs.py`:

1. Add the slug, name, stage word, and mission to `INITIATIVES`.
2. Add the display title to `TITLES`.
3. Write the messaging body and the brand body using the existing `sec`, `p`, `ul`, `plain`, and
   `keywords` helpers, following the shape of the three that exist.
4. Add both bodies to the `bodies` map in each of the `SECTIONS` entries.
5. Add the slug and its display name to `INITIATIVE_NAMES` in `tools/brandsource.py`, so the
   manifest names it correctly rather than guessing from the slug.

Then:

```bash
python3 tools/gen_docs.py
python3 tools/build_ai.py
python3 tools/brand_lint.py
```

The manifest, `llms.txt`, and `sitemap.xml` pick the initiative up on their own, because
`build_ai.py` scans the folders rather than holding a list.

A fourth initiative is a change to the house, not just a page. The Brand Guide's §10 and the
Messaging Guide's §03 and §07 both state that there are three, in a fixed order. Both need a
governed edit and a version bump. Use [`brand-release`](../brand-release/SKILL.md) for that half.

## Adding a top-level guide

1. Create `<name>/index.html`. Copy the chrome from an existing guide: the `:root` token block, the
   `.sitenav` markup, and the midnight footer. Do not restate token values, copy them, because the
   linter compares every page's `:root` against the Brand Guide and fails on drift.
2. Add the new nav link to **every** page in the portal, including the generated ones in
   `tools/gen_docs.py`. The linter warns when one page's navigation differs from the rest.
3. Give the page a `<title>`, a `robots` meta tag, and a version kicker if it carries standards.
4. Add a card for it on the homepage, `index.html`.
5. Rebuild and lint.

## Every new page must

- Carry the shared navigation and the midnight footer.
- Take its colors from the same `:root` values as the Brand Guide.
- Use only DM Serif Display, DM Serif Text, and DM Sans.
- Put text over footage on the Midnight scrim, in white or Parchment, never Flame.
- Appear in `sitemap.xml` and `llms.txt`, which happens automatically on rebuild.

## Finish

```bash
python3 tools/build_ai.py
python3 tools/brand_lint.py
```

Then audit the page with [`brand-audit`](../brand-audit/SKILL.md) before committing. A new page is
branded work, and branded work gets audited.

Retiring a page: move it to `archive/` rather than deleting it, then rebuild so discovery drops it.
