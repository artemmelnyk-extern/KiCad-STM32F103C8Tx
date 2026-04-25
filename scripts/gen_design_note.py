#!/usr/bin/env python3
"""
gen_design_note.py — Generate a design note markdown file from a KiCad schematic.

Usage:
    python3 scripts/gen_design_note.py [--sch tproject.kicad_sch] [--out docs/design-notes/0001-Decoupling.md]

The script parses the KiCad S-expression schematic, extracts all placed components,
groups them by type, and writes a structured Markdown design note.
"""

import re
import subprocess
import argparse
from pathlib import Path
from datetime import date
from collections import defaultdict


# ---------------------------------------------------------------------------
# KiCad schematic parser
# ---------------------------------------------------------------------------

def parse_schematic(sch_path: Path) -> list[dict]:
    """
    Extract all placed symbol instances from a .kicad_sch file.
    Returns a list of dicts: {lib_id, reference, value}
    Skips power symbols (#PWR) and library symbol definitions (lib_sym block).
    """
    text = sch_path.read_text(encoding="utf-8")

    # Split into top-level (symbol ...) blocks (tab-indented at root level)
    # KiCad 6+ uses a single tab for top-level items inside the kicad_sch block
    symbol_blocks = re.split(r'\n\t\(symbol\b', text)

    components = []
    for block in symbol_blocks[1:]:  # first chunk is the file header
        lib_id  = _extract_property(block, "lib_id")
        ref     = _extract_property(block, 'property "Reference"')
        value   = _extract_property(block, 'property "Value"')

        if not lib_id or not ref or not value:
            continue
        if ref.startswith("#PWR") or ref.startswith("#FLG"):
            continue
        # skip library symbol definitions block
        if block.strip().startswith("(lib_sym"):
            continue

        components.append({
            "lib_id":    lib_id,
            "reference": ref,
            "value":     value,
        })

    return components


def _extract_property(block: str, key: str) -> str | None:
    """Pull the first quoted string value after 'key' in an S-expression block."""
    pattern = rf'\({re.escape(key)}\s+"([^"]+)"'
    m = re.search(pattern, block)
    return m.group(1) if m else None


# ---------------------------------------------------------------------------
# Grouping helpers
# ---------------------------------------------------------------------------

COMPONENT_CATEGORIES = {
    "MCU":          lambda c: "MCU_ST_STM32F1" in c["lib_id"] or "MCU_ST_STM32F0" in c["lib_id"],
    "Capacitor":    lambda c: c["lib_id"] in ("Device:C", "Device:C_Small", "Device:C_Polarized"),
    "FerriteBead":  lambda c: c["lib_id"] == "Device:FerriteBead",
    "Resistor":     lambda c: c["lib_id"] in ("Device:R", "Device:R_Small"),
    "Crystal":      lambda c: c["lib_id"] in ("Device:Crystal", "Device:Crystal_GND24"),
    "Inductor":     lambda c: c["lib_id"] == "Device:L",
    "LED":          lambda c: c["lib_id"] in ("Device:LED", "Device:LED_Small"),
    "Connector":    lambda c: "Connector" in c["lib_id"],
    "Regulator":    lambda c: any(k in c["lib_id"] for k in ("Regulator", "LDO")),
}


def categorise(components: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for comp in components:
        matched = False
        for category, predicate in COMPONENT_CATEGORIES.items():
            if predicate(comp):
                groups[category].append(comp)
                matched = True
                break
        if not matched:
            groups["Other"].append(comp)
    return dict(groups)


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def git_diff_stat(repo_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "diff", "--stat"],
            cwd=repo_root, capture_output=True, text=True
        )
        return result.stdout.strip() or "(no unstaged changes — working tree clean)"
    except FileNotFoundError:
        return "(git not available)"


def git_log_oneline(repo_root: Path, n: int = 5) -> str:
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", f"-{n}"],
            cwd=repo_root, capture_output=True, text=True
        )
        return result.stdout.strip() or "(no commits yet)"
    except FileNotFoundError:
        return "(git not available)"


# ---------------------------------------------------------------------------
# Markdown generation
# ---------------------------------------------------------------------------

DECOUPLING_DESCRIPTIONS = {
    "100n": "HF bypass / decoupling (1–100 MHz switching transients)",
    "10n":  "VHF bypass on VDDA",
    "1u":   "Low-frequency bulk filtering",
    "10u":  "Main bulk reservoir",
    "4.7u": "Bulk reservoir",
    "100u": "Large bulk reservoir",
}

FERRITE_DESCRIPTIONS = {
    "120R": "120 Ω @ 100 MHz — isolates VDDA from digital VDD noise",
    "600R": "600 Ω @ 100 MHz — strong isolation for sensitive analog supply",
}


def value_description(comp: dict) -> str:
    v = comp["value"]
    if comp["lib_id"] == "Device:FerriteBead":
        return FERRITE_DESCRIPTIONS.get(v, "Ferrite bead")
    if comp["lib_id"] in ("Device:C", "Device:C_Small"):
        return DECOUPLING_DESCRIPTIONS.get(v, "Capacitor")
    return ""


def render_component_table(comps: list[dict], header_cols: list[str]) -> str:
    rows = []
    for c in sorted(comps, key=lambda x: (x["reference"][0], int(re.sub(r'\D', '', x["reference"]) or 0))):
        desc = value_description(c)
        if "Description" in header_cols:
            rows.append(f"| {c['reference']} | {c['value']} | {desc} |")
        else:
            rows.append(f"| {c['reference']} | {c['value']} |")

    if "Description" in header_cols:
        header = "| Ref | Value | Description |"
        sep    = "|-----|-------|-------------|"
    else:
        header = "| Ref | Value |"
        sep    = "|-----|-------|"

    return "\n".join([header, sep] + rows)


def build_markdown(components: list[dict], sch_name: str, repo_root: Path,
                   note_number: str, title: str) -> str:
    today = date.today().isoformat()
    groups = categorise(components)

    mcu_section = ""
    if "MCU" in groups:
        mcu = groups["MCU"][0]
        mcu_section = f"""
## MCU

**{mcu['reference']}** — `{mcu['value']}` (`{mcu['lib_id']}`)

"""

    cap_section = ""
    if "Capacitor" in groups:
        cap_section = f"""
## Capacitors

{render_component_table(groups['Capacitor'], ['Ref', 'Value', 'Description'])}

"""

    ferrite_section = ""
    if "FerriteBead" in groups:
        ferrite_section = f"""
## Ferrite Beads

{render_component_table(groups['FerriteBead'], ['Ref', 'Value', 'Description'])}

"""

    other_sections = ""
    for category in ("Resistor", "Crystal", "Inductor", "LED", "Connector", "Regulator", "Other"):
        if category in groups:
            other_sections += f"""
## {category}s

{render_component_table(groups[category], ['Ref', 'Value'])}

"""

    diff_stat = git_diff_stat(repo_root)
    git_log   = git_log_oneline(repo_root)

    return f"""\
# {note_number} — {title}

**Date:** {today}
**Status:** Implemented
**Schematic:** `{sch_name}`

---
{mcu_section}{cap_section}{ferrite_section}{other_sections}
---

## Git Status at Time of Note

```
{diff_stat}
```

### Recent Commits

```
{git_log}
```

---

## References

- ST AN2834 — *How to achieve EMC compliance with STM32 microcontrollers*
  <https://www.st.com/resource/en/application_note/an2834.pdf>
- Datasheet: see `docs/datasheets/`
- ST Reference Manual RM0008
"""


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate a KiCad design note markdown file.")
    parser.add_argument("--sch",   default="tproject.kicad_sch",
                        help="Path to the .kicad_sch file (default: tproject.kicad_sch)")
    parser.add_argument("--out",   default="docs/design-notes/0001-Decoupling.md",
                        help="Output markdown path (default: docs/design-notes/0001-Decoupling.md)")
    parser.add_argument("--note",  default="0001",
                        help="Note number prefix (default: 0001)")
    parser.add_argument("--title", default="Power Decoupling Network",
                        help="Note title (default: 'Power Decoupling Network')")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    sch_path  = (repo_root / args.sch).resolve()
    out_path  = (repo_root / args.out).resolve()

    if not sch_path.exists():
        print(f"ERROR: schematic not found: {sch_path}")
        raise SystemExit(1)

    print(f"Parsing: {sch_path}")
    components = parse_schematic(sch_path)
    print(f"Found {len(components)} placed component(s): "
          f"{', '.join(sorted(set(c['reference'] for c in components)))}")

    md = build_markdown(components, sch_path.name, repo_root, args.note, args.title)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md, encoding="utf-8")
    print(f"Written: {out_path}")


if __name__ == "__main__":
    main()
