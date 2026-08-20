# THE WORD FOR ALL THE WORLD: Brand System

The single source of truth for how this ministry looks, speaks, and is represented, by anyone and
by anything. Published at **[brand.theword.world](https://brand.theword.world)** via Cloudflare
Pages, open to people, search engines, and AI agents alike.

One system, two faces:

- **The portal** is the human face. Beautiful, readable, printable guides.
- **[`/ai`](https://brand.theword.world/ai/)** is the machine face. The same standards as raw
  Markdown and JSON, versioned, checksummed, and built for agents to retrieve.

Both are generated from the same sources, so they cannot disagree.

---

## Where to start

| You are | Go here |
| --- | --- |
| A person who needs the brand | [Brand Guide](https://brand.theword.world/brand) and [Messaging Guide](https://brand.theword.world/brand/messaging) |
| An AI agent, or pointing one at this | [`/ai/manifest.json`](https://brand.theword.world/ai/manifest.json) |
| Setting up a tool or another repository | [Give it to an AI](#give-it-to-an-ai) below |
| Changing the brand | [`/brand-release`](.claude/skills/brand-release/SKILL.md) |
| Checking work against the brand | [`/brand-audit`](.claude/skills/brand-audit/SKILL.md) |
| Maintaining this repository | [How it is built](#how-it-is-built) below |

---

## The directory

### Human-facing guides

| Guide | URL | What it governs |
| --- | --- | --- |
| Brand Guide | [`/brand`](https://brand.theword.world/brand) | How we look. Design direction, the six laws, color, tokens and states, typography, logo, photography and video, the record, sub-brands, voice, changelog. |
| Messaging Guide | [`/brand/messaging`](https://brand.theword.world/brand/messaging) | How we speak. The foundation, the prophecy, origin, identity, values, message architecture, the journey, the five audiences, voice and vocabulary, proof policy, governance. |
| Initiative brand guides | [`/letterhead`](https://brand.theword.world/letterhead) | How each initiative looks under the parent brand. |
| Initiative messaging documents | [`/documents`](https://brand.theword.world/documents) | What each initiative is, in the words of the ministry. |
| Assets | [`/assets`](https://brand.theword.world/assets) | Every logo, in every format, with its clear space, minimum size, and ink rules. Fonts, photography and video policy, download packs, and the rules for a partnership lockup. |
| Components | [`/components`](https://brand.theword.world/components) | Forty components rendered live by the published stylesheet, on either ground, with specs, rules, and markup to copy. |
| Channels | [`/channels`](https://brand.theword.world/channels) | Nine surfaces, each with its sizes, character limits, safe areas, file formats, and pre-approved copy. |
| Reviews | [`/reviews`](https://brand.theword.world/reviews) | Every system review, in order, with what each found and the version it produced. |

### The three initiatives

One house, three named front doors, in a fixed order.

| Stage | Initiative | Brand guide | Messaging document |
| --- | --- | --- | --- |
| CLEAN | Revival To My City | [`/letterhead/revival-to-my-city`](https://brand.theword.world/letterhead/revival-to-my-city) | [`/documents/revival-to-my-city`](https://brand.theword.world/documents/revival-to-my-city) |
| BURN | EVERY1 Movement | [`/letterhead/every1`](https://brand.theword.world/letterhead/every1) | [`/documents/every1`](https://brand.theword.world/documents/every1) |
| TRAIN | School of the Local Church | [`/letterhead/school-of-the-local-church`](https://brand.theword.world/letterhead/school-of-the-local-church) | [`/documents/school-of-the-local-church`](https://brand.theword.world/documents/school-of-the-local-church) |

### The machine-readable layer

Raw Markdown and JSON, no navigation, no scripts, no decoration. Served with permissive CORS and
correct content types so any agent can fetch them.

| File | What it is |
| --- | --- |
| [`/ai/manifest.json`](https://brand.theword.world/ai/manifest.json) | **The doorway.** Versions, links, and a SHA-256 for every other file. Agents read this first. |
| [`/ai/brand-system.md`](https://brand.theword.world/ai/brand-system.md) | The complete standard, visual and verbal, as one document. |
| [`/ai/SKILL.md`](https://brand.theword.world/ai/SKILL.md) | The installable agent skill: retrieval and audit workflow. |
| [`/ai/tokens.json`](https://brand.theword.world/ai/tokens.json) | Colors, typography, system tokens and states. |
| [`/ai/audit.md`](https://brand.theword.world/ai/audit.md) | The rubric every piece of work is checked against, with its report template. |
| [`/ai/components.json`](https://brand.theword.world/ai/components.json) | Component specs, written against token names and resolved to current values. |
| [`/ai/assets.json`](https://brand.theword.world/ai/assets.json) | Every approved logo, photograph, and video, with usage rules and known gaps. |
| [`/ai/channels.json`](https://brand.theword.world/ai/channels.json) | One entry per surface: sizes, safe areas, limits, rules, and the audit checks that apply. |
| [`/ai/copy-bank.json`](https://brand.theword.world/ai/copy-bank.json) | Pre-approved strings by channel, each within the limit it was written against. |
| [`/ai/tokens.dtcg.json`](https://brand.theword.world/ai/tokens.dtcg.json) | The same tokens in W3C Design Tokens format, for design tooling. |
| [`/ai/tokens.ts`](https://brand.theword.world/ai/tokens.ts) · [`/ai/tailwind.preset.js`](https://brand.theword.world/ai/tailwind.preset.js) | The same tokens for applications. |
| [`/assets/brand.css`](https://brand.theword.world/assets/brand.css) | The tokens and the component layer, as one stylesheet anyone can link. |
| [`/ai/approved-examples.md`](https://brand.theword.world/ai/approved-examples.md) | Worked output that passes the audit. |
| [`/ai/anti-patterns.md`](https://brand.theword.world/ai/anti-patterns.md) | What not to do, including every DON'T and every banned word. |
| [`/llms.txt`](https://brand.theword.world/llms.txt) | Discovery file for tools that look for one. |

### Skills

| Skill | Use it when |
| --- | --- |
| [`/brand-release`](.claude/skills/brand-release/SKILL.md) | Changing anything the published standard says. Handles the edit, version bump, changelog, rebuild, and commit. |
| [`/brand-sync`](.claude/skills/brand-sync/SKILL.md) | Regenerating and validating the AI layer after an edit. |
| [`/brand-audit`](.claude/skills/brand-audit/SKILL.md) | Checking any work against the current standard. |
| [`/brand-new-page`](.claude/skills/brand-new-page/SKILL.md) | Adding a page, guide, or initiative to the portal. |
| [`/brand-skills`](.claude/skills/brand-skills/SKILL.md) | Creating, editing, or retiring the skills themselves. |
| [`the-word-brand`](skills/the-word-brand/SKILL.md) | The installable loader for other projects and other AI tools. |

---

## Give it to an AI

Three ways, in order of reliability.

**1. Install the skill.** Most reliable, because the tool then knows the retrieval workflow without
being told. See [`skills/README.md`](skills/README.md) for per-tool instructions. Then just say:

> Use THE WORD brand to create and audit this.

**2. Put it in the repository.** Any project whose work must be on brand gets an `AGENTS.md` or
`CLAUDE.md` containing:

```markdown
All branded work must use the current THE WORD Brand System.

Before creating or reviewing branded work, retrieve:
https://brand.theword.world/ai/manifest.json

Follow the skill and audit resources declared by that manifest. Do not use cached
standards when the current manifest is accessible. State the brand-system version
you used in your audit report.
```

**3. Paste it into the conversation.** Works with any assistant that can read a URL:

```text
Before beginning, retrieve https://brand.theword.world/ai/manifest.json. Follow the
current brand system and skill identified in that manifest. When finished, audit the
result using the current audit standard and state which brand-system version you used.
```

To confirm any of these worked, ask: *"What version of THE WORD brand system are you working from,
and what is the hex value of Ember?"* A working setup fetches the manifest and answers with the
current version and `#C13A24`.

---

## How it is built

### The architecture, in one rule

> The visual guides own every mechanical fact. `ai-source/` owns everything an agent needs that no
> visual page states. `ai/` is generated from both and is never edited by hand.

Change a hex in the Brand Guide and `/ai/tokens.json` follows on the next build. Change how agents
should behave and you edit `ai-source/`, where no generator can touch it. Nothing is stated in two
places, so nothing can go stale in one of them.

```text
assets/logos/_masters/ ─→ tools/build_logos.py ─→ assets/logos/the-word/  (generated, published)
                                               ─→ assets/downloads/*.zip  (generated, published)
                                               ─→ assets/index.html       (generated, published)
                                               ─→ ai-source/logo-manifest.json

brand/index.html            ─┐
brand/messaging/index.html   ├─→ tools/build_ai.py ─→ ai/            (generated, published)
assets/ letterhead/ documents/│                    ─→ skills/         (generated, installable)
ai-source/                  ─┘                     ─→ llms.txt, sitemap.xml, _headers

tools/brand_lint.py ─→ proves the pages, the AI layer, and delivery still agree
```

### Layout

```text
├── index.html              Portal homepage
├── brand/                  Brand Guide, and messaging/ for the Messaging Guide
├── letterhead/             Initiative brand guides        (generated by tools/gen_docs.py)
├── documents/              Initiative messaging documents (generated by tools/gen_docs.py)
├── assets/
│   ├── index.html          GENERATED. The Assets page: logos, fonts, packs.
│   ├── logos/_masters/     HAND-HELD. The approved artwork everything else comes from.
│   ├── logos/the-word/     GENERATED. Five configurations x three inks, SVG and PNG.
│   ├── downloads/          GENERATED. The ZIP packs.
│   └── images/ videos/     Photography and footage
├── ai/                     GENERATED. The machine-readable layer. Never edit by hand.
├── ai-source/              HAND-AUTHORED. Audit rubric, agent rules, components, channels,
│                           copy bank, consumers, component CSS, examples, skill.
├── components/             GENERATED. The live component gallery.
├── channels/               GENERATED. The per-surface specifications.
├── reviews/                System reviews. A new one is a directory drop.
├── packages/
│   ├── brand/              GENERATED. @theword/brand: the tokens, in every shape.
│   └── ui/                 src/ is HAND-WRITTEN React; its manifest is generated.
├── skills/                 GENERATED. The installable loader skill.
├── .claude/skills/         Maintenance skills for this repository.
├── tools/
│   ├── svgkit.py           SVG parsing, measuring, and rasterizing, with no external binaries
│   ├── build_logos.py      Generation: derives every logo file from the approved masters
│   ├── brandsource.py      Extraction: reads the guides, returns structured data
│   ├── build_ai.py         Generation: writes ai/, skills/, llms.txt, sitemap.xml, _headers
│   ├── brand_lint.py       Validation: drift detection across the whole portal
│   ├── brand_check.py      Validation: the mechanical audit, against any file or URL
│   ├── gen_docs.py         Generates the initiative guides and documents
│   ├── fetch_fonts.py      One-off: self-hosts the three families from Google Fonts
│   ├── sync_figma.py       One-off: pushes the tokens into the Figma library
│   └── sync_canva.py       One-off: prints the Canva brand kit setup sheet
├── archive/                Retired versions of guides
├── _headers                Cloudflare Pages headers, /ai block generated
├── robots.txt              Open to all crawlers
├── sitemap.xml             GENERATED
└── llms.txt                GENERATED
```

### The three commands

```bash
python3 tools/build_logos.py   # derive every logo file from the approved masters
python3 tools/build_ai.py      # regenerate everything else derived
python3 tools/brand_lint.py    # prove it all still agrees
```

Three more are run by hand, never in CI, because they need the network and the build does not:

```bash
python3 tools/fetch_fonts.py   # re-download and self-host the three approved families
python3 tools/sync_figma.py    # push the tokens into the Figma library (--dry-run to preview)
python3 tools/sync_canva.py    # print the Canva brand kit setup sheet
```

And one runs anywhere, on anything:

```bash
python3 tools/brand_check.py page.html https://example.org/campaign
```

It decides the mechanical half of the audit: unknown colours, fonts outside the three, text in
or on Flame, banned words, a missing endorsement line, a removed focus ring, images with no alt
text. It ships as a [composite Action](.github/actions/brand-check/) other repositories can add
in three lines. **A clean run is not a passed audit**, and it says so every time.

Run all three after any change. Commit the regenerated files together with the change that caused them:
a commit where the guide says one thing and the manifest says another is a commit where the site is
lying about being canonical.

### What keeps it honest for years

This system claims to be canonical. Four mechanisms make that claim survive turnover, redesigns,
and time:

1. **The build fails rather than lies.** `tools/brandsource.py` raises `SourceError` when a pattern
   it depends on stops matching in a guide. It never falls back to a stale or default value, so the
   AI layer cannot quietly drift away from the visual guides.
2. **The linter checks the whole portal, not just the build.** Palette drift between pages,
   improvised colors, text on Flame, unapproved fonts, broken asset links, discovery gaps, manifest
   checksums, navigation consistency, the two copies of the skill, WCAG contrast for every pair the
   system puts on screen, social cards on every page, the React library against the component
   specifications, and every registered consumer's version. Sixteen checks, listed in
   [`/brand-sync`](.claude/skills/brand-sync/SKILL.md).
3. **CI blocks the deploy.** The GitHub Action runs the build in `--check` mode and the linter
   before deploying. Stale or inconsistent output never reaches `brand.theword.world`.
4. **The manifest is checksummed and versioned.** Every file carries a SHA-256 and a version, so an
   agent can tell whether a cached copy is current, and every audit report names the version it was
   measured against.

### Cloudflare setup, one time

1. **Pages**: dashboard → Workers & Pages → Create → Pages → Connect to Git → this repo. Framework
   preset *None*, build command empty, output directory `/`.
2. **Custom domain**: add `brand.theword.world` in the Pages project.
3. **Access**: leave it public. Do **not** put a Cloudflare Access application in front of this
   site: every crawler and every agent would get the login page instead of the standards.
4. **Deploy**: pushing to `main` publishes in about thirty seconds, gated by the checks above.

---

## Conventions

- **No em dashes** in prose written for this repository. Use a colon, a comma, or a period.
- Brand tokens are stated once, in the Brand Guide's `:root` block. Every other page copies those
  values, and the linter fails if any page drifts.
- Text over footage: Midnight scrim, white or Parchment type. Never Flame. This is standing law.
- Every page shares the same chrome: `.sitenav` over a full-bleed video hero, and the midnight
  footer. A new page adds its nav link to every other page.
- Old versions of a guide go to `archive/` rather than being deleted, so an audit citing v4.3 can
  still be checked against v4.3.
- Every change to a published standard gets a version bump and a changelog entry. No silent edits,
  ever. That rule is written into the guides themselves, and it applies to this repository too.
