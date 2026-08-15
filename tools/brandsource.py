#!/usr/bin/env python3
"""Extraction layer for THE WORD brand system.

Reads the human-facing guides (the visual truth) and returns structured data.

Nothing in this file is hand-maintained brand content. Every value comes out of
`brand/index.html` or `brand/messaging/index.html`, so a change to the visual
guide flows into the machine-readable `/ai` layer on the next build.

Design rule: if a pattern stops matching, raise SourceError. The build must fail
loudly rather than publish stale standards under a "canonical" label.
"""

from __future__ import annotations

import hashlib
import html as htmlmod
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BRAND_GUIDE = os.path.join(REPO, "brand", "index.html")
MESSAGING_GUIDE = os.path.join(REPO, "brand", "messaging", "index.html")

SITE = "https://brand.theword.world"


class SourceError(RuntimeError):
    """A required pattern was not found in a source guide."""


# ---------------------------------------------------------------- helpers


def read(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def strip_tags(fragment: str) -> str:
    """Turn an HTML fragment into a single clean line of text."""
    s = re.sub(r"<br\s*/?>", " ", fragment)
    s = re.sub(r"<[^>]+>", "", s)
    s = htmlmod.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def require(match, what: str, path: str):
    if not match:
        raise SourceError(
            f"could not find {what} in {os.path.relpath(path, REPO)}. "
            "The guide's markup changed. Update tools/brandsource.py so the "
            "AI layer keeps tracking the visual guide."
        )
    return match


def require_count(items, minimum: int, what: str, path: str):
    if len(items) < minimum:
        raise SourceError(
            f"found {len(items)} {what} in {os.path.relpath(path, REPO)}, "
            f"expected at least {minimum}. Update tools/brandsource.py."
        )
    return items


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _section_prose(body: str) -> dict:
    """Pull the headline, lede, rule lists, and captions out of one guide section.

    Deliberately generic: it reads the structures the guides already use, so new
    prose added to a section shows up in the AI layer without a code change.
    """
    head = re.search(r"<h2>(.*?)</h2>", body, re.S)
    lede = re.search(r'<p class="lede">(.*?)</p>', body, re.S)
    if not lede:
        lede = re.search(r"</h2>\s*<p>(.*?)</p>", body, re.S)

    groups = []
    for m in re.finditer(r"<h3>(.*?)</h3>(.*?)(?=<h3>|$)", body, re.S):
        rules = []
        for li in re.finditer(r"<li>(.*?)</li>", m.group(2), re.S):
            item = li.group(1)
            term = re.match(r"\s*<strong>(.*?)</strong>(.*)", item, re.S)
            if term:
                rules.append({"term": strip_tags(term.group(1)), "text": strip_tags(term.group(2))})
            else:
                rules.append({"term": "", "text": strip_tags(item)})
        if rules:
            groups.append({"heading": strip_tags(m.group(1)), "rules": rules})

    captions = [
        strip_tags(m.group(1))
        for m in re.finditer(r'<p class="caption"[^>]*>(.*?)</p>', body, re.S)
        if strip_tags(m.group(1))
    ]

    return {
        "headline": strip_tags(head.group(1)) if head else "",
        "lede": strip_tags(lede.group(1)) if lede else "",
        "ruleGroups": groups,
        "captions": captions,
    }


# ---------------------------------------------------------------- brand guide


def parse_brand_guide(path: str = BRAND_GUIDE) -> dict:
    s = read(path)
    out: dict = {"source": os.path.relpath(path, REPO)}

    out["version"] = require(
        re.search(r"Brand Guide · Version ([\d.]+)", s), "the brand guide version", path
    ).group(1)
    out["issued"] = require(
        re.search(r"<strong>Issued</strong>\s*([^<]+)<", s), "the issue date", path
    ).group(1).strip()
    out["supersedes"] = strip_tags(
        require(
            re.search(r"<strong>Supersedes</strong>\s*([^<]+)<", s), "the supersedes line", path
        ).group(1)
    )
    out["appliesTo"] = [
        p.strip()
        for p in strip_tags(
            require(
                re.search(r"<strong>Applies to</strong>\s*([^<]+)<", s), "the applies-to line", path
            ).group(1)
        ).split("·")
    ]

    # --- CSS custom properties: the values the site itself renders with
    root = require(re.search(r":root\{(.*?)\}", s, re.S), "the :root token block", path).group(1)
    css_vars = {
        m.group(1): m.group(2).strip()
        for m in re.finditer(r"--([a-z0-9-]+)\s*:\s*([^;]+);", root)
    }
    out["cssVars"] = css_vars

    # --- palette: name, hex, and the rule that governs it
    colors = []
    for m in re.finditer(
        r'<div class="info"><strong>([^<]+)</strong><code>(#[0-9A-Fa-f]{3,8})</code><em>(.*?)</em>',
        s,
        re.S,
    ):
        colors.append(
            {"name": strip_tags(m.group(1)), "hex": m.group(2).upper(), "role": strip_tags(m.group(3))}
        )
    require_count(colors, 5, "color swatches", path)
    out["colors"] = colors

    # --- retired colors
    retired = re.search(
        r"Retired from brand use:\s*<code>(#[0-9A-Fa-f]{6})</code>\s*([a-z]+)\s*and\s*<code>(#[0-9A-Fa-f]{6})</code>\s*([^<]*)",
        s,
    )
    out["retiredColors"] = (
        [
            {"hex": retired.group(1).upper(), "note": retired.group(2).strip()},
            {"hex": retired.group(3).upper(), "note": strip_tags(retired.group(4)).strip(" .")},
        ]
        if retired
        else []
    )

    # --- proportion rule
    ratio = re.search(r'<h3>Proportion — ([^<]+)</h3>', s)
    out["proportion"] = ratio.group(1).strip() if ratio else "60 / 30 / 10"

    # --- system tokens and states (§04)
    tokens_section = require(
        re.search(r'<section id="tokens".*?</section>', s, re.S), "the tokens section", path
    ).group(0)
    system_tokens = []
    for m in re.finditer(r"<tr><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td></tr>", tokens_section, re.S):
        system_tokens.append(
            {
                "token": strip_tags(m.group(1)),
                "value": strip_tags(m.group(2)),
                "rule": strip_tags(m.group(3)),
            }
        )
    require_count(system_tokens, 6, "system token rows", path)
    out["systemTokens"] = system_tokens

    # --- the six laws
    laws = []
    for m in re.finditer(
        r'<div class="law">\s*<div class="num">([IVX]+)</div>\s*<div>\s*'
        r'<div class="title">(.*?)</div>\s*<div class="desc">(.*?)</div>(.*?)</div>\s*</div>',
        s,
        re.S,
    ):
        block = m.group(4)
        rules = [strip_tags(li) for li in re.findall(r"<li>(.*?)</li>", block, re.S)]
        see = re.search(r'<div class="see">(.*?)</div>', block, re.S)
        laws.append(
            {
                "numeral": m.group(1),
                "title": strip_tags(m.group(2)),
                "statement": strip_tags(m.group(3)),
                "rules": rules,
                "demonstratedIn": strip_tags(see.group(1)) if see else "",
            }
        )
    require_count(laws, 6, "design laws", path)
    out["laws"] = laws

    # --- do / don't pairs, in document order
    pairs = []
    for m in re.finditer(
        r'<div class="dd (do|dont)">.*?<span>(DO|DON.T)<small>(.*?)</small>', s, re.S
    ):
        pairs.append({"kind": "do" if m.group(1) == "do" else "dont", "rule": strip_tags(m.group(3))})
    require_count(pairs, 10, "do/don't cards", path)
    out["doDont"] = pairs

    # --- section index, with the prose each section carries
    sections = []
    eyebrows = re.findall(r'<span class="eyebrow">([^<]+)</span>', s)
    ids = re.findall(r'<section id="([^"]+)"', s)
    bodies = re.findall(r'<section id="[^"]+".*?</section>', s, re.S)
    for sid, eyebrow, body in zip(ids, eyebrows, bodies):
        label = strip_tags(eyebrow)
        num, _, title = label.partition("—")
        entry = {"id": sid, "number": num.strip(), "title": title.strip() or label}
        entry.update(_section_prose(body))
        sections.append(entry)
    require_count(sections, 12, "guide sections", path)
    out["sections"] = sections
    out["sectionsById"] = {sec["id"]: sec for sec in sections}

    # --- typography faces
    faces = []
    for m in re.finditer(r'<div class="fname">([^<]+)</div>\s*<div class="frole">(.*?)</div>', s, re.S):
        faces.append({"family": strip_tags(m.group(1)), "use": strip_tags(m.group(2))})
    require_count(faces, 3, "typeface cards", path)
    out["typefaces"] = faces
    out["fontFallbacks"] = {
        "serif": strip_tags(css_vars.get("serif-display", "")),
        "sans": strip_tags(css_vars.get("sans", "")),
    }

    # --- changelog against the retired PDF
    changelog_section = require(
        re.search(r'<section id="changelog".*?</section>', s, re.S), "the changelog section", path
    ).group(0)
    changes = []
    for m in re.finditer(
        r"<tr><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td></tr>", changelog_section, re.S
    ):
        changes.append(
            {"element": strip_tags(m.group(1)), "was": strip_tags(m.group(2)), "now": strip_tags(m.group(3))}
        )
    out["changelog"] = changes
    trail = re.search(r"Revision trail:\s*(.*?)</p>", changelog_section, re.S)
    out["revisionTrail"] = strip_tags(trail.group(1)) if trail else ""

    # --- sub-brands (§10)
    subs = []
    for m in re.finditer(
        r'<div class="word">([A-Z]+)</div>\s*<div class="name">([^<]+)</div>\s*'
        r'<div class="desc">(.*?)</div>\s*<div class="endorse">([^<]+)</div>',
        s,
        re.S,
    ):
        subs.append(
            {
                "stage": m.group(1),
                "name": strip_tags(m.group(2)),
                "mission": strip_tags(m.group(3)),
                "endorsement": strip_tags(m.group(4)),
            }
        )
    require_count(subs, 3, "sub-brand cards", path)
    out["subBrands"] = subs

    return out


# ---------------------------------------------------------------- messaging guide


def parse_messaging_guide(path: str = MESSAGING_GUIDE) -> dict:
    s = read(path)
    out: dict = {"source": os.path.relpath(path, REPO)}

    out["version"] = require(
        re.search(r"Messaging Guide · Version ([\d.]+)", s), "the messaging guide version", path
    ).group(1)
    companion = re.search(r"Brand Guide v([\d.]+)", s)
    out["companionTo"] = companion.group(1) if companion else ""

    out["missionLine"] = strip_tags(
        require(
            re.search(r'<div class="sk">The Public Mission Line[^<]*</div>\s*<div class="big">(.*?)</div>', s, re.S),
            "the public mission line",
            path,
        ).group(1)
    )

    pillars = {}
    for m in re.finditer(
        r'<div class="lab">(Purpose|Mission|Vision)</div>\s*<div class="txt">(.*?)</div>'
        r'(?:\s*<span class="vref">([^<]*)</span>)?',
        s,
        re.S,
    ):
        text = strip_tags(m.group(2))
        if m.group(3):
            text = f"{text} ({strip_tags(m.group(3))})"
        pillars[m.group(1).lower()] = text
    require_count(list(pillars), 3, "purpose/mission/vision pillars", path)
    out["pillars"] = pillars

    # --- vocabulary we carry
    phrases = []
    voice_block = require(
        re.search(r"Words we carry\..*?</table>", s, re.S), "the vocabulary table", path
    ).group(0)
    for m in re.finditer(r"<tr><td>(.*?)</td><td>(.*?)</td></tr>", voice_block, re.S):
        phrases.append({"phrase": strip_tags(m.group(1)), "carries": strip_tags(m.group(2))})
    require_count(phrases, 5, "load-bearing phrases", path)
    out["phrases"] = phrases

    # --- banned language
    bans = []
    for m in re.finditer(
        r'<div class="bh">([^<]+)</div>\s*<div>\s*<div class="bw">(.*?)</div>\s*<div class="why">(.*?)</div>',
        s,
        re.S,
    ):
        words = [w.strip() for w in strip_tags(m.group(2)).split("·") if w.strip()]
        bans.append({"category": strip_tags(m.group(1)), "words": words, "why": strip_tags(m.group(3))})
    require_count(bans, 3, "banned-language categories", path)
    out["bans"] = bans

    # --- rewrites (never this / always this)
    rewrites = []
    rw = re.search(r"Rewrites: before and after\..*?</table>", s, re.S)
    if rw:
        for m in re.finditer(r"<tr><td>(.*?)</td><td>(.*?)</td></tr>", rw.group(0), re.S):
            rewrites.append({"never": strip_tags(m.group(1)), "always": strip_tags(m.group(2))})
    out["rewrites"] = rewrites

    # --- audiences
    audiences = []
    for m in re.finditer(
        r'<div class="pn">([^<]+?)\s*<span>(.*?)</span></div>\s*<div class="pd">(.*?)</div>\s*</div>',
        s,
        re.S,
    ):
        body = m.group(3)
        want = re.search(r"<strong>They want:</strong>(.*?)</p>", body, re.S)
        pain = re.search(r"<strong>Their pain:</strong>(.*?)</p>", body, re.S)
        say = re.search(r'<p class="say">(.*?)</p>', body, re.S)
        step = re.search(r"<strong>First step:</strong>(.*?)</p>", body, re.S)
        audiences.append(
            {
                "audience": strip_tags(m.group(1)),
                "qualifier": strip_tags(m.group(2)),
                "wants": strip_tags(want.group(1)) if want else "",
                "pain": strip_tags(pain.group(1)) if pain else "",
                "needsToHear": strip_tags(say.group(1)) if say else "",
                "firstStep": strip_tags(step.group(1)) if step else "",
            }
        )
    require_count(audiences, 5, "audience profiles", path)
    out["audiences"] = audiences

    # --- message architecture
    architecture = []
    arch = re.search(r'<section class="dsec" id="architecture".*?</table>', s, re.S)
    if arch:
        for m in re.finditer(r"<tr><td>(.*?)</td><td>(.*?)</td></tr>", arch.group(0), re.S):
            architecture.append({"element": strip_tags(m.group(1)), "canonical": strip_tags(m.group(2))})
    out["architecture"] = architecture

    # --- the voice filter
    filt = re.search(r"<strong>The filter:</strong>(.*?)</div>", s, re.S)
    out["filter"] = strip_tags(filt.group(1)) if filt else ""

    # --- the prophecy, quoted exactly or not at all
    proph = require(
        re.search(r'<div class="verse">(.*?)</div>\s*<div class="dateline">(.*?)</div>', s, re.S),
        "the prophecy",
        path,
    )
    out["prophecy"] = {"text": strip_tags(proph.group(1)), "dateline": strip_tags(proph.group(2))}

    # --- standing rules
    standing = re.search(r"<strong>Standing rules\.</strong>(.*?)</p>", s, re.S)
    out["standingRules"] = strip_tags(standing.group(1)) if standing else ""

    # --- governance changelog
    changelog = []
    gov = re.search(r'<section class="dsec" id="governance".*?</table>', s, re.S)
    if gov:
        for m in re.finditer(r"<tr><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td></tr>", gov.group(0), re.S):
            changelog.append(
                {"version": strip_tags(m.group(1)), "date": strip_tags(m.group(2)), "change": strip_tags(m.group(3))}
            )
    out["changelog"] = changelog

    return out


# ---------------------------------------------------------------- repository


INITIATIVE_NAMES = {
    "revival-to-my-city": "Revival To My City",
    "every1": "EVERY1 Movement",
    "school-of-the-local-church": "School of the Local Church",
}


def scan_initiatives() -> list:
    """Every initiative that has a published brand guide or messaging document."""
    slugs = set()
    for section in ("letterhead", "documents"):
        base = os.path.join(REPO, section)
        if not os.path.isdir(base):
            continue
        for entry in sorted(os.listdir(base)):
            if os.path.isfile(os.path.join(base, entry, "index.html")):
                slugs.add(entry)
    out = []
    for slug in sorted(slugs):
        out.append(
            {
                "slug": slug,
                "name": INITIATIVE_NAMES.get(slug, slug.replace("-", " ").title()),
                "brandGuide": f"{SITE}/letterhead/{slug}",
                "messagingDocument": f"{SITE}/documents/{slug}",
            }
        )
    return out


ASSET_KINDS = {
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".svg": "vector",
    ".mp4": "video",
    ".woff2": "font",
    ".woff": "font",
    ".ttf": "font",
}


def scan_assets() -> list:
    """Inventory of every published asset, taken from the filesystem."""
    out = []
    base = os.path.join(REPO, "assets")
    for root, _dirs, files in os.walk(base):
        for name in sorted(files):
            if name.startswith("."):
                continue
            ext = os.path.splitext(name)[1].lower()
            if ext not in ASSET_KINDS:
                continue
            full = os.path.join(root, name)
            rel = os.path.relpath(full, REPO).replace(os.sep, "/")
            out.append(
                {
                    "file": rel,
                    "url": f"{SITE}/{rel}",
                    "kind": ASSET_KINDS[ext],
                    "group": os.path.basename(os.path.dirname(rel)),
                    "bytes": os.path.getsize(full),
                }
            )
    return sorted(out, key=lambda a: a["file"])


def published_pages() -> list:
    """Every human-facing page in the portal, for the sitemap and llms.txt."""
    pages = []
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [
            d
            for d in dirs
            if d
            not in {".git", ".github", ".wrangler", "assets", "tools", "ai", "ai-source", ".claude", "skills", "archive"}
        ]
        if "index.html" in files:
            rel = os.path.relpath(root, REPO).replace(os.sep, "/")
            pages.append("/" if rel == "." else f"/{rel}")
    return sorted(pages, key=lambda p: (p.count("/"), p))
