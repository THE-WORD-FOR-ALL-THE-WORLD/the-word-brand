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
    # Optional. The guide stopped defining itself against the retired PDF at v5.0;
    # older archived versions still carry the line, so the field survives when present.
    sup = re.search(r"<strong>Supersedes</strong>\s*([^<]+)<", s)
    out["supersedes"] = strip_tags(sup.group(1)).strip() if sup else ""
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
    ratio = re.search(r'<h3>Proportion\s*[—:]\s*([^<]+)</h3>', s)
    out["proportion"] = ratio.group(1).strip() if ratio else "60 / 30 / 10"

    # --- system tokens and states (§04)
    tokens_section = require(
        re.search(r'<section id="tokens".*?</section>', s, re.S), "the tokens section", path
    ).group(0)
    system_tokens = []
    # The named scales live in this section too, in their own tables. They are read
    # by parse_scales() with their headers intact, so they are removed here rather
    # than being flattened into name/value/rule triples they do not fit.
    for m in re.finditer(
        r"<tr><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td></tr>", strip_scale_tables(tokens_section), re.S
    ):
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
        # v5.0 moved the eyebrow separator from an em dash to a middot.
        # Archived guides still use the em dash, so both are accepted.
        parts = re.split(r"\s[—·]\s", label, maxsplit=1)
        num = parts[0].strip()
        title = parts[1].strip() if len(parts) > 1 else ""
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
    # v5.0 replaced the element/was/now comparison against the retired PDF with a
    # release record: version, date, owner, what changed, and who approved it.
    changes = []
    for m in re.finditer(
        r"<tr><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td></tr>",
        changelog_section,
        re.S,
    ):
        changes.append(
            {
                "version": strip_tags(m.group(1)),
                "date": strip_tags(m.group(2)),
                "owner": strip_tags(m.group(3)),
                "changed": strip_tags(m.group(4)),
                "approved": strip_tags(m.group(5)),
            }
        )
    require_count(changes, 1, "changelog rows", path)
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
    # v5.1 gave each door a ground, a Flame ceiling, and a register.
    idents = []
    for block in re.findall(r'<dl class="ident">(.*?)</dl>', s, re.S):
        idents.append(
            {
                strip_tags(k).lower(): strip_tags(v)
                for k, v in re.findall(r"<dt>(.*?)</dt>\s*<dd>(.*?)</dd>", block, re.S)
            }
        )
    for sub, ident in zip(subs, idents):
        sub["identity"] = ident
    require_count(subs, 3, "sub-brand cards", path)
    out["subBrands"] = subs

    # --- channels (§12, v5.8; parent-only from v5.9, doors carry their own cards)
    channels = []
    chan_sec = re.search(r'<section id="channels".*?</section>', s, re.S)
    if chan_sec:
        channels = _chanfacts(chan_sec.group(0))
        require_count(channels, 1, "channel facts cards", path)
    out["channels"] = channels

    return out


def _chanfacts(html: str) -> list:
    """Every channel facts card in a fragment: name, kind, and platform rows."""
    cards = []
    for m in re.finditer(
        r'<div class="chanfacts">\s*<div class="cfname">(.*?)</div>\s*'
        r'<div class="cfserv">(.*?)</div>(.*?)</table>',
        html,
        re.S,
    ):
        rows = [
            (strip_tags(platform), strip_tags(handle))
            for platform, handle in re.findall(
                r'<td class="cfp">(.*?)</td><td class="cfh[^"]*">(.*?)</td>', m.group(3), re.S
            )
        ]
        cards.append({"name": strip_tags(m.group(1)), "kind": strip_tags(m.group(2)), "rows": rows})
    return cards


def door_channels() -> list:
    """Each initiative's channel facts card, read from its published brand guide.

    From v5.9 a door's channels live in its own guide rather than in Brand
    Guide §12, so the machine layer collects them from the door pages, in the
    journey's fixed order."""
    cards = []
    for slug in INITIATIVE_NAMES:
        path = os.path.join(REPO, "brand", slug, "index.html")
        if os.path.isfile(path):
            cards.extend(_chanfacts(read(path)))
    return cards


# ---------------------------------------------------------------- messaging guide


def parse_messaging_guide(path: str = MESSAGING_GUIDE) -> dict:
    """Read the Messaging Standard.

    The guide is set as a plain document, so nothing here keys off a visual
    class. Every field a machine needs is carried on a data- attribute, which
    means the page can be redesigned without silently changing what the build
    publishes. If a hook goes missing, require() fails the build rather than
    letting the AI layer publish a guide with a hole in it.
    """
    s = read(path)
    out: dict = {"source": os.path.relpath(path, REPO)}

    out["version"] = require(
        re.search(r"Messaging Guide · Version ([\d.]+)", s), "the messaging guide version", path
    ).group(1)
    companion = re.search(r"Brand Guide v([\d.]+)", s)
    out["companionTo"] = companion.group(1) if companion else ""

    def field(name, what):
        return strip_tags(
            require(
                re.search(r'<div data-field="%s">(.*?)</div>' % name, s, re.S), what, path
            ).group(1)
        )

    out["missionLine"] = field("mission-line", "the public mission line")
    out["filter"] = field("filter", "the voice filter")
    out["standingRules"] = field("standing-rules", "the standing rules")

    # --- purpose, mission, vision
    pillars = {}
    for m in re.finditer(r'<div data-pillar="(Purpose|Mission|Vision)">(.*?)</div>', s, re.S):
        body = m.group(2)
        ref = re.search(r"<span data-vision-ref>(.*?)</span>", body, re.S)
        text = strip_tags(re.sub(r"<span data-vision-ref>.*?</span>", "", body, flags=re.S))
        if ref:
            out["vision"] = {"text": text, "reference": strip_tags(ref.group(1))}
            text = f"{text} ({strip_tags(ref.group(1))})"
        pillars[m.group(1).lower()] = text
    require_count(list(pillars), 3, "purpose/mission/vision pillars", path)
    out["pillars"] = pillars
    require(out.get("vision"), "the vision reference", path)

    # --- the authority tier each section carries
    tiers = []
    for m in re.finditer(r'<section data-sec id="([a-z0-9-]+)" data-tier="([A-Z]+)"', s):
        tiers.append({"section": m.group(1), "tier": m.group(2)})
    require_count(tiers, 10, "sections carrying an authority tier", path)
    out["tiers"] = tiers
    out["locked"] = [t["section"] for t in tiers if t["tier"] == "LOCKED"]

    # --- vocabulary we carry
    phrases = []
    voice_block = require(
        re.search(r"<table data-phrases.*?</table>", s, re.S), "the vocabulary table", path
    ).group(0)
    for m in re.finditer(r"<tr><td>(.*?)</td><td>(.*?)</td></tr>", voice_block, re.S):
        phrases.append({"phrase": strip_tags(m.group(1)), "carries": strip_tags(m.group(2))})
    require_count(phrases, 20, "load-bearing phrases", path)
    out["phrases"] = phrases

    # --- banned language
    bans = []
    for m in re.finditer(
        r'<div data-ban="([^"]+)">.*?<p data-words>(.*?)</p>\s*<p data-why[^>]*>(.*?)</p>',
        s,
        re.S,
    ):
        words = [w.strip() for w in strip_tags(m.group(2)).split("·") if w.strip()]
        bans.append({"category": strip_tags(m.group(1)), "words": words, "why": strip_tags(m.group(3))})
    require_count(bans, 4, "banned-language categories", path)
    out["bans"] = bans

    # --- rewrites (never this / always this)
    rewrites = []
    for m in re.finditer(
        r'<div class="ex" data-rewrite>.*?<p class="off">(.*?)</p>.*?<p class="on">(.*?)</p>',
        s,
        re.S,
    ):
        def clean(x):
            return strip_tags(re.sub(r'<span class="lbl">.*?</span>', "", x, flags=re.S))
        rewrites.append({"never": clean(m.group(1)), "always": clean(m.group(2))})
    require_count(rewrites, 8, "before-and-after rewrites", path)
    out["rewrites"] = rewrites

    # --- audiences, in the master-brand priority order
    audiences = []
    for m in re.finditer(r'<div data-audience="([^"]+)" data-posture="([^"]+)">', s):
        audiences.append({"audience": m.group(1), "posture": m.group(2)})
    require_count(audiences, 7, "audience profiles", path)
    out["audiences"] = audiences

    # --- message architecture
    architecture = []
    arch = re.search(r'<section data-sec id="architecture".*?</table>', s, re.S)
    if arch:
        for m in re.finditer(r"<tr><td>(.*?)</td><td>(.*?)</td></tr>", arch.group(0), re.S):
            architecture.append({"element": strip_tags(m.group(1)), "canonical": strip_tags(m.group(2))})
    out["architecture"] = architecture

    # --- the prophecy, quoted exactly or not at all
    proph = require(
        re.search(r'<blockquote data-field="prophecy">(.*?)</blockquote>', s, re.S),
        "the prophecy",
        path,
    ).group(1)
    dateline = require(
        re.search(r'data-field="prophecy-dateline">(.*?)</span>', proph, re.S),
        "the prophecy dateline",
        path,
    ).group(1)
    out["prophecy"] = {
        "text": strip_tags(re.sub(r"<span class=\"dateline\".*?</span>", "", proph, flags=re.S)),
        "dateline": strip_tags(dateline),
    }

    # --- the blocks EVERY1's own site republishes, kept as markup so the
    # generator renders the parent's words rather than a copy of them.
    every1 = {}
    for m in re.finditer(r'<div data-every1="([a-z]+)">(.*?)\n  </div>', s, re.S):
        every1[m.group(1)] = m.group(2).strip()
    require_count(list(every1), 2, "EVERY1 republish blocks", path)
    out["every1Blocks"] = every1

    # --- governance changelog
    changelog = []
    gov = re.search(r'<section data-sec id="governance".*?</table>', s, re.S)
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
        entry = {
            "slug": slug,
            "name": INITIATIVE_NAMES.get(slug, slug.replace("-", " ").title()),
            "messagingDocument": f"{SITE}/documents/{slug}",
        }
        # Only claim a per-initiative brand guide when the page actually exists.
        # /letterhead became the document template at v5.0; the per-door guides
        # live under /brand/<slug> from v5.2.
        if os.path.isfile(os.path.join(REPO, "brand", slug, "index.html")):
            entry["brandGuide"] = f"{SITE}/brand/{slug}"
        out.append(entry)
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
    for root, dirs, files in os.walk(base):
        # A leading underscore means working material, not a published asset:
        # _masters holds the approved artwork every logo is derived from, and
        # _inbox holds files on their way to becoming masters. Neither ships.
        dirs[:] = [d for d in dirs if not d.startswith("_")]
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


SCALE_TABLE = re.compile(r'<table data-scale="([a-z-]+)"\s*>(.*?)</table>', re.S)


def strip_scale_tables(section: str) -> str:
    return SCALE_TABLE.sub("", section)


def parse_scales(path: str) -> dict:
    """Every <table data-scale="name"> in a guide, as a list of row dicts.

    One reader for all of them. A new scale is a new table in the guide and needs
    no change here, which is the point: the guide stays the place a value is
    stated, and the build stays the place it is carried.
    """
    s = read(path)
    out: dict = {}
    for m in SCALE_TABLE.finditer(s):
        name, body = m.group(1), m.group(2)
        rows = re.findall(r"<tr>(.*?)</tr>", body, re.S)
        if not rows:
            raise SourceError(f"{path}: the '{name}' scale table has no rows.")
        headers = [strip_tags(c).strip().lower() for c in re.findall(r"<th>(.*?)</th>", rows[0], re.S)]
        if not headers:
            raise SourceError(f"{path}: the '{name}' scale table has no header row.")
        entries = []
        for row in rows[1:]:
            cells = [strip_tags(c).strip() for c in re.findall(r"<td>(.*?)</td>", row, re.S)]
            if len(cells) != len(headers):
                raise SourceError(
                    f"{path}: a row in the '{name}' scale has {len(cells)} cells "
                    f"but the header has {len(headers)}."
                )
            entries.append(dict(zip(headers, cells)))
        if not entries:
            raise SourceError(f"{path}: the '{name}' scale table has a header but no values.")
        out[name] = entries
    return out


def scan_reviews() -> list:
    """Every system review on the record, newest first.

    A review is any directory under reviews/ with an index.html. Its title and
    summary come from the page itself, so publishing a new review needs no edit
    here: drop the directory in and it registers itself in llms.txt and the
    sitemap on the next build.
    """
    root = os.path.join(REPO, "reviews")
    if not os.path.isdir(root):
        return []
    out = []
    for name in sorted(os.listdir(root), reverse=True):
        index = os.path.join(root, name, "index.html")
        if not os.path.isfile(index):
            continue
        page = read(index)
        title = require(
            re.search(r"<title>(.*?)(?:\s*·[^·<]*)?</title>", page, re.S),
            "the review title",
            index,
        ).group(1).strip()
        desc = re.search(r'<meta name="description" content="([^"]*)"', page)
        out.append(
            {
                "slug": name,
                "name": strip_tags(title),
                "url": f"{SITE}/reviews/{name}",
                "summary": strip_tags(desc.group(1)).strip() if desc else "",
            }
        )
    return out


def published_pages() -> list:
    """Every human-facing page in the portal, for the sitemap and llms.txt."""
    pages = []
    for root, dirs, files in os.walk(REPO):
        # assets/ is walked rather than skipped: it holds the raw files, but it also
        # holds the Assets page. Only directories with an index.html become pages, so
        # the media subfolders are picked up by neither.
        dirs[:] = [
            d
            for d in dirs
            if not d.startswith("_")
            # every1/ is a second site with its own root, discovery files and domain.
            # It is published from this build but it is not a page of this portal.
            and d not in {".git", ".github", ".wrangler", "tools", "ai", "ai-source",
                          ".claude", "skills", "archive", "every1", "packages", "_working"}
        ]
        if "index.html" in files:
            rel = os.path.relpath(root, REPO).replace(os.sep, "/")
            pages.append("/" if rel == "." else f"/{rel}")
    return sorted(pages, key=lambda p: (p.count("/"), p))
