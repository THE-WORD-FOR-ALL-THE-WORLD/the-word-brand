#!/usr/bin/env python3
"""Run the mechanical half of the brand audit against any file or URL.

    python3 tools/brand_check.py page.html
    python3 tools/brand_check.py https://example.org/campaign
    python3 tools/brand_check.py post.md caption.txt styles.css
    python3 tools/brand_check.py --strict page.html      exit 1 on a warning too

Roughly half of ai/audit.md is decidable by a machine: an unknown hex, a font
that is not one of the three, text on Flame, a banned word, a missing endorsement
line, an image with no alt text. This decides those and stays silent about the
rest, because the other half needs a person.

A clean result is NOT a passed audit. It means nothing mechanical is wrong. The
gates about invented facts, staged imagery, the prophecy, and who the hero is
still need a reader, and this prints that reminder every time so nobody mistakes
one for the other.

Inside this repository it reads ai/. Anywhere else it fetches the published
manifest, so it is always measuring against the current standard.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request

SITE = "https://brand.theword.world"
HERE = os.path.dirname(os.path.abspath(__file__))
LOCAL_AI = os.path.join(os.path.dirname(HERE), "ai")

GENERIC_FONTS = {
    "georgia", "times new roman", "serif", "sans-serif", "-apple-system", "segoe ui",
    "helvetica", "arial", "monospace", "sf mono", "consolas", "inherit", "system-ui",
    "ui-monospace", "menlo", "courier new", "cursive", "initial", "unset", "revert",
}

# EVERY1 is absent on purpose. It is the recorded exception to Law III and carries no
# endorsement line, so flagging its absence would fail a surface for being correct.
INITIATIVES = ["Revival To My City", "School of the Local Church"]
EXEMPT_FROM_G6 = ["EVERY1"]
ENDORSEMENT = "A ministry of THE WORD FOR ALL THE WORLD"


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "brand-check/1.0"})
    with urllib.request.urlopen(req, timeout=30) as fh:
        return fh.read().decode("utf-8", errors="replace")


def load_standard(offline: bool) -> dict:
    """The current standard, from disk inside this repo or from the manifest outside it."""
    if offline or os.path.isdir(LOCAL_AI):
        read = lambda name: open(os.path.join(LOCAL_AI, name), encoding="utf-8").read()
        source = "local ai/"
    else:
        manifest = json.loads(fetch(f"{SITE}/ai/manifest.json"))
        read = lambda name: fetch(f"{SITE}/ai/{name}")
        source = manifest["manifest"]

    tokens = json.loads(read("tokens.json"))
    anti = read("anti-patterns.md")

    known = {c["hex"].upper() for c in tokens["color"].values()}
    for t in tokens["system"].values():
        known |= {m.upper() for m in re.findall(r"#[0-9A-Fa-f]{6}", t["value"])}
    known |= {"#FFF", "#FFFFFF", "#000", "#000000"}

    # anti-patterns.md publishes every banned word under one heading, as bullets,
    # grouped by category. Read the bullets, not the prose around them: the prose
    # explains why each list exists and naturally contains examples.
    banned = []
    section = re.search(r"^## Every banned word\s*$(.*)", anti, re.S | re.M)
    if section:
        for line in section.group(1).splitlines():
            m = re.match(r"^\s*[-*]\s+(.+?)\s*$", line)
            if not m:
                continue
            # Strip the trailing qualifier first, then the quotes: an entry like
            # "fresh anointing" (unexplained) otherwise keeps its closing quote and
            # then matches nothing.
            word = re.sub(r"\s*\([^)]*\)\s*$", "", m.group(1).strip()).strip()
            word = word.strip('"').strip("'").strip("`").strip().lower()
            # Entries describing a pattern rather than a phrase cannot be matched.
            if not word or "emoji" in word or word.startswith("all-"):
                continue
            banned.append(word)

    # The repository records a short allowlist of non-brand colours with a written
    # reason: gradient stops standing in for footage that has not been cut yet.
    # Honour it when it is reachable, so the guide does not fail its own check for
    # a concession it documents.
    allow_path = os.path.join(os.path.dirname(HERE), "ai-source", "overrides.json")
    if os.path.exists(allow_path):
        overrides = json.loads(open(allow_path, encoding="utf-8").read())
        known |= {c.upper() for c in overrides.get("lint", {}).get("allowedColors", [])}

    return {
        "version": tokens["version"],
        "source": source,
        "known": known,
        "flame": tokens["color"]["flame"]["hex"].upper(),
        "families": {f["family"].lower() for f in tokens["typography"]["families"]},
        "banned": sorted(set(banned)),
    }


def strip_specimens(text: str) -> str:
    """Remove regions where a violation is the subject matter rather than a mistake.

    A DON'T card shows text on Flame on purpose, and a swatch labels a colour with
    its own name. Checking those would fail a page for teaching the rule, which is
    the opposite of what this is for. Same regions the repository's own linter
    strips, so the two agree about what counts.
    """
    text = re.sub(r'<div class="dd dont">.*?(?=<div class="dd |</div>\s*</div>\s*</section>)', "", text, flags=re.S)
    text = re.sub(r'<div class="ban">.*?</div>\s*</div>\s*</div>', "", text, flags=re.S)
    text = re.sub(r'<div class="ratio-bar">.*?</div>\s*</div>', "", text, flags=re.S)
    text = re.sub(r'<div class="swatches">.*?</div>\s*</div>\s*</div>', "", text, flags=re.S)
    # The banned-word lists themselves, which necessarily contain banned words.
    text = re.sub(r'<div class="bw">.*?</div>', "", text, flags=re.S)
    # Messaging Standard v2.0 sets the same specimens in plain document markup:
    # the ban lists carry data-words, and a before-and-after quotes the wrong
    # version in .off in order to correct it in .on.
    text = re.sub(r"<p data-words>.*?</p>", "", text, flags=re.S)
    text = re.sub(r'<p class="off">.*?</p>', "", text, flags=re.S)
    # An explicit marker, for a rule that has to quote the wrong wording in
    # order to forbid it. Preferred over guessing from the surrounding markup:
    # the author says "this is a specimen" and the check believes them.
    text = re.sub(r"<span data-specimen>.*?</span>", "", text, flags=re.S)
    # Tables and lists that exist to name language we do not use. The heading
    # above them says so, which is what makes them findable.
    text = re.sub(
        r"<h[34][^>]*>[^<]*(?:avoid|do not use|prohibited|not used)[^<]*</h[34]>\s*"
        r"(?:<p[^>]*>.*?</p>\s*)?(?:<table.*?</table>|<ul>.*?</ul>)",
        "", text, flags=re.S | re.I,
    )
    # A "never this / always this" rewrite table, which quotes the wrong version in
    # order to correct it. Any table whose first header cell says "never".
    text = re.sub(
        r"<table[^>]*>\s*<tr>\s*<th>\s*Never\b.*?</table>", "", text, flags=re.S | re.I
    )
    return text


def styles(text: str) -> str:
    return "\n".join(re.findall(r'style="([^"]*)"', text) + re.findall(r"<style[^>]*>(.*?)</style>", text, re.S))


def check(name: str, text: str, std: dict) -> list:
    findings = []
    is_markup = "<" in text and ">" in text
    if is_markup:
        text = strip_specimens(text)
    style_text = styles(text) if is_markup else text
    prose = re.sub(r"<[^>]+>", " ", text) if is_markup else text

    # B1: every colour traces to the palette or a recorded state.
    for hexval in sorted(set(re.findall(r"#[0-9A-Fa-f]{3,8}\b", style_text))):
        if hexval.upper() not in std["known"]:
            findings.append(("fail", "B1", f"{hexval} is not in the palette or a recorded state."))

    # C1: only the three approved families.
    for m in re.finditer(r"font-family\s*:\s*([^;\"}]+)", style_text):
        for family in m.group(1).split(","):
            f = family.strip().strip("'\"").lower()
            if not f or f.startswith("var(") or f in GENERIC_FONTS or f in std["families"]:
                continue
            findings.append(("fail", "C1", f"'{family.strip()}' is not one of the three approved families."))

    # G4: Flame never carries text and never sits under it.
    flame = std["flame"]
    for m in re.finditer(r'style="([^"]*)"', text):
        rule = m.group(1)
        if re.search(rf"background(?:-color)?\s*:\s*({re.escape(flame)}|var\(--flame\))", rule, re.I) and re.search(
            r"(?<!background-)color\s*:", rule, re.I
        ):
            findings.append(("fail", "G4", "Text is set directly on Flame. Fire at text size is Ember."))
        if re.search(rf"(?<!background-)color\s*:\s*({re.escape(flame)}|var\(--flame\))", rule, re.I):
            # Flame text on a light ground is 2.9:1 and is what the gate is for. On
            # Midnight it is 5.4:1 and is the recorded treatment for eyebrows and
            # official-record numerals. The ground is not always knowable from one
            # declaration, so a bare Flame colour is raised for a person to confirm
            # rather than failed outright.
            light = re.search(
                r"background(?:-color)?\s*:\s*(#F7F3EC|#FFF(?:FFF)?|var\(--parchment\)|var\(--white\))",
                rule, re.I,
            )
            if light:
                findings.append(("fail", "G4", "Text is set in Flame on a light ground. That is 2.9:1. Use Ember."))
            else:
                findings.append(
                    ("warn", "G4",
                     "Text is set in Flame. Allowed only on Midnight, where it is the recorded "
                     "treatment for eyebrows and record numerals. Confirm the ground.")
                )

    # H2: the focus ring is never removed.
    if re.search(r"outline\s*:\s*(none|0)\b", style_text, re.I):
        findings.append(("fail", "H2", "A focus outline is removed. It is never removed."))

    # H4: every image carries meaningful alternative text.
    for m in re.finditer(r"<img\b[^>]*>", text, re.I):
        tag = m.group(0)
        alt = re.search(r'alt="([^"]*)"', tag)
        if alt is None:
            findings.append(("fail", "H4", f"An image has no alt attribute: {tag[:70]}"))
        elif not alt.group(1).strip() and 'role="presentation"' not in tag and 'aria-hidden' not in tag:
            findings.append(("warn", "H4", f"An image has empty alt text and is not marked decorative: {tag[:70]}"))

    # G9: banned language.
    low = prose.lower()
    for word in std["banned"]:
        if re.search(r"\b" + re.escape(word) + r"\b", low):
            findings.append(("fail", "G9", f"Banned term '{word}' appears in the copy."))

    # G6: an initiative named without the endorsement line.
    #
    # The gate is about a surface that SPEAKS FOR an initiative, not about the
    # parent naming its own doors in a sentence. Putting "A ministry of THE WORD
    # FOR ALL THE WORLD" on THE WORD's own page would be wrong, not compliant. So
    # this fires on the two cases that are actually violations: the initiative
    #name carried in the title or a heading, meaning the piece speaks for it, or the
    # parent going unnamed anywhere in the piece at all.
    if ENDORSEMENT.lower() not in low:
        # What LEADS the piece: its title and its top heading. A section heading on a
        # parent page that lists the doors is the parent speaking, and putting the
        # endorsement there would be wrong rather than compliant.
        headings = " ".join(
            re.findall(r"<h1[^>]*>(.*?)</h1>", text, re.S | re.I)
            + re.findall(r"<title[^>]*>(.*?)</title>", text, re.S | re.I)
            + re.findall(r'<meta property="og:title" content="([^"]*)"', text, re.I)
        )
        headings = re.sub(r"<[^>]+>", " ", headings)
        parent_named = "the word for all the world" in low
        for initiative in INITIATIVES:
            in_heading = re.search(rf"\b{re.escape(initiative)}\b", headings) is not None
            in_prose = re.search(rf"\b{re.escape(initiative)}\b", prose) is not None
            if in_heading:
                findings.append(
                    ("fail", "G6", f"'{initiative}' leads this piece, so it needs '{ENDORSEMENT}'.")
                )
                break
            if in_prose and not parent_named:
                findings.append(
                    ("fail", "G6",
                     f"'{initiative}' appears and the parent is never named. Add '{ENDORSEMENT}'.")
                )
                break

    # --- the verbal system, Messaging Standard v2.0 §16
    # These are rules the guide used to state in prose and nobody could run.
    # They are mechanical, so the check runs them rather than trusting a reader.

    # M1: em dashes are not used. §16.8, and the house style of this repository.
    # The prophecy is quoted exactly and is the one recorded exception.
    if "\u2014" in prose and "as tensions grow between man and foe" not in low:
        n = prose.count("\u2014")
        findings.append(
            ("fail", "M1", f"{n} em dash{'es' if n > 1 else ''}. Use a colon, a comma, or a period.")
        )

    # M2: EVERY1 always carries the numeral. §16.9.
    for wrong in ("Every1", "EveryOne", "Every One", "EVERYONE", "Every-1"):
        if re.search(rf"\b{re.escape(wrong)}\b", prose):
            findings.append(("fail", "M2", f"'{wrong}' is written EVERY1, always with the numeral."))
            break

    # M3: Spirit-led and Spirit-filled are hyphenated. §16.9.
    for m in re.finditer(r"\bSpirit[  ](led|filled)\b", prose):
        findings.append(("fail", "M3", f"'Spirit {m.group(1)}' is hyphenated: Spirit-{m.group(1)}."))
        break

    # M4: He is Lord; a person acknowledges it. §16.4 and §13.
    if re.search(r"\bmakes?\s+(?:Jesus|Him)\s+Lord\b", prose, re.I):
        findings.append(
            ("fail", "M4", "'make Jesus Lord' is prohibited. He is Lord. Use 'confess Jesus as Lord'.")
        )

    # M5: the Holy Spirit is a Person, never an it. §13.
    if re.search(r"\bHoly Spirit[^.?!]{0,40}\bit\b", prose):
        findings.append(
            ("warn", "M5", "The Holy Spirit may be referred to as 'it' here. He is a Person.")
        )

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("targets", nargs="+", help="file paths or URLs")
    parser.add_argument("--strict", action="store_true", help="a warning fails too")
    parser.add_argument("--offline", action="store_true", help="never fetch; use the local ai/ directory")
    args = parser.parse_args()

    try:
        std = load_standard(args.offline)
    except Exception as exc:
        print(f"BLOCKED: could not load the brand system ({exc}).", file=sys.stderr)
        print("Do not describe the work as brand compliant.", file=sys.stderr)
        return 2

    all_findings = []
    for target in args.targets:
        try:
            text = fetch(target) if target.startswith(("http://", "https://")) else open(target, encoding="utf-8").read()
        except Exception as exc:
            print(f"BLOCKED: could not read {target} ({exc}).", file=sys.stderr)
            return 2
        for level, code, message in check(target, text, std):
            all_findings.append((level, code, target, message))

    fails = [f for f in all_findings if f[0] == "fail"]
    warns = [f for f in all_findings if f[0] == "warn"]

    print("BRAND CHECK, mechanical only")
    print(f"Brand system: v{std['version']} · measured against: {std['source']}")
    print(f"Scope: {', '.join(args.targets)}")
    print()
    if not all_findings:
        print("MECHANICAL: PASS")
    else:
        print(f"MECHANICAL: {len(fails)} failure(s), {len(warns)} warning(s)")
        print()
        for level, code, target, message in all_findings:
            print(f"  {level.upper():4s} {code:3s} {target}: {message}")
    print()
    print("NOT CHECKED, and these decide the audit:")
    print("  G1 invented facts · G2 stock or generated imagery · G3 the prophecy quoted exactly")
    print("  G7 governmental iconography · G8 unattributed authority · G10 who the hero is")
    print("  and every judgement in sections A, D, E, and F of the audit.")
    print()
    print("A clean result here is not a passed audit. Run ai/audit.md with a reader.")

    if fails or (args.strict and warns):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
