# 0019 — Silkscreen

**Date:** 2026-05-03
**Status:** Implemented
**References:** Design notes 0008 (PCB setup), 0018 (power routing); IPC-7351C §8 (silkscreen guidelines)

---

## Summary

Final silkscreen pass adding connector function labels on F.SilkS, board identity
information on B.SilkS, one reference designator repositioning, and a zone fill
operation that computed the copper pour polygons for the three power zones defined
in note 0018.

| Metric | Value |
|--------|-------|
| File changed | `tproject.kicad_pcb` |
| New `gr_text` labels | 9 |
| F.SilkS labels | 6 |
| B.SilkS labels | 3 |
| Reference repositioned | 1 (J4) |
| Zone fills computed | 3 |

---

## 1 — Front Silkscreen Labels (F.SilkS)

Six functional labels added adjacent to connectors and indicators to aid assembly
and field use. All labels use font size 1 × 1 mm, stroke thickness 0.1 mm, justified
left-bottom, except SWD which uses 1 × 1.25 mm height for emphasis.

| Text | Position (x, y) mm | Component labelled | Notes |
|------|--------------------|--------------------|-------|
| `BOOT` | (37.5, 70.5) | SW1 SPDT | Identifies BOOT0 switch |
| `UART` | (45.0, 53.5) | J3 Conn_01x04 | USART1 header |
| `I2C` | (46.5, 81.5) | J4 Conn_01x04 | I2C2 header |
| `USB` | (70.75, 60.25) | J1 USB Micro-B | USB connector area |
| `ON` | (72.25, 78.25) | D1 LED | Power-on LED indicator |
| `SWD` | (59.75, 53.5) | J2 Conn_01x04 | SWD debug header (1×1.25 mm font) |

---

## 2 — Back Silkscreen Labels (B.SilkS)

Three board identity labels placed on the back copper side. All use font size 1 × 1 mm,
stroke thickness 0.1 mm, mirrored (correct orientation when viewed from back).

| Text | Position (x, y) mm | Purpose |
|------|--------------------|---------| 
| `1.0.0` | (42.0, 75.25) | Board hardware revision |
| `3May26` | (43.5, 77.25) | Release date |
| `itma.tech` | (44.0, 79.0) | Project / manufacturer identifier |

---

## 3 — Reference Designator Repositioning

One reference label was adjusted to avoid overlap with silkscreen text and copper pours.

| Ref | Old position (relative, rot°) | New position (relative, rot°) | Reason |
|-----|-------------------------------|-------------------------------|--------|
| J4 | (0, −2.38, 90°) | (−0.5, −2.67, 180°) | Rotated 180° and shifted slightly to clear adjacent I2C label and copper fill boundary |

---

## 4 — Zone Fill Computation

The three copper pour zones defined in note 0018 were filled for the first time in this
step (`Edit → Fill All Zones` / `B` shortcut). This produced `filled_polygon` entries
and updated each zone's `fill` attribute from unset to `fill yes`.

| Zone | Net | Fill status change | Filled polygon vertices |
|------|-----|--------------------|------------------------|
| VBUS pour | VBUS (net 2) | `(fill …)` → `(fill yes …)` | ~40 pts — narrow polygon around LDO input pads |
| +3.3V pour | +3.3V (net 3) | `(fill …)` → `(fill yes yes …)` | ~35 pts — wraps LDO output and via fence |
| GND pour | GND (net 1) | `(fill …)` → `(fill yes …)` | ~100 pts — largest zone, covers MCU VSS cluster |

The board outline keepout zone (net 0) also had its filled polygon updated due to the new
copper zones displacing its inner boundary near the mounting holes.

---

## 5 — Rationale

### Connector labels

Unlabelled 4-pin headers are ambiguous in the field; a one-word silk label identifies
function without needing a schematic. Placed outside the component courtyard to comply
with IPC-7351C clearance requirements.

### Back-side identity marks

Version, date, and domain placed on B.SilkS keeps the front face uncluttered while
providing traceability information visible during PCB inspection and rework.

### Zone fill timing

Zones were left unfilled during routing (notes 0015–0018) to keep the ratsnest visible
and avoid DRC artefacts from partially routed nets. Filling at this final stage gives the
correct copper coverage with all signal and power routes complete.
