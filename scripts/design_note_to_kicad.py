#!/usr/bin/env python3
"""
design_note_to_kicad.py — Generate tproject.kicad_sch and tproject.kicad_pro
from design note markdown files in docs/design-notes/.

Usage:
    python3 scripts/design_note_to_kicad.py [--notes docs/design-notes] [--name tproject]

The script:
  1. Parses all markdown tables in design notes to build a component BOM
     (Reference | Value | lib_id | Footprint | Datasheet columns supported)
  2. Looks up each component's symbol definition from KiCad system libraries
  3. Generates a valid .kicad_sch with components placed in a grid layout
  4. Generates a minimal .kicad_pro

LIMITATIONS:
  - No wires or net connections are generated (components are placed unconnected)
  - Layout is auto-grid, not optimised for readability
  - Re-run KiCad ERC after opening to check connectivity
"""

import re
import json
import uuid
import argparse
from pathlib import Path
from datetime import date


KICAD_SYM_DIRS = [
    Path("/usr/share/kicad/symbols"),
    Path("/usr/local/share/kicad/symbols"),
    Path.home() / ".local/share/kicad/8.0/symbols",
    Path.home() / ".local/share/kicad/9.0/symbols",
]

# Grid spacing between components (mm)
GRID_X = 30.0
GRID_Y = 30.0
ORIGIN_X = 50.0
ORIGIN_Y = 50.0
COLS = 6  # components per row before wrapping


# ---------------------------------------------------------------------------
# Markdown BOM parser
# ---------------------------------------------------------------------------

# Map column headers (lowercase) to canonical field names
COLUMN_ALIASES = {
    "ref":          "reference",
    "reference":    "reference",
    "designator":   "reference",
    "value":        "value",
    "val":          "value",
    "lib_id":       "lib_id",
    "lib id":       "lib_id",
    "library":      "lib_id",
    "footprint":    "footprint",
    "fp":           "footprint",
    "datasheet":    "datasheet",
    "ds":           "datasheet",
    "description":  "description",
    "desc":         "description",
    "purpose":      "description",
}

# If no lib_id column in the note, infer from reference prefix
REF_TO_LIB = {
    "C":  "Device:C",
    "R":  "Device:R",
    "L":  "Device:L",
    "FB": "Device:FerriteBead",
    "Y":  "Device:Crystal",
    "U":  None,   # can't infer MCU, must be in note
    "D":  "Device:LED",
    "J":  "Connector_Generic:Conn_01x02",
    "SW": "Switch:SW_Push",
    "Q":  "Device:Q_NPN_BCE",
    "TP": "Device:TestPoint",
}


def parse_markdown_tables(md_path: Path) -> list[dict]:
    """
    Parse all pipe-table blocks from a markdown file.
    Returns a list of row dicts with canonical field names.
    """
    text = md_path.read_text(encoding="utf-8")
    components = []

    # Find all markdown tables (contiguous lines containing |)
    table_blocks = re.findall(r'(?m)((?:^\|.+\|\s*\n){2,})', text)

    for block in table_blocks:
        rows = [line.strip() for line in block.strip().splitlines() if line.strip()]
        if len(rows) < 3:
            continue  # need header + separator + at least one data row

        # Parse header
        header_row = rows[0]
        sep_row    = rows[1]

        # Validate it's actually a table separator
        if not re.match(r'^\|[-| :]+\|$', sep_row):
            continue

        headers = [h.strip().lower() for h in header_row.strip('|').split('|')]
        col_map = {}  # index -> canonical field name
        for i, h in enumerate(headers):
            canonical = COLUMN_ALIASES.get(h)
            if canonical:
                col_map[i] = canonical

        if "reference" not in col_map.values():
            continue  # no reference column — not a BOM table

        for row in rows[2:]:
            cells = [c.strip() for c in row.strip('|').split('|')]
            if len(cells) < len(headers):
                continue

            comp: dict = {}
            for i, field in col_map.items():
                if i < len(cells):
                    comp[field] = cells[i]

            ref = comp.get("reference", "")
            if not ref or ref.startswith("#"):
                continue

            # Infer lib_id from reference prefix if not provided
            if not comp.get("lib_id"):
                prefix = re.match(r'[A-Za-z]+', ref)
                if prefix:
                    inferred = REF_TO_LIB.get(prefix.group().upper())
                    if inferred:
                        comp["lib_id"] = inferred

            if not comp.get("lib_id"):
                print(f"  WARNING: cannot determine lib_id for {ref} — skipping")
                continue

            components.append(comp)

    return components


# ---------------------------------------------------------------------------
# KiCad symbol library reader
# ---------------------------------------------------------------------------

def find_sym_file(lib_name: str) -> Path | None:
    """Find a .kicad_sym file by library name (e.g. 'Device', 'power')."""
    filename = f"{lib_name}.kicad_sym"
    for sym_dir in KICAD_SYM_DIRS:
        candidate = sym_dir / filename
        if candidate.exists():
            return candidate
    return None


def _read_raw_symbol(text: str, sym_name: str) -> str | None:
    """
    Extract the raw S-expression block for a symbol from library text.
    Returns the block starting at \t(symbol "name" and ending at its closing ).
    """
    pattern = rf'\(symbol\s+"{re.escape(sym_name)}"[\s\n]'
    m = re.search(pattern, text)
    if not m:
        return None
    # Rewind to start of line
    line_start = text.rfind('\n', 0, m.start()) + 1
    start = line_start
    depth = 0
    for i, ch in enumerate(text[start:]):
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
            if depth == 0:
                return text[start:start + i + 1]
    return None


def _extract_properties(block: str) -> dict[str, str]:
    """Return {prop_name: full_property_block} from a symbol S-expression block."""
    props = {}
    for m in re.finditer(r'\(property\s+"([^"]+)"[\s\S]+?(?=\n\t+\(|\n\t+\)|\Z)', block):
        props[m.group(1)] = m.group(0)
    return props


def extract_lib_symbol(lib_id: str) -> str | None:
    """
    Extract a symbol block from the .kicad_sym file and reformat it for
    embedding inside a schematic's (lib_symbols ...) section.

    Handles alias symbols that use (extends "BaseName") by fetching the full
    base symbol geometry and applying the alias's property overrides.
    Normalises the symbol name to "LibName:SymName" and re-indents with +2 tabs.
    """
    if ":" not in lib_id:
        return None
    lib_name, sym_name = lib_id.split(":", 1)

    sym_file = find_sym_file(lib_name)
    if not sym_file:
        print(f"  WARNING: symbol library not found: {lib_name}")
        return None

    text = sym_file.read_text(encoding="utf-8")

    raw = _read_raw_symbol(text, sym_name)
    if not raw:
        print(f"  WARNING: symbol '{sym_name}' not found in {sym_file.name}")
        return None

    # Detect (extends "BaseName") — if present, use the base symbol's geometry
    extends_m = re.search(r'\(extends\s+"([^"]+)"', raw)
    if extends_m:
        base_name = extends_m.group(1)
        base_raw = _read_raw_symbol(text, base_name)
        if not base_raw:
            print(f"  WARNING: base symbol '{base_name}' not found — using alias stub")
        else:
            # Apply property overrides from the alias onto the base symbol
            alias_props = {}
            for m in re.finditer(
                    r'(\(property\s+"([^"]+)"[^\n]*\n(?:\t[^\n]*\n)*\t\t\))',
                    raw, re.MULTILINE):
                alias_props[m.group(2)] = m.group(1)

            def replace_prop(match):
                pname = match.group(2)
                if pname in alias_props:
                    return alias_props[pname]
                return match.group(0)

            merged = re.sub(
                r'(\(property\s+"([^"]+)"[^\n]*\n(?:\t[^\n]*\n)*\t\t\))',
                replace_prop,
                base_raw,
                flags=re.MULTILINE
            )
            raw = merged

    # Rename the symbol to full "LibName:SymName"
    raw = re.sub(
        rf'(\(symbol\s+)"{re.escape(sym_name)}"',
        rf'\1"{lib_id}"',
        raw, count=1
    )
    # Also rename the base symbol name if extends was resolved
    if extends_m:
        raw = re.sub(
            rf'(\(symbol\s+)"{re.escape(extends_m.group(1))}"',
            rf'\1"{lib_id}"',
            raw, count=1
        )

    # Re-indent: strip one leading tab per line (top-level in .kicad_sym)
    # then add two tabs to nest inside (lib_symbols ...)
    lines = raw.splitlines()
    result = []
    for line in lines:
        stripped = line[1:] if line.startswith('\t') else line
        result.append('\t\t' + stripped if stripped.strip() else '')
    return "\n".join(result)


# ---------------------------------------------------------------------------
# UUID helpers
# ---------------------------------------------------------------------------

def new_uuid() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# S-expression schematic builder
# ---------------------------------------------------------------------------

HIDDEN_PROP = '''\
\t\t\t\t(effects
\t\t\t\t\t(font
\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t)
\t\t\t\t\t(hide yes)
\t\t\t\t)'''

VISIBLE_PROP_LEFT = '''\
\t\t\t\t(effects
\t\t\t\t\t(font
\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t)
\t\t\t\t\t(justify left)
\t\t\t\t)'''

VISIBLE_PROP = '''\
\t\t\t\t(effects
\t\t\t\t\t(font
\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t)
\t\t\t\t)'''


def build_property(name: str, value: str, x: float, y: float,
                   angle: int = 0, hidden: bool = False, justify_left: bool = False) -> str:
    effects = HIDDEN_PROP if hidden else (VISIBLE_PROP_LEFT if justify_left else VISIBLE_PROP)
    return (
        f'\t\t(property "{name}" "{value}"\n'
        f'\t\t\t(at {x:.4f} {y:.4f} {angle})\n'
        f'{effects}\n'
        f'\t\t)'
    )


def build_symbol_instance(comp: dict, x: float, y: float,
                           project_name: str, sheet_uuid: str) -> str:
    """Generate a placed symbol S-expression block."""
    ref      = comp["reference"]
    value    = comp["value"]
    lib_id   = comp["lib_id"]
    footprint = comp.get("footprint", "")
    datasheet = comp.get("datasheet", "~")
    sym_uuid = new_uuid()

    # Infer number of pins for pin uuid entries (simplified: just 2 for passives)
    pin_lines = ""
    if lib_id in ("Device:C", "Device:C_Small", "Device:R", "Device:R_Small",
                  "Device:L", "Device:FerriteBead"):
        pin_lines = (
            f'\t\t(pin "1"\n\t\t\t(uuid "{new_uuid()}")\n\t\t)\n'
            f'\t\t(pin "2"\n\t\t\t(uuid "{new_uuid()}")\n\t\t)\n'
        )
    elif "Crystal" in lib_id:
        pin_lines = (
            f'\t\t(pin "1"\n\t\t\t(uuid "{new_uuid()}")\n\t\t)\n'
            f'\t\t(pin "2"\n\t\t\t(uuid "{new_uuid()}")\n\t\t)\n'
            f'\t\t(pin "3"\n\t\t\t(uuid "{new_uuid()}")\n\t\t)\n'
            f'\t\t(pin "4"\n\t\t\t(uuid "{new_uuid()}")\n\t\t)\n'
        )

    ref_prop   = build_property("Reference", ref,  x + 3.81, y - 1.27, justify_left=True)
    value_prop = build_property("Value",     value, x + 3.81, y + 1.27, justify_left=True)
    fp_prop    = build_property("Footprint", footprint, x, y, hidden=True)
    ds_prop    = build_property("Datasheet", datasheet, x, y, hidden=True)
    desc_prop  = build_property("Description", comp.get("description", ""), x, y, hidden=True)

    return (
        f'\t(symbol\n'
        f'\t\t(lib_id "{lib_id}")\n'
        f'\t\t(at {x:.4f} {y:.4f} 0)\n'
        f'\t\t(unit 1)\n'
        f'\t\t(exclude_from_sim no)\n'
        f'\t\t(in_bom yes)\n'
        f'\t\t(on_board yes)\n'
        f'\t\t(dnp no)\n'
        f'\t\t(fields_autoplaced yes)\n'
        f'\t\t(uuid "{sym_uuid}")\n'
        f'{ref_prop}\n'
        f'{value_prop}\n'
        f'{fp_prop}\n'
        f'{ds_prop}\n'
        f'{desc_prop}\n'
        f'{pin_lines}'
        f'\t\t(instances\n'
        f'\t\t\t(project "{project_name}"\n'
        f'\t\t\t\t(path "/{sheet_uuid}"\n'
        f'\t\t\t\t\t(reference "{ref}")\n'
        f'\t\t\t\t\t(unit 1)\n'
        f'\t\t\t\t)\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        f'\t)'
    )


def build_schematic(components: list[dict], project_name: str) -> str:
    sheet_uuid = new_uuid()

    # Collect unique lib_ids and extract their symbol definitions
    lib_ids_seen: dict[str, str] = {}  # lib_id -> symbol block
    for comp in components:
        lid = comp["lib_id"]
        if lid not in lib_ids_seen:
            block = extract_lib_symbol(lid)
            if block:
                lib_ids_seen[lid] = block
            else:
                lib_ids_seen[lid] = f'\t\t; WARNING: symbol "{lid}" not found in system libraries'

    lib_symbols_content = "\n".join(lib_ids_seen.values())

    # Place components in a grid
    symbol_blocks = []
    for i, comp in enumerate(components):
        col = i % COLS
        row = i // COLS
        x = ORIGIN_X + col * GRID_X
        y = ORIGIN_Y + row * GRID_Y
        block = build_symbol_instance(comp, x, y, project_name, sheet_uuid)
        symbol_blocks.append(block)

    symbols_content = "\n".join(symbol_blocks)

    today = date.today().isoformat()

    return (
        f'(kicad_sch\n'
        f'\t(version 20250114)\n'
        f'\t(generator "design_note_to_kicad.py")\n'
        f'\t(generator_version "1.0")\n'
        f'\t(uuid "{sheet_uuid}")\n'
        f'\t(paper "A4")\n'
        f'\t(lib_symbols\n'
        f'{lib_symbols_content}\n'
        f'\t)\n'
        f'{symbols_content}\n'
        f')'
    )


# ---------------------------------------------------------------------------
# Project file generator
# ---------------------------------------------------------------------------

def build_project(project_name: str, sheet_uuid: str | None = None) -> str:
    """Generate a minimal .kicad_pro JSON file."""
    # Re-read the schematic to get the sheet uuid if not provided
    today = date.today().isoformat()
    project = {
        "board": {
            "3dviewports": [],
            "design_settings": {"defaults": {}, "diff_pair_dimensions": [],
                                 "drc_exclusions": [], "rules": {},
                                 "track_widths": [], "via_dimensions": []},
            "ipc2581": {"dist": "", "distpn": "", "internal_id": "", "mfg": "", "mpn": ""},
            "layer_pairs": [],
            "layer_presets": [],
            "viewports": []
        },
        "boards": [],
        "cvpcb": {"equivalence_files": []},
        "libraries": {"pinned_footprint_libs": [], "pinned_symbol_libs": []},
        "meta": {"filename": f"{project_name}.kicad_pro", "version": 3},
        "net_settings": {
            "classes": [{"bus_width": 12, "clearance": 0.2, "diff_pair_gap": 0.25,
                         "diff_pair_via_gap": 0.25, "diff_pair_width": 0.2,
                         "line_style": 0, "microvia_diameter": 0.3,
                         "microvia_drill": 0.1, "name": "Default",
                         "pcb_color": "rgba(0, 0, 0, 0.000)", "priority": 2147483647,
                         "schematic_color": "rgba(0, 0, 0, 0.000)", "width": 0.25}],
            "meta": {"version": 3},
            "net_colors": None
        },
        "pcbnew": {
            "last_paths": {"gencad": "", "idf": "", "netlist": "", "plot": "",
                           "pos_files": "", "specctra_dsn": "", "step": "",
                           "svg": "", "vrml": ""},
            "page_layout_descr_file": ""
        },
        "schematic": {
            "annotate_start_num": 0,
            "drawing": {"default_bus_thickness": 12.0, "default_junction_size": 36.0,
                        "default_line_thickness": 6.0, "default_text_size": 50.0,
                        "default_wire_thickness": 6.0, "field_names": [],
                        "intersheets_ref_own_page": False, "intersheets_ref_prefix": "",
                        "intersheets_ref_short": False, "intersheets_ref_show": False,
                        "intersheets_ref_suffix": "", "junction_size_choice": 3,
                        "label_size_ratio": 0.375, "operating_point_overlay_i_precision": 3,
                        "operating_point_overlay_i_range": "~A",
                        "operating_point_overlay_v_precision": 3,
                        "operating_point_overlay_v_range": "~V",
                        "overbar_offset_ratio": 1.23, "pin_symbol_size": 25.0,
                        "text_offset_ratio": 0.15},
            "legacy_lib_dir": "",
            "legacy_lib_list": [],
            "meta": {"version": 1},
            "net_format_name": "",
            "page_layout_descr_file": "",
            "plot_directory": "",
            "space_save_all_events": True,
            "spice_current_sheet_as_root": False,
            "spice_external_command": "spice \"%I\"",
            "spice_model_current_sheet_as_root": True,
            "spice_save_all_currents": False,
            "spice_save_all_dissipations": False,
            "spice_save_all_voltages": False,
            "subpart_first_id": 65,
            "subpart_id_separator": 0
        },
        "sheets": [[sheet_uuid or new_uuid(), "Root"]],
        "text_variables": {}
    }
    return json.dumps(project, indent=2)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate KiCad schematic and project from design note markdown files.")
    parser.add_argument("--notes", default="docs/design-notes",
                        help="Folder containing design note .md files (default: docs/design-notes)")
    parser.add_argument("--name",  default="tproject",
                        help="Project name / output file base name (default: tproject)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Parse and print BOM only, do not write files")
    args = parser.parse_args()

    repo_root  = Path(__file__).resolve().parent.parent
    notes_dir  = (repo_root / args.notes).resolve()
    sch_out    = repo_root / f"{args.name}.kicad_sch"
    pro_out    = repo_root / f"{args.name}.kicad_pro"

    if not notes_dir.exists():
        print(f"ERROR: design notes folder not found: {notes_dir}")
        raise SystemExit(1)

    # Collect all design notes
    md_files = sorted(notes_dir.glob("*.md"))
    if not md_files:
        print(f"ERROR: no .md files found in {notes_dir}")
        raise SystemExit(1)

    print(f"Reading design notes from: {notes_dir}")
    all_components: list[dict] = []
    seen_refs: set[str] = set()

    for md in md_files:
        print(f"  Parsing: {md.name}")
        comps = parse_markdown_tables(md)
        for comp in comps:
            ref = comp["reference"]
            if ref in seen_refs:
                print(f"    SKIP duplicate reference: {ref}")
                continue
            seen_refs.add(ref)
            all_components.append(comp)
            print(f"    + {ref:6s}  {comp.get('value',''):8s}  {comp['lib_id']}")

    if not all_components:
        print("ERROR: no components found in design notes. "
              "Ensure BOM tables have a 'Ref' or 'Reference' column.")
        raise SystemExit(1)

    print(f"\nTotal components: {len(all_components)}")

    if args.dry_run:
        print("Dry run — no files written.")
        return

    print(f"\nGenerating: {sch_out}")
    sch_content = build_schematic(all_components, args.name)
    sch_out.write_text(sch_content, encoding="utf-8")

    # Extract sheet UUID from generated schematic for .kicad_pro
    m = re.search(r'\(uuid\s+"([^"]+)"', sch_content)
    sheet_uuid = m.group(1) if m else new_uuid()

    print(f"Generating: {pro_out}")
    pro_content = build_project(args.name, sheet_uuid)
    pro_out.write_text(pro_content, encoding="utf-8")

    print("\nDone. Open in KiCad — components are placed in a grid, unconnected.")
    print("Next steps:")
    print("  1. Run ERC to see missing connections")
    print("  2. Add wires and power symbols manually")
    print("  3. Assign footprints if not already in the design note")


if __name__ == "__main__":
    main()
