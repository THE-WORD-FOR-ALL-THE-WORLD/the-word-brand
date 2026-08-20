# @theword/ui

React components for THE WORD FOR ALL THE WORLD, implementing brand system v7.0
(updated 2026-08-20).

**This package is a consumer, never a source.** The specifications live at
<https://brand.theword.world/ai/components.json> and are rendered at <https://brand.theword.world/components>. When this package
disagrees with them, they are right and this is a bug. A component whose look is decided
here rather than there has taken the brand with it, which is the one thing this structure
exists to prevent.

## Install

```bash
npm install @theword/ui @theword/brand react
```

The components carry no styles of their own. They render the class names that
`@theword/brand` defines, so import the stylesheet once at the root:

```ts
// app/layout.tsx
import "@theword/brand/css"
```

Next.js needs to transpile the source, which ships as TypeScript:

```js
// next.config.js
module.exports = { transpilePackages: ["@theword/ui"] }
```

## What is here

| Component | Specification | Use |
| --- | --- | --- |
| `Button` | `button-primary` | The main call to action. One per view. |
| `Button` | `button-ghost` | The secondary action beside a primary button, on Midnight or over footage. |
| `Eyebrow` | `eyebrow` | Opens a section or a record. Names what the reader is about to read. |
| `Headline` | `headline-serif` | Section and page headlines where the institution speaks. |
| `Card` | `card` | A repeated unit in a grid: a guide, an initiative, a document. |
| `Record` | `record-document` | The canonical treatment for the prophecy, vision statements, official impact summaries, field reports, and initiative documents. Law II and Law IV in their purest form. |
| `Footage` | `hero-video` | Page and priority-panel heroes. |
| `Caption` | `photo-caption` | Every published photograph. A photo without its record does not publish. |
| `LowerThird` | `lower-third` | Naming a speaker on screen. |
| `Stat` | `stat-figure` | Impact reports and per-conference reports. |
| `Endorsement` | `endorsement-line` | Wherever an initiative's name appears. |
| `Field` | `form-field` | Every input on every surface: a partner form, a sign-up, a dashboard. |
| `TableScroll` | `data-table` | Official figures, schedules, and any grid of records. |

## What is deliberately not here

- **body**: a typographic rule, not a component
- **testimony**: a four-slot writing structure, not a component
- **site-chrome**: per-application navigation, built from Eyebrow, Button, and the logo assets
- **email-layout**: email markup: tables and inline styles, which React does not build
- **email-button**: email markup: tables and inline styles, which React does not build

## Naming

Component names match the ids in `components.json`, the Figma layer names, and the
Storybook stories. A Card is a Card wherever anyone looks it up, which is what makes an
audit finding, a design file, and a pull request able to refer to the same thing.

## Licence

Free to use for work produced for or about THE WORD FOR ALL THE WORLD. Not a licence to
use the wordmark, photography, or video for any other purpose. Contact brand@theword.world.
