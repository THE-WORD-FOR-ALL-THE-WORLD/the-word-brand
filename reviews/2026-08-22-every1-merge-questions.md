# Answers to the seven merge questions

**From:** brand@theword.world
**Answers:** `brand-7.6-divergence.md`, questions 1 to 7
**Released in:** brand system **v7.7**, 2026-08-22
**Verify against:** `https://brand.every1movement.com/ai/manifest.json`

---

## The short answer to two of them, and why it is our fault you had to ask

**Q1 and Q6 were already answered in the Brand Guide, and the machine layer was not
carrying the answers.**

§09 has said for several versions, in the caption under the radius table:

> Three steps, no others. Nothing in this system is a pill, and nothing is a perfect circle
> except the avatar crop.

And under the motion table:

> Motion confirms an action. It never performs. Nothing bounces, nothing springs.

Both are real published rules. Neither reached `/ai`. What we published was
`{"radius-button": "3px", "radius-card": "4px", "radius-frame": "6px"}` and three durations,
with nothing to say what governed them. So you built a `9999` pill and a
`celebrationSpringIn`, against a standard that forbids both, and you could not have known.

This is the same failure as D6 one release ago: the brand had the answer and the manifest did
not carry it. Twice in two releases is a pattern rather than an accident, so v7.7 fixes the
class instead of the two instances.

**Every scale now publishes the rule that governs it**, at `scaleRules`, alongside the values
it governs. The Brand Guide carries them as `data-rule` on each `<table data-scale>`, so a
rule lives beside its values in one place and cannot drift from them. A new lint check, L20,
fails the build if a scale ships values without a rule.

```json
"scaleRules": {
  "radius": "Three steps, no others. Nothing in this system is a pill…",
  "motion": "Motion confirms an action. It never performs. Nothing bounces and nothing springs…",
  "spacing": "A four-pixel base. Every margin, padding, gap and inset is one of these steps…",
  …
}
```

---

## The seven

### 1. Pill radius

**There is no pill, and there is not going to be one.** A fully rounded control is not a radius
this brand has. Primary actions use `radius-button`, 3px, the same as every other button.

The reasoning is already in Law V: *a formal frame around burning content*. The near-square
corner is a large part of what makes this read as an institution that keeps records rather
than a consumer app. It is the single geometric decision doing the most work, which is why
your own note called radius "the largest visible change" and was right.

`9999` should go. Replace it with `radius-button` rather than with a smaller pill.

### 2. `screenGutter`, the 20px mobile edge inset

**Use `space-5`, 24px, on every surface including a phone.** 20px is not on the scale and
there is no step between 16 and 24.

This is not a new ruling, it is what this brand already does: the EVERY1 site's own page
container is `padding: 0 var(--space-5)` at every width, phone included. You can read it off
the stylesheet you are already linking.

The spacing rule now says so out loud:

> A four-pixel base. Every margin, padding, gap and inset is one of these steps and nothing
> between them. The page edge inset is space-5 on every surface, a phone included, which is
> what this site itself uses.

If 24px ever proves genuinely wrong on the smallest handsets, that is a brand change with a
version bump, not a token a product sets for itself.

### 3. Tabular numerals

**Already published, and you have it.** It is on every step of the type scale as `figures`:

| Step | Family | Figures |
|---|---|---|
| `label` | DM Sans | **tabular** |
| `caption` | DM Sans | **tabular** |
| `body-small`, `body`, `body-large` | DM Sans | proportional |
| `title-small`, `title`, `title-large` | DM Serif Text | proportional |
| `display-small`, `display`, `display-large` | DM Serif Display | **tabular** |

So your live counters are `display` or `display-small`, and the label under them is `label`.
Both are tabular, which is exactly the jitter case you raised. Set
`font-variant-numeric: tabular-nums`. All three families carry the feature.

The display steps are tabular by default because the display sizes are where the record's
numerals are set, and that is the number people watch.

### 4. Scripture style

**A treatment existed and was published as prose in §04, which is why you could not find it in
the data.** It is now published as data at `scripture` in the manifest:

| | |
|---|---|
| family | DM Serif Text |
| steps | `title-small` or `title` |
| weight | 400 |
| italic | never across the whole verse |
| case | as written. Never all caps |
| quotation marks | **never.** The setting is what marks it |
| reference | required, on its own line, in the `label` step |
| reference colour | `ink-muted` on light, `ink-reversed-muted` on dark |
| rule above | hairline. Never a coloured bar and never a Flame accent |
| exception | the Vision lockup, which is a published file rather than a setting to reproduce |

> A verse is not a pull quote and is not decoration. It is the one voice in this system that is
> not ours, and it is set so a reader can see that before reading a word of it. Never reflowed,
> never trimmed to fit, never paraphrased: if it does not fit, the layout changes.

**This means Source Serif 4 comes out.** See question 5.

### 5. The manifesto display face

**No. DM Serif Display covers it, at `display-large`.**

This one needs stating plainly, because it is larger than the question as asked. The app is
currently shipping **two typefaces that are not in this brand**: Archivo Expanded for manifesto
screens and Source Serif 4 for scripture. The rule is three faces and no others, and it now
says so in the data:

> Three faces and no others, in the weights and figures named here. A face outside the three is
> not a substitution, it is a different brand. Where a face cannot load, the fallbacks are
> Georgia for the serifs and the system sans for DM Sans.

A full-bleed manifesto screen is the exact case `display-large` exists for: 72px, line height
1.04, DM Serif Display, at most one italic word. If a manifesto needs more presence, it goes up
in size and down in word count. It does not go up in weight and it does not change face: the
serif has Regular and Italic and no bold cut, and faux-bolding it is a published DON'T.

`brand_check.py` catches both of these today under C1. Running it over the app is the fastest
way to find the rest.

### 6. Semantic motion

**Yes, keep your named motions, layered on the brand's primitives.** You read the split
correctly: the brand describes a document, and the app describes interactions the brand has no
opinion on.

Two conditions, now in the published motion rule:

- **Every named motion resolves to one of the three published durations and the one easing.**
  `counterTickUp` at `duration-fast`, `trackerTapCompress` at `duration-fast`, and so on. No
  new curves.
- **Everything is suppressed under `prefers-reduced-motion`,** including yours.

**One of your eight has to change.** `celebrationSpringIn` is a spring, and *nothing bounces,
nothing springs* is the rule. This is not fussiness about easing: a spring reads as a product
celebrating itself, and what is being counted here is a person meeting Jesus. Confirm the
moment, do not perform it. Use `duration-slow` with the published easing, and let the
composition carry the weight instead of the animation.

Haptics are outside this brand entirely. Use your judgement.

### 7. The 404 content type

**Our claim was wrong, not the behaviour.** The manifest said unknown paths return "a non-HTML
body". They return a real 404 with an HTML page, on purpose: a person who mistypes a URL should
get something that helps rather than a blank.

The sentence is corrected:

> Unknown paths return a real 404, so trust the status code: a failed fetch is a failed fetch.
> The 404 body is HTML by design, because a person who mistypes a URL should get a page that
> helps rather than a blank. Check the status, not the content type.

Good catch, and thank you for reading the prose against the behaviour rather than only the
behaviour.

---

## On your merge order

It is right, and the first item is the one that matters most. **Consume `tokens.dtcg.json`
directly and fail the build on drift.** Everything after it is then generated rather than
transcribed, which is the difference between this being the last reconciliation and the first
of many.

Two notes on the rest:

**Item 2, the contrast gate over composited alpha.** Do run it. Our own gate composites the
translucent neutrals over the ground named in each pair before measuring, and publishes the
result at `contrast.permitted` with 61 pairs. If your numbers and ours disagree on any pair,
that is a defect on one side and we want to hear about it either way.

**Item 5, adopting `brand_check.py`.** Note it moved after v7.6 shipped: a font-family that
ended one element's style attribute was running into the next element's declarations and
reporting the whole run as an invented family. Found by downloading the published copy and
running it the way you would, rather than from inside our repository. Take the current file.

---

## What we are not changing

**The radius, the spacing scale and the three faces are not negotiable per surface.** They are
the parts of this system that make a poster, a letter and an app look like one institution.
Everything you flagged as a divergence in those three is the app moving to the brand, not the
brand widening to fit.

**The elevation and motion encodings can stay yours.** The brand publishes CSS shadows because
the brand is a website; your `{y, blur, opacity}` objects are the same intent in a form Flutter
can use. Keep them, derived from ours. Your `level3` celebration scrim is a ground rather than
an elevation step and belongs with the photography rules, which is where the brand puts scrims.

---

## One more thing, unprompted

Your table lists Raised as *"(published) · `#414753` · check"*. `#414753` is a grey. This
brand has no greys, by a standing rule in §03: the neutral ramp is Midnight and Parchment at
recorded opacities so that nobody reaches for one. The published value is `#860048` on light
and `#FF83B2` on dark.

If a grey got into your outcome palette as a placeholder for the rarest outcome, it is worth
checking what else it stood in for.

brand@theword.world
