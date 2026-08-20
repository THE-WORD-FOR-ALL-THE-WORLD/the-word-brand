# @theword/brand

Design tokens for THE WORD FOR ALL THE WORLD, brand system v7.2
(messaging v1.0, updated 2026-08-20).

**Generated. Never edited by hand.** Every value here is read out of the Brand Guide at
<https://brand.theword.world/brand> by `tools/build_ai.py`. Changing a token means changing the guide and
cutting a release, which is what keeps every application on the same brand.

## Install

```bash
npm install @theword/brand
```

## Use it

The tokens are CSS custom properties. Import them once, at the root of the application.

```ts
// app/layout.tsx
import "@theword/brand/tokens.css"
```

Then build with `var(--ember)`, `var(--space-5)`, `var(--text-body)`, and the rest.

For the component layer as well, which is what a landing page or an email wants,
import the full stylesheet instead:

```ts
import "@theword/brand/css"
```

### Tailwind

The preset replaces Tailwind's default palette and type scale rather than extending
them, so an off-brand colour is not one class away.

```js
// tailwind.config.js
module.exports = { presets: [require("@theword/brand/tailwind")] }
```

### In TypeScript

Where CSS cannot reach, a canvas, a chart library, a native view:

```ts
import { color, spacing, fontSize } from "@theword/brand"
```

## Fonts

This package ships no font binaries. In a Next.js application load them with
`next/font/google`, which self-hosts them at build time:

```ts
import { DM_Sans, DM_Serif_Display, DM_Serif_Text } from "next/font/google"
```

Anywhere else, link <https://brand.theword.world/assets/fonts/fonts.css>, which serves the same three
families self-hosted with permissive CORS.

## What this package is not

It is not the brand. The brand is the published system at <https://brand.theword.world>, and the audit at
<https://brand.theword.world/ai/audit.md> is what work is measured against. This package is one of several
ways to consume it, and it is a consumer, never a source. A token changed here and not
in the guide is a bug, and the next build overwrites it.

## Licence

Free to use for work produced for or about THE WORD FOR ALL THE WORLD. Not a licence to
use the wordmark, photography, or video for any other purpose. Contact brand@theword.world.
