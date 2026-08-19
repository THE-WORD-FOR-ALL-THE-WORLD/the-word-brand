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
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import brandsource as bs  # noqa: E402

REPO = bs.REPO
SKIP_DIRS = {".git", ".github", ".wrangler", "node_modules", "archive"}

errors: list = []
warnings: list = []


def err(code: str, message: str):
    errors.append(f"{code}  {message}")


def warn(code: str, message: str):
    warnings.append(f"{code}  {message}")


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
            target = os.path.join(REPO, m.group(1).lstrip("/"))
            if not os.path.exists(target):
                err("L7", f"{rel} points at {m.group(1)}, which does not exist.")


def check_discovery(ai_dir: str):
    """L8: everything published is discoverable, and /ai is served correctly."""
    sitemap = bs.read(os.path.join(REPO, "sitemap.xml"))
    llms = bs.read(os.path.join(REPO, "llms.txt"))
    headers = bs.read(os.path.join(REPO, "_headers"))

    for page in bs.published_pages():
        url = f"{bs.SITE}{page}" if page != "/" else f"{bs.SITE}/"
        if url not in sitemap:
            err("L8", f"{page} is published but missing from sitemap.xml. Run tools/build_ai.py.")

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
        s = bs.read(os.path.join(REPO, rel))
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


def check_logo_sources(files: list):
    """
    L12: every logo a live page shows comes from the published set.

    The retired 368x32 wordmark PNGs live in archive/ so an archived guide still
    renders. Nothing in the live portal may reach back for them, and no page may
    link straight at a master, which is working artwork rather than a published file.
    """
    published = "/assets/logos/the-word/"
    allowed_other = ("/assets/logos/rtmc/",)
    for rel in files:
        s = bs.read(os.path.join(REPO, rel))
        for m in re.finditer(r'(?:src|href)="(/assets/logos/[^"]+)"', s):
            url = m.group(1)
            if url.startswith(published) or url.startswith(allowed_other):
                continue
            if "/_masters/" in url or "/_inbox/" in url:
                err("L12", f"{rel}: links to working artwork {url}. Link to the published file.")
            else:
                err("L12", f"{rel}: uses a retired logo {url}. The published marks are at {published}.")


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
