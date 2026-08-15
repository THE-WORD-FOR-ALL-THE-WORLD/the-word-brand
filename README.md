# THE WORD — Brand Portal

Brand site for **THE WORD FOR ALL THE WORLD**, published at
**https://brand.theword.world** via Cloudflare Pages.

The site is publicly readable and open to crawlers, including AI assistants. You can hand
`https://brand.theword.world` (or `https://brand.theword.world/llms.txt`) to Claude, ChatGPT,
or any other tool as a link and it will be able to read the whole brand system.

## Structure

```
├── index.html            # Portal homepage (document hub)
├── brand/index.html      # Brand Guide       → brand.theword.world/brand
├── brand/messaging/index.html  # Messaging Guide → brand.theword.world/brand/messaging
├── templates/          # Document templates   → brand.theword.world/templates/<name>
├── assets/
│   ├── logos/
│   ├── fonts/
│   └── images/
├── archive/            # Retired versions of guides
├── _headers            # Cloudflare Pages headers
├── robots.txt          # Allows all crawlers, points to the sitemap
├── sitemap.xml         # Every public page
└── llms.txt            # Machine-readable index for AI assistants
```

Each guide lives in its own folder as `index.html`, so `brand/index.html` is served at
`/brand`. To add a new guide (e.g. Letterhead):

1. Create `letterhead/index.html` (ask Claude/ChatGPT to draft or revise it).
2. Add a card for it on the homepage (`index.html`) and remove the "Coming soon" state.
3. Commit and push to `main` — Cloudflare Pages publishes automatically in ~30 seconds.
4. Review at `brand.theword.world/letterhead`. To roll back, revert the commit.

## Cloudflare setup (one-time)

1. **Pages**: Cloudflare dashboard → Workers & Pages → Create → Pages →
   Connect to Git → select this repo. Framework preset: *None*, build command: *empty*,
   output directory: `/`. Deploy.
2. **Custom domain**: In the Pages project → Custom domains → add `brand.theword.world`
   (the `theword.world` zone is already on Cloudflare, so this is one click).
3. **Access**: the site is intentionally public so AI tools and search engines can read it.
   Do **not** put a Cloudflare Access application in front of `brand.theword.world`. If one
   exists, remove it (Zero Trust → Access → Applications), otherwise every crawler gets the
   login page instead of the site.
4. **Indexing**: allowed via `robots.txt`, `sitemap.xml`, and the per-page `robots` meta tag.
   Add new pages to `sitemap.xml` and `llms.txt` when you create them.

## Conventions

- Brand tokens (from the Brand Guide): midnight `#0B1A2D`, word blue `#023D6F`,
  parchment `#F7F3EC`, flame `#F85842`, ember `#C13A24`.
- Fonts: DM Serif Display (headlines), DM Serif Text, DM Sans (body) — loaded from Google Fonts.
- Old versions of a guide go to `archive/` rather than being deleted.
- Every page shares the same chrome: `.sitenav` (wordmark + Home / Brand Guide / Messaging,
  `.active` on the current page) over a full-bleed video hero, and the unified midnight
  footer (wordmark · tagline · domain). When adding a page, copy the chrome from an
  existing guide and add its nav link to **all** pages.
- Text over footage: midnight scrim + white type only — never Flame (Brand Guide law).
