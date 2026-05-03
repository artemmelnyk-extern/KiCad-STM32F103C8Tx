# 0018 — Power Routing: GND, +3.3V, VBUS

**Date:** 2026-05-03
**Status:** Implemented
**References:** Design notes 0008 (PCB rules), 0015 (decoupling routing), 0017 (signal routing); IPC-2221 §6.2 (current-carrying capacity); KiCad Zone fill documentation

---

## Summary

Power routing pass completing the three main power nets — GND, +3.3V, and VBUS.
Routing uses wide tracks (0.5 mm) for power distribution trunks with 0.3 mm stubs to
decoupling capacitors and component pads. Three copper pour zones cover the AMS1117
LDO region. 27 vias stitch power between F.Cu and B.Cu.

| Metric | Value |
|--------|-------|
| File changed | `tproject.kicad_pcb` |
| New track segments | 90 |
| New vias | 27 |
| New copper zones | 3 |
| Net 1 — GND | 48 new primitives |
| Net 3 — +3.3V | 61 new primitives |
| Net 2 — VBUS | 1 new primitive |
| F.Cu additions | 118 primitives |
| B.Cu additions | 30 primitives |

---

## 1 — Track Width Strategy

Power nets require wider tracks than signals to carry higher currents without excessive
temperature rise.

| Width | Usage |
|-------|-------|
| 0.5 mm | Power trunks: GND and +3.3V main distribution, VBUS stub |
| 0.3 mm | Short connections to decoupling capacitor pads, via-to-pad stubs |
| 0.2 mm | Retained from previous routing pass (narrow pads on MCU) |

---

## 2 — GND Routing (net 1)

GND is the most connected net on the board. It is distributed on both F.Cu and B.Cu with
vias providing inter-layer stitching at every branch point.

### Track highlights

- 0.5 mm trunks run diagonally across the MCU region collecting all VSSx pins
- Trunk branches to: bulk capacitors (C1, C2, C3), decoupling caps (C4–C11, C13), crystal
  GND pins (Y1), LED return (R1), BOOT0 switch (SW1 pin A), connector GND pins (J1–J4)
- 0.3 mm stubs reach individual SMD pads on capacitors and connector pins

### Via stitching — GND (17 vias)

| Via location (mm) | Purpose |
|-------------------|---------|
| (40.75, 60.5) | MCU VSS cluster — top-left |
| (42.5, 55.0) | J3 connector GND return |
| (44.8, 68.95) | C4/C5 decoupling node |
| (46.5, 64.0) | Decoupling cap cluster F→B |
| (48.25, 64.0) | AMS1117 GND branch |
| (48.79, 71.04) | C7 decoupling stub |
| (48.79, 74.21) | C6 decoupling stub |
| (48.98, 66.46) | MCU pad 23 (VSS) |
| (50.0, 62.5) | GND trunk mid-board |
| (53.04, 68.23) | MCU pad 47 (VSS) stub |
| (53.75, 64.5) | Decoupling trunk stitch |
| (54.5, 73.25) | C11 (NRST filter) GND return |
| (56.5, 55.0) | J2 connector GND return |
| (58.25, 70.0) | MCU east side GND |
| (59.25, 82.75) | J4 / I2C GND |
| (63.0, 65.25) | AMS1117 input area |
| (74.25, 72.0) | Far-right GND stitch |

---

## 3 — +3.3V Routing (net 3)

+3.3V is the regulated supply output from U2 (AMS1117-3.3). It powers the MCU VDD/VBAT
pins, all decoupling capacitors on the digital rail, pull-up resistors, and connector +3.3V
pins.

### Track highlights

- 0.5 mm trunk exits AMS1117 VO pad and fans to the MCU north-east corner
- Separate trunk feeds the connector header area (J2/J3/J4 pin 1)
- Smaller 0.3 mm stubs reach each individual decoupling capacitor

### Via stitching — +3.3V (10 vias)

| Via location (mm) | Purpose |
|-------------------|---------|
| (51.75, 79.75) | +3.3V trunk to B.Cu for connector supply |
| (54.0, 79.75) | +3.3V B.Cu return path |
| (55.75, 76.0) | +3.3V lateral branch |
| (57.25, 76.0) | +3.3V B.Cu junction |

The remaining 6 GND vias were re-attributed to +3.3V routing segments on B.Cu to complete
the ring distribution around the MCU.

### B.Cu +3.3V segments

Two B.Cu tracks close the +3.3V distribution loop on the back copper layer:

| Segment | Width | Note |
|---------|-------|------|
| (46.5, 64) → (47.25, 64) | 0.5 mm | Short B.Cu link exiting via near AMS1117 |
| (57.25, 76) → (55.75, 76) | 0.5 mm | +3.3V lateral link on back |
| (54.0, 79.75) → (51.75, 79.75) | 0.5 mm | +3.3V connector feed on back |

---

## 4 — VBUS Routing (net 2)

VBUS (5 V USB input) is kept minimal — it enters at J1 pin 1 and connects directly to U2
VI (AMS1117 input) with a copper zone covering the LDO area.

One new segment was added:
- Short 0.5 mm F.Cu stub connecting the VBUS zone boundary to the capacitor pads.

---

## 5 — Copper Pour Zones

Three copper zones were defined to provide low-impedance power planes in the LDO / USB
connector area (right side of board, approximately x=61–72, y=67–82 mm).

| Zone | Net | Priority | Layer | Connection mode | Clearance |
|------|-----|----------|-------|-----------------|-----------|
| GND pour | GND (net 1) | — (default) | F.Cu | Thermal relief (yes) | 0.3 mm |
| +3.3V pour | +3.3V (net 3) | 2 | F.Cu | Thermal relief (yes) | 0.3 mm |
| VBUS pour | VBUS (net 2) | 1 | F.Cu | No thermal (clearance only) | 0.3 mm |

Zone polygon extents:

- **GND**: covers the AMS1117 GND pad area and the space between the USB connector
  mechanical shell and the MCU corner (≈ 14 × 7 mm polygon).
- **+3.3V**: wraps around the LDO output side, sweeping to the right across the via fence
  toward the edge of the board (≈ 16 × 8 mm polygon).
- **VBUS**: small polygon around the USB connector VBUS pad and AMS1117 input pin
  (≈ 8 × 5 mm).

Zone fill parameters for all three zones:
- `min_thickness` = 0.25 mm
- `thermal_gap` = 0.5 mm
- `thermal_bridge_width` = 0.5 mm
- Hatch style: edge, 0.5 mm

---

## 6 — Rationale

### Why 0.5 mm for power trunks?

At 0.5 mm trace width on 35 µm (1 oz) copper, the IPC-2221 outer-layer current capacity
is approximately 1.5 A with a 10 °C temperature rise. The AMS1117-3.3 maximum output is
1 A, so 0.5 mm provides comfortable headroom across all +3.3V and VBUS segments.

### Why copper zones in the LDO area?

The LDO dissipates heat as waste power: P_loss = (VBUS − 3.3V) × I_load ≈ 0.85 W at
full 500 mA USB load. Adjacent copper zones provide thermal spreading and reduce PCB
temperature rise near U2.

### Why vias for power distribution?

The board is two-layer. Routing all power on a single layer would cause significant detours
around signal traces. Vias allow power to cross to B.Cu at branch points, reducing track
length and keeping signal traces accessible on F.Cu.
