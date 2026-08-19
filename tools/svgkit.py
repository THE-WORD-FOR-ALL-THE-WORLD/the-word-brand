#!/usr/bin/env python3
"""
svgkit: the minimum SVG needed to treat a logo master as data.

Parse the paths, apply the transforms, measure the artwork, and rasterize it.
No external binaries, no network, no design tool. tools/build_logos.py uses this
to derive every published logo file from the approved vector masters, so the PNG
a partner downloads and the SVG the site serves are provably the same artwork.

Pillow is needed only to rasterize. Parsing and measuring work without it, which
is what the linter uses, so CI never needs an imaging library installed.
"""

import math
import re

# Curve flattening tolerance, in user units. The masters are ~1000 units wide,
# so this puts the error far below a printer's dot at any size we publish.
FLATTEN_TOLERANCE = 0.05
MAX_SUBDIV = 16


# ── transforms ────────────────────────────────────────────────────────────────
# A 2D affine as (a, b, c, d, e, f), matching SVG's matrix(a b c d e f):
#     x' = a·x + c·y + e
#     y' = b·x + d·y + f

IDENTITY = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


def mat_mul(m, n):
    a1, b1, c1, d1, e1, f1 = m
    a2, b2, c2, d2, e2, f2 = n
    return (
        a1 * a2 + c1 * b2,
        b1 * a2 + d1 * b2,
        a1 * c2 + c1 * d2,
        b1 * c2 + d1 * d2,
        a1 * e2 + c1 * f2 + e1,
        b1 * e2 + d1 * f2 + f1,
    )


def mat_apply(m, x, y):
    a, b, c, d, e, f = m
    return (a * x + c * y + e, b * x + d * y + f)


_TRANSFORM_RE = re.compile(r"(matrix|translate|scale|rotate|skewX|skewY)\s*\(([^)]*)\)")


def parse_transform(text):
    """SVG transform attribute to a single matrix. Left-to-right, as SVG applies it."""
    m = IDENTITY
    if not text:
        return m
    for name, raw in _TRANSFORM_RE.findall(text):
        v = [float(n) for n in re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", raw)]
        if name == "matrix" and len(v) == 6:
            t = tuple(v)
        elif name == "translate":
            t = (1, 0, 0, 1, v[0], v[1] if len(v) > 1 else 0)
        elif name == "scale":
            sx = v[0]
            sy = v[1] if len(v) > 1 else sx
            t = (sx, 0, 0, sy, 0, 0)
        elif name == "rotate":
            r = math.radians(v[0])
            cos, sin = math.cos(r), math.sin(r)
            t = (cos, sin, -sin, cos, 0, 0)
            if len(v) == 3:
                t = mat_mul((1, 0, 0, 1, v[1], v[2]), mat_mul(t, (1, 0, 0, 1, -v[1], -v[2])))
        elif name == "skewX":
            t = (1, 0, math.tan(math.radians(v[0])), 1, 0, 0)
        elif name == "skewY":
            t = (1, math.tan(math.radians(v[0])), 0, 1, 0, 0)
        else:
            continue
        m = mat_mul(m, t)
    return m


# ── path data ─────────────────────────────────────────────────────────────────

_TOKEN_RE = re.compile(r"([MmZzLlHhVvCcSsQqTtAa])|([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)")


def _tokens(d):
    for cmd, num in _TOKEN_RE.findall(d):
        yield cmd if cmd else float(num)


def _flatten_cubic(pts, p0, p1, p2, p3, depth=0):
    """Recursive subdivision, stopping once the curve is flat enough to be a line."""
    if depth >= MAX_SUBDIV:
        pts.append(p3)
        return
    # Distance of the control points from the chord approximates the error.
    dx, dy = p3[0] - p0[0], p3[1] - p0[1]
    d1 = abs((p1[0] - p3[0]) * dy - (p1[1] - p3[1]) * dx)
    d2 = abs((p2[0] - p3[0]) * dy - (p2[1] - p3[1]) * dx)
    if (d1 + d2) ** 2 <= FLATTEN_TOLERANCE * (dx * dx + dy * dy):
        pts.append(p3)
        return
    mid = lambda a, b: ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)  # noqa: E731
    p01, p12, p23 = mid(p0, p1), mid(p1, p2), mid(p2, p3)
    p012, p123 = mid(p01, p12), mid(p12, p23)
    p0123 = mid(p012, p123)
    _flatten_cubic(pts, p0, p01, p012, p0123, depth + 1)
    _flatten_cubic(pts, p0123, p123, p23, p3, depth + 1)


def _arc(pts, p0, rx, ry, rot, large, sweep, p1):
    """Endpoint-parameterised elliptical arc, per the SVG implementation notes."""
    if rx == 0 or ry == 0 or p0 == p1:
        pts.append(p1)
        return
    rx, ry = abs(rx), abs(ry)
    phi = math.radians(rot)
    cos, sin = math.cos(phi), math.sin(phi)
    dx2, dy2 = (p0[0] - p1[0]) / 2, (p0[1] - p1[1]) / 2
    x1, y1 = cos * dx2 + sin * dy2, -sin * dx2 + cos * dy2
    # Scale the radii up if they are too small to span the two endpoints.
    lam = x1 * x1 / (rx * rx) + y1 * y1 / (ry * ry)
    if lam > 1:
        s = math.sqrt(lam)
        rx, ry = rx * s, ry * s
    num = rx * rx * ry * ry - rx * rx * y1 * y1 - ry * ry * x1 * x1
    den = rx * rx * y1 * y1 + ry * ry * x1 * x1
    co = math.sqrt(max(0.0, num / den)) if den else 0.0
    if large == sweep:
        co = -co
    cx1, cy1 = co * rx * y1 / ry, -co * ry * x1 / rx
    cx = cos * cx1 - sin * cy1 + (p0[0] + p1[0]) / 2
    cy = sin * cx1 + cos * cy1 + (p0[1] + p1[1]) / 2

    def angle(ux, uy, vx, vy):
        dot = ux * vx + uy * vy
        n = math.hypot(ux, uy) * math.hypot(vx, vy)
        a = math.acos(max(-1.0, min(1.0, dot / n))) if n else 0.0
        return -a if ux * vy - uy * vx < 0 else a

    th0 = angle(1, 0, (x1 - cx1) / rx, (y1 - cy1) / ry)
    dth = angle((x1 - cx1) / rx, (y1 - cy1) / ry, (-x1 - cx1) / rx, (-y1 - cy1) / ry)
    if not sweep and dth > 0:
        dth -= 2 * math.pi
    elif sweep and dth < 0:
        dth += 2 * math.pi
    steps = max(2, int(abs(dth) / (math.pi / 32)) + 1)
    for i in range(1, steps + 1):
        th = th0 + dth * i / steps
        x, y = rx * math.cos(th), ry * math.sin(th)
        pts.append((cos * x - sin * y + cx, sin * x + cos * y + cy))


def parse_path(d):
    """Path data to a list of closed subpaths, each a list of (x, y) points."""
    subpaths, pts = [], []
    cur = start = (0.0, 0.0)
    prev_cubic = prev_quad = None
    cmd = None
    stack = list(_tokens(d))
    i, n = 0, len(stack)

    def flush():
        nonlocal pts
        if len(pts) >= 3:
            subpaths.append(pts)
        pts = []

    def take(k):
        nonlocal i
        vals = stack[i : i + k]
        i += k
        return vals

    while i < n:
        tok = stack[i]
        if isinstance(tok, str):
            cmd = tok
            i += 1
            if cmd in "Zz":
                flush()
                cur = start
                prev_cubic = prev_quad = None
                continue
            if i >= n:
                break
        elif cmd is None:
            break
        elif cmd in "Mm":
            # A repeated coordinate pair after M is an implicit lineto.
            cmd = "L" if cmd == "M" else "l"

        rel = cmd.islower()
        c = cmd.upper()
        ox, oy = cur if rel else (0.0, 0.0)

        if c == "M":
            x, y = take(2)
            flush()
            cur = start = (x + ox, y + oy)
            pts = [cur]
            prev_cubic = prev_quad = None
        elif c == "L":
            x, y = take(2)
            cur = (x + ox, y + oy)
            pts.append(cur)
            prev_cubic = prev_quad = None
        elif c == "H":
            (x,) = take(1)
            cur = (x + ox, cur[1])
            pts.append(cur)
            prev_cubic = prev_quad = None
        elif c == "V":
            (y,) = take(1)
            cur = (cur[0], y + oy)
            pts.append(cur)
            prev_cubic = prev_quad = None
        elif c in ("C", "S"):
            if c == "C":
                x1, y1, x2, y2, x, y = take(6)
                p1 = (x1 + ox, y1 + oy)
            else:
                x2, y2, x, y = take(4)
                p1 = (2 * cur[0] - prev_cubic[0], 2 * cur[1] - prev_cubic[1]) if prev_cubic else cur
            p2 = (x2 + ox, y2 + oy)
            p3 = (x + ox, y + oy)
            if not pts:
                pts = [cur]
            _flatten_cubic(pts, cur, p1, p2, p3)
            cur, prev_cubic, prev_quad = p3, p2, None
        elif c in ("Q", "T"):
            if c == "Q":
                x1, y1, x, y = take(4)
                q = (x1 + ox, y1 + oy)
            else:
                x, y = take(2)
                q = (2 * cur[0] - prev_quad[0], 2 * cur[1] - prev_quad[1]) if prev_quad else cur
            p3 = (x + ox, y + oy)
            # Exact degree elevation, quadratic to cubic.
            p1 = (cur[0] + 2 / 3 * (q[0] - cur[0]), cur[1] + 2 / 3 * (q[1] - cur[1]))
            p2 = (p3[0] + 2 / 3 * (q[0] - p3[0]), p3[1] + 2 / 3 * (q[1] - p3[1]))
            if not pts:
                pts = [cur]
            _flatten_cubic(pts, cur, p1, p2, p3)
            cur, prev_quad, prev_cubic = p3, q, None
        elif c == "A":
            rx, ry, rot, large, sweep, x, y = take(7)
            p1 = (x + ox, y + oy)
            if not pts:
                pts = [cur]
            _arc(pts, cur, rx, ry, rot, int(large), int(sweep), p1)
            cur = p1
            prev_cubic = prev_quad = None
        else:
            break

    flush()
    return subpaths


# ── documents ─────────────────────────────────────────────────────────────────

_VIEWBOX_RE = re.compile(r'viewBox\s*=\s*"([^"]+)"')
_TAG_RE = re.compile(r"<(g|path|svg)\b([^>]*?)(/?)>|</(g)>", re.S)
_ATTR_RE = re.compile(r'([\w:-]+)\s*=\s*"([^"]*)"')


class Shape:
    """One filled path, already in the document's own user space."""

    __slots__ = ("subpaths", "fill", "rule")

    def __init__(self, subpaths, fill, rule):
        self.subpaths = subpaths
        self.fill = fill
        self.rule = rule


def load(path):
    """Read an SVG into (shapes, viewBox). Handles nested <g>, transforms, currentColor."""
    src = open(path, encoding="utf-8").read()
    vb = _VIEWBOX_RE.search(src)
    viewbox = [float(v) for v in re.split(r"[\s,]+", vb.group(1).strip())] if vb else None

    shapes = []
    # Inherited state per nesting level: transform, fill, and the value currentColor resolves to.
    stack = [(IDENTITY, "#000000", "#000000")]

    for m in _TAG_RE.finditer(src):
        if m.group(4):  # </g>
            if len(stack) > 1:
                stack.pop()
            continue
        tag, attrs_raw, selfclose = m.group(1), m.group(2) or "", m.group(3)
        attrs = dict(_ATTR_RE.findall(attrs_raw))
        pmat, pfill, pcolor = stack[-1]

        mat = mat_mul(pmat, parse_transform(attrs.get("transform", "")))
        color = attrs.get("color", pcolor)
        fill = attrs.get("fill", pfill)
        if fill == "currentColor":
            fill = color

        if tag == "svg":
            # The root can carry color/fill that everything below inherits.
            stack[0] = (mat, fill, color)
            continue
        if tag == "g":
            if not selfclose:
                stack.append((mat, fill, color))
            continue

        if fill.lower() in ("none", "transparent"):
            continue
        d = attrs.get("d")
        if not d:
            continue
        subs = [[mat_apply(mat, x, y) for (x, y) in sp] for sp in parse_path(d)]
        subs = [s for s in subs if len(s) >= 3]
        if subs:
            shapes.append(Shape(subs, fill, attrs.get("fill-rule", "nonzero")))

    return shapes, viewbox


def bbox(shapes):
    """Tight bounding box of the artwork itself, ignoring the canvas."""
    xs, ys = [], []
    for sh in shapes:
        for sp in sh.subpaths:
            for x, y in sp:
                xs.append(x)
                ys.append(y)
    if not xs:
        return None
    return (min(xs), min(ys), max(xs), max(ys))


# ── rasterizing ───────────────────────────────────────────────────────────────


def _hex_rgb(c):
    c = c.strip()
    if c.startswith("#"):
        c = c[1:]
        if len(c) == 3:
            c = "".join(ch * 2 for ch in c)
        return tuple(int(c[i : i + 2], 16) for i in (0, 2, 4))
    named = {"white": (255, 255, 255), "black": (0, 0, 0), "none": None}
    return named.get(c.lower(), (0, 0, 0))


def _coverage(shape, w, h, xform, ss):
    """
    Scanline fill of one shape into a coverage bytearray, honouring its fill rule.

    Supersampled ss× vertically and horizontally, then box-filtered by the caller,
    which is what gives the edges their antialiasing.
    """
    W, H = w * ss, h * ss
    cov = bytearray(W * H)
    edges = []
    for sp in shape.subpaths:
        pts = [xform(x, y) for x, y in sp]
        pts = [(x * ss, y * ss) for x, y in pts]
        for i in range(len(pts)):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % len(pts)]
            if y0 == y1:
                continue
            edges.append((min(y0, y1), max(y0, y1), x0, y0, x1, y1, 1 if y1 > y0 else -1))
    if not edges:
        return cov, W, H

    edges.sort(key=lambda e: e[0])
    ymin = max(0, int(math.floor(min(e[0] for e in edges))))
    ymax = min(H - 1, int(math.ceil(max(e[1] for e in edges))))
    evenodd = shape.rule == "evenodd"
    active, nxt = [], 0

    for py in range(ymin, ymax + 1):
        yc = py + 0.5
        while nxt < len(edges) and edges[nxt][0] <= yc:
            active.append(edges[nxt])
            nxt += 1
        if active:
            active = [e for e in active if e[1] > yc]
        xs = []
        for lo, hi, x0, y0, x1, y1, wind in active:
            if lo <= yc < hi:
                xs.append((x0 + (yc - y0) * (x1 - x0) / (y1 - y0), wind))
        if not xs:
            continue
        xs.sort()
        row = py * W
        if evenodd:
            for i in range(0, len(xs) - 1, 2):
                _span(cov, row, xs[i][0], xs[i + 1][0], W)
        else:
            depth = 0
            for i in range(len(xs) - 1):
                depth += xs[i][1]
                if depth != 0:
                    _span(cov, row, xs[i][0], xs[i + 1][0], W)
    return cov, W, H


def _span(cov, row, xa, xb, W):
    """Fill one horizontal run. Slice assignment keeps this out of the Python loop."""
    a = max(0, int(math.ceil(xa - 0.5)))
    b = min(W - 1, int(math.floor(xb - 0.5)))
    if b >= a:
        cov[row + a : row + b + 1] = b"\xff" * (b - a + 1)


def rasterize(shapes, width, height, xform, supersample=4):
    """
    Render shapes to an RGBA Pillow image. xform maps user space to pixel space.

    Each shape is scanline-filled at supersample× into a coverage mask, then Pillow
    downsamples it with a box filter and composites it. Everything per-pixel happens
    in C, so a 3200px master renders in well under a second.
    """
    from PIL import Image

    ss = supersample
    out = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    for sh in shapes:
        rgb = _hex_rgb(sh.fill)
        if rgb is None:
            continue
        cov, W, H = _coverage(sh, width, height, xform, ss)
        mask = Image.frombytes("L", (W, H), bytes(cov)).resize((width, height), Image.BOX)
        out.paste(Image.new("RGBA", (width, height), rgb + (255,)), (0, 0), mask)
    return out
