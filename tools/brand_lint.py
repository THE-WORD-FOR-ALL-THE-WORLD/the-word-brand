#!/usr/bin/env python3
"""Drift detector for the brand portal.

    python3 tools/brand_lint.py           report errors and warnings
    python3 tools/brand_lint.py --strict  treat warnings as failures

The AI layer claims to be canonical. This is what makes that claim true a year
from now: it checks that the published pages, the machine-readable files, and the
delivery configuration still agree with the Brand Guide.

Errors fail the build. Warnings are reported and do not.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import brandsource as bs  # noqa: E402
import build_ai  # noqa: E402
import colorkit as ck  # noqa: E402

REPO = bs.REPO
SKIP_DIRS = {".git", ".github", ".wrangler", "node_modules", "archive"}

errors: list = []
warnings: list = []


def err(code: str, message: str):
    errors.append(f"{code}  {message}")


def warn(code: str, message: str):
    warnings.append(f"{code}  {message}")


# A repository publishing two sites has two roots. A page under every1/ resolves
# "/assets/..." against every1/assets, not against the repository root, so a check
# that assumes one root reports every correct link as broken.
SITE_ROOTS = {"every1/": "every1"}


def site_root(rel: str) -> str:
    for prefix, root in SITE_ROOTS.items():
        if rel.startswith(prefix):
            return root
    return ""


def html_files() -> list:
    out = []
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in sorted(files):
            if name.endswith(".html"):
                out.append(os.path.relpath(os.path.join(root, name), REPO))
    return sorted(out)


def strip_specimens(s: str) -> str:
    """Remove regions where color is the subject matter rather than the design.

    A DON'T card shows a violation on purpose. A swatch and a proportion bar label
    a color with its own name. Checking these would flag the guide for teaching.
    """
    s = re.sub(r'<div class="dd dont">.*?(?=<div class="dd |</div>\s*</div>\s*</section>)', "", s, flags=re.S)
    s = re.sub(r'<div class="ban">.*?</div>\s*</div>\s*</div>', "", s, flags=re.S)
    s = re.sub(r'<div class="ratio-bar">.*?</div>\s*</div>', "", s, flags=re.S)
    s = re.sub(r'<div class="swatches">.*?</div>\s*</div>\s*</div>', "", s, flags=re.S)
    # The component gallery renders every component, including the site chrome.
    # A rendered specimen and a copyable markup block are the subject matter, not
    # the page's own markup, and reading them as such made L10 report that the
    # gallery's navigation "differs from the rest of the portal".
    s = re.sub(r'<div class="stage[^"]*">.*?</div>', "", s, flags=re.S)
    s = re.sub(r"<pre>.*?</pre>", "", s, flags=re.S)
    return s


def style_text(s: str) -> str:
    parts = re.findall(r'style="([^"]*)"', s)
    parts += re.findall(r"<style>(.*?)</style>", s, re.S)
    return "\n".join(parts)


# ---------------------------------------------------------------- checks


def check_sources():
    """L1: the guides still parse. Everything downstream depends on this."""
    try:
        return bs.parse_brand_guide(), bs.parse_messaging_guide()
    except bs.SourceError as exc:
        err("L1", str(exc))
        return None, None


def check_ai_source_present():
    """L2: every hand-authored input the build needs still exists."""
    required = [
        "overrides.json",
        "agent-rules.md",
        "audit.md",
        "anti-patterns.md",
        "approved-examples.md",
        "components.json",
        "components.css",
        "channels.json",
        "copy-bank.json",
        "consumers.json",
        "governance.json",
        "asset-notes.json",
        "skill.md",
    ]
    for name in required:
        if not os.path.exists(os.path.join(REPO, "ai-source", name)):
            err("L2", f"ai-source/{name} is missing. The build cannot run without it.")


def check_palette_drift(brand: dict, files: list):
    """L3: every page renders the Brand Guide's values, not its own copy of them."""
    canonical = {}
    for color in brand["colors"]:
        canonical[bs.strip_tags(color["name"]).lower().replace(" ", "-")] = color["hex"].upper()

    for rel in files:
        s = bs.read(os.path.join(REPO, rel))
        root = re.search(r":root\{(.*?)\}", s, re.S)
        if not root:
            # A page with no :root of its own has to be reading the generated one.
            # Before brand.tokens.css existed this check simply skipped such a page,
            # which meant a page could drop its tokens and silently go unchecked.
            if "/assets/brand.tokens.css" not in s and "/assets/brand.css" not in s:
                err(
                    "L3",
                    f"{rel} declares no brand tokens and links neither brand.tokens.css nor "
                    "brand.css, so nothing ties it to the Brand Guide.",
                )
            continue
        for m in re.finditer(r"--([a-z0-9-]+)\s*:\s*(#[0-9A-Fa-f]{3,8})\s*;", root.group(1)):
            name, value = m.group(1), m.group(2).upper()
            if name in canonical and canonical[name] != value:
                err(
                    "L3",
                    f"{rel} sets --{name} to {value}; the Brand Guide says {canonical[name]}. "
                    "Update the page, or update the guide and rebuild.",
                )


def check_unknown_colors(brand: dict, allowed: list, files: list):
    """L4: no improvised colors. Every hex traces to the palette or a recorded state."""
    known = {c["hex"].upper() for c in brand["colors"]}
    known |= {c["hex"].upper() for c in brand["retiredColors"]}
    known |= {
        m.group(0).upper()
        for t in brand["systemTokens"]
        for m in re.finditer(r"#[0-9A-Fa-f]{6}", t["value"])
    }
    known |= {a.upper() for a in allowed}
    known |= {"#FFF", "#FFFFFF", "#000", "#000000"}

    found: dict = {}
    for rel in files:
        s = strip_specimens(bs.read(os.path.join(REPO, rel)))
        for hexval in re.findall(r"#[0-9A-Fa-f]{3,8}\b", style_text(s)):
            if hexval.upper() not in known:
                found.setdefault(hexval.upper(), set()).add(rel)
    for hexval, where in sorted(found.items()):
        warn(
            "L4",
            f"{hexval} is not in the palette, a recorded state, or the lint allowlist. "
            f"Used in: {', '.join(sorted(where))}",
        )


def check_text_on_flame(files: list):
    """L5: Flame never carries text. Brand Guide §03, Law V."""
    for rel in files:
        s = strip_specimens(bs.read(os.path.join(REPO, rel)))
        for m in re.finditer(r'style="([^"]*)"', s):
            style = m.group(1)
            if re.search(r"background(?:-color)?\s*:\s*(#F85842|var\(--flame\))", style, re.I) and re.search(
                r"(?<!background-)color\s*:", style, re.I
            ):
                err("L5", f"{rel} sets text directly on Flame. Flame never carries text.")


def check_fonts(files: list):
    """L6: only the three approved families appear."""
    approved = {"dm serif display", "dm serif text", "dm sans"}
    generic = {
        "georgia",
        "times new roman",
        "serif",
        "sans-serif",
        "-apple-system",
        "segoe ui",
        "helvetica",
        "arial",
        "monospace",
        "sf mono",
        "consolas",
        "inherit",
        "system-ui",
    }
    for rel in files:
        s = bs.read(os.path.join(REPO, rel))
        for m in re.finditer(r"font-family\s*:\s*([^;\"}]+)", style_text(s)):
            for family in m.group(1).split(","):
                name = family.strip().strip("'\"").lower()
                if not name or name.startswith("var("):
                    continue
                if name not in approved and name not in generic:
                    warn("L6", f"{rel} uses the font family '{family.strip()}', which is not in the guide.")


def check_asset_links(files: list):
    """L7: every asset a page points at is actually published."""
    for rel in files:
        s = bs.read(os.path.join(REPO, rel))
        for m in re.finditer(r'(?:src|href|poster)="(/assets/[^"]+)"', s):
            # Download links carry a ?v= stamp so a version bump defeats any cache.
            # The file on disk is the path without it.
            path = m.group(1).split("?", 1)[0].split("#", 1)[0]
            if not os.path.exists(os.path.join(REPO, site_root(rel), path.lstrip("/"))):
                err("L7", f"{rel} points at {m.group(1)}, which does not exist.")


def check_discovery(ai_dir: str):
    """L8: everything published is discoverable, and /ai is served correctly."""
    sitemap = bs.read(os.path.join(REPO, "sitemap.xml"))
    llms = bs.read(os.path.join(REPO, "llms.txt"))
    headers = bs.read(os.path.join(REPO, "_headers"))

    # Just the card index, not the whole homepage: the nav carries every front door
    # already, so checking the full page would pass no matter what the cards say.
    home = bs.read(os.path.join(REPO, "index.html"))
    cards = re.search(r'<div class="cards">(.*?)\n\s*</div>\s*</div>\s*</main>', home, re.S)
    home = cards.group(1) if cards else ""
    if not cards:
        warn("L8", "index.html has no card index to check. Has the homepage been restructured?")
    for page in bs.published_pages():
        url = f"{bs.SITE}{page}" if page != "/" else f"{bs.SITE}/"
        if url not in sitemap:
            err("L8", f"{page} is published but missing from sitemap.xml. Run tools/build_ai.py.")
        if page == "/":
            continue
        # llms.txt and the homepage card index are the two hand-curated lists of what
        # exists. A new page that reaches neither is published but unfindable.
        if url not in llms:
            err("L8", f"{page} is published but missing from llms.txt. Add it in tools/build_ai.py.")
        # Only top-level front doors belong in the homepage card index. A sub-page is
        # reached through its own section, which is the design rather than a gap.
        if page.count("/") == 1 and f'href="{page}/"' not in home and f'href="{page}"' not in home:
            warn("L8", f"{page} is a front door but the homepage card index does not link to it.")

    # Without a 404.html, Cloudflare Pages answers every unmatched path with index.html
    # and a 200. An agent that mistypes an /ai/ URL then parses the homepage as if it
    # were the resource, which breaks the one promise this portal makes.
    if not os.path.exists(os.path.join(REPO, "404.html")):
        err(
            "L8",
            "404.html is missing. Without it Cloudflare Pages serves the homepage with a 200 "
            "for every path that does not exist, so nothing can tell a real resource from a typo.",
        )

    if f"{bs.SITE}/ai/manifest.json" not in llms:
        err("L8", "llms.txt does not point at the AI manifest. Run tools/build_ai.py.")

    for name in sorted(os.listdir(ai_dir)):
        if name.endswith((".md", ".json")) and f"/ai/{name}" not in headers:
            err(
                "L8",
                f"ai/{name} has no _headers entry, so it will be served with the wrong content type. "
                "Run tools/build_ai.py.",
            )

    robots = bs.read(os.path.join(REPO, "robots.txt"))
    if "Disallow: /ai" in robots:
        err("L8", "robots.txt blocks /ai. The AI layer exists to be crawled.")


def check_manifest_integrity(ai_dir: str):
    """L9: the manifest's checksums match what is on disk."""
    manifest_path = os.path.join(ai_dir, "manifest.json")
    if not os.path.exists(manifest_path):
        err("L9", "ai/manifest.json is missing. Run tools/build_ai.py.")
        return
    manifest = json.loads(bs.read(manifest_path))
    for entry in manifest.get("files", []):
        path = os.path.join(ai_dir, entry["name"])
        if not os.path.exists(path):
            err("L9", f"manifest lists ai/{entry['name']}, which does not exist.")
            continue
        if bs.sha256(bs.read(path)) != entry["sha256"]:
            err(
                "L9",
                f"ai/{entry['name']} does not match its manifest checksum. "
                "Run tools/build_ai.py so agents can trust the manifest.",
            )


def check_navigation(files: list):
    """L10: the portal chrome is the same on every page."""
    sets = {}
    for rel in files:
        # A page served from another site carries that site's chrome, not the
        # portal's. Comparing the two reports a difference that is the point.
        if any(rel.startswith(prefix) for prefix in SITE_ROOTS):
            continue
        s = strip_specimens(bs.read(os.path.join(REPO, rel)))
        nav = re.search(r'<div class="links">(.*?)</div>', s, re.S)
        if not nav:
            continue
        links = tuple(sorted(re.findall(r'href="([^"]+)"', nav.group(1))))
        sets.setdefault(links, []).append(rel)
    if len(sets) > 1:
        common = max(sets, key=lambda k: len(sets[k]))
        for links, pages in sets.items():
            if links == common:
                continue
            missing = sorted(set(common) - set(links))
            extra = sorted(set(links) - set(common))
            detail = []
            if missing:
                detail.append(f"missing {', '.join(missing)}")
            if extra:
                detail.append(f"extra {', '.join(extra)}")
            warn("L10", f"{', '.join(pages)}: navigation differs from the rest of the portal ({'; '.join(detail)}).")


def check_skill_copies():
    """L11: the installable skill and the published skill are byte-identical."""
    published = os.path.join(REPO, "ai", "SKILL.md")
    installed = os.path.join(REPO, "skills", "the-word-brand", "SKILL.md")
    for path in (published, installed):
        if not os.path.exists(path):
            err("L11", f"{os.path.relpath(path, REPO)} is missing. Run tools/build_ai.py.")
            return
    if bs.read(published) != bs.read(installed):
        err("L11", "ai/SKILL.md and skills/the-word-brand/SKILL.md have drifted apart. Run tools/build_ai.py.")


def check_contrast(tokens: dict):
    """L14: every pair the guide puts on screen still passes WCAG AA.

    The audit asks a human to check this by eye (H1). Half of it is arithmetic, and
    arithmetic belongs in the build. Ember was chosen over Flame for text because
    Flame is 3.3:1 and fails; nothing should be able to quietly undo that.

    The pairs and the measurements both come from tools/build_ai.py, which is also
    what publishes them at /ai/tokens.json. Measuring here against a second list of
    pairs would let the gate and the published number drift apart, which is the exact
    failure this whole layer exists to prevent.
    """
    published = tokens.get("contrast", {})
    if not published.get("permitted"):
        err("L14", "the tokens carry no contrast block. Run tools/build_ai.py.")
        return

    for pair in published["permitted"]:
        fg, bg, floor = pair["foreground"], pair["ground"], pair["requires"]
        try:
            ratio = build_ai.measure(tokens, fg, bg)
        except (KeyError, ValueError) as exc:
            err("L14", f"the contrast pair {fg} on {bg} cannot be measured: {exc}")
            continue
        if abs(ratio - pair["ratio"]) > 0.02:
            err(
                "L14",
                f"{fg} on {bg} measures {ratio:.2f}:1 but tokens.json publishes "
                f"{pair['ratio']}:1. Run tools/build_ai.py.",
            )
        if ratio + 0.005 < floor:
            err(
                "L14",
                f"{fg} on {bg} is {ratio:.2f}:1 and needs {floor}:1 ({pair['use']}). "
                "Change the value in the Brand Guide, or change what it is used for.",
            )

    # The forbidden pairs are published so a downstream build can cite a rule rather
    # than assert it. If one of them ever started passing, the rule would need
    # rewriting rather than keeping, so say so instead of staying quiet about it.
    for pair in published.get("forbidden", []):
        try:
            ratio = build_ai.measure(tokens, pair["foreground"], pair["ground"])
        except (KeyError, ValueError):
            continue
        if ratio + 0.005 >= 4.5:
            warn(
                "L14",
                f"{pair['foreground']} on {pair['ground']} is published as forbidden but now "
                f"measures {ratio:.2f}:1 and passes AA. The rule and the palette disagree.",
            )


def check_separation(tokens: dict):
    """L17: the outcome palette still tells itself apart, under every kind of vision.

    Six categories a reader learns by colour are six categories only while the closest
    pair stays far enough apart. A palette edit that pulls two of them together is a
    misread record in the field rather than a rough edge, so it fails the build here.
    """
    outcomes = tokens.get("outcome", {})
    if not outcomes:
        return
    published = tokens.get("separation", {})
    if not published.get("themes"):
        err("L17", "the outcome palette carries no separation block. Run tools/build_ai.py.")
        return
    floor = published.get("floor", build_ai.SEPARATION_FLOOR)
    lookup = build_ai.color_lookup(tokens)
    for theme, data in published["themes"].items():
        values = [outcomes[k][theme] for k in outcomes]
        values += [
            ck.resolve(lookup[name], "#FFFFFF")
            for name in data["measuredAgainst"]
            if name not in outcomes
        ]
        measured = ck.separations(values)
        for view, value in measured.items():
            if abs(value - data["minimum"].get(view, -1)) > 0.02:
                err(
                    "L17",
                    f"the {theme} outcome palette measures {value:.2f} under {view} but "
                    f"tokens.json publishes {data['minimum'].get(view)}. Run tools/build_ai.py.",
                )
            if value + 0.005 < floor:
                a, b, distance = ck.closest_pair(values, view)
                err(
                    "L17",
                    f"the {theme} outcome palette is only {value:.2f} apart under {view} and "
                    f"needs {floor}. The closest pair is {a} and {b} at {distance:.2f}. "
                    "Two outcomes that look alike are a misread record in the field.",
                )


def check_every1_type():
    """L20: the EVERY1 site is DM Sans led, and the serif appears only for scripture.

    Brand Guide section 11: sub-brand materials are DM Sans led, and the serif appears
    only where the parent speaks. The EVERY1 site shipped for five releases with every
    headline in DM Serif Display, and nothing checked it, because the faces were the
    parent's three and the parent's guide sets headlines in the serif. This reads the
    two published EVERY1 pages and fails any rule or inline style that sets the display
    serif at all, or the text serif on anything but the scripture setting. It also
    fails a third-party font request: the faces are self-hosted on both sites.
    """
    root = os.path.join(REPO, "every1")
    if not os.path.isdir(root):
        return
    for page in ("index.html", "messaging/index.html"):
        path = os.path.join(root, page)
        if not os.path.exists(path):
            continue
        s = bs.read(path)
        if "fonts.googleapis.com" in s or "fonts.gstatic.com" in s:
            err("L20", f"every1/{page} requests a face from Google Fonts. The site self-hosts "
                       "its faces at /assets/fonts/, like the portal.")
        # The prose may name the display serif, to say it is never used. A stylesheet
        # or an inline style may not.
        styled = "".join(re.findall(r"<style>(.*?)</style>", s, re.S)) + "".join(
            re.findall(r'style="([^"]*)"', s))
        if "serif-display" in styled or "DM Serif Display" in styled:
            err("L20", f"every1/{page} sets DM Serif Display. EVERY1 is DM Sans led, and the "
                       "parent's display serif is never set on one of its surfaces.")
        # Every CSS rule that names the text serif has to be a scripture setting: on the
        # brand page that is .vision .verse, on the messaging standard it is .vision. A
        # type specimen (.spec) shows the face it names, and :root only declares the stack.
        for css in re.findall(r"<style>(.*?)</style>", s, re.S):
            for m in re.finditer(r"([^{}]+)\{[^{}]*serif-text[^{}]*\}", css):
                selector = m.group(1).strip().split("}")[-1].strip()
                if selector.startswith(":root"):
                    continue
                if not any(k in selector for k in ("vision", "verse", ".spec")):
                    err("L20", f"every1/{page} sets the text serif on '{selector}'. On an EVERY1 "
                               "surface the serif is scripture only.")
        for m in re.finditer(r'<([a-z0-9]+)[^>]*style="[^"]*serif-text[^"]*"', s):
            err("L20", f"every1/{page} sets the text serif inline on a <{m.group(1)}>. The "
                       "serif is scripture only, and scripture is a class, not an inline style.")


def check_every1_delivery():
    """L18: the EVERY1 site serves everything its manifest declares.

    This check exists because it did not. The manifest declared 120 files and the site
    served 40, and with no 404.html underneath it Cloudflare Pages answered each of the
    80 missing ones with the homepage and a 200. A consumer that trusted the manifest
    got a web page where it asked for a PNG, and nothing anywhere caught it.
    """
    root = os.path.join(REPO, "every1")
    if not os.path.isdir(root):
        return

    # Without a 404.html, Cloudflare Pages answers every unmatched path with index.html
    # and a 200, which is what made the missing files silent rather than loud.
    if not os.path.exists(os.path.join(root, "404.html")):
        err(
            "L18",
            "every1/404.html is missing. Without it the EVERY1 Pages project serves its "
            "homepage with a 200 for every path that does not exist, so a declared asset "
            "that is not published looks to a consumer like a success.",
        )

    manifest_path = os.path.join(root, "ai", "manifest.json")
    if not os.path.exists(manifest_path):
        err("L18", "every1/ai/manifest.json is missing. Run tools/build_ai.py.")
        return
    manifest = json.loads(bs.read(manifest_path))
    prefix = build_ai.EVERY1_SITE_URL

    def local(url: str):
        if not url.startswith(prefix):
            err("L18", f"{url} is declared by the EVERY1 manifest but is not on its own site.")
            return None
        return os.path.join(root, url[len(prefix):].lstrip("/"))

    declared = 0
    for mark in manifest.get("marks", []):
        for entry in mark.get("files", []):
            declared += 1
            path = local(entry["url"])
            if path is None:
                continue
            if not os.path.exists(path):
                err(
                    "L18",
                    f"the EVERY1 manifest declares {entry['url']}, which the site does not "
                    "publish. Either publish it or stop declaring it: the mismatch is the "
                    "defect, not which way it is resolved.",
                )
                continue
            data = open(path, "rb").read()
            if "sha256" in entry and hashlib.sha256(data).hexdigest() != entry["sha256"]:
                err("L18", f"{entry['url']} does not match its manifest checksum. "
                           "Run tools/build_ai.py.")
            if "bytes" in entry and len(data) != entry["bytes"]:
                err("L18", f"{entry['url']} is {len(data)} bytes, not the {entry['bytes']} declared.")
    if declared == 0:
        err("L18", "the EVERY1 manifest declares no mark files at all. Run tools/build_logos.py.")

    for entry in manifest.get("files", []):
        path = local(entry["url"])
        if path is None:
            continue
        if not os.path.exists(path):
            err("L18", f"the EVERY1 manifest declares {entry['url']}, which is not published.")
            continue
        if bs.sha256(bs.read(path)) != entry["sha256"]:
            err("L18", f"{entry['url']} does not match its manifest checksum. "
                       "Run tools/build_ai.py.")

    # Anything a page offers as a download has to be there. brand_check.py was
    # advertised on the EVERY1 site for two releases without ever being published,
    # and the only reason anyone found out was a partner trying to use it.
    for page in ("index.html", os.path.join("messaging", "index.html")):
        full = os.path.join(root, page)
        if not os.path.exists(full):
            continue
        for href in sorted(set(re.findall(r'href="(/[^"#?]+\.[a-z0-9]+)"', bs.read(full)))):
            if not os.path.exists(os.path.join(root, href.lstrip("/"))):
                err(
                    "L18",
                    f"every1/{page} links {href}, which the EVERY1 site does not publish. "
                    "Publish the file or remove the link.",
                )


def check_scale_rules(tokens: dict):
    """L20: every scale publishes the rule that governs it, not only its values.

    The values were machine-readable for years and the rules were not, so "nothing in
    this system is a pill" and "nothing bounces, nothing springs" were real published
    rules that no consumer of /ai could see. Two products built a pill button and a
    spring animation against a standard that forbade both, and neither could have known.
    A scale with values and no rule is that gap reopening.
    """
    published = tokens.get("scaleRules", {})
    for name in ("spacing", "radius", "elevation", "motion", "breakpoint", "type",
                 "neutral", "outcome", "progression"):
        if name not in tokens:
            continue
        if not published.get(name):
            err(
                "L20",
                f"the '{name}' scale publishes values with no rule. Add data-rule to its "
                "<table data-scale> in the Brand Guide, or a consumer gets the numbers and "
                "has to guess what governs them.",
            )


def check_maskable_icon():
    """L19: the Android adaptive icon still fits inside the shape Android may crop to.

    Android guarantees only the inner circle at 66% diameter and crops everything else
    to whatever shape the launcher picks. A mark that overflows it loses a corner on
    some phones and not others, which is the worst kind of bug to be told about. This
    measures the rendered file rather than trusting the padding constant: the padding
    was right by arithmetic and wrong by eight tenths of a pixel the first time.
    """
    path = os.path.join(REPO, "assets", "logos", "every1", "icon",
                        "every1-icon-maskable-512.png")
    if not os.path.exists(path):
        err("L19", "the EVERY1 maskable icon is missing. Run tools/build_logos.py.")
        return
    try:
        from PIL import Image
    except ImportError:
        return  # CI has no imaging library, and --check already proved the file exists
    image = Image.open(path).convert("RGB")
    width, height = image.size
    pixels = image.load()
    ground = (11, 26, 45)
    xs, ys = [], []
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            if abs(r - ground[0]) + abs(g - ground[1]) + abs(b - ground[2]) > 24:
                xs.append(x)
                ys.append(y)
    if not xs:
        err("L19", "the EVERY1 maskable icon is a blank Midnight square.")
        return
    cx, cy = width / 2, height / 2
    corners = [(min(xs), min(ys)), (max(xs), min(ys)), (min(xs), max(ys)), (max(xs), max(ys))]
    furthest = max(math.hypot(x - cx, y - cy) for x, y in corners)
    safe = 0.33 * width
    if furthest > safe:
        err(
            "L19",
            f"the EVERY1 maskable icon reaches {furthest:.1f}px from centre and Android's safe "
            f"zone is {safe:.1f}px. Increase the maskable pad in tools/build_logos.py, or the "
            "mark loses a corner on whichever launcher crops hardest.",
        )


def check_every1_favicon():
    """L21: the EVERY1 favicon is opaque and carries the whole mark.

    This check exists because it did not. The door declared a transparent SVG as its
    favicon for two releases, and a transparent favicon takes the tab's own colour
    behind it: on the light chrome most systems ship, the reversed file's white E
    disappeared and the tab showed a lone Flame 1. The door was recognised by half its
    own icon. The favicon is now a plated PNG, and this measures the pixels rather than
    trusting the mode constant: fully opaque, and all three of White, Midnight and Flame
    present, so a plate change that erases one half of a two-tone mark fails here.
    """
    for name in ("every1-favicon-32.png", "every1-favicon-48.png"):
        path = os.path.join(REPO, "assets", "logos", "every1", "icon", name)
        if not os.path.exists(path):
            err("L21", f"the EVERY1 favicon {name} is missing. Run tools/build_logos.py.")
            continue
        try:
            from PIL import Image
        except ImportError:
            return  # CI has no imaging library, and --check already proved the file exists
        image = Image.open(path).convert("RGBA")
        pixels = image.load()
        width, height = image.size
        found = {"plate": 0, "word": 0, "accent": 0}
        for y in range(height):
            for x in range(width):
                r, g, b, a = pixels[x, y]
                if a != 255:
                    err("L21", f"the EVERY1 favicon {name} has transparent pixels. A tab paints "
                               "its own colour behind them, which is how the reversed mark "
                               "vanished on light chrome. The favicon is plated.")
                    return
                for key, (tr, tg, tb) in (("plate", (255, 255, 255)),
                                          ("word", (11, 26, 45)),
                                          ("accent", (248, 88, 66))):
                    if abs(r - tr) + abs(g - tg) + abs(b - tb) <= 30:
                        found[key] += 1
        missing = sorted(k for k, n in found.items() if n < 4)
        if missing:
            err("L21", f"the EVERY1 favicon {name} is missing its {', '.join(missing)}. The tab "
                       "carries the whole two-tone mark on its plate, never half of it.")


def check_consumers():
    """L15: the React library still implements what the specifications say.

    The library is hand-written and the specifications are published, so nothing
    but a check keeps them in step. This catches the two ways they come apart: a
    component specified with a React name that nothing exports, and a package
    still stamped with an older brand version than the one being released.
    """
    spec_path = os.path.join(REPO, "ai", "components.json")
    index_path = os.path.join(REPO, "packages", "ui", "src", "index.ts")
    pkg_path = os.path.join(REPO, "packages", "ui", "package.json")
    brand_pkg_path = os.path.join(REPO, "packages", "brand", "package.json")
    if not os.path.exists(spec_path):
        return
    components = json.loads(bs.read(spec_path))
    declared = components["version"]

    if not os.path.exists(index_path):
        err("L15", "packages/ui/src/index.ts is missing. The React library has no entry point.")
    else:
        exported = set(re.findall(r"export \{([^}]*)\}", bs.read(index_path)))
        names = {n.strip() for group in exported for n in group.split(",") if n.strip()}
        for c in components["components"]:
            if c.get("react") and c["react"] not in names:
                err(
                    "L15",
                    f"components.json says {c['id']} is implemented in React as {c['react']}, "
                    "but packages/ui does not export it.",
                )

    # The registry: every surface running this brand, and what it is running.
    registry_path = os.path.join(REPO, "ai-source", "consumers.json")
    if os.path.exists(registry_path):
        for c in json.loads(bs.read(registry_path))["consumers"]:
            synced = c.get("syncedVersion")
            if synced == "auto":
                continue
            if synced is None:
                warn(
                    "L16",
                    f"{c['name']} ({c['kind']}) has never been synced. It is running an unknown "
                    f"version of the brand while the system is at v{declared}.",
                )
            elif synced != declared:
                warn(
                    "L16",
                    f"{c['name']} ({c['kind']}) is on v{synced}; the system is at v{declared}. "
                    "Sync it, then update ai-source/consumers.json.",
                )

    for path in (pkg_path, brand_pkg_path):
        if not os.path.exists(path):
            err("L15", f"{os.path.relpath(path, REPO)} is missing. Run tools/build_ai.py.")
            continue
        pkg = json.loads(bs.read(path))
        stamped = pkg.get("brand", {}).get("version")
        if stamped != declared:
            err(
                "L15",
                f"{pkg['name']} is stamped with brand v{stamped} but the system is v{declared}. "
                "Run tools/build_ai.py.",
            )


def check_stylesheet_vars():
    """L17: every variable brand.css uses is a variable brand.css defines.

    A var() with no definition does not error. It falls back to whatever the
    property inherits, so the page still renders and the mistake is invisible
    until someone looks closely at the wrong ground. That is exactly how the dark
    theme shipped referencing five colours the stylesheet never defined.
    """
    path = os.path.join(REPO, "assets", "brand.css")
    if not os.path.exists(path):
        err("L17", "assets/brand.css is missing. Run tools/build_ai.py.")
        return
    css = bs.read(path)
    defined = set(re.findall(r"^\s*--([a-z0-9-]+)\s*:", css, re.M))
    used = set(re.findall(r"var\(\s*--([a-z0-9-]+)", css))
    for name in sorted(used - defined):
        err(
            "L17",
            f"assets/brand.css uses --{name} and never defines it. A var() with no "
            "definition falls back silently, so this renders wrong rather than failing.",
        )
    # A variable defined and never used is not an error: the token layer is
    # published for other people to build with, not only for this stylesheet.


SPECIFICITY = re.compile(r"#[\w-]+|\.[\w-]+|\[[^\]]+\]|::[\w-]+|:[\w-]+|\b[a-zA-Z][\w-]*")


def specificity(selector: str) -> tuple:
    """(id, class, element) for the selector shapes this repository actually uses."""
    ids = classes = elements = 0
    for token in SPECIFICITY.findall(selector):
        if token.startswith("#"):
            ids += 1
        elif token.startswith("::"):
            elements += 1
        elif token.startswith(".") or token.startswith("[") or token.startswith(":"):
            classes += 1
        else:
            elements += 1
    return (ids, classes, elements)


def _matches(selector: str, classes: set, tag: str, dark: bool) -> bool:
    """Does this selector match an element with these classes, in this theme?

    Only the forms this repository writes: descendant chains of tags and classes,
    optionally led by [data-theme="dark"]. Anything carrying a combinator or a
    pseudo class is treated as not matching, so the check stays conservative and
    never invents a conflict that is not there.
    """
    if any(c in selector for c in (">", "+", "~", ":")):
        return False
    parts = selector.split()
    if '[data-theme="dark"]' in parts:
        if not dark:
            return False
        parts = [p for p in parts if p != '[data-theme="dark"]']
    if not parts:
        return False
    bits = re.findall(r"\.[\w-]+|^[a-zA-Z][\w-]*", parts[-1])
    if not bits:
        return False
    for bit in bits:
        if bit.startswith("."):
            if bit[1:] not in classes:
                return False
        elif bit != tag:
            return False
    return True


def check_theme_swaps(files: list):
    """L18: a light/dark pair resolves to exactly one visible element per theme.

    A page that swaps two images by class is one specificity mistake away from
    showing both, and showing both reads as a content bug rather than a CSS one.
    That is what shipped in v7.0: `.topbar .brand img { display: block }` at 0,2,1
    outranked `.mark-dark { display: none }` at 0,1,0, so both marks rendered, in
    both themes, and the theme toggle did nothing at all.
    """
    for rel in files:
        page = bs.read(os.path.join(REPO, rel))
        css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", page, re.S))
        if not css:
            continue

        rules = []
        for m in re.finditer(r"([^{}]+)\{([^}]*)\}", css):
            decl = re.search(r"(?:^|;)\s*display\s*:\s*([\w-]+)", m.group(2))
            if not decl:
                continue
            for selector in m.group(1).split(","):
                selector = selector.strip()
                if selector:
                    rules.append((selector, specificity(selector), decl.group(1)))
        if not rules:
            continue

        # Elements whose class names differ only by a -light / -dark suffix.
        stems = {}
        for m in re.finditer(r'<(\w+)[^>]*\sclass="([^"]*)"', page):
            tag, classes = m.group(1), set(m.group(2).split())
            for c in classes:
                if c.endswith("-light") or c.endswith("-dark"):
                    stem, variant = c.rsplit("-", 1)
                    stems.setdefault(stem, {})[variant] = (tag, classes)

        for stem, pair in stems.items():
            if set(pair) != {"light", "dark"}:
                continue
            for dark in (False, True):
                shown = []
                for variant, (tag, classes) in sorted(pair.items()):
                    winner, best = None, (-1, -1, -1)
                    for selector, spec, value in rules:
                        if _matches(selector, classes, tag, dark) and spec >= best:
                            winner, best = value, spec
                    if winner != "none":
                        shown.append(variant)
                if len(shown) != 1:
                    err(
                        "L18",
                        f"{rel}: in {'dark' if dark else 'light'} mode the '{stem}' pair resolves "
                        f"to {len(shown)} visible element(s) ({', '.join(shown) or 'none'}). "
                        "Exactly one should show; check which display rule wins on specificity.",
                    )


def check_social_cards(files: list):
    """L13: every page previews correctly when it is shared.

    A brand URL is shared into a partner's inbox and a volunteer's group chat. A
    page with no card previews as a blank rectangle, which reads as a dead link.
    The card itself is generated by build_logos.py from the approved wordmark, so
    this only has to check that each page claims it.
    """
    required = [
        ('<meta property="og:title"', "an og:title"),
        ('<meta property="og:description"', "an og:description"),
        ('<meta property="og:image"', "an og:image"),
        ('<meta property="og:url"', "an og:url"),
        ('<meta name="description"', "a meta description"),
        ('rel="icon"', "a favicon link"),
    ]
    card = os.path.join(REPO, "assets", "images", "og-card.png")
    if not os.path.exists(card):
        err("L13", "assets/images/og-card.png is missing. Run tools/build_logos.py.")
    for rel in files:
        s = bs.read(os.path.join(REPO, rel))
        missing = [label for needle, label in required if needle not in s]
        if missing:
            err("L13", f"{rel} is missing {', '.join(missing)}.")


def check_logo_sources(files: list):
    """
    L12: every logo a live page shows comes from the published set.

    The published brands are whichever directories exist under assets/logos/, so a new
    door needs no change here. An underscore prefix means working artwork: _masters
    holds the approved originals and _inbox holds files on their way to becoming one,
    and neither is a thing a page may link to. Retired marks live in archive/ so an
    archived guide still renders, and nothing live may reach back for them.
    """
    root = os.path.join(REPO, "assets", "logos")
    published = {
        d for d in os.listdir(root)
        if os.path.isdir(os.path.join(root, d)) and not d.startswith("_")
    } if os.path.isdir(root) else set()

    for rel in files:
        if site_root(rel):
            # A second site holds flat copies of its own brand's marks, written by the
            # build from the published set. L7 already proves each one exists.
            continue
        s = bs.read(os.path.join(REPO, rel))
        for m in re.finditer(r'(?:src|href)="(/assets/logos/([^"/]+)/[^"]*|/assets/logos/[^"/]+)"', s):
            url = m.group(1).split("?", 1)[0]
            folder = m.group(2)
            if folder in published:
                continue
            if folder and folder.startswith("_"):
                err("L12", f"{rel}: links to working artwork {url}. Link to the published file.")
            else:
                err(
                    "L12",
                    f"{rel}: uses a logo outside the published set, {url}. "
                    f"Published brands: {', '.join(sorted(published)) or 'none'}.",
                )


# ---------------------------------------------------------------- main


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = parser.parse_args()

    check_ai_source_present()
    brand, _messaging = check_sources()
    if brand is None:
        print("\n".join(errors), file=sys.stderr)
        return 2

    overrides = json.loads(bs.read(os.path.join(REPO, "ai-source", "overrides.json")))
    allowed = overrides.get("lint", {}).get("allowedColors", [])
    ai_dir = os.path.join(REPO, "ai")
    files = html_files()

    check_palette_drift(brand, files)
    check_unknown_colors(brand, allowed, files)
    check_text_on_flame(files)
    check_fonts(files)
    check_asset_links(files)
    check_logo_sources(files)
    check_social_cards(files)
    check_consumers()
    check_stylesheet_vars()
    check_theme_swaps(files)
    tokens = build_ai.build_tokens(
        brand,
        _messaging,
        overrides.get("manifest", {}).get("updated") or brand["issued"],
        overrides,
        bs.parse_scales(os.path.join(REPO, "brand", "index.html")),
    )
    check_contrast(tokens)
    check_separation(tokens)
    check_scale_rules(tokens)
    check_every1_delivery()
    check_every1_type()
    check_maskable_icon()
    check_every1_favicon()
    check_navigation(files)
    check_skill_copies()
    if os.path.isdir(ai_dir):
        check_discovery(ai_dir)
        check_manifest_integrity(ai_dir)
    else:
        err("L9", "ai/ does not exist. Run tools/build_ai.py.")

    for line in warnings:
        print(f"WARN   {line}")
    for line in errors:
        print(f"ERROR  {line}", file=sys.stderr)

    print(
        f"\n{len(files)} pages checked · {len(errors)} error(s) · {len(warnings)} warning(s)"
    )
    if errors:
        return 1
    if warnings and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
