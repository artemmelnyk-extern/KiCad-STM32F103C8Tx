# 0013 — Power Supply Circuit Placement (AMS1117-3.3 and Associated Passives)

**Date:** 2026-04-29
**Status:** Implemented
**References:** Design notes 0005 (power supply schematic), 0009 (initial floorplan), 0012 (previous placement); AMS1117 datasheet §7; IPC-7351B decoupling placement guidelines

---

## Summary

Nine power-supply components were relocated from their initial parking positions to their
final pre-routing positions, forming a coherent power cluster directly below-right of U1
(STM32F103C8T6 at (56, 67.25)). The AMS1117-3.3 LDO (U2) moved ~51 mm left — from
the far-right parking area to (65.5, 78.75) — anchoring the cluster at a central,
short-trace distance from both the USB input (J1) and the MCU VDD supply pins.

Fifteen components are unchanged from design note 0012.

---

## 1 — Component Position Changes

| Ref | Value        | Footprint      | Old (x, y) rot°        | New (x, y) rot°           | Role |
|-----|--------------|----------------|------------------------|---------------------------|------|
| U2  | AMS1117-3.3  | SOT-223-3      | (116.29, 62.34) r=0    | **(65.5, 78.75) r=−90°**  | 3.3 V LDO regulator |
| C1  | 22 µF        | 0805           | (124.53, 44.35) r=0    | **(63.55, 72.0) r=0°**    | +3.3 V output bulk cap |
| C5  | 100 nF       | 0402           | (122.65, 66.0) r=0     | **(60.25, 75.0) r=0°**    | LDO output HF bypass |
| C2  | 22 µF        | 0805           | (124.53, 47.36) r=0    | **(71.25, 79.2) r=90°**   | VBUS input bulk cap |
| D1  | RED LED      | LED_0603       | (124.35, 50.16) r=0    | **(73.75, 78.0) r=90°**   | Power indicator |
| R1  | 1.5 kΩ       | 0402           | (108.54, 61.72) r=0    | **(70.75, 73.24) r=90°**  | LED current limiter |
| C3  | 10 µF        | 0603           | (118.62, 67.71) r=0    | **(50.475, 59.0) r=0°**   | VDD/VDDA intermediate bulk |
| C6  | 100 nF       | 0402           | (122.65, 71.0) r=0     | **(63.0, 65.52) r=90°**   | VDD HF decoupling (MCU right side) |
| C7  | 100 nF       | 0402           | (53.48, 60.0) r=0      | **(52.5, 60.75) r=0°**    | VDD HF decoupling (MCU above) |

---

## 2 — Power Supply Cluster Layout

U2 (AMS1117-3.3, SOT-223-3) is now centred at **(65.5, 78.75)**, rotated −90° so its
**VO (output) pin** faces toward U1 (left/top) and its **VI (input) pin** faces toward
J1 USB connector (right).

```
X →    50    56    60    63    65    70    71
       |     |     |     |     |     |     |
  59  C3     .     .     .     .     .     .     ← VDD bulk (MCU supply path)
       .     .     .     .     .     .     .
  65   .     U1    .     .     .     .     .
       .     .     .    C6     .     .     .     ← HF bypass, MCU right side
  67   .     .     .     .     .    J1     .     ← USB Micro-B
       .     .     .     .     .     .     .
  72   .     .     .    C1     .     .     .     ← 22µF output bulk (VO side)
  73   .     .     .     .     .    R1     .     ← LED series resistor
  75   .     .    C5     .     .     .     .     ← 100nF output HF bypass
       .     .     .     .     .     .     .
  78   .     .     .     .     .    D1     .     ← Power LED
  79   .     .     .     .    U2    C2     .     ← LDO + 22µF input bulk (VI side)
```

### Distance summary

| Pair | Distance (approx.) | Significance |
|------|--------------------|--------------|
| U2 → U1 | 14.4 mm | VDD distribution trace length |
| U2 VO → C1 | 7.0 mm | Output cap proximity (AMS1117 requires ≥10 µF within short trace) |
| U2 VO → C5 | 6.5 mm | HF bypass proximity |
| U2 VI → C2 | 5.8 mm | Input cap proximity |
| U2 VI → J1 | 5.2 mm | VBUS entry trace length |

---

## 3 — Placement Rationale

### 3.1 U2 (AMS1117-3.3 LDO)

The AMS1117-3.3 was moved from its right-side parking position to **(65.5, 78.75)**,
rotated −90°, placing it:

- **Below and to the right of U1**, so the VO (output) pin naturally faces up-left toward
  the MCU VDD network — minimising the power trace from regulator output to MCU supply pins.
- **Near J1** (USB Micro-B at (70.8, 65.875)), keeping the VBUS → VI trace short (~5 mm).
  This avoids routing 5 V across the board and reduces I²R drop before regulation.
- The −90° rotation orients the SOT-223 tab (GND) downward on B.Cu for thermal spreading
  and a direct ground connection via the bottom copper layer.

### 3.2 Output capacitors — C1 and C5

The AMS1117 datasheet specifies a minimum **10 µF output capacitor** for stability (ESR
0.1–1.0 Ω range). C1 (22 µF, 0805, MLCC) and C5 (100 nF, 0402) are placed on the VO
side of U2:

- **C1** at (63.55, 72.0) — 7 mm from U2, pads oriented for a direct VO → cap → GND path.
- **C5** at (60.25, 75.0) — smaller HF bypass, placed between C1 and U2 to cover
  frequencies above C1's self-resonance (~5 MHz for 22 µF 0805 MLCC).

Together they provide: 22 µF bulk stability + 100 nF HF decoupling on the +3.3 V rail.

### 3.3 Input capacitor — C2

**C2** (22 µF, 0805) is placed at (71.25, 79.2) on the VI (input/VBUS) side of U2.
The 22 µF on VI damps input voltage transients from the USB cable inductance and ensures
the LDO does not latch up on hot-plug. Rotated 90° to align pads with the vertical
VBUS trace from J1.

### 3.4 Power indicator — D1 and R1

**D1** (RED LED, 0603) at (73.75, 78.0) and **R1** (1.5 kΩ, 0402) at (70.75, 73.24) are
placed adjacent to the power supply cluster. Both rotated 90° to form a vertical
current path: +3.3V → R1 → D1 → GND. Placed near the board edge so the LED is
visible from outside the enclosure.

### 3.5 VDD intermediate bulk — C3

**C3** (10 µF, 0603) was repositioned to **(50.475, 59.0)** — above-left of U1 — to sit
at the entry point of the +3.3 V supply into the MCU decoupling network. It bridges the
LDO output capacitor bank (C1/C5, ~14 mm away) and the per-pin 100 nF decouplers
(C4/C7/C8), absorbing mid-frequency ripple (100 kHz–1 MHz) between the two stages.

### 3.6 VDD HF decouplers — C6 and C7 (minor adjustments)

- **C6** (100 nF) moved to (63.0, 65.52) r=90° — right side of U1, covering VDD pin 48
  (LQFP-48 right side). Short trace to MCU pad.
- **C7** (100 nF) minor nudge to (52.5, 60.75) — above U1, covering VDD pin 24.

---

## 4 — Final Power Supply Cluster — Complete Position Table

| Ref | Value       | X (mm)  | Y (mm)  | Rot (°) | Notes |
|-----|-------------|---------|---------|---------|-------|
| U2  | AMS1117-3.3 | 65.500  | 78.750  | −90     | LDO, VO faces up-left toward U1 |
| C1  | 22 µF       | 63.550  | 72.000  |   0     | VO output bulk |
| C5  | 100 nF      | 60.250  | 75.000  |   0     | VO HF bypass |
| C2  | 22 µF       | 71.250  | 79.200  |  90     | VI input bulk |
| R1  | 1.5 kΩ      | 70.750  | 73.240  |  90     | LED current limiter |
| D1  | RED LED     | 73.750  | 78.000  |  90     | Power indicator |
| C3  | 10 µF       | 50.475  | 59.000  |   0     | VDD intermediate bulk |
| C6  | 100 nF      | 63.000  | 65.520  |  90     | VDD HF decoupling, U1 right |
| C7  | 100 nF      | 52.500  | 60.750  |   0     | VDD HF decoupling, U1 above |

---

## 5 — Unchanged Components (19)

C4, C8, C9, C10, C11, C12, C13, FB1, J1, J2, J3, J4, R2, R3, R4, R5, SW1, U1, Y1 —
retain positions from design notes 0009–0012.

---

## 6 — Next Steps

1. **Draw board outline** (Edge.Cuts) — all 27 components are now in final pre-routing
   positions. Left boundary ≈ X=38 (SW1), right boundary ≈ X=76 (D1/C2), top ≈ Y=52
   (J2/J3), bottom ≈ Y=82 (J4/C2).
2. **Route power rails** first: +3.3 V pour and GND pour on B.Cu. Connect U2 tab to GND.
3. **Route critical analog paths**: VDDA via FB1 → C9/C10; crystal OSC traces.
4. **Route USB differential pair** (J1 → R3 → U1 PA11/PA12).
