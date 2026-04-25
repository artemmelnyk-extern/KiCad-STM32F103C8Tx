# Documentation & Scripts Overview

This project uses a documentation-driven workflow where design notes serve as both human-readable documentation and machine-readable component sources for KiCad schematic generation.

---

## Folder Structure

```
docs/
├── README.md              ← this file
├── datasheets/            ← drop PDF datasheets here (MCU, crystals, passives, etc.)
└── design-notes/          ← design decision documents with machine-readable BOM tables
    └── 0001-Decoupling.md ← STM32F103C8T6 power decoupling network

scripts/
├── gen_design_note.py     ← .kicad_sch → markdown design note
└── design_note_to_kicad.py← markdown design note → .kicad_sch + .kicad_pro
```

---

## Scripts

### `scripts/gen_design_note.py`

Reads the KiCad schematic and generates a design note markdown file from the placed components.

**Usage:**
```bash
python3 scripts/gen_design_note.py
python3 scripts/gen_design_note.py --sch tproject.kicad_sch --out docs/design-notes/0001-Decoupling.md
```

**What it does:**
1. Parses `tproject.kicad_sch` (S-expression format, tab-indented)
2. Extracts all placed symbols — reference, value, footprint, lib_id, datasheet
3. Categorises components by reference prefix (U, C, R, L, FB, …)
4. Writes a structured markdown file with a BOM table and sections per category

**Direction:** `schematic → documentation`

---

### `scripts/design_note_to_kicad.py`

Reads all design note markdown files in `docs/design-notes/` and generates a fresh `tproject.kicad_sch` and `tproject.kicad_pro` from the BOM tables embedded in them.

**Usage:**
```bash
python3 scripts/design_note_to_kicad.py
python3 scripts/design_note_to_kicad.py --notes docs/design-notes --name tproject --dry-run
```

**What it does:**
1. Scans every `.md` file in `docs/design-notes/` for pipe tables with a `Ref` column
2. Parses columns: `Ref`, `Value`, `lib_id` (e.g. `Device:C`), `Footprint`, `Datasheet`
3. For each component, extracts the symbol definition from the KiCad system libraries at `/usr/share/kicad/symbols/` — including resolving `(extends ...)` alias chains (e.g. `STM32F103C8Tx` extends `STM32F103C_8-B_Tx`)
4. Places all components in a grid layout on the schematic sheet
5. Writes `tproject.kicad_sch` (S-expression) and `tproject.kicad_pro` (JSON)

**Direction:** `documentation → schematic`

**Known limitation:** components are placed unconnected. Wires, power symbols, and net labels must be added manually in KiCad after generation.

**Dry-run mode:** use `--dry-run` to preview parsed components without writing any files.

---

## Design Note Format

Design notes live in `docs/design-notes/` and follow the naming pattern `NNNN-Topic.md`.

For `design_note_to_kicad.py` to pick up components, a note must contain a pipe table with at minimum a `Ref` column. The full set of supported columns:

| Column | Required | Notes |
|--------|----------|-------|
| `Ref` | yes | Reference designator, e.g. `C1`, `U1`, `FB1` |
| `Value` | yes | Component value, e.g. `100n`, `STM32F103C8T6` |
| `lib_id` | recommended | Full KiCad lib ID: `LibName:SymName`. If omitted, inferred from ref prefix. |
| `Footprint` | recommended | Full footprint ID: `LibName:FpName` |
| `Datasheet` | optional | URL or `~` |

Example BOM table:

```markdown
## Bill of Materials (machine-readable)
| Ref | Value | lib_id | Footprint | Datasheet |
|-----|-------|--------|-----------|-----------|
| U1  | STM32F103C8T6 | MCU_ST_STM32F1:STM32F103C8Tx | Package_QFP:LQFP-48_7x7mm_P0.5mm | https://www.st.com/resource/en/datasheet/stm32f103c8.pdf |
| C1  | 100n | Device:C | Capacitor_SMD:C_0402_1005Metric | ~ |
| FB1 | 120R | Device:FerriteBead | Inductor_SMD:L_0402_1005Metric | ~ |
```

Duplicate references across multiple tables in the same run are silently skipped (first occurrence wins).

---

## Typical Workflow

### Starting a new design from scratch
1. Write `docs/design-notes/0001-MyTopic.md` with a BOM table
2. Run `python3 scripts/design_note_to_kicad.py`
3. Open `tproject.kicad_sch` in KiCad — components placed in grid
4. Add wires, power symbols, labels manually
5. Commit everything

### Updating documentation from an existing schematic
1. Run `python3 scripts/gen_design_note.py`
2. Review and edit the generated `docs/design-notes/0001-Decoupling.md`
3. Add design rationale, references, decision notes
4. Commit the updated documentation

### Validation
```bash
kicad-cli sch export python-bom tproject.kicad_sch --output /tmp/bom_check.csv
```
A successful export confirms the schematic loads correctly and all symbols resolve.
