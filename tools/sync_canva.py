#!/usr/bin/env python3
"""Produce the Canva brand kit setup sheet from the published tokens.

    python3 tools/sync_canva.py

Canva is where the people who are not designers actually make things: the flyer
for a city gathering, the certificate, the conference recap. That makes it the
surface where the brand most often breaks, and the one this repository could not
see at all until now.

Canva's Connect API is read-only for brand kit colours and fonts, so this does not
push. It prints exactly what to set, read out of the current tokens, so nobody is
typing a hex from memory. When the API gains write access this becomes a push and
the checklist becomes its dry run.

After following the sheet, record the version in ai-source/consumers.json. That is
what lets the linter answer "is Canva on the current brand" without anyone opening
Canva to look.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import brandsource as bs  # noqa: E402

# The recurring jobs. A blank canvas is where improvisation starts, so each of
# these exists to make the on-brand version the easy version.
TEMPLATES = [
    ("Event flyer", "1080x1350", "A city gathering or conference. Footage, scrim, serif headline, date and place."),
    ("Social post", "1080x1080", "The square. Photograph with its caption, or an official-record figure on Midnight."),
    ("Story", "1080x1920", "Type inside the safe area: nothing in the top 250px or the bottom 350px."),
    ("Conference report", "1080x1350", "Official figures with their source line. Flame numerals on Midnight."),
    ("Certificate", "A4 landscape", "School of the Local Church only, and the only place its seal may appear."),
    ("Quote card", "1080x1080", "Serif on Parchment. Attribution required, and never over a photograph."),
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", help="write the sheet to a file as well as stdout")
    args = parser.parse_args()

    tokens = json.loads(bs.read(os.path.join(bs.REPO, "ai", "tokens.json")))
    consumers = json.loads(bs.read(os.path.join(bs.REPO, "ai-source", "consumers.json")))
    kits = [c for c in consumers["consumers"] if c["kind"] == "canva-brand-kit"]

    L = []
    add = L.append
    add(f"CANVA BRAND KIT SETUP · THE WORD FOR ALL THE WORLD · brand system v{tokens['version']}")
    add("=" * 78)
    add("")

    if len(kits) > 1:
        add("FIRST: there is more than one kit, and that is the problem to fix.")
        add("")
        for k in kits:
            add(f"  {k['location']}   {k['name']}")
        add("")
        add("  Two kits means two answers to what the brand red is, and the people using")
        add("  Canva are the ones least able to tell which is right. Keep one, rename it")
        add(f"  'THE WORD · v{tokens['version']}' so the version is visible to everyone who opens it,")
        add("  and move any design worth keeping out of the other before deleting it.")
        add("  Deleting a kit is not reversible, so this is a decision for the brand")
        add("  owners rather than for a script.")
        add("")

    add("COLOURS  Set exactly these six, and remove every other colour from the kit.")
    add("")
    for key, c in tokens["color"].items():
        add(f"  {c['hex']}   {c['name']:<11}  {c['role']}")
    add("")
    add("  Flame never carries text and never sits under text. In Canva that rule has")
    add("  to be carried by the templates, because the kit cannot enforce it.")
    add("")

    add("FONTS  Add all three from Canva's font library. Do not substitute.")
    add("")
    for f in tokens["typography"]["families"]:
        add(f"  {f['family']:<20} {f['use']}")
    add("")

    add("LOGOS  Upload the PNGs. Canva needs a paid plan to accept SVG, and the")
    add("       1600px raster covers every layout anyone builds there.")
    add("")
    # Checked against disk rather than listed from memory: the glyph is cut at
    # square sizes and the lockups at widths, and a sheet that names a file nobody
    # can find is worse than no sheet.
    missing = []
    for name in (
        "the-word-horizontal-1600.png",
        "the-word-horizontal-reversed-1600.png",
        "the-word-stacked-1600.png",
        "the-word-stacked-reversed-1600.png",
        "the-word-glyph-reversed-1024.png",
    ):
        rel = f"assets/logos/the-word/png/{name}"
        if os.path.exists(os.path.join(bs.REPO, rel)):
            add(f"  {rel}")
        else:
            missing.append(rel)
    if missing:
        raise SystemExit(
            "These files are named in the sheet but are not on disk:\n  "
            + "\n  ".join(missing)
            + "\nRun tools/build_logos.py, or fix the list in tools/sync_canva.py."
        )
    add("")
    add("  The glyph is the avatar. A wordmark in a circle is unreadable.")
    add("")

    add("BRAND TEMPLATES  Build these once and lock them, so the on-brand version is")
    add("                 the easy version rather than the disciplined one.")
    add("")
    for name, size, note in TEMPLATES:
        add(f"  {name:<20} {size:<14} {note}")
    add("")

    add("AFTERWARDS")
    add("")
    add(f"  Set syncedVersion to \"{tokens['version']}\" for the kit you kept, in")
    add("  ai-source/consumers.json, and remove the row for the kit you deleted.")
    add("  Then run tools/brand_lint.py: it will stop warning about Canva.")

    sheet = "\n".join(L)
    print(sheet)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(sheet + "\n")
        print(f"\nWritten to {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
