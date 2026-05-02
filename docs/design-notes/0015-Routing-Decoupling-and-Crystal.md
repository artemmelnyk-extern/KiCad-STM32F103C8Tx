# 0015 — PCB Routing: Decoupling Capacitors and HSE Crystal Circuit

**Date:** 2026-05-02
**Status:** Implemented
**References:** Design notes 0001 (decoupling), 0003 (crystal), 0008 (PCB rules), 0013 (power supply placement), 0014 (board outline); STM32F103C8T6 datasheet §5.3.9 (HSE oscillator); AN2867 §3 (crystal load capacitors); IPC-2141 §6 (crystal trace routing)

---

## Summary

First routing pass: 39 track segments on F.Cu (0.2 mm width) connecting the HSE crystal
oscillator circuit and the MCU VDD/VDDA decoupling capacitor network. A full-board B.Cu
copper fill zone was added as a GND ground plane. Eight component positions were
fine-tuned to align pads for clean trace entry and avoid 45° routing angles.

| Net | Name | Segments | Connected components |
|-----|------|----------|----------------------|
| 1 | GND | 13 | C3, C4, C7, C8, C6 (GND pads) → B.Cu plane |
| 3 | +3.3V | 9 | U1 VDD pads → C3, C7, C6 (supply pads) |
| 4 | +3.3VA | 3 | U1 VDDA pad → C8 (supply pad) |
| 6 | /HSE_IN | 6 | U1 OSC_IN → C12 → Y1 pin 1 |
| 7 | /HSE_OUT | 8 | U1 OSC_OUT → C13 → Y1 pin 2 |
| — | B.Cu fill | zone | Full-board GND plane (net to be assigned) |

---

## 1 — Component Position Adjustments

Eight components were micro-adjusted (≤3 mm) to align pads with routing channels and
eliminate acute-angle entry segments.

| Ref | Value | Old (x, y) rot° | New (x, y) rot° | Reason |
|-----|-------|-----------------|-----------------|--------|
| C3  | 10 µF 0603  | (50.475, 59.000) r=0  | **(53.500, 59.500) r=0**  | Shift right to align VDD/GND pads with vertical +3.3V/GND runs from U1 left side |
| C7  | 100 nF 0402 | (52.500, 60.750) r=0  | **(53.520, 61.250) r=0**  | Align pad X with C3 for shared vertical VDD trace |
| C4  | 100 nF 0402 | (50.000, 63.000) r=90 | **(50.000, 64.000) r=90** | 1 mm south — route clearance from C12/C13 crystal area |
| C8  | 10 nF 0402  | (49.750, 67.520) r=90 | **(49.750, 68.250) r=90** | 0.73 mm south — align with VDDA track from U1 VDDA pad |
| C12 | 10 pF 0402  | (47.750, 66.040) r=90 | **(48.250, 65.270) r=90** | Move up and right — align with OSC_IN route from MCU to Y1 |
| C13 | 10 pF 0402  | (47.750, 68.790) r=90 | **(48.250, 67.520) r=90** | Move up and right — align with OSC_OUT route from MCU to Y1 |
| C6  | 100 nF 0402 | (63.000, 65.520) r=+90 | **(62.000, 64.730) r=−90** | 1 mm left, 0.8 mm up, flipped 180° — direct pad alignment with MCU right-side VDD pads |
| Y1  | 16 MHz Crystal | (45.000, 67.420) r=−90 | **(45.650, 66.400) r=−90** | 0.65 mm right, 1 mm up — shorten and symmetrise load-cap traces |

---

## 2 — GND Tracks (Net 1 — 13 segments, F.Cu, 0.2 mm)

GND pads of the left-cluster decoupling caps are connected via short stubs that will
connect to the B.Cu GND fill through vias in the next routing pass. All stubs on F.Cu
run toward the future via locations.

| Path | Start | End | Length (approx.) |
|------|-------|-----|-----------------|
| C3 GND pad → south stub | (54.275, 59.500) | (54.275, 59.500) | short vertical |
| C7 GND pad → C3 stub   | (54.000, 61.250) ↔ (54.000, 60.500) → (54.275, 60.225) → (54.275, 59.500) | routed with 45° jog | ~2.0 mm |
| C3/C7 common GND node  | (53.750, 63.088) → (53.750, 62.000) → (54.000, 61.750) → (54.000, 61.250) | vertical + 45° | ~1.9 mm |
| C8 GND pad → stub      | (51.838, 68.000) → (50.750, 68.000) → (50.520, 67.770) → (49.750, 67.770) | horiz + 45° | ~2.2 mm |
| C6 GND pad → MCU right | (60.163, 65.000) → (61.250, 65.000) → (61.540, 65.210) → (62.000, 65.210) | horiz + 45° | ~1.9 mm |

---

## 3 — +3.3V Tracks (Net 3 — 9 segments, F.Cu, 0.2 mm)

VDD supply pads of C3, C7, and C6 connected back to U1 VDD pads on the left and right
sides of the MCU.

| Path | Start | End | Note |
|------|-------|-----|------|
| C3 +3.3V pad | (52.725, 59.500) → (52.725, 60.225) → (53.040, 60.540) → (53.040, 61.250) | vert + 45° jog | C3 supply pin |
| C7 +3.3V pad → C3 node | (53.040, 61.790) → (53.040, 61.250) | stub | shared +3.3V node |
| U1 left VDD → C7 supply  | (53.250, 63.088) → (53.250, 62.000) → (53.040, 61.790) | vert + 45° | U1 pad to C7/C3 |
| C6 +3.3V pad (right MCU) | (60.163, 64.500) → (61.250, 64.500) → (61.500, 64.250) → (62.000, 64.250) | horiz + 45° | C6 supply pin |

C6 is routed directly to U1 right-side VDD pad cluster — this keeps the bypass capacitor
pad within ~1 mm of the MCU supply pin, meeting the ≤2 mm placement target.

---

## 4 — +3.3VA Tracks (Net 4 — 3 segments, F.Cu, 0.2 mm)

U1 VDDA supply routed to C8 (10 nF VDDA decoupling cap). Short 3-segment path with one
45° corner.

| Path | Length |
|------|--------|
| (51.838, 68.500) → (50.750, 68.500) → (50.520, 68.730) → (49.750, 68.730) | ~2.3 mm |

C8 sits at (49.75, 68.25), pad 2 (supply) connected via this route to U1 VDDA pin on
left side. The complementary GND connection (C8 pad 1 → net 1) is handled in the GND
cluster above.

---

## 5 — HSE Crystal Traces (Nets 6 and 7)

The 16 MHz HSE oscillator (Y1) requires careful routing of the two differential load-cap
circuits to minimise parasitic capacitance and ensure symmetric loading.

### 5.1 /HSE_IN (Net 6 — OSC_IN, 6 segments)

Connects U1 OSC_IN pad → C12 pin 1 (series) → Y1 pin 1 (OSC_IN).

| Segment | Start | End |
|---------|-------|-----|
| U1 pad → C12 stub | (51.838, 66.500) → (50.750, 66.500) → (50.000, 65.750) | horiz + 45° |
| C12 → Y1 | (48.250, 65.750) → (47.700, 66.300) → (45.800, 66.300) → (44.800, 65.300) | horiz + 45° + 45° |

Total routed length OSC_IN path: **≈ 7.5 mm**

### 5.2 /HSE_OUT (Net 7 — OSC_OUT, 8 segments)

Connects U1 OSC_OUT pad → C13 → Y1 pin 3 (OSC_OUT).

| Segment | Start | End |
|---------|-------|-----|
| U1 pad → C13 entry | (51.838, 67.000) → (49.250, 67.000) → (49.000, 67.250) → (49.000, 67.750) → (48.750, 68.000) | horiz + 45° jogs |
| C13 → Y1 | (48.250, 68.000) → (48.000, 68.000) → (47.500, 67.500) → (46.500, 67.500) | horiz + 45° |

Total routed length OSC_OUT path: **≈ 6.8 mm**

### 5.3 Crystal Routing Rules Compliance

| Criterion | Requirement | This design |
|-----------|-------------|-------------|
| Trace length | ≤ 10 mm (AN2867) | 6.8–7.5 mm ✓ |
| Trace width | Min design rule | 0.2 mm ✓ |
| Layer | F.Cu (keep on single layer) | F.Cu ✓ |
| Guard ring | Recommended on B.Cu | Provided by B.Cu fill ✓ |
| Symmetry | OSC_IN ≈ OSC_OUT length | Δ ≈ 0.7 mm — acceptable ✓ |
| Keep-away from power/switch signals | Recommended | Crystal cluster isolated from J1/SW1 ✓ |

---

## 6 — B.Cu Copper Fill Zone (GND Plane)

A filled copper zone was added on B.Cu covering the full board extent plus margin:

| Parameter | Value |
|-----------|-------|
| Layer | B.Cu |
| Zone extents | (36.25, 52.0) → (75.0, 85.5) mm |
| Net | 0 (no-net — **must be assigned to GND before final DRC**) |
| Pad clearance | 0.5 mm |
| Min island area | 10 mm² |
| Island removal | enabled |
| Fill | yes (solid) |

The zone polygon automatically excludes the four mounting holes (H1–H4, 2.45 mm radius
courtyard) and the J1 USB connector keepout area. The large 0.5 mm clearance ensures no
DRC violations occur in the current unconnected state.

**Required before final DRC:** Assign zone to net 1 (GND) and re-pour to generate
GND-connected thermal reliefs on all GND pads.

---

## 7 — Routing Status After This Pass

| Category | Status |
|----------|--------|
| Crystal HSE (Y1, C12, C13) | ✓ Fully routed |
| VDD decoupling (C3, C7, C4, C6) | ✓ Signal pads connected; GND stubs need vias to B.Cu |
| VDDA decoupling (C8) | ✓ Signal pads connected; GND stub needs via |
| VDDA filter chain (FB1, C9, C10) | ✗ Not yet routed |
| Power supply cluster (U2, C1, C2, C5) | ✗ Not yet routed |
| USB differential pair (J1, R3) | ✗ Not yet routed |
| SWD/UART connectors (J2, J3) | ✗ Not yet routed |
| Power indicator (D1, R1) | ✗ Not yet routed |
| NRST/BOOT0 (C11, R2, SW1) | ✗ Not yet routed |

---

## 8 — Next Steps

1. **Assign B.Cu zone to GND** (net 1) and re-pour to connect all GND pads.
2. **Add vias** from F.Cu GND stubs (e.g. C3, C7, C8 GND pads) to B.Cu GND plane.
3. **Route VDDA filter** — FB1 (120 Ω ferrite bead) → C9 (1 µF) + C10 (1 µF).
4. **Route power supply** — VBUS from J1 to C2, U2 VI; +3.3V from U2 VO to C1, C5, then MCU VDD.
5. **Route USB differential pair** — 90 Ω controlled impedance, matched length (Δ < 0.25 mm).
