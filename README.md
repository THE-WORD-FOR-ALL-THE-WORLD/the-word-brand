# THE WORD — Brand Portal

Private internal brand site for **THE WORD FOR ALL THE WORLD**, published at
**https://brand.theword.world** via Cloudflare Pages and protected by Cloudflare Access.

## Structure

```
├── index.html          # Portal homepage (document hub)
├── brand/index.html    # Brand Guide          → brand.theword.world/brand
├── templates/          # Document templates   → brand.theword.world/templates/<name>
├── assets/
│   ├── logos/
│   ├── fonts/
│   └── images/
├── archive/            # Retired versions of guides
├── _headers            # Cloudflare Pages headers (noindex)
└── robots.txt          # Blocks search crawlers
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
3. **Access**: Zero Trust → Access → Applications → Add application → Self-hosted.
   Protect **both** `brand.theword.world` and the `*.pages.dev` domain (add both as
   application domains). Policy: Allow → Emails / email domain of the team.
   Identity: One-time PIN and/or Google login.
4. **Disable automatic `pages.dev` indexing**: already handled by `robots.txt` + `_headers`.

## Conventions

- Brand tokens (from the Brand Guide): midnight `#0B1A2D`, word blue `#023D6F`,
  parchment `#F7F3EC`, flame `#F85842`, ember `#C13A24`.
- Fonts: DM Serif Display (headlines), DM Serif Text, DM Sans (body) — loaded from Google Fonts.
- Old versions of a guide go to `archive/` rather than being deleted.
