#!/usr/bin/env python3
"""Match the palette to the nearest Pantone in the reference set.

    python3 tools/match_pantone.py

Prints the nearest Pantone Solid Coated colour for each brand colour, with the
CIEDE2000 distance so the quality of the match is visible rather than implied.

What this is NOT: a colour match. Every reference value is a published screen
approximation of an ink, so the result is a starting point for a printer, not a
substitute for a book or a press proof. The distance is printed precisely so a
poor match announces itself: anything above about 2 is visible side by side, and
above 5 the two colours are plainly different.

When a proof confirms or corrects a value, record it in the Brand Guide's print
table through a changelog entry, per GOV10.
"""

from __future__ import annotations

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import brandsource as bs  # noqa: E402


def srgb_to_lab(hex_value: str) -> tuple:
    r, g, b = (int(hex_value[i : i + 2], 16) / 255 for i in (1, 3, 5))

    def linear(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = linear(r), linear(g), linear(b)
    x = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
    y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
    z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041
    # D65 white point
    x, y, z = x / 0.95047, y / 1.00000, z / 1.08883

    def f(t):
        return t ** (1 / 3) if t > 216 / 24389 else (841 / 108) * t + 4 / 29

    fx, fy, fz = f(x), f(y), f(z)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def ciede2000(lab1: tuple, lab2: tuple) -> float:
    """The 2000 formula, because CIE76 overstates differences in blues."""
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2
    avg_L = (L1 + L2) / 2
    C1, C2 = math.hypot(a1, b1), math.hypot(a2, b2)
    avg_C = (C1 + C2) / 2
    G = 0.5 * (1 - math.sqrt(avg_C**7 / (avg_C**7 + 25**7))) if avg_C else 0
    a1p, a2p = a1 * (1 + G), a2 * (1 + G)
    C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    avg_Cp = (C1p + C2p) / 2
    h1p = math.degrees(math.atan2(b1, a1p)) % 360
    h2p = math.degrees(math.atan2(b2, a2p)) % 360

    dLp = L2 - L1
    dCp = C2p - C1p
    if C1p * C2p == 0:
        dhp = 0.0
    elif abs(h2p - h1p) <= 180:
        dhp = h2p - h1p
    else:
        dhp = h2p - h1p - 360 if h2p > h1p else h2p - h1p + 360
    dHp = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dhp) / 2)

    if C1p * C2p == 0:
        avg_hp = h1p + h2p
    elif abs(h1p - h2p) <= 180:
        avg_hp = (h1p + h2p) / 2
    elif h1p + h2p < 360:
        avg_hp = (h1p + h2p + 360) / 2
    else:
        avg_hp = (h1p + h2p - 360) / 2

    T = (
        1
        - 0.17 * math.cos(math.radians(avg_hp - 30))
        + 0.24 * math.cos(math.radians(2 * avg_hp))
        + 0.32 * math.cos(math.radians(3 * avg_hp + 6))
        - 0.20 * math.cos(math.radians(4 * avg_hp - 63))
    )
    Sl = 1 + (0.015 * (avg_L - 50) ** 2) / math.sqrt(20 + (avg_L - 50) ** 2)
    Sc = 1 + 0.045 * avg_Cp
    Sh = 1 + 0.015 * avg_Cp * T
    Rt = (
        -2
        * math.sqrt(avg_Cp**7 / (avg_Cp**7 + 25**7))
        * math.sin(math.radians(60 * math.exp(-(((avg_hp - 275) / 25) ** 2))))
        if avg_Cp
        else 0
    )
    return math.sqrt(
        (dLp / Sl) ** 2 + (dCp / Sc) ** 2 + (dHp / Sh) ** 2 + Rt * (dCp / Sc) * (dHp / Sh)
    )


def quality(delta: float) -> str:
    if delta < 1:
        return "indistinguishable side by side"
    if delta < 2:
        return "very close"
    if delta < 5:
        return "visibly different, usable as a starting point"
    return "not a match: expect a custom mix"


def main() -> int:
    ref = json.loads(bs.read(os.path.join(bs.REPO, "ai-source", "pantone-reference.json")))
    tokens = json.loads(bs.read(os.path.join(bs.REPO, "ai", "tokens.json")))
    lookup = {name: srgb_to_lab(hexv) for name, hexv in ref["colors"].items()}

    print(f"Nearest Pantone Solid Coated, brand system v{tokens['version']}")
    print("Computed from screen approximations. Confirm every one on a press proof.\n")
    for key, colour in tokens["color"].items():
        name, hexv = colour["name"], colour["hex"]
        if name in ref.get("noMatch", {}):
            print(f"  {name:<11} {hexv}   no Pantone: {ref['noMatch'][name]}")
            continue
        lab = srgb_to_lab(hexv)
        best, delta = min(
            ((n, ciede2000(lab, l)) for n, l in lookup.items()), key=lambda x: x[1]
        )
        print(f"  {name:<11} {hexv}   {best:<22} dE2000 {delta:5.2f}   {quality(delta)}")
    print("\nReference set:", len(ref["colors"]), "colours. Add to ai-source/pantone-reference.json as they are confirmed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
