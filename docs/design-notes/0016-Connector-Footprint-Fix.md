# 0016 — Connector Footprint Fix: Conn_01x04 (J2, J3, J4)

**Date:** 2026-05-02
**Status:** Implemented
**References:** Design note 0005 (Power Supply and Connectors), design note 0007 (Footprint Assignment); git commit `3de90ea`

---

## Summary

All three 4-pin single-row connectors (J2, J3, J4) were assigned the wrong footprint
during the footprint assignment step (0007). They carried a 1.00 mm pitch SMD footprint
instead of the correct 2.54 mm pitch through-hole footprint. This caused the PCB 3D
view to render tiny SMD land patterns in place of standard pin headers.

| Ref | Value        | Wrong footprint (before) | Correct footprint (after) |
|-----|--------------|--------------------------|---------------------------|
| J2  | Conn_01x04   | `Connector_PinHeader_1.00mm:PinHeader_1x04_P1.00mm_Vertical_SMD_Pin1Right` | `Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical` |
| J3  | Conn_01x04   | `Connector_PinHeader_1.00mm:PinHeader_1x04_P1.00mm_Vertical_SMD_Pin1Right` | `Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical` |
| J4  | Conn_01x04   | `Connector_PinHeader_1.00mm:PinHeader_1x04_P1.00mm_Vertical_SMD_Pin1Right` | `Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical` |

---

## 1 — Root Cause

During footprint assignment the library browser returned the 1.00 mm SMD pin header as
the first match for `PinHeader_1x04`. The correct 2.54 mm through-hole variant sits in a
different library (`Connector_PinHeader_2.54mm`) and was not selected. Both libraries
exist in KiCad 9's standard footprint library set, but KiCad 9 changed the ordering and
default display of search results compared to earlier KiCad versions, making the SMD
variant appear first.

---

## 2 — Correct Footprint Specification

| Parameter      | Value |
|----------------|-------|
| Library        | `Connector_PinHeader_2.54mm` |
| Footprint name | `PinHeader_1x04_P2.54mm_Vertical` |
| Pitch          | 2.54 mm (0.1 in) |
| Rows × Pins    | 1 × 4 |
| Package style  | Through-hole, vertical |
| Pad drill      | 1.0 mm nominal |
| Pad size       | 1.7 × 1.7 mm nominal |

---

## 3 — Fix Applied

The `Footprint` property was corrected in `tproject.kicad_sch` for all three connector
instances. No net connections, pin assignments, or component values were altered. The PCB
layout requires an **Update PCB from Schematic** pass to replace the SMD land patterns
with the 2.54 mm through-hole footprints and reposition pads accordingly.

### Steps to update PCB after this change

1. Open `tproject.kicad_pcb` in KiCad PCB editor.
2. Run **Tools → Update PCB from Schematic…** (or press `F8`).
3. Confirm the three footprint changes for J2, J3, J4.
4. Re-place J2, J3, J4 at their intended board positions (see design note 0012 for
   reference positions).
5. Re-run DRC to verify no clearance violations are introduced.
