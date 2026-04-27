# 0009 — Initial PCB Component Placement (STM32F103C8T6)

**Date:** 2026-04-27
**Status:** Implemented
**References:** Design notes 0001–0008; STM32F103C8T6 datasheet (DS5319); ST AN2867 (oscillator design)

---

## Summary

All 26 schematic components were placed on the PCB front copper layer (F.Cu) in a single
session. No board outline (Edge.Cuts), no copper routes, and no vias exist yet — this
commit establishes the component floorplan that will drive the subsequent routing phase.

The layout is organised into three functional clusters plus a peripheral group:

| Cluster | Centre (mm) | Contents |
|---------|-------------|----------|
| MCU + crystal | (51, 67) | U1, Y1, C4, C7, C8, C9, C10, C12, C13, FB1, R5 |
| Power supply | (118, 57) | U2, J1, C1, C2, C3, C5, C6, D1, R1 |
| Control / interface | (107, 58) | SW1, R2, R3, R4, C11 |
| Expansion connectors | (119, 55) | J2, J3, J4 |

---

## 1 — Floorplan Overview

Approximate top-view layout (Y axis down, units mm, not to scale):

```
X →   38        50        60        100       116       125
      |         |         |         |         |         |
  38  R5        C7        .         .         .         .
      .         .         .         .         .         .
  44  .         .         .         .         C1        .
      .         .         .         .         .         .
  47  .         .         .         .         J1  C2    .
      .         .         .         .         .         .
  50  .         .         .         .         D1        .
      .         .         .         .         .         .
  55  .         .         .         J2  J3    .    J4   .
      .         .         .         .         .         .
  60  .    C4   .         .         .   U2    .         .
      .         .         .   SW1   .         .         .
  63  .         .         .         R1        .         .
      .         .         .         R2        .         .
  66  Y1  C12   .         .         R3        C5        .
      .    .    U1        .         R4        .         .
  68  .   C13   .         .         .         .   C6  C11
      .         .         .         .         C3        .
  72  .    FB1  .         .         .         .         .
      .   C9    .         .         .         .         .
  74  .   C10   .         .         .         .         .
```

---

## 2 — Component Placement Table

All components placed on **F.Cu** (top face). Coordinates are KiCad PCB origin (mm).

### MCU cluster

| Ref  | Value             | Footprint          | X (mm) | Y (mm) | Rot (°) | Role |
|------|-------------------|--------------------|--------|--------|---------|------|
| U1   | STM32F103C8T6     | LQFP-48 7×7 mm     |  56.00 |  67.25 |    0    | Main MCU |
| C4   | 100 nF            | 0402               |  50.00 |  63.00 |   90    | VDD decoupling — above-left |
| C7   | 100 nF            | 0402               |  53.48 |  60.00 |    0    | VDD decoupling — above |
| C8   | 10 nF             | 0402               |  49.75 |  67.52 |   90    | VDDA HF decoupling |
| C9   | 1 µF              | 0402               |  49.27 |  72.08 |  180    | VDDA bulk decoupling |
| C10  | 1 µF              | 0402               |  49.27 |  73.58 |  180    | VDDA bulk decoupling |
| FB1  | 120 Ω (ferrite)   | L_0603             |  51.25 |  72.54 |  −90    | VDD power-line filter |

### Crystal cluster

| Ref  | Value   | Footprint                  | X (mm) | Y (mm) | Rot (°) | Role |
|------|---------|----------------------------|--------|--------|---------|------|
| Y1   | 16 MHz  | Crystal_SMD_3225-4Pin      |  45.00 |  67.42 |  −90    | HSE crystal |
| C12  | 10 pF   | 0402                       |  47.75 |  66.04 |   90    | HSE load cap (OSC_IN side) |
| C13  | 10 pF   | 0402                       |  47.75 |  68.79 |   90    | HSE load cap (OSC_OUT side) |

### I²C pull-up (left of board)

| Ref  | Value   | Footprint | X (mm) | Y (mm) | Rot (°) | Role |
|------|---------|-----------|--------|--------|---------|------|
| R5   | 1.5 kΩ  | 0402      |  39.70 |  68.32 |    0    | I2C2 SDA pull-up |

### Power supply cluster

| Ref  | Value        | Footprint             | X (mm)  | Y (mm)  | Rot (°) | Role |
|------|--------------|-----------------------|---------|---------|---------|------|
| U2   | AMS1117-3.3  | SOT-223-3             | 116.29  |  62.34  |    0    | 3.3 V LDO |
| C1   | 22 µF        | 0805                  | 124.53  |  44.35  |    0    | +3.3 V output bulk cap |
| C2   | 22 µF        | 0805                  | 124.53  |  47.36  |    0    | VBUS input bulk cap |
| C3   | 10 µF        | 0603                  | 118.62  |  67.71  |    0    | VDD/VDDA intermediate bulk |
| C5   | 100 nF       | 0402                  | 122.65  |  66.00  |    0    | LDO output HF bypass |
| C6   | 100 nF       | 0402                  | 122.65  |  71.00  |    0    | LDO output HF bypass |
| D1   | RED LED      | LED_0603              | 124.35  |  50.16  |    0    | Power indicator |
| R1   | 1.5 kΩ       | 0402                  | 108.54  |  61.72  |    0    | LED current limiter |

### Control / interface cluster

| Ref  | Value      | Footprint                        | X (mm)  | Y (mm)  | Rot (°) | Role |
|------|------------|----------------------------------|---------|---------|---------|------|
| SW1  | SW_SPDT    | SW_E-Switch_EG1224_SPDT_Angled   |  99.60  |  46.46  |    0    | BOOT0 select switch (THT) |
| R2   | 10 kΩ      | 0402                             | 108.54  |  63.71  |    0    | BOOT0 series resistor |
| R3   | 1.5 kΩ     | 0402                             | 108.54  |  65.70  |    0    | USB D+ pull-up |
| R4   | 1.5 kΩ     | 0402                             | 108.54  |  67.69  |    0    | I2C2 SCL pull-up |
| C11  | 100 nF     | 0402                             | 125.52  |  71.00  |    0    | NRST filter cap |
| J1   | USB Micro-B| USB_Micro-B_Wuerth_629105150521  | 116.83  |  46.71  |    0    | USB connector |

### Expansion connectors

| Ref  | Value          | Footprint                                 | X (mm)  | Y (mm) | Rot (°) |
|------|----------------|-------------------------------------------|---------|--------|---------|
| J2   | Conn_01x04_Pin | PinHeader_1x04_P1.00mm_Vertical_SMD       | 114.14  |  55.11 |    0    |
| J3   | Conn_01x04_Pin | PinHeader_1x04_P1.00mm_Vertical_SMD       | 119.69  |  55.11 |    0    |
| J4   | Conn_01x04_Pin | PinHeader_1x04_P1.00mm_Vertical_SMD       | 125.24  |  55.11 |    0    |

---

## 3 — Placement Rationale

### 3.1 MCU (U1) and VDD decoupling

The STM32F103C8T6 LQFP-48 body is centred at **(56, 67.25)**. It has four VDD supply
pins (pins 1 VBAT, 24, 36, 48) and one VDDA analogue supply (pin 9).

**VDD decoupling strategy** (per design note 0001 and ST datasheet Table 5):

- **C4, C7** (100 nF 0402) — placed above U1, providing high-frequency bypassing for the
  VDD pins on the top side of the package. Minimum trace length is achieved with rotations
  oriented toward the nearest VDD pad.
- **FB1** (120 Ω ferrite bead, 0603) — placed below-left of U1 at (51.25, 72.54), in line
  with the AVDD/VDDA supply path. Ferrite bead isolates the analogue supply from digital
  switching noise on the VDD rail.
- **C8** (10 nF 0402) — placed left of U1 for VDDA high-frequency decoupling. The
  10 nF / 10 nF combination provides low impedance from ~100 MHz downward.
- **C9, C10** (1 µF 0402 × 2) — placed below-left of U1 for VDDA bulk energy storage
  (analogue supply stability under ADC conversions).

### 3.2 Crystal circuit (Y1, C12, C13)

The 16 MHz SMD crystal is placed at **(45, 67.42)**, rotated −90° so its long axis aligns
horizontally, keeping the pads close to U1's OSC_IN (PD0, pin 5) and OSC_OUT (PD1, pin 6)
on the left side of the package. Distance between Y1 and U1 centres: ≈ **11 mm**.

Load capacitors:

- **C12** (10 pF, 0402) at (47.75, 66.04) — OSC_IN side
- **C13** (10 pF, 0402) at (47.75, 68.79) — OSC_OUT side

Both rotated 90° and positioned symmetrically on either side of the crystal to keep trace
lengths balanced and parasitic capacitance equal on both oscillator pins (see design note
0003 for load capacitance calculation).

**R5** (1.5 kΩ I2C SDA pull-up) is placed at the far left (39.70, 68.32) alongside the
crystal cluster because PB11 (I2C2_SDA) exits the left side of the MCU package.

### 3.3 Power supply cluster

AMS1117-3.3 (**U2**, SOT-223-3) is placed at the right of the board, keeping the noisy
USB VBUS entry (J1) and 5 V→3.3 V conversion away from the analogue MCU circuitry on the
left side:

- **C1, C2** (22 µF 0805) — output and input bulk capacitors stacked vertically above U2,
  as required by the AMS1117 stability specification (≥ 10 µF on both VI and VO).
- **C5, C6** (100 nF 0402) — HF bypass directly beside U2 for LDO output impedance.
- **C3** (10 µF 0603) — intermediate bulk capacitor bridging the regulator output area with
  the main VDD distribution.
- **D1** (RED LED, 0603) + **R1** (1.5 kΩ) — power indicator placed in the top-right corner
  so it remains visible after the board is installed.

### 3.4 Control / interface area

- **SW1** (THT SPDT) — BOOT0 select switch, placed centrally to be reachable in assembled
  form; through-hole body confirmed against B.Cu keepout rules from design note 0008.
- **R2** (10 kΩ) — BOOT0 series, **R3** (1.5 kΩ) — USB D+ pull-up, **R4** (1.5 kΩ) — I2C
  SCL pull-up: stacked vertically at X = 108.54 for efficient routing to the right side of U1.
- **C11** (100 nF) — NRST filter cap, placed near the power supply cluster since NRST is
  routed to the right connector side.
- **J1** (USB Micro-B) — placed at the top edge, oriented outward for panel cut-out access.

### 3.5 Expansion connectors (J2, J3, J4)

Three 4-pin 1.00 mm pitch SMD pin headers are aligned at Y = 55.11 with a 5.55 mm pitch
between them, forming a contiguous 12-pin break-out row. This placement leaves the MCU
routing area clear and provides a consistent connector edge for a mating board or flex cable.

---

## 4 — Next Steps

1. **Draw board outline** on Edge.Cuts layer (dimensions TBD based on connector and SW1 envelope).
2. **Route copper** — power pour on B.Cu for GND, critical signals (USB D+/D−, OSC traces) first.
3. **Run DRC** after routing and verify all net connections and clearance rules (0.2 mm min,
   0.2 mm track per design note 0008).
