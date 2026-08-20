#!/usr/bin/env python3
"""Turn a raw export in _inbox into an approved master.

    python3 tools/promote_master.py _inbox/every1-v2/E1-icon.svg every1-icon "EVERY1 icon"

A master is not just a tidy export. It has to carry three things the build depends
on, and a Canva export carries none of them:

  1. No <defs> or <clipPath>. Their paths are never drawn, but anything reading
     the file as artwork counts them, which inflates the measured box and with it
     the clear space and minimum size derived from it.
  2. currentColor on the parts that take the ink, so one drawing serves three inks.
  3. data-role on the parts that do not, so an ink can colour them separately.

The path data is left exactly as exported. Nothing here re-draws a curve: the
transform is textual, so the Beziers that came out of the design tool are the
Beziers that ship.
"""

from __future__ import annotations

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import svgkit  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGOS = os.path.join(REPO, "assets", "logos")
MASTERS = os.path.join(LOGOS, "_masters")

# Which fill means what. The word takes the ink; the numeral is the door's accent
# and is named so an ink can decide its colour independently.
WORD_FILLS = {"#0b1a2d", "#ffffff", "#000000"}
ACCENT_FILLS = {"#f85842"}


def promote(src_path: str, slug: str, title: str, note: str, extra: dict, find_bar: bool) -> str:
    src = open(src_path, encoding="utf-8").read()

    for block in (r"<defs\b.*?</defs>", r"<clipPath\b.*?</clipPath>"):
        while True:
            out = re.sub(block, "", src, flags=re.S)
            if out == src:
                break
            src = out
    src = re.sub(r'\s*clip-path="[^"]*"', "", src)
    src = re.sub(r"\s*(?:zoomAndPan|version|xmlns:xlink)=\"[^\"]*\"", "", src)

    # The country bar is three rectangles in the bottom band. They cannot be told
    # apart from the mark by colour, because USA's bar is Flame and White and the
    # numeral is Flame too. Geometry separates them: a flag segment is a wide, short
    # axis-aligned rectangle sitting below the type. Found this way, the same rule
    # works for a country nobody has drawn yet.
    bar_index = {}
    if find_bar:
        shapes_pre, _ = svgkit.load(src_path)
        ax0, ay0, ax1, ay1 = svgkit.bbox(shapes_pre)
        band = ay1 - (ay1 - ay0) * 0.22
        bars = []
        for i, sh in enumerate(shapes_pre):
            pts = [p for sp in sh.subpaths for p in sp]
            bx0 = min(p[0] for p in pts); bx1 = max(p[0] for p in pts)
            by0 = min(p[1] for p in pts); by1 = max(p[1] for p in pts)
            if by0 < band:
                continue
            w_, h_ = bx1 - bx0, by1 - by0
            if h_ <= 0 or w_ / h_ < 3:
                continue
            if len(sh.subpaths) != 1 or len(sh.subpaths[0]) > 6:
                continue
            bars.append((bx0, i))
        bars.sort()
        for n, (_, i) in enumerate(bars):
            bar_index[i] = f"flag-{chr(ord('a') + n)}"
        if bar_index:
            print(f"  flag bar: {len(bar_index)} segments -> {', '.join(bar_index.values())}")

    # A Canva export paints the <g>, not the <path>. The build reads data-role off the
    # path itself, so the fill has to be resolved down the tree and written onto each
    # path, or every mark comes out one colour with its accent silently lost.
    tag_re = re.compile(r"<(\w+)([^>]*?)(/?)>|</(\w+)>")
    stack = ["#000000"]
    out, pos, path_n = [], 0, 0
    for m in tag_re.finditer(src):
        out.append(src[pos:m.start()])
        pos = m.end()
        if m.group(4):  # closing tag
            if m.group(4) == "g" and len(stack) > 1:
                stack.pop()
            out.append(m.group(0))
            continue
        tag, attrs, selfclose = m.group(1), m.group(2) or "", m.group(3)
        found = re.search(r'fill="(#[0-9A-Fa-f]{6})"', attrs)
        fill = found.group(1).lower() if found else stack[-1]
        if tag == "svg":
            stack[0] = fill
            out.append(m.group(0))
            continue
        if tag == "g":
            if not selfclose:
                stack.append(fill)
            # The wrapper stops carrying colour; every path below now states its own.
            attrs = re.sub(r'\s*fill(?:-opacity)?="[^"]*"', "", attrs)
            out.append(f"<g{attrs}{selfclose}>")
            continue
        if tag == "path":
            # A stroke-only path is not artwork and the loader skips it, so it must
            # not advance the counter either, or every index after it points at the
            # wrong shape. This is how the Uganda bar came out mistagged.
            literal = re.search(r'fill="([^"]*)"', attrs)
            if literal and literal.group(1).strip().lower() in ("none", "transparent"):
                # Dropped, not kept. It draws nothing, the loader ignores it, and any
                # step downstream that repaints every path would turn it into a solid
                # block. A Canva export leaves several of these behind.
                continue
            attrs = re.sub(r'\s*fill(?:-opacity)?="[^"]*"', "", attrs)
            role_here = bar_index.get(path_n)
            path_n += 1
            if role_here:
                out.append(f'<path fill="{fill}" data-role="{role_here}"{attrs}{selfclose}>')
            elif fill in extra:
                # A colour the brand does not own, most often a national flag bar.
                # It is tagged so the ink decides it, rather than left as a literal
                # nobody can reach: a one-colour ink has to be able to flatten it.
                out.append(f'<path fill="{fill}" data-role="{extra[fill]}"{attrs}{selfclose}>')
            elif fill in ACCENT_FILLS:
                out.append(f'<path fill="{fill}" data-role="accent"{attrs}{selfclose}>')
            elif fill in WORD_FILLS:
                out.append(f'<path fill="currentColor"{attrs}{selfclose}>')
            else:
                raise SystemExit(
                    f"{src_path}: path fill {fill} is neither the word, the accent, nor mapped "
                    f"with --map. Map it to a role or correct the artwork."
                )
            continue
        out.append(m.group(0))
    out.append(src[pos:])
    src = "".join(out)

    shapes, _ = svgkit.load(src_path)
    x0, y0, x1, y1 = svgkit.bbox(shapes)
    w, h = x1 - x0, y1 - y0

    def r(v):
        return f"{round(v, 3):g}"

    head = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{r(x0)} {r(y0)} {r(w)} {r(h)}" '
        f'width="{r(w)}" height="{r(h)}" role="img" aria-labelledby="title" color="#0B1A2D">\n'
        f'  <title id="title">MASTER · {title}</title>\n'
        f"  <!-- APPROVED MASTER. Hand-held artwork, not generated.\n"
        f"       {note}\n"
        f"       Promoted from {os.path.relpath(src_path, LOGOS)} by tools/promote_master.py:\n"
        f"       definitions stripped, the word set to currentColor, the numeral tagged\n"
        f"       data-role=\"accent\". No path data was altered. -->\n"
    )
    body = src.split(">", 1)[1] if src.lstrip().startswith("<svg") else src
    body = re.sub(r"^\s*<svg[^>]*>", "", src, flags=re.S)
    body = re.sub(r"^\s*", "", body)
    return head + body


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", help="path under assets/logos/, e.g. _inbox/every1-v2/E1-icon.svg")
    ap.add_argument("slug", help="master filename without .svg")
    ap.add_argument("title", help="human title for the <title> element")
    ap.add_argument("--note", default="Supplied from Canva as outlined type.", help="provenance line")
    ap.add_argument(
        "--map", action="append", default=[],
        help="give a non-brand fill a role, e.g. --map '#ffde59=flag-b'. Repeatable.",
    )
    ap.add_argument(
        "--flag-bar", action="store_true",
        help="find the country bar by geometry and tag its segments flag-a, flag-b, flag-c",
    )
    args = ap.parse_args()
    extra = {}
    for pair in args.map:
        colour, _, role = pair.partition("=")
        if not role:
            raise SystemExit(f"--map needs colour=role, got {pair!r}")
        extra[colour.strip().lower()] = role.strip()

    src_path = os.path.join(LOGOS, args.source)
    if not os.path.exists(src_path):
        raise SystemExit(f"no such file: {src_path}")
    out = promote(src_path, args.slug, args.title, args.note, extra, args.flag_bar)
    dest = os.path.join(MASTERS, f"{args.slug}.svg")
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(out)

    shapes, _ = svgkit.load(dest)
    x0, y0, x1, y1 = svgkit.bbox(shapes)
    roles = sorted({s.role or "(word)" for s in shapes})
    print(f"wrote {os.path.relpath(dest, REPO)}")
    print(f"  {x1 - x0:.2f} x {y1 - y0:.2f}, {len(shapes)} paths, roles: {', '.join(roles)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
