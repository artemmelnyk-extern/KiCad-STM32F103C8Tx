# 0014 — Board Outline and Mounting Holes

**Date:** 2026-04-29
**Status:** Implemented
**References:** Design notes 0008 (PCB setup/rules), 0013 (power supply placement); M2 screw specification ISO 7380; IPC-2221A §12.1 (keepout around mounting hardware)

---

## Summary

The board outline (Edge.Cuts) was drawn and four M2 non-plated through-hole mounting
holes (H1–H4) were added at the corners. Eight components received minor position
adjustments to maintain clearance from the board edge and mounting-hole keepouts.
The schematic was updated with four `Mechanical:MountingHole` symbols (excluded from
BOM, included on board, not DNP).

The resulting PCB footprint is **38.54 mm × 33.17 mm** — a compact single-board
format suitable for direct mounting into an enclosure or onto a DIN-rail bracket with
standard M2 hardware.

---

## 1 — Board Outline (Edge.Cuts)

### 1.1 Geometry

The outline is a rectangle with four rounded corners, defined by four straight lines and
four quarter-circle arcs on the `Edge.Cuts` layer (line width 0.05 mm).

| Segment | Start (x, y) mm | End (x, y) mm | Type |
|---------|-----------------|---------------|------|
| Left edge   | (36.290, 54.750) | (36.290, 82.500) | Line |
| Top edge    | (39.000, 52.040) | (72.078, 52.086) | Line |
| Right edge  | (74.826, 54.750) | (74.826, 82.500) | Line |
| Bottom edge | (39.000, 85.210) | (72.116, 85.210) | Line |
| Top-left corner  | arc: (36.290, 54.750) → mid (37.084, 52.834) → (39.000, 52.040) | — | Arc r≈2.71 mm |
| Top-right corner | arc: (72.078, 52.086) → mid (74.016, 52.836) → (74.826, 54.750) | — | Arc r≈2.71 mm |
| Bottom-left corner  | arc: (39.000, 85.210) → mid (37.084, 84.416) → (36.290, 82.500) | — | Arc r≈2.71 mm |
| Bottom-right corner | arc: (74.826, 82.500) → mid (74.033, 84.416) → (72.116, 85.210) | — | Arc r≈2.71 mm |

### 1.2 Board Dimensions

| Parameter | Value |
|-----------|-------|
| Width (X) | 38.54 mm (74.826 − 36.290) |
| Height (Y) | 33.17 mm (85.210 − 52.040) |
| Corner radius | ≈ 2.71 mm |
| Board area | ≈ 12.8 cm² |
| Outline layer | Edge.Cuts |
| Outline width | 0.05 mm |

### 1.3 ASCII Footprint Map

```
X →   36.3  39    47   52.1   56    63    70   72.1  74.8
      |     |     |     |      |     |     |     |     |
52  --+arc  H2    .     .      .     .     .    H3  arc+--
      |     .    R2    J3      U1    .    J2     .     |
56    |    SW1    .     .      .     .     .     .     |
      |     .    C3     .      .     .    R1     .     |
63    |     .     .     .      .     .     .     .     |
      |     .    C8     .      .    D1     .     .     |
67    |     .    Y1     .      U1    .    J1     .     |
      |     .    C4     .      .    C6     .     .     |
72    |     .    FB1    .      .    C1    R1     .     |
      |     .     .     .      .   U2     C2     .     |
79    |     .     .     .      .    .     .      .     |
82  --+arc  H1    .     .      .    .     .     H4  arc+--
      |     |     |     |      |     |     |     |     |
```

*(Y increases downward. Positions approximate.)*

---

## 2 — Mounting Holes (H1–H4)

### 2.1 Footprint

`MountingHole:MountingHole_2.2mm_M2` — non-plated through-hole (NPTH), no annular copper
ring. Drill diameter: 2.2 mm. Courtyard circle: 2.45 mm radius.

Attributes: `exclude_from_pos_files`, `exclude_from_bom`.

### 2.2 Positions

| Ref | X (mm) | Y (mm) | Location |
|-----|--------|--------|----------|
| H1  | 39.500 | 82.500 | Bottom-left corner |
| H2  | 39.000 | 54.750 | Top-left corner |
| H3  | 72.161 | 54.750 | Top-right corner |
| H4  | 72.000 | 82.250 | Bottom-right corner |

### 2.3 Corner Inset

Each hole is inset ≈ 2.7 mm from the board edge tangent lines — consistent with the
corner arc radius. This positions the hole centre at the arc centre, so the hole
courtyard (2.45 mm radius) clears the board edge by ≈ 0.26 mm.

### 2.4 Schematic Symbols

Four `Mechanical:MountingHole` symbols were added in the schematic under the label
**"Mounting Holes"** (`in_bom: no`, `on_board: yes`, `dnp: no`). Footprint assigned:
`MountingHole:MountingHole_2.2mm_M2`.

---

## 3 — Component Position Adjustments

Eight components were repositioned to maintain edge clearance and clear mounting-hole
courtyards. No electrical connections changed.

| Ref | Value | Old (x, y) rot° | New (x, y) rot° | Reason |
|-----|-------|-----------------|-----------------|--------|
| J2  | Conn_01x04 | (59.375, 54.000) r=0  | **(59.875, 56.000) r=0**  | Moved 2 mm south — was overlapping top Edge.Cuts (Y=52) |
| J3  | SWD Conn_01x04 | (52.125, 54.000) r=0  | **(53.625, 55.000) r=0**  | Moved 1 mm south, 1.5 mm right — same top-edge clearance |
| SW1 | SW_SPDT PCM12 | (40.430, 56.650) r=−90 | **(38.830, 63.750) r=−90** | Moved 7.1 mm south, 1.6 mm left — centred on left edge for panel-mount lever; clears H2 (54.75) and H1 (82.5) keepouts |
| R2  | 10k BOOT0 R_0402 | (47.240, 57.250) r=0  | **(47.990, 57.250) r=0**  | 0.75 mm right — minor clearance from J3 adjusted position |
| U2  | AMS1117-3.3 SOT-223 | (65.500, 78.750) r=−90 | **(63.000, 79.500) r=−90** | 2.5 mm left, 0.75 mm south — clear right Edge.Cuts at X=74.8 |
| C2  | 22 µF C_0805 | (71.250, 79.200) r=90 | **(68.750, 78.050) r=90** | 2.5 mm left, 1.15 mm up — pushed left to keep within X<74.8 |
| D1  | RED LED 0603 | (73.750, 78.000) r=90 | **(73.250, 73.963) r=90** | 4 mm up, 0.5 mm left — moved away from H4 keepout |
| R1  | 1.5 kΩ R_0402 | (70.750, 73.240) r=90 | **(69.750, 73.240) r=90** | 1 mm left — minor clearance adjustment |

### 3.1 Key Move: SW1 to Left Edge

SW1 (PCM12 SPDT) was moved from its interior position (40.43, 56.65) to **(38.83, 63.75)**,
placing the switch body 2.5 mm from the left board edge (X=36.29). At −90° rotation the
actuator lever faces left, protruding through a slot in the enclosure wall. This is the
standard panel-mount orientation for the PCM12. The new Y=63.75 centres SW1 between
the two left-side mounting holes (H2 at Y=54.75 and H1 at Y=82.5).

---

## 4 — Unchanged Components

C1, C3–C13, FB1, J1, J4, R3, R4, R5, U1, Y1 — positions unchanged from design
notes 0009–0013.

---

## 5 — Files Changed

| File | Change |
|------|--------|
| `tproject.kicad_pcb` | Edge.Cuts outline (8 segments/arcs), 4× MountingHole footprints, 8 adjusted component positions |
| `tproject.kicad_sch` | `Mechanical:MountingHole` library symbol added; 4× H1–H4 instances placed; "Mounting Holes" section label added |
| `tproject.kicad_pro` | Project metadata update |

---

## 6 — Next Steps

1. **DRC** — run Design Rule Check against 0.2 mm clearance and 0.2 mm track rules.
   Verify all component courtyard clearances to board edge and mounting holes.
2. **Copper pours** — define GND pour on B.Cu and +3.3 V pour on F.Cu inner area.
3. **Route power rails** — VBUS from J1 to U2 VI; +3.3 V from U2 VO to MCU VDD network.
4. **Route USB differential pair** — J1 to R3 to U1 PA11/PA12 (impedance-controlled, 90 Ω diff).
5. **Silkscreen** — add board title, revision, and pin-1 indicators.
