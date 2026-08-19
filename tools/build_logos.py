#!/usr/bin/env python3
"""
Derive every published logo file from the approved vector masters.

    assets/logos/_masters/*.svg   the approved artwork, one file per configuration
              │
              ├─→ assets/logos/the-word/*.svg        three inks, transparent, tight-cropped
              ├─→ assets/logos/the-word/png/*.png    four widths, transparent
              ├─→ assets/logos/the-word/favicon/*    the glyph, at icon sizes
              ├─→ assets/downloads/*.zip             the packs a partner or printer asks for
              └─→ ai-source/logo-manifest.json       what the page and the AI layer both read

The masters are the only hand-held files. Everything else is generated, so a colour
variant cannot drift from the artwork it claims to be, and the PNG in a partner's
deck is provably the same shape as the SVG on the site.

    python3 tools/build_logos.py            rebuild everything
    python3 tools/build_logos.py --check    fail if anything is stale, for CI

Rasterizing needs Pillow. --check does not, so CI stays dependency-free.
"""

import argparse
import hashlib
import json
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import svgkit  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTERS = os.path.join(REPO, "assets", "logos", "_masters")
OUT = os.path.join(REPO, "assets", "logos", "the-word")
PNG = os.path.join(OUT, "png")
FAVICON = os.path.join(OUT, "favicon")
DOWNLOADS = os.path.join(REPO, "assets", "downloads")
MANIFEST = os.path.join(REPO, "ai-source", "logo-manifest.json")

# Deterministic timestamp for zip entries, so an unchanged pack is byte-identical
# and does not show up as a spurious diff on every build.
ZIP_DATE = (2026, 1, 1, 0, 0, 0)

# The three inks, and the grounds the Brand Guide permits each one on.
INKS = {
    "": {
        "hex": "#0B1A2D",
        "name": "Midnight ink",
        "grounds": ["parchment", "white"],
        "note": "The default. Use on Parchment and White.",
    },
    "-reversed": {
        "hex": "#FFFFFF",
        "name": "Reversed, white",
        "grounds": ["midnight", "word-blue", "photography with a Midnight scrim"],
        "note": "Use on Midnight, on Word Blue, and over photography that carries a Midnight scrim.",
    },
    "-black": {
        "hex": "#000000",
        "name": "One colour, black",
        "grounds": ["white", "parchment"],
        "note": (
            "For single-colour reproduction only: embroidery, engraving, newsprint, stamps, and "
            "any vendor who asks for pure black. On screen use the Midnight ink instead."
        ),
    },
}

PNG_WIDTHS = [400, 800, 1600, 3200]
GLYPH_SIZES = [512, 1024, 2048]
# (file, pixels, pad as a fraction of the glyph, plate the Midnight ground behind it).
# Browser favicons stay tight and transparent so they read at 16px. Home-screen icons
# get a Midnight plate and a real safe area, because the OS rounds their corners.
FAVICONS = [
    ("favicon-16.png", 16, 0.02, False),
    ("favicon-32.png", 32, 0.02, False),
    ("favicon-48.png", 48, 0.02, False),
    ("apple-touch-icon-180.png", 180, 0.16, True),
    ("icon-192.png", 192, 0.16, True),
    ("icon-512.png", 512, 0.16, True),
]

# One entry per master. `clear` is the clear-space rule as a multiple of the cap
# height of THE WORD, which the build measures from the artwork itself.
CONFIGS = [
    {
        "slug": "horizontal",
        "master": "the-word-logo",
        "name": "Horizontal lockup",
        "primary": True,
        "clear": 0.5,
        "min_px": 180,
        "min_mm": 40,
        "use": (
            "The default mark. Site navigation, letterhead, email headers, banners, slide masters, "
            "and video lower-thirds. Anywhere the space is wider than it is tall."
        ),
    },
    {
        "slug": "stacked",
        "master": "the-word-stacked",
        "name": "Stacked lockup",
        "primary": False,
        "clear": 0.5,
        "min_px": 120,
        "min_mm": 25,
        "use": (
            "Square and portrait spaces: merchandise, book and report covers, posters, tote bags, "
            "and social posts that are not wide."
        ),
    },
    {
        "slug": "bare",
        "master": "the-word-bare",
        "name": "Bare wordmark",
        "primary": False,
        "clear": 0.5,
        "min_px": 90,
        "min_mm": 20,
        "use": (
            "THE WORD with no endorsement line. Use where the sub-line would fall below legibility, "
            "or where the surrounding context already says who we are."
        ),
    },
    {
        "slug": "glyph",
        "master": "the-word-glyph",
        "name": "Microphone glyph",
        "primary": False,
        "cap_is_height": True,
        "clear": 0.25,
        "min_px": 24,
        "min_mm": 8,
        "use": (
            "The mark reduced to the microphone O. Favicons, app icons, profile pictures, stickers, "
            "watermarks, and any square that is too small for the wordmark to be read."
        ),
    },
    {
        "slug": "heritage",
        "master": "the-word-heritage-est-2018",
        "name": "Heritage lockup, EST 2018",
        "primary": False,
        "clear": 0.4,
        "min_px": 140,
        "min_mm": 30,
        "use": (
            "The founding date lockup. Certificates, commemorative print, apparel, and anywhere the "
            "record of when this began is part of the point. Not the default mark."
        ),
    },
]

# ── reading the masters ───────────────────────────────────────────────────────

_RECT_RE = re.compile(r"<rect\b[^>]*/>\s*", re.S)
_SVG_OPEN_RE = re.compile(r"<svg\b[^>]*>", re.S)
_TITLE_RE = re.compile(r"<title\b[^>]*>.*?</title>\s*", re.S)
_DESC_RE = re.compile(r"<desc\b[^>]*>.*?</desc>\s*", re.S)
_COMMENT_RE = re.compile(r"<!--.*?-->\s*", re.S)
_G_OPEN_RE = re.compile(r"<g\b([^>]*)>")
_FILL_ATTR_RE = re.compile(r'\s(?:fill|color)="[^"]*"')


def cap_height(shapes, box):
    """
    Cap height of THE WORD, measured from the artwork.

    In every lockup the leftmost ink is the left edge of the T, whose arm spans the
    full cap height. Sampling a thin column at the left edge therefore returns the
    cap height without needing to know anything about the typeface.
    """
    x0, y0, x1, y1 = box
    band = x0 + (x1 - x0) * 0.04
    ys = [
        y
        for sh in shapes
        for sp in sh.subpaths
        for (x, y) in sp
        if x <= band
    ]
    return (max(ys) - min(ys)) if len(ys) >= 2 else (y1 - y0)


def read_master(slug, cap_is_height=False):
    """Parse a master and return its source text, artwork box, and cap height."""
    path = os.path.join(MASTERS, f"{slug}.svg")
    shapes, _vb = svgkit.load(path)
    if not shapes:
        raise SystemExit(f"{path}: no drawable paths")
    box = svgkit.bbox(shapes)
    # The glyph has no letterforms to measure, so its own height is the reference.
    cap = (box[3] - box[1]) if cap_is_height else cap_height(shapes, box)
    return {"src": open(path, encoding="utf-8").read(), "shapes": shapes, "box": box, "cap": cap}


def make_svg(master, cfg, ink_suffix, ink):
    """
    Emit one published SVG: the master's own path data, re-inked and tight-cropped.

    The path data is passed through untouched rather than re-serialised from the
    parsed geometry, so curves stay curves and nothing is lost in translation. Only
    the canvas and the fills change.
    """
    src = master["src"]
    x0, y0, x1, y1 = master["box"]
    w, h = x1 - x0, y1 - y0

    body = _RECT_RE.sub("", src)  # the master's background square is not part of the mark
    body = _TITLE_RE.sub("", body)
    body = _DESC_RE.sub("", body)
    body = _COMMENT_RE.sub("", body)  # the master's provenance note does not describe this file
    body = _SVG_OPEN_RE.sub("", body, count=1)
    body = body.replace("</svg>", "").strip()

    # Every fill becomes the ink. Groups carry it so per-path currentColor resolves.
    body = _FILL_ATTR_RE.sub("", body)
    body = _G_OPEN_RE.sub(lambda m: f'<g{m.group(1)} fill="{ink["hex"]}">', body)
    body = re.sub(r"<path\b", f'<path fill="{ink["hex"]}"', body)

    label = f'THE WORD FOR ALL THE WORLD, {cfg["name"].lower()}'
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{r(x0)} {r(y0)} {r(w)} {r(h)}" '
        f'width="{r(w)}" height="{r(h)}" role="img" aria-label="{label}">',
        f"  <title>{label}</title>",
        f"  <!-- Generated by tools/build_logos.py from assets/logos/_masters/{cfg['master']}.svg. "
        f"Do not edit by hand. Clear space: {cfg['clear']}x {clear_ref(cfg)} "
        f"({r(master['cap'] * cfg['clear'])} units here) on all four sides. "
        f"Minimum width {cfg['min_px']}px / {cfg['min_mm']}mm. -->",
        "  " + body,
        "</svg>",
        "",
    ]
    return "\n".join(lines)


def clear_ref(cfg):
    """What the clear-space rule is measured against, in words a human can act on."""
    return "its own height" if cfg.get("cap_is_height") else "the cap height of THE WORD"


def r(v):
    """Trim float noise so an unchanged build produces an unchanged file."""
    return f"{round(v, 2):g}"


# ── rasterizing ───────────────────────────────────────────────────────────────


def render(master, ink_hex, width, height=None, pad=0.0, square=False):
    from PIL import Image

    x0, y0, x1, y1 = master["box"]
    aw, ah = x1 - x0, y1 - y0
    if square:
        side = max(aw, ah) * (1 + pad * 2)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        x0, y0 = cx - side / 2, cy - side / 2
        aw = ah = side
    s = width / aw
    height = height or max(1, round(ah * s))

    shapes = [svgkit.Shape(sh.subpaths, ink_hex, sh.rule) for sh in master["shapes"]]
    return svgkit.rasterize(shapes, width, height, lambda x, y: ((x - x0) * s, (y - y0) * s))


# ── writing ───────────────────────────────────────────────────────────────────


class Writer:
    """Collects what would be written, so --check can compare without touching disk."""

    def __init__(self, check):
        self.check = check
        self.stale = []
        self.written = 0

    def blob(self, path, data):
        rel = os.path.relpath(path, REPO)
        current = open(path, "rb").read() if os.path.exists(path) else None
        if current == data:
            return
        if self.check:
            self.stale.append(rel)
            return
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as fh:
            fh.write(data)
        self.written += 1

    def text(self, path, s):
        self.blob(path, s.encode("utf-8"))

    def image(self, path, img):
        import io

        buf = io.BytesIO()
        img.save(buf, "PNG", optimize=True)
        self.blob(path, buf.getvalue())


def build(check):
    if not os.path.isdir(MASTERS):
        raise SystemExit(f"missing {os.path.relpath(MASTERS, REPO)}: nothing to build from")

    w = Writer(check)
    masters = {}
    entries = []

    for cfg in CONFIGS:
        m = read_master(cfg["master"], cfg.get("cap_is_height", False))
        masters[cfg["slug"]] = m
        x0, y0, x1, y1 = m["box"]
        aw, ah = x1 - x0, y1 - y0

        files = []
        for suffix, ink in INKS.items():
            stem = f"the-word-{cfg['slug']}{suffix}"
            w.text(os.path.join(OUT, f"{stem}.svg"), make_svg(m, cfg, suffix, ink))
            files.append({"file": f"assets/logos/the-word/{stem}.svg", "format": "svg", "ink": ink["name"]})

            widths = GLYPH_SIZES if cfg["slug"] == "glyph" else PNG_WIDTHS
            for px in widths:
                name = f"{stem}-{px}.png"
                # The manifest is written the same way in both modes, so --check compares
                # like for like. Only the pixels are skipped, because CI has no Pillow.
                if check:
                    if not os.path.exists(os.path.join(PNG, name)):
                        w.stale.append(f"assets/logos/the-word/png/{name}")
                else:
                    w.image(
                        os.path.join(PNG, name),
                        render(m, ink["hex"], px, square=(cfg["slug"] == "glyph")),
                    )
                files.append(
                    {
                        "file": f"assets/logos/the-word/png/{name}",
                        "format": "png",
                        "ink": ink["name"],
                        "width": px,
                    }
                )

        entries.append(
            {
                "slug": cfg["slug"],
                "name": cfg["name"],
                "primary": cfg["primary"],
                "use": cfg["use"],
                "aspect": round(aw / ah, 4),
                "capHeight": round(m["cap"], 2),
                "clearSpace": f"{cfg['clear']}x {clear_ref(cfg)} on all four sides",
                "clearSpaceReference": clear_ref(cfg),
                "clearSpaceRatio": cfg["clear"],
                "minimumWidth": {"screen": f"{cfg['min_px']}px", "print": f"{cfg['min_mm']}mm"},
                "files": files,
            }
        )

    # The glyph doubles as the site icon set.
    g = masters["glyph"]
    if check:
        for name, _px, _pad, _plate in FAVICONS:
            if not os.path.exists(os.path.join(FAVICON, name)):
                w.stale.append(f"assets/logos/the-word/favicon/{name}")
        # Zipping needs no imaging library, so the packs are content-verified in CI
        # rather than merely checked for existence.
        write_packs(w)
    else:
        for name, px, pad, plate in FAVICONS:
            img = render(g, "#FFFFFF" if plate else "#0B1A2D", px, square=True, pad=pad)
            if plate:
                from PIL import Image

                ground = Image.new("RGBA", (px, px), (11, 26, 45, 255))
                ground.alpha_composite(img)
                img = ground
            w.image(os.path.join(FAVICON, name), img)

        write_packs(w)

    manifest = {
        "_README": (
            "Generated by tools/build_logos.py. The published logo set, its rules, and every "
            "derived file. build_ai.py folds this into /ai/assets.json and assets/index.html "
            "renders from it, so the page, the standard, and the files cannot disagree."
        ),
        "inks": [
            {"suffix": s or "(none)", "hex": i["hex"], "name": i["name"], "grounds": i["grounds"], "note": i["note"]}
            for s, i in INKS.items()
        ],
        "never": [
            "Never place any logo on Flame (#F85842).",
            "Never redraw, restretch, rotate, or recolour the mark outside the three published inks.",
            "Never add effects: no shadow, glow, bevel, outline, or gradient.",
            "Never set the mark below its published minimum width.",
            "Never rebuild a lockup by typesetting it. Use the published file.",
        ],
        "provenance": (
            "The masters in assets/logos/_masters are a vector reconstruction, not an original "
            "drawing. The THE WORD letterforms and the microphone are an autotrace on a 0.25-unit "
            "grid, roughly 1/394 of the mark's height, so curves are dense polygons rather than "
            "Bezier curves. This is invisible on screen and in normal print. On large-format work, "
            "a banner, a vehicle, or a building sign, faceting can become visible under close "
            "inspection, and the mark should be redrawn as true curves before that use."
        ),
        "configurations": entries,
        "packs": PACKS,
    }
    w.text(MANIFEST, json.dumps(manifest, indent=2) + "\n")
    w.text(os.path.join(REPO, "assets", "index.html"), render_page(masters, entries))

    if check:
        if w.stale:
            print("Logo files are stale. Run: python3 tools/build_logos.py")
            for s in sorted(w.stale)[:20]:
                print(f"  {s}")
            if len(w.stale) > 20:
                print(f"  ... and {len(w.stale) - 20} more")
            return 1
        print("Logo files are current.")
        return 0

    print(f"Wrote {w.written} file(s) from {len(CONFIGS)} master(s).")
    return 0


# ── the page ──────────────────────────────────────────────────────────────────

# The two typefaces, stated once here and rendered into the Fonts section. Both are
# free on Google Fonts, which is why volunteers and field teams can always get them.
FONTS = [
    {
        "name": "DM Serif Display",
        "role": "Headlines",
        "css": "'DM Serif Display', Georgia, 'Times New Roman', serif",
        "note": (
            "Every headline and every display numeral. Sentence case, at most one italic word for "
            "emphasis. One weight exists, so there is no bold: go bigger instead."
        ),
        "url": "https://fonts.google.com/specimen/DM+Serif+Display",
    },
    {
        "name": "DM Serif Text",
        "role": "Pull quotes",
        "css": "'DM Serif Text', Georgia, 'Times New Roman', serif",
        "note": (
            "Scripture, pull quotes, and section headings. Never below 22px, where it turns harder "
            "to read rather than more formal."
        ),
        "url": "https://fonts.google.com/specimen/DM+Serif+Text",
    },
    {
        "name": "DM Sans",
        "role": "Everything else",
        "css": "'DM Sans', -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif",
        "note": (
            "Body copy, navigation, buttons, eyebrows, labels, captions, and tables. True bold and "
            "true italics. This is the face the wordmark was drawn beside."
        ),
        "url": "https://fonts.google.com/specimen/DM+Sans",
    },
]

# The literal snippet a developer pastes. Stored unescaped and escaped at render
# time, because a <pre> holding raw tags gets parsed as markup and shows nothing.
FONT_CSS_IMPORT = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1'
    "&family=DM+Serif+Text:ital@0;1&family=DM+Sans:ital,opsz,wght@0,9..40,400;"
    '0,9..40,500;0,9..40,600;0,9..40,700&display=swap" rel="stylesheet">'
)


def esc(text):
    """Escape for HTML text content, so a code sample is shown rather than parsed."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def kb(path):
    """Human-sized file size, for the meta line on a card."""
    full = os.path.join(REPO, path)
    if not os.path.exists(full):
        return "missing"
    n = os.path.getsize(full)
    return f"{n / 1024 / 1024:.1f} MB" if n >= 1024 * 1024 else f"{max(1, round(n / 1024))} KB"


def mark_card(cfg, entry, master):
    """One logo configuration: specimen on both grounds, the specs, and every download."""
    slug = cfg["slug"]
    x0, y0, x1, y1 = master["box"]
    aw, ah = x1 - x0, y1 - y0
    base = "/assets/logos/the-word"
    svg = f"{base}/the-word-{slug}.svg"

    # Clear space as a percentage of the artwork's width. CSS resolves percentage
    # padding against width on all four sides, so one number gives an even margin.
    clear_pct = round(cfg["clear"] * master["cap"] / aw * 100, 2)

    widths = GLYPH_SIZES if slug == "glyph" else PNG_WIDTHS
    png_links = " ".join(
        f'<a href="{base}/png/the-word-{slug}-{p}.png" download>{p}px</a>' for p in widths
    )
    png_rev = " ".join(
        f'<a href="{base}/png/the-word-{slug}-reversed-{p}.png" download>{p}px</a>' for p in widths
    )
    tag = "The default mark" if cfg["primary"] else "Alternate"

    return f"""
        <div class="card" id="{slug}">
          <div class="card-h">
            <h3>{cfg['name']}</h3>
            <span class="meta">{tag} · {r(aw)} × {r(ah)} · SVG {kb(f'assets/logos/the-word/the-word-{slug}.svg')}</span>
          </div>
          <code class="slug">the-word-{slug}.svg</code>
          <p class="use">{cfg['use']}</p>

          <div class="two">
            <div class="stage light"><img src="{svg}" alt="{cfg['name']}, Midnight ink on Parchment" loading="lazy"></div>
            <div class="stage dark"><img src="{base}/the-word-{slug}-reversed.svg" alt="{cfg['name']}, reversed on Midnight" loading="lazy"></div>
          </div>

          <dl class="specs">
            <div><dt>Clear space</dt><dd>{cfg['clear']}× {clear_ref(cfg)}, all four sides</dd></div>
            <div><dt>Minimum width</dt><dd>{cfg['min_px']}px screen · {cfg['min_mm']}mm print</dd></div>
          </dl>

          <div class="grab">
            <a href="{svg}" download>SVG</a>
            <a class="ghost" href="{base}/the-word-{slug}-reversed.svg" download>SVG reversed</a>
            <a class="ghost" href="{base}/the-word-{slug}-black.svg" download>SVG black</a>
          </div>
          <div class="sizes"><span>PNG, Midnight</span>{png_links}</div>
          <div class="sizes"><span>PNG, reversed</span>{png_rev}</div>
        </div>"""


def render_page(masters, entries):
    cards = "\n".join(
        mark_card(cfg, e, masters[cfg["slug"]]) for cfg, e in zip(CONFIGS, entries)
    )

    ink_rows = "\n".join(
        f"        <tr><td><code>the-word-&lt;mark&gt;{s or ''}.svg</code></td>"
        f'<td><span class="sw" style="background:{i["hex"]};'
        f'{"border:1px solid var(--rule);" if i["hex"] == "#FFFFFF" else ""}"></span>{i["name"]} '
        f'<code>{i["hex"]}</code></td><td>{i["note"]}</td></tr>'
        for s, i in INKS.items()
    )

    pack_cards = "\n".join(
        f"""        <div class="pack">
          <h3>{p['name']}</h3>
          <p>{p['note']}</p>
          <a href="/{p['file']}" download>Download · {kb(p['file'])}</a>
        </div>"""
        for p in PACKS
        if os.path.exists(os.path.join(REPO, p["file"]))
    )

    font_cards = "\n".join(
        f"""        <div class="font">
          <div class="aa" style="font-family:{f['css']};">Aa</div>
          <div class="fmeta">
            <h3>{f['name']}</h3>
            <span class="role">{f['role']}</span>
            <p>{f['note']}</p>
            <a href="{f['url']}" rel="noopener">Get it on Google Fonts</a>
          </div>
        </div>"""
        for f in FONTS
    )

    hz = masters["horizontal"]
    hx0, hy0, hx1, hy1 = hz["box"]
    clear_pct = round(CONFIGS[0]["clear"] * hz["cap"] / (hx1 - hx0) * 100, 2)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
<title>Assets · THE WORD FOR ALL THE WORLD</title>
<meta name="description" content="Every approved logo, in every format, with the clear space, minimum size, and colour rules that come with it. Fonts, photography, video, and download packs for THE WORD FOR ALL THE WORLD.">
<link rel="icon" href="/assets/logos/the-word/favicon/favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="/assets/logos/the-word/favicon/apple-touch-icon-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Serif+Text:ital@0;1&family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&display=swap" rel="stylesheet">
<style>
  :root{{
    --midnight:#0B1A2D;
    --word-blue:#023D6F;
    --parchment:#F7F3EC;
    --flame:#F85842;
    --ember:#C13A24;
    --white:#FFFFFF;
    --rule:rgba(11,26,45,.18);
    --rule-light:rgba(247,243,236,.22);
    --serif-display:'DM Serif Display', Georgia, 'Times New Roman', serif;
    --serif-text:'DM Serif Text', Georgia, 'Times New Roman', serif;
    --sans:'DM Sans', -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif;
  }}
  *{{margin:0;padding:0;box-sizing:border-box;}}
  @media (prefers-reduced-motion: no-preference){{html{{scroll-behavior:smooth;}}}}
  body{{font-family:var(--sans);font-size:17px;line-height:1.7;color:var(--midnight);background:var(--parchment);-webkit-font-smoothing:antialiased;}}
  a:focus-visible,button:focus-visible{{outline:2px solid var(--ember);outline-offset:3px;border-radius:3px;}}
  .sitenav a:focus-visible,.band a:focus-visible,footer a:focus-visible{{outline-color:var(--flame);}}
  .wrap{{max-width:1020px;margin:0 auto;padding:0 32px;width:100%;}}

  /* site nav · unified chrome */
  .sitenav{{position:absolute;top:0;left:0;right:0;z-index:10;}}
  .sitenav .bar{{max-width:1240px;margin:0 auto;padding:26px 36px;display:flex;justify-content:space-between;align-items:center;gap:20px;}}
  .sitenav .logo img{{height:20px;width:auto;display:block;}}
  .sitenav .links{{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:12px 28px;font-size:12.5px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;}}
  .sitenav .links a{{color:rgba(247,243,236,.9);text-decoration:none;}}
  .sitenav .links a:hover{{color:var(--white);}}
  .sitenav .links a.active{{color:var(--white);border-bottom:1px solid rgba(255,255,255,.6);padding-bottom:2px;}}

  .band{{background:var(--midnight);color:var(--parchment);padding:150px 0 64px;text-align:center;}}
  .band .kicker{{font-size:13px;font-weight:600;letter-spacing:.22em;text-transform:uppercase;color:var(--white);opacity:.8;margin-bottom:18px;display:block;}}
  .band h1{{font-family:var(--serif-display);font-weight:400;line-height:1.1;font-size:clamp(34px,5vw,54px);}}
  .band h1 em{{font-style:italic;}}
  .band p{{margin:18px auto 0;max-width:640px;color:rgba(247,243,236,.85);}}

  main{{padding:72px 0 96px;}}
  .section-label{{font-size:12px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:var(--ember);margin-bottom:24px;}}
  h2{{font-family:var(--serif-text);font-weight:400;font-size:clamp(26px,3.4vw,36px);line-height:1.2;margin-bottom:16px;}}
  .lede{{max-width:70ch;color:rgba(11,26,45,.85);}}
  .lede a{{color:var(--word-blue);}}
  .lede a:hover{{color:var(--ember);}}
  .blk{{margin-top:64px;}}

  .law{{background:var(--white);border:1px solid var(--rule);border-left:3px solid var(--word-blue);padding:28px 30px;margin-top:8px;}}
  .law ol{{margin:0 0 0 20px;}}
  .law li{{margin-bottom:12px;font-size:15.5px;line-height:1.7;}}
  .law li:last-child{{margin-bottom:0;}}
  .law li b{{font-weight:700;}}

  /* clear space diagram */
  .diagram{{display:grid;grid-template-columns:1fr;gap:18px;margin-top:24px;}}
  @media(min-width:760px){{.diagram{{grid-template-columns:1.4fr 1fr;align-items:center;}}}}
  .cs-box{{background:var(--white);border:1px solid var(--rule);padding:34px;}}
  .cs-inner{{outline:1.5px dashed var(--ember);outline-offset:0;padding:{clear_pct}%;}}
  .cs-inner img{{width:100%;height:auto;display:block;}}
  .cs-note{{font-size:15px;color:rgba(11,26,45,.85);}}
  .cs-note b{{display:block;font-size:12px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--ember);margin-bottom:8px;}}

  /* mark cards */
  .kit{{margin-top:26px;display:grid;gap:26px;}}
  .card{{background:var(--white);border:1px solid var(--rule);border-radius:4px;padding:26px 28px 24px;scroll-margin-top:20px;}}
  .card-h{{display:flex;justify-content:space-between;align-items:baseline;gap:16px;flex-wrap:wrap;margin-bottom:6px;}}
  .card-h h3{{font-family:var(--serif-text);font-weight:400;font-size:23px;line-height:1.2;}}
  .card-h .meta{{font-size:11.5px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:rgba(11,26,45,.8);}}
  .card .slug{{font-family:'SF Mono', Consolas, monospace;font-size:12.5px;color:var(--word-blue);background:rgba(2,61,111,.07);border-radius:3px;padding:2px 7px;}}
  .card .use{{font-size:14.5px;color:rgba(11,26,45,.8);margin:10px 0 20px;max-width:66ch;}}
  .two{{display:grid;grid-template-columns:1fr;gap:12px;}}
  @media(min-width:620px){{.two{{grid-template-columns:1fr 1fr;}}}}
  .stage{{border:1px solid var(--rule);border-radius:3px;padding:30px 26px;display:flex;align-items:center;justify-content:center;min-height:120px;}}
  .stage.light{{background:var(--parchment);}}
  .stage.dark{{background:var(--midnight);border-color:transparent;}}
  .stage img{{width:100%;max-width:330px;height:auto;display:block;}}
  #glyph .stage img{{max-width:104px;}}

  .specs{{display:flex;flex-wrap:wrap;gap:10px 34px;margin-top:16px;padding-top:14px;border-top:1px solid var(--rule);}}
  .specs dt{{font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:rgba(11,26,45,.6);}}
  .specs dd{{font-size:14.5px;}}

  .grab{{display:flex;flex-wrap:wrap;gap:10px;margin-top:16px;}}
  .grab a{{font-size:11.5px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;text-decoration:none;color:var(--white);background:var(--ember);border-radius:3px;padding:10px 16px;}}
  .grab a:hover{{background:#A62F1B;}}
  .grab a.ghost{{background:transparent;color:var(--word-blue);border:1px solid var(--rule);}}
  .grab a.ghost:hover{{color:var(--ember);border-color:var(--ember);background:transparent;}}
  .sizes{{display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px;margin-top:12px;font-size:13px;}}
  .sizes span{{font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:rgba(11,26,45,.55);min-width:118px;}}
  .sizes a{{color:var(--word-blue);text-decoration:none;border-bottom:1px solid rgba(2,61,111,.3);}}
  .sizes a:hover{{color:var(--ember);border-color:var(--ember);}}

  table{{width:100%;border-collapse:collapse;margin-top:14px;font-size:15px;background:var(--white);border:1px solid var(--rule);}}
  th,td{{text-align:left;padding:13px 16px;border-bottom:1px solid var(--rule);vertical-align:top;}}
  tr:last-child td{{border-bottom:none;}}
  th{{font-size:11.5px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:rgba(11,26,45,.8);}}
  td code{{font-family:'SF Mono', Consolas, monospace;font-size:12.5px;background:rgba(2,61,111,.07);border-radius:3px;padding:1px 6px;}}
  .sw{{display:inline-block;width:12px;height:12px;border-radius:2px;margin-right:7px;vertical-align:-1px;}}

  .packs{{display:grid;gap:16px;margin-top:24px;grid-template-columns:1fr;}}
  @media(min-width:700px){{.packs{{grid-template-columns:1fr 1fr;}}}}
  .pack{{background:var(--white);border:1px solid var(--rule);border-radius:4px;padding:22px 24px;display:flex;flex-direction:column;gap:8px;}}
  .pack h3{{font-family:var(--serif-text);font-weight:400;font-size:20px;}}
  .pack p{{font-size:14.5px;color:rgba(11,26,45,.8);flex:1;}}
  .pack a{{align-self:flex-start;font-size:11.5px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;text-decoration:none;color:var(--white);background:var(--word-blue);border-radius:3px;padding:10px 16px;margin-top:6px;}}
  .pack a:hover{{background:var(--ember);}}

  .fonts{{display:grid;gap:16px;margin-top:24px;}}
  .font{{background:var(--white);border:1px solid var(--rule);border-radius:4px;padding:22px 24px;display:flex;gap:24px;align-items:flex-start;}}
  .font .aa{{font-size:56px;line-height:1;color:var(--midnight);min-width:80px;text-align:center;}}
  .font h3{{font-family:var(--serif-text);font-weight:400;font-size:21px;display:inline;}}
  .font .role{{font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--ember);margin-left:10px;}}
  .font p{{font-size:14.5px;color:rgba(11,26,45,.8);margin:8px 0 10px;max-width:62ch;}}
  .font a{{font-size:13px;color:var(--word-blue);text-decoration:none;border-bottom:1px solid rgba(2,61,111,.3);}}
  .font a:hover{{color:var(--ember);border-color:var(--ember);}}
  pre{{background:var(--midnight);color:rgba(247,243,236,.92);border-radius:4px;padding:18px 20px;margin-top:16px;overflow-x:auto;font-family:'SF Mono', Consolas, monospace;font-size:12.5px;line-height:1.7;}}

  .note{{max-width:70ch;margin-top:14px;font-size:15px;color:rgba(11,26,45,.8);}}
  .note code{{font-family:'SF Mono', Consolas, monospace;font-size:13px;background:rgba(2,61,111,.07);border-radius:3px;padding:1px 6px;}}
  .note a{{color:var(--word-blue);}}
  .note a:hover{{color:var(--ember);}}

  footer{{background:var(--midnight);color:rgba(247,243,236,.75);padding:40px 0;font-size:12.5px;letter-spacing:.06em;text-transform:uppercase;font-weight:500;}}
  footer .wrap{{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px;}}
  footer img{{height:16px;width:auto;display:block;opacity:.9;}}
  @media(max-width:640px){{.sitenav .bar{{padding:20px 24px;}}.font{{flex-direction:column;gap:12px;}}}}
</style>
</head>
<body>

<nav class="sitenav">
  <div class="bar">
    <a class="logo" href="/" aria-label="THE WORD FOR ALL THE WORLD, portal home">
      <img src="/assets/logos/the-word/the-word-horizontal-reversed.svg" alt="THE WORD FOR ALL THE WORLD">
    </a>
    <div class="links">
      <a href="/">Home</a>
      <a href="/brand/">Brand Guide</a>
      <a href="/brand/messaging/">Messaging</a>
      <a href="/documents/">Documents</a>
      <a href="/letterhead/">Letterhead</a>
      <a href="/signatures/">Signatures</a>
      <a href="/assets/" class="active">Assets</a>
    </div>
  </div>
</nav>

<div class="band">
  <span class="kicker">Assets · Logos, Fonts, Files</span>
  <h1>Take the mark.<br>Use it <em>right.</em></h1>
  <p>Every approved logo, in every format anyone has ever asked us for, with the rules attached rather than filed somewhere else. Nothing here needs permission to download. Everything here has a rule about how it may be placed.</p>
</div>

<main>
  <div class="wrap">

    <div class="section-label">The Law</div>
    <h2>Five rules, and they are not negotiable.</h2>
    <p class="lede">Brand Guide <a href="/brand/#logo">§05</a> says the wordmark is fixed and is not redrawn. These are the mechanics of that sentence.</p>
    <div class="law">
      <ol>
        <li><b>Never on Flame.</b> Flame <code>#F85842</code> is for calls to action. The mark cannot compete with a button, so it never sits on one. Midnight, Word Blue, Parchment, White, or photography carrying a Midnight scrim.</li>
        <li><b>Never redraw it.</b> Do not retype it, restretch it, rotate it, outline it, or rebuild a lockup by setting the words yourself. Download the file. If the format you need is not here, ask for it.</li>
        <li><b>Never recolour it.</b> Three inks are published and no fourth exists. Not a brand colour, not a client colour, not a gradient.</li>
        <li><b>Never add effects.</b> No drop shadow, glow, bevel, outline, or stroke. The mark is flat.</li>
        <li><b>Never crowd it, never shrink it past the floor.</b> Clear space and minimum size are published per mark below and both are measured, not estimated.</li>
      </ol>
    </div>

    <div class="diagram">
      <div class="cs-box">
        <div class="cs-inner"><img src="/assets/logos/the-word/the-word-horizontal.svg" alt="The horizontal lockup with its clear space shown as a dashed boundary"></div>
      </div>
      <div class="cs-note">
        <b>Clear space</b>
        Keep a margin equal to half the cap height of THE WORD on all four sides. Nothing enters it: no text, no rule, no photograph edge, no other logo, no page trim. The dashed line is the boundary, not the mark.
      </div>
    </div>

    <div class="blk">
      <div class="section-label">The Marks</div>
      <h2>Five configurations, three inks each.</h2>
      <p class="lede">Every file below is generated from the same approved artwork, so a PNG and an SVG of the same mark are the same shape. Transparent backgrounds throughout, cropped to the artwork, so you control the spacing using the clear-space rule above.</p>

      <div class="kit">
{cards}
      </div>
    </div>

    <div class="blk">
      <div class="section-label">Ink</div>
      <h2>Which colour, and where it is allowed.</h2>
      <table>
        <tr><th>File</th><th>Ink</th><th>Use it on</th></tr>
{ink_rows}
      </table>
      <p class="note">There is no Flame version, no Ember version, and no Word Blue version of the mark. Word Blue is a ground the reversed mark sits on, not an ink the mark is drawn in.</p>
    </div>

    <div class="blk">
      <div class="section-label">Which File</div>
      <h2>SVG everywhere it is accepted.</h2>
      <p class="lede">The vector is the master. Reach for a PNG only where the destination refuses SVG. Pick a PNG at least twice the width it will be displayed at, and never scale one up.</p>
      <table>
        <tr><th>Where it is going</th><th>Use</th><th>Why</th></tr>
        <tr><td>A website or app</td><td><code>.svg</code></td><td>Sharp at every screen density, and smaller than the PNG it replaces.</td></tr>
        <tr><td>Microsoft Word or PowerPoint</td><td><code>.svg</code></td><td>Insert, then Pictures. Stays sharp when printed or exported to PDF.</td></tr>
        <tr><td>Google Docs or Slides</td><td><code>.png</code></td><td>Google will not import SVG. Use 1600px and let it scale down.</td></tr>
        <tr><td>Canva</td><td><code>.png</code></td><td>SVG upload needs a paid plan. The 1600px file covers most layouts.</td></tr>
        <tr><td>Email signature or newsletter</td><td><code>.png</code></td><td>Most email clients block SVG. Use 400px or 800px.</td></tr>
        <tr><td>Figma, Illustrator, Affinity</td><td><code>.svg</code></td><td>Imports as editable paths and can join a shared library.</td></tr>
        <tr><td>A printer, a banner, a vehicle</td><td><code>.svg</code></td><td>Send the vector and the hex values. Never send a PNG to a printer.</td></tr>
        <tr><td>Embroidery or engraving</td><td><code>-black.svg</code></td><td>One colour, no anti-aliasing to misread. The vendor digitises from this.</td></tr>
        <tr><td>A social profile picture</td><td><code>glyph</code></td><td>The wordmark is unreadable in a circle. The glyph is built for it.</td></tr>
      </table>
    </div>

    <div class="blk">
      <div class="section-label">Packs</div>
      <h2>Everything at once.</h2>
      <p class="lede">For handing to a printer, a partner, a new designer, or anyone who asked for "the logo files" and meant all of them. Each pack carries the usage rules as a text file alongside the artwork.</p>
      <div class="packs">
{pack_cards}
      </div>
    </div>

    <div class="blk">
      <div class="section-label">Partnership Lockups</div>
      <h2>When our mark sits beside someone else's.</h2>
      <p class="lede">There is no published co-brand lockup yet, so build one from the rules rather than improvising a new mark.</p>
      <div class="law">
        <ol>
          <li><b>Equal optical weight, never equal measurement.</b> Match the partner's mark to ours by how large it reads, not by matching pixel heights. A tall square mark set to our wordmark's height will overpower it.</li>
          <li><b>Separate with a hairline rule.</b> A 1px vertical rule in Midnight at 20% opacity, with our full clear space on both sides of it. Never overlap, never touch, never enclose either mark in a box.</li>
          <li><b>We lead when we are the host, and follow when we are the guest.</b> The organisation whose event, venue, or publication it is goes first.</li>
          <li><b>The endorsement line is words, not artwork.</b> Set "In partnership with" or "A ministry of" in DM Sans 600, uppercase, letterspaced 0.18em, at 40% of the cap height of THE WORD. It sits above the marks, never between them.</li>
          <li><b>A partnership lockup is approved once, then reused.</b> Send the first use to <a href="mailto:brand@theword.world">brand@theword.world</a>. It gets published here so nobody rebuilds it a second way.</li>
        </ol>
      </div>
    </div>

    <div class="blk">
      <div class="section-label">Fonts</div>
      <h2>Two families, free to everyone.</h2>
      <p class="lede">DM Serif and DM Sans were drawn as companions on shared proportions, which is why the pages read as one rhythm. Both are free on Google Fonts under the Open Font License, so every volunteer, partner, and field team can install them at no cost. Brand Guide <a href="/brand/#type">§04</a> governs how they are set.</p>
      <div class="fonts">
{font_cards}
      </div>
      <p class="note">On the web, paste this into the <code>&lt;head&gt;</code> before your stylesheet. It loads all three faces in the weights this system uses, and nothing it does not.</p>
      <pre>{esc(FONT_CSS_IMPORT)}</pre>
      <p class="note">In Word, Canva, or Adobe, install the families from the Google Fonts links above rather than substituting. Georgia is the serif fallback and Arial the sans fallback when a system genuinely cannot take a font, for example an email template or a government form. Never substitute a different display face.</p>
    </div>

    <div class="blk">
      <div class="section-label">Photography and Video</div>
      <h2>Real people. Real fire. Real change.</h2>
      <p class="lede">The photographs and footage in <a href="/ai/assets.json">the published inventory</a> are the approved library. Brand Guide <a href="/brand/#media">§06</a> governs how they are used, and two rules matter more than the rest.</p>
      <div class="law">
        <ol>
          <li><b>Never generate or substitute imagery of people or ministry.</b> No stock, no AI, no illustration standing in for a moment that did not happen. If the picture you need does not exist, request it and leave the slot empty.</li>
          <li><b>Type over footage sits on a Midnight scrim at roughly 70% at the text, and is White or Parchment.</b> Never Flame, never Ember, over photography.</li>
        </ol>
      </div>
      <p class="note">Need a photograph or a clip that is not in the library: <a href="mailto:brand@theword.world">brand@theword.world</a>. Say what it is for and what has to be visible in it.</p>
    </div>

    <div class="blk">
      <div class="section-label">For Agents</div>
      <h2>Everything here is machine-readable.</h2>
      <p class="note">Every file on this page is listed in <a href="/ai/assets.json">/ai/assets.json</a> with its status, its approved grounds, its clear space, its minimum size, and its usage note. An agent choosing a logo reads that file rather than this one, and <a href="/ai/manifest.json">/ai/manifest.json</a> carries its checksum. Provenance for each master, including how the artwork was produced, is recorded there.</p>
    </div>

  </div>
</main>

<footer>
  <div class="wrap">
    <a href="/" aria-label="THE WORD FOR ALL THE WORLD, portal home"><img src="/assets/logos/the-word/the-word-horizontal-reversed.svg" alt="THE WORD FOR ALL THE WORLD"></a>
    <span>Every tribe. Every tongue. Every nation. EVERY1.</span>
    <span>brand.theword.world · Internal use</span>
  </div>
</footer>

</body>
</html>
"""


PACKS = [
    {
        "file": "assets/downloads/the-word-logos-svg.zip",
        "name": "Vector pack, SVG",
        "note": "Every configuration in all three inks. For designers, printers, and anyone using Illustrator, Figma, or Word.",
        "globs": ["assets/logos/the-word/*.svg"],
    },
    {
        "file": "assets/downloads/the-word-logos-png.zip",
        "name": "Raster pack, PNG",
        "note": "Every configuration in all three inks, at four widths, transparent. For Google Docs, Slides, Canva, and email.",
        "globs": ["assets/logos/the-word/png/*.png"],
    },
    {
        "file": "assets/downloads/the-word-logos-all.zip",
        "name": "Complete logo pack",
        "note": "Vector, raster, and the icon set, with the usage rules included as a text file.",
        "globs": [
            "assets/logos/the-word/*.svg",
            "assets/logos/the-word/png/*.png",
            "assets/logos/the-word/favicon/*.png",
        ],
        "readme": True,
    },
    {
        "file": "assets/downloads/revival-to-my-city-logos.zip",
        "name": "Revival To My City",
        "note": "The approved RTMC wordmark in all its published forms.",
        "globs": ["assets/logos/rtmc/*.svg"],
    },
]
# Signatures are deliberately not packaged. They are the real signatures of real people,
# and /signatures already offers each one on its own with the rules attached. A one-click
# bundle of every signature makes misuse easier and adds nothing a signer actually needs.


def pack_readme():
    lines = [
        "THE WORD FOR ALL THE WORLD",
        "Logo files and the rules that come with them",
        "",
        "The current standard always lives at https://brand.theword.world/assets",
        "If this pack and the site disagree, the site is right.",
        "",
        "WHICH FILE",
        "",
    ]
    for c in CONFIGS:
        lines += [f"  {c['name']}  (the-word-{c['slug']}-*)", f"    {c['use']}", ""]
    lines += ["INK", ""]
    for suffix, ink in INKS.items():
        lines += [
            f"  {'the-word-<config>' + (suffix or '')}  {ink['name']}  {ink['hex']}",
            f"    {ink['note']}",
            "",
        ]
    lines += ["NEVER", ""]
    lines += [
        "  Never place any logo on Flame (#F85842).",
        "  Never redraw, restretch, rotate, or recolour the mark.",
        "  Never add a shadow, glow, bevel, outline, or gradient.",
        "  Never set a mark below its published minimum width.",
        "  Never rebuild a lockup by typesetting it. Use the file.",
        "",
        "CLEAR SPACE",
        "",
        "  Keep clear space around the mark equal to half the cap height of THE WORD",
        "  on all four sides. Nothing enters that space: no text, no rule, no edge.",
        "",
        "Questions, or you need a format that is not here: brand@theword.world",
        "",
    ]
    return "\n".join(lines)


def write_packs(w):
    import glob
    import io

    for pack in PACKS:
        members = []
        for pattern in pack["globs"]:
            members += sorted(glob.glob(os.path.join(REPO, pattern)))
        if not members:
            continue
        buf = io.BytesIO()
        # Deterministic: sorted members, fixed timestamps, fixed compression.
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            if pack.get("readme"):
                info = zipfile.ZipInfo("READ-ME-FIRST.txt", ZIP_DATE)
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, pack_readme())
            for m in members:
                arc = os.path.relpath(m, os.path.join(REPO, "assets"))
                info = zipfile.ZipInfo(arc, ZIP_DATE)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                z.writestr(info, open(m, "rb").read())
        w.blob(os.path.join(REPO, pack["file"]), buf.getvalue())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="fail if generated files are stale")
    args = ap.parse_args()
    return build(args.check)


if __name__ == "__main__":
    sys.exit(main())
