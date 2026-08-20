# THE WORD brand check, as a GitHub Action

Add this to any repository whose output has to be on brand.

```yaml
# .github/workflows/brand.yml
name: Brand
on: [pull_request]

jobs:
  brand:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: nathan-zimmer/the-word-brand/.github/actions/brand-check@main
        with:
          targets: "dist/**/*.html src/**/*.css"
```

It measures against the manifest at <https://brand.theword.world/ai/manifest.json>, so it
is always checking against the current standard and never against a copy that was current
when the workflow was written. A release of the brand system changes what this reports,
which is the point.

## What it decides

An unknown colour, a font outside the three, text in Flame on a light ground or on a Flame
ground, a banned word, an initiative leading a piece without the endorsement line, a
removed focus ring, an image with no alternative text.

## What it does not decide

Invented facts, stock or generated imagery, whether the prophecy is quoted exactly, who the
hero of the copy is, and every judgement in the audit's identity, composition, record, and
voice sections. **A clean run is not a passed audit.** It means nothing mechanical is wrong.
Run [the audit](https://brand.theword.world/ai/audit.md) with a reader before publishing.
