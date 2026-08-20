#!/usr/bin/env python3
"""Push the published tokens into a Figma library as Variables.

    export FIGMA_TOKEN=figd_...        a personal access token with file write scope
    export FIGMA_FILE_KEY=...          the library file's key, from its URL
    python3 tools/sync_figma.py --dry-run
    python3 tools/sync_figma.py

One direction only: this repository to Figma, never the other way. The moment a
designer changes a variable in Figma instead of in the Brand Guide there are two
standards, and the one with the nicer interface wins. Designers propose a change
as a pull request against brand/index.html; when it merges, this runs.

Needs the network, so it is never part of the build or of CI's verify step.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import brandsource as bs  # noqa: E402

API = "https://api.figma.com/v1"
COLLECTION = "THE WORD"


def rgba(value: str) -> dict:
    """A hex or rgba() token as Figma's 0..1 colour object."""
    value = value.strip()
    m = re.fullmatch(r"#([0-9A-Fa-f]{6})", value)
    if m:
        h = m.group(1)
        r, g, b, a = *(int(h[i : i + 2], 16) / 255 for i in (0, 2, 4)), 1.0
        return {"r": r, "g": g, "b": b, "a": a}
    m = re.fullmatch(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+)\s*)?\)", value)
    if not m:
        raise ValueError(f"cannot read the colour {value!r}")
    return {
        "r": int(m.group(1)) / 255,
        "g": int(m.group(2)) / 255,
        "b": int(m.group(3)) / 255,
        "a": float(m.group(4)) if m.group(4) else 1.0,
    }


def px(value: str) -> float:
    m = re.match(r"(-?[\d.]+)", value.strip())
    if not m:
        raise ValueError(f"cannot read the dimension {value!r}")
    return float(m.group(1))


def variables(tokens: dict) -> list:
    """Every token Figma can hold, as (name, type, value).

    Elevation and motion are left out on purpose: Figma has no variable type for a
    shadow or an easing curve, and a string that looks like one would be a value
    designers could bind to and developers could not.
    """
    out = []
    for key, c in tokens["color"].items():
        out.append((f"color/{key}", "COLOR", rgba(c["hex"])))
    for key, n in tokens["neutral"].items():
        out.append((f"neutral/{key}", "COLOR", rgba(n["value"])))
    for key, t in tokens["system"].items():
        if t["value"].startswith("#"):
            out.append((f"state/{key}", "COLOR", rgba(t["value"])))
    for key, value in tokens["spacing"].items():
        out.append((f"spacing/{key}", "FLOAT", px(value)))
    for key, value in tokens["radius"].items():
        out.append((f"radius/{key}", "FLOAT", px(value)))
    for key, t in tokens["typeScale"].items():
        out.append((f"fontSize/{key}", "FLOAT", px(t["size"])))
        out.append((f"lineHeight/{key}", "FLOAT", float(t["lineHeight"])))
    for key, value in tokens["breakpoint"].items():
        out.append((f"breakpoint/{key}", "FLOAT", px(value)))
    return out


def call(path: str, token: str, payload=None):
    req = urllib.request.Request(
        f"{API}{path}",
        headers={"X-Figma-Token": token, "Content-Type": "application/json"},
        data=json.dumps(payload).encode() if payload is not None else None,
        method="POST" if payload is not None else "GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as fh:
            return json.loads(fh.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:400]
        raise SystemExit(f"Figma said {exc.code}: {detail}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="print the payload and send nothing")
    args = parser.parse_args()

    tokens = json.loads(bs.read(os.path.join(bs.REPO, "ai", "tokens.json")))
    wanted = variables(tokens)
    print(f"Brand system v{tokens['version']}: {len(wanted)} variables")

    if args.dry_run:
        for name, kind, value in wanted:
            print(f"  {kind:6s} {name:34s} {value}")
        return 0

    token = os.environ.get("FIGMA_TOKEN")
    file_key = os.environ.get("FIGMA_FILE_KEY")
    if not token or not file_key:
        print(
            "Set FIGMA_TOKEN and FIGMA_FILE_KEY. Create the token at\n"
            "  https://www.figma.com/developers/api#access-tokens\n"
            "with file_variables:write scope, which needs an Enterprise plan. Without it,\n"
            "run --dry-run and enter the values by hand, then record the version in\n"
            "ai-source/consumers.json so the linter can see what Figma is on.",
            file=sys.stderr,
        )
        return 2

    existing = call(f"/files/{file_key}/variables/local", token)
    collections = existing.get("meta", {}).get("variableCollections", {})
    collection_id = next(
        (cid for cid, c in collections.items() if c.get("name") == COLLECTION), None
    )
    by_name = {
        v["name"]: vid
        for vid, v in existing.get("meta", {}).get("variables", {}).items()
        if v.get("variableCollectionId") == collection_id
    }

    creates, updates, values = [], [], []
    if collection_id is None:
        collection_id = "tempCollection"
        creates.append(
            {"action": "CREATE", "id": collection_id, "name": COLLECTION, "initialModeId": "tempMode"}
        )

    for i, (name, kind, value) in enumerate(wanted):
        if name in by_name:
            var_id = by_name[name]
        else:
            var_id = f"tempVar{i}"
            updates.append(
                {
                    "action": "CREATE",
                    "id": var_id,
                    "name": name,
                    "variableCollectionId": collection_id,
                    "resolvedType": kind,
                }
            )
        values.append({"variableId": var_id, "modeId": "tempMode", "value": value})

    payload = {
        "variableCollections": creates,
        "variables": updates,
        "variableModeValues": values,
    }
    call(f"/files/{file_key}/variables", token, payload)
    print(f"Pushed {len(values)} values ({len(updates)} new) into the '{COLLECTION}' collection.")
    print("Record the version in ai-source/consumers.json so the linter can see it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
