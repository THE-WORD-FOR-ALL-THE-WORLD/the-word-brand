# Brand Audit

> **Brand system v5.6 · Messaging guide v1.0 · Updated 2026-08-15**
> Canonical source: <https://brand.theword.world/ai/manifest.json>
> This file is hand-authored in `ai-source/` and published unchanged. The build never rewrites its body.

The standard for checking any work against THE WORD brand system. Run it before presenting
anything: a page, a post, a deck, a flyer, a script, a caption, an email, a document.

An audit that was not run against the current manifest is not an audit. Fetch
`https://brand.theword.world/ai/manifest.json` first and record the versions it reports.

## How to run it

1. Load the manifest, `tokens.json`, and `brand-system.md`. Load the initiative's own guide if
   the work speaks for Revival To My City, EVERY1, or the School of the Local Church.
2. Work the gates in order. **Any gate failure fails the whole audit**, no matter how the scored
   checks come out.
3. Score every applicable check. Mark anything that does not apply as `n/a` and say why in one
   clause. Do not silently skip.
4. Report using the template at the bottom, verbatim in structure.

## Gates: any failure fails the audit

| # | Gate | Fails when |
| --- | --- | --- |
| G1 | **Invented facts** | A statistic, quote, testimony, name, date, or Bible reference appears that did not come from the official ministry record. Bracketed placeholders (`[n]`, `[city]`) pass. Plausible-looking figures fail. |
| G2 | **Synthetic or stock imagery** | Any photograph or video frame of people, ministry, or the field that is stock, AI-generated, or staged. Documentary capture only. |
| G3 | **The prophecy** | The prophecy is paraphrased, excerpted, trimmed, or reworded. It is quoted exactly and in full, or it is absent. |
| G4 | **Flame carrying text** | Any text set in Flame, or any text sitting directly on Flame. Fire at text size is Ember. |
| G5 | **Text on footage without a scrim** | Type over photography or video without the Midnight scrim, or in a color other than White or Parchment. |
| G6 | **Missing endorsement** | An initiative's name appears without "A ministry of THE WORD FOR ALL THE WORLD." |
| G7 | **Governmental iconography** | Seals, crests, flags, eagles, or any device that imitates a government office. |
| G8 | **Unattributed authority** | A vision statement, field report, testimony, or official record published without the name of the person or office behind it. |
| G9 | **Banned language** | Any term from the Messaging Guide's hype, corporate-polish, or churchy-insider lists, used straight rather than explained. |
| G10 | **Wrong hero** | The copy makes THE WORD the hero of the story instead of the believer and the local church. |

## Scored checks

Score each: **pass**, **fail**, or **n/a**.

### A. Identity and register (4 checks)

- **A1** The speaker is unambiguous: parent institution, or one named initiative, not a blend.
- **A2** The register matches the speaker. Parent work is serif-led, formal, record-shaped.
  Initiative work is DM Sans led, and the serif appears only where the parent speaks.
- **A3** Initiative naming is exact: `Revival To My City`, `EVERY1` (always styled EVERY1, never
  Every1 or EVERY ONE), `School of the Local Church`.
- **A4** The work lives as a named page under the house, not as a scattered separate identity.

### B. Color (5 checks)

- **B1** Every color used appears in `tokens.json`. No improvised hexes, no retired colors
  (`#0077AA`, and `#5FAD56` outside a form success state).
- **B2** The 60 / 30 / 10 proportion holds: Parchment ground, Midnight structure, Flame at a tenth
  or less.
- **B3** Text contrast: body copy is Midnight on light grounds, White or Parchment on Midnight.
  Word Blue never appears as text on Midnight.
- **B4** Interactive elements use Ember fill with white labels, and the hover state is the recorded
  button-hover value.
- **B5** Flame and Ember are not used side by side as if they were two accents. One or the other.

### C. Typography (4 checks)

- **C1** Only DM Serif Display, DM Serif Text, and DM Sans appear, within their stated size bands.
- **C2** No faux bold or faux italic on the serifs. The serifs have Regular and Italic only. Where
  more emphasis is wanted, the size goes up.
- **C3** Serif headlines are sentence case with at most one italic word. The serif is never set in
  all caps.
- **C4** Body text is DM Sans. The serif does not run below 22px.

### D. Composition (4 checks)

- **D1** No more than three to five priorities on a page, deck, or panel.
- **D2** Every priority word links to a real destination. No decorative priorities.
- **D3** Whitespace is generous. Crowding reads as hype.
- **D4** Corner radii come from the three recorded steps and nowhere else.

### E. The record (4 checks)

- **E1** Records open with a letterspaced kicker and close with a dateline: what, where, when.
- **E2** Published photography carries a caption in the record register, with names where known
  and permitted.
- **E3** Numbers cite the official ministry record rather than being frozen into the copy.
- **E4** Signatures, where used, are scanned ink. Never a script font pretending to be ink.

### F. Voice and message (6 checks)

- **F1** The work is aimed at one of the five named audiences, and it is obvious which.
- **F2** The public mission line, where quoted, is exact.
- **F3** Load-bearing phrases are used exactly as written in the Messaging Guide.
- **F4** Sentences are short, one idea each. Jesus is named directly, not softened into "faith" or
  "spirituality."
- **F5** The piece ends with something the reader can do. Invitation before information.
- **F6** It passes the filter: would Nathan actually say this, does it point to Jesus Himself, is it
  clear to a new believer, does it invite response.

### G. Media (4 checks)

- **G1** Video is muted, looping, roughly 6 to 15 seconds, cut from real field footage.
- **G2** Every spoken word is subtitled, DM Sans 500 or heavier, on the scrim bar.
- **G3** A still fallback ships with every loop, honored under `prefers-reduced-motion`.
- **G4** Every subject is shown as a co-laborer in the gospel, never as an object of pity. Consent
  was obtained before capture.

### H. Accessibility (4 checks)

- **H1** Text contrast meets WCAG AA: 4.5:1 for body, 3:1 for large text.
- **H2** A visible focus ring appears on every interactive element and is never removed.
- **H3** Muted text uses the recorded muted values and goes no lighter.
- **H4** Every image carries meaningful alternative text, and video carries captions.

## Report template

Return exactly this shape. Keep it short. Do not pad a clean audit.

```
BRAND AUDIT
Brand system: v<brandVersion> · Messaging: v<messagingVersion> · Manifest fetched: <yes/no>
Speaker: <THE WORD FOR ALL THE WORLD | Revival To My City | EVERY1 | School of the Local Church>
Scope: <what was audited>

GATES: <PASS | FAIL>
<one line per failed gate: G#, what triggered it, where>

SCORE: <passed>/<applicable> checks
<one line per failed check: ID, what is wrong, the fix>

NOT APPLICABLE: <IDs, with a clause each>

OPEN QUESTIONS
<anything the standards do not cover, or any conflict found between guides>

VERDICT: <SHIP | REVISE | BLOCKED>
```

Verdicts:

- **SHIP**: every gate passes and every applicable check passes.
- **REVISE**: every gate passes, one or more checks fail. List the fixes.
- **BLOCKED**: any gate fails, or the manifest could not be fetched. Name the reason. Do not
  describe blocked work as brand compliant.
