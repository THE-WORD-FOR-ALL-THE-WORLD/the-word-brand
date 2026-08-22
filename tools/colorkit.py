#!/usr/bin/env python3
"""Colour measurement for the brand system: contrast, perceptual distance, colour blindness.

One implementation, imported by the build and by the linter, so a number published at
/ai/tokens.json and a number the linter gates on cannot disagree. Nothing here has any
dependency outside the standard library, because the build never reaches the network and
CI installs nothing.

    contrast("#C13A24", "#F7F3EC")     WCAG 2.1 relative contrast, 1.0 to 21.0
    de2000(hex2lab(a), hex2lab(b))     CIEDE2000 perceptual distance
    simulate("#5FAD56", "deuteranopia")   the same colour to a dichromat
    separations([...])                 the closest pair in a set, under each kind of vision

Why CIEDE2000 rather than a hex comparison: two colours can differ in every channel and
still be the same colour to a reader. A badge palette is only distinguishable if the
closest pair in it is far enough apart, and that is a perceptual measurement, not an
arithmetic one.
"""

from __future__ import annotations

import math
import re

# ------------------------------------------------------------------ sRGB basics


def hex2rgb(value: str) -> tuple:
    h = value.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        raise ValueError(f"{value!r} is not a six digit hex colour.")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def rgb2hex(rgb: tuple) -> str:
    return "#" + "".join("%02X" % max(0, min(255, round(c * 255))) for c in rgb)


def _to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _from_linear(c: float) -> float:
    return c * 12.92 if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055


def luminance(value: str) -> float:
    """WCAG relative luminance."""
    r, g, b = (_to_linear(c) for c in hex2rgb(value))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(foreground: str, background: str) -> float:
    """WCAG 2.1 contrast ratio. 4.5 is AA for body text, 3.0 for large text."""
    a, b = luminance(foreground), luminance(background)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def blend(foreground: str, background: str, alpha: float) -> str:
    """Flatten a translucent colour over a ground, so it can be measured.

    A token written as rgba() has no contrast ratio until it is composited. This is
    what turns the neutral ramp into numbers.
    """
    f, b = hex2rgb(foreground), hex2rgb(background)
    return rgb2hex(tuple(f[i] * alpha + b[i] * (1 - alpha) for i in range(3)))


_RGBA = re.compile(
    r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([0-9]*\.?[0-9]+)\s*)?\)"
)


def resolve(value: str, ground: str) -> str:
    """A token value as a flat hex, compositing any rgba() over the ground it sits on.

    Half the neutral ramp is written as rgba, because that is how it is authored and
    how it renders. A ratio can only be measured once it is flattened, and it has to
    be flattened against the ground it is actually used on, or the number is fiction.
    """
    v = value.strip()
    m = _RGBA.match(v)
    if not m:
        return v.upper()
    r, g, b = (int(m.group(i)) for i in (1, 2, 3))
    alpha = float(m.group(4)) if m.group(4) is not None else 1.0
    return blend(rgb2hex((r / 255, g / 255, b / 255)), ground, alpha)


# --------------------------------------------------------------- sRGB and CIELAB

_RGB2XYZ = ((0.4124564, 0.3575761, 0.1804375),
            (0.2126729, 0.7151522, 0.0721750),
            (0.0193339, 0.1191920, 0.9503041))
_XYZ2RGB = ((3.2404542, -1.5371385, -0.4985314),
            (-0.9692660, 1.8760108, 0.0415560),
            (0.0556434, -0.2040259, 1.0572252))
_WHITE = (0.95047, 1.0, 1.08883)


def _mul(m: tuple, v: tuple) -> tuple:
    return tuple(sum(m[i][j] * v[j] for j in range(3)) for i in range(3))


def hex2lab(value: str) -> tuple:
    xyz = _mul(_RGB2XYZ, tuple(_to_linear(c) for c in hex2rgb(value)))

    def f(t):
        return t ** (1 / 3) if t > 216 / 24389 else (841 / 108) * t + 4 / 29

    fx, fy, fz = (f(xyz[i] / _WHITE[i]) for i in range(3))
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def lab2hex(lab: tuple) -> str:
    return rgb2hex(tuple(_from_linear(max(0.0, min(1.0, c))) for c in _lab2rgb(lab)))


def _lab2rgb(lab: tuple) -> tuple:
    L, a, b = lab
    fy = (L + 16) / 116
    fx, fz = fy + a / 500, fy - b / 200

    def g(t):
        return t ** 3 if t ** 3 > 216 / 24389 else (108 / 841) * (t - 4 / 29)

    xyz = tuple(g(v) * _WHITE[i] for i, v in enumerate((fx, fy, fz)))
    return _mul(_XYZ2RGB, xyz)


def lch2lab(L: float, C: float, h: float) -> tuple:
    r = math.radians(h)
    return (L, C * math.cos(r), C * math.sin(r))


def lab2lch(lab: tuple) -> tuple:
    L, a, b = lab
    return (L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360)


def in_gamut(lab: tuple, tolerance: float = 0.6) -> bool:
    """True when a Lab value survives a round trip through sRGB without being clipped."""
    rgb = _lab2rgb(lab)
    if any(c < -0.001 or c > 1.001 for c in rgb):
        return False
    return de2000(lab, hex2lab(lab2hex(lab))) < tolerance


# -------------------------------------------------------------------- CIEDE2000


def de2000(lab1: tuple, lab2: tuple) -> float:
    """CIEDE2000 colour difference. Under 1 is indistinguishable side by side."""
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2
    C1, C2 = math.hypot(a1, b1), math.hypot(a2, b2)
    Cbar = (C1 + C2) / 2
    G = 0.5 * (1 - math.sqrt(Cbar ** 7 / (Cbar ** 7 + 25 ** 7))) if Cbar > 0 else 0.5
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360 if (a1p or b1) else 0.0
    h2p = math.degrees(math.atan2(b2, a2p)) % 360 if (a2p or b2) else 0.0
    dLp, dCp = L2 - L1, C2p - C1p
    if C1p * C2p == 0:
        dhp = 0.0
    elif abs(h2p - h1p) <= 180:
        dhp = h2p - h1p
    elif h2p - h1p > 180:
        dhp = h2p - h1p - 360
    else:
        dhp = h2p - h1p + 360
    dHp = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dhp) / 2)
    Lbp, Cbp = (L1 + L2) / 2, (C1p + C2p) / 2
    if C1p * C2p == 0:
        hbp = h1p + h2p
    elif abs(h1p - h2p) <= 180:
        hbp = (h1p + h2p) / 2
    elif h1p + h2p < 360:
        hbp = (h1p + h2p + 360) / 2
    else:
        hbp = (h1p + h2p - 360) / 2
    T = (1 - 0.17 * math.cos(math.radians(hbp - 30))
         + 0.24 * math.cos(math.radians(2 * hbp))
         + 0.32 * math.cos(math.radians(3 * hbp + 6))
         - 0.20 * math.cos(math.radians(4 * hbp - 63)))
    Rc = 2 * math.sqrt(Cbp ** 7 / (Cbp ** 7 + 25 ** 7)) if Cbp > 0 else 0.0
    Sl = 1 + (0.015 * (Lbp - 50) ** 2) / math.sqrt(20 + (Lbp - 50) ** 2)
    Sc, Sh = 1 + 0.045 * Cbp, 1 + 0.015 * Cbp * T
    Rt = -math.sin(math.radians(2 * (30 * math.exp(-(((hbp - 275) / 25) ** 2))))) * Rc
    return math.sqrt((dLp / Sl) ** 2 + (dCp / Sc) ** 2 + (dHp / Sh) ** 2
                     + Rt * (dCp / Sc) * (dHp / Sh))


def distance(a: str, b: str) -> float:
    return de2000(hex2lab(a), hex2lab(b))


# ------------------------------------------------------- colour vision deficiency
#
# Machado, Oliveira and Fernandes (2009), at severity 1.0, applied in linear RGB.
# These are the three dichromacies. Together they cover roughly one man in twelve
# and one woman in two hundred, which is more people than any other accessibility
# case this system has to answer for.

CVD = {
    "protanopia": ((0.152286, 1.052583, -0.204868),
                   (0.114503, 0.786281, 0.099216),
                   (-0.003882, -0.048116, 1.051998)),
    "deuteranopia": ((0.367322, 0.860646, -0.227968),
                     (0.280085, 0.672501, 0.047413),
                     (-0.011820, 0.042940, 0.968881)),
    "tritanopia": ((1.255528, -0.076749, -0.178779),
                   (-0.078411, 0.930809, 0.147602),
                   (0.004733, 0.691367, 0.303900)),
}

VIEWS = ("normal",) + tuple(CVD)


def simulate(value: str, kind: str) -> str:
    """The same colour as it reaches a reader with this dichromacy."""
    if kind == "normal":
        return value.upper()
    linear = tuple(_to_linear(c) for c in hex2rgb(value))
    return rgb2hex(tuple(_from_linear(max(0.0, min(1.0, c)))
                         for c in _mul(CVD[kind], linear)))


def separations(values: list, views: tuple = VIEWS) -> dict:
    """The closest pair in a set, per kind of vision.

    A palette is only as distinguishable as its closest pair, so this returns the
    minimum rather than an average. An average hides the one collision that matters.
    """
    out = {}
    for view in views:
        labs = [hex2lab(simulate(v, view)) for v in values]
        out[view] = min(de2000(labs[i], labs[j])
                        for i in range(len(labs)) for j in range(i + 1, len(labs)))
    return out


def closest_pair(values: list, view: str = "normal") -> tuple:
    """The two colours a reader is most likely to confuse, and their distance."""
    labs = {v: hex2lab(simulate(v, view)) for v in values}
    best = None
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            d = de2000(labs[values[i]], labs[values[j]])
            if best is None or d < best[2]:
                best = (values[i], values[j], d)
    return best
