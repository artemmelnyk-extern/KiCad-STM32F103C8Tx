# 0010 — USB and SWO/SWD Circuit Component Placement Refinement

**Date:** 2026-04-27
**Status:** Implemented
**References:** Design notes 0004 (USB), 0009 (initial placement); USB 2.0 Full-Speed spec §7.1.8; ST UM1724 (STM32 Nucleo SWD layout)

---

## Summary

Four components from the initial floorplan (design note 0009) were relocated to their
final pre-routing positions to support two signal-integrity-sensitive circuits:

1. **USB Full-Speed** — J1 (USB Micro-B) + R3 (D+ pull-up) moved adjacent to U1 with
   matched differential-pair trace length in mind.
2. **SWD/SWO debug header** — J3 (4-pin 1.00 mm SMD header) moved above U1 to sit near
   the MCU's SWD and SWO pins.

No copper routes or vias were added in this commit; all changes are footprint position
and rotation updates only.

---

## 1 — USB Circuit Placement

### Component moves

| Ref | Value       | Previous position (mm)    | New position (mm)          | Rotation change |
|-----|-------------|--------------------------|----------------------------|-----------------|
| J1  | USB Micro-B | (116.83, 46.71) rot=0°   | **(70.80, 65.875) rot=90°** | +90° |
| R3  | 1.5 kΩ D+   | (108.54, 65.70) rot=0°   | **(64.75, 65.49) rot=−90°** | −90° |

### Rationale

The USB Micro-B connector (**J1**) and the D+ pull-up resistor (**R3**) were originally
placed in the right-hand power cluster as temporary parking positions. For USB Full-Speed
(12 Mbit/s) differential signalling, the key layout rules are:

- **D+ and D− traces must be length-matched** (ΔL < 0.5 mm for FS per USB 2.0 §7.1.8).
- **Total stub length from connector to MCU should be minimised** (< 25 mm recommended).
- **R3 (series pull-up)** must sit on the D+ net between J1 pad 3 and MCU pin PA12
  (pin 33, LQFP-48 right side) to force USB FS device enumeration.

New position analysis:

```
Board X-axis (mm): 56      64.75  70.8
                   |          |    |
                  U1        R3    J1
                  (MCU)     (D+) (USB)
                 PA12 pin→──R3───J1 pad 3
                 PA11 pin→───────J1 pad 2
```

- **J1** rotated 90° so its five signal pads (VBUS, D−, D+, ID, GND) face vertically toward
  the MCU. The connector opening faces the bottom board edge (−Y direction), providing
  panel cut-out access from the board edge without running the cable across the board.
- With J1 at X=70.8 and U1 at X=56, the D+/D− pads of J1 are approximately **14.8 mm**
  from the corresponding MCU pads (PA11/PA12 on the right side of LQFP-48). This is well
  within the < 25 mm guideline.
- **R3** at X=64.75 sits between J1 and U1, placing it on the D+ line with minimal stub.
  Rotated −90° so its pads align with the vertical D+ trace.

---

## 2 — SWD/SWO Debug Header Placement

### Component move

| Ref | Value          | Previous position (mm)    | New position (mm)      | Rotation change |
|-----|----------------|--------------------------|------------------------|-----------------|
| J3  | Conn_01x04_Pin | (119.69, 55.11) rot=0°   | **(62.875, 58.0) rot=0°** | none |

### SWD/SWO pin assignment on STM32F103C8T6

| MCU pin | Signal   | Net        | LQFP-48 side |
|---------|----------|------------|--------------|
| 34 — PA13 | SWDIO   | SWD_DATA   | Right |
| 37 — PA14 | SWDCLK  | SWD_CLK    | Right |
| 39 — PB3  | SWO     | SWO_TDO    | Right (lower) |
| — (VCC/GND) | —     | +3.3V / GND | — |

### Rationale

J3 is used as the 4-pin SWD + SWO debug connector (VCC, GND, SWDIO, SWDCLK; SWO via
PB3 on a separate net). It was relocated from the right-side connector bank at X=119 to
**(62.875, 58)**, which places it:

- Directly **above U1** (MCU centre at (56, 67.25), J3 is 9.25 mm above).
- Within ~6–10 mm of the MCU's PA13 (SWDIO) and PA14 (SWDCLK) pads on the right side
  of the LQFP-48 package.

This keeps the SWD traces short and avoids routing debug signals across the full board.
A short SWD stub reduces susceptibility to capacitive loading on the SWDCLK line, which
is important at the 4 MHz default SWD clock.

```
      J3 (62.875, 58)
       ↓  ↓  ↓  ↓
      [SWD/SWO header]
             ↑
           ~9 mm
             ↑
      U1 (56, 67.25)  ←─ PA13/PA14 pads on right side of LQFP-48
```

---

## 3 — Minor R4 Adjustment

| Ref | Value         | Previous position (mm) | New position (mm)  |
|-----|---------------|------------------------|--------------------|
| R4  | 1.5 kΩ I2C SCL| (108.54, 67.69) rot=0° | (107.99, 70.74) rot=0° |

R4 (I2C2 SCL pull-up) received a minor position nudge (~3 mm south) to improve clearance
with adjacent components in the right-hand resistor column. Function is unchanged.

---

## 4 — Updated Position Summary (Affected Components)

| Ref | Value       | X (mm)  | Y (mm)  | Rot (°) | Layer | Footprint |
|-----|-------------|---------|---------|---------|-------|-----------|
| J1  | USB Micro-B | 70.80   | 65.875  |  90     | F.Cu  | USB_Micro-B_Wuerth_629105150521 |
| J3  | SWD/SWO hdr | 62.875  | 58.00   |   0     | F.Cu  | PinHeader_1x04_P1.00mm_Vertical_SMD |
| R3  | 1.5 kΩ D+   | 64.75   | 65.49   | −90     | F.Cu  | R_0402_1005Metric |
| R4  | 1.5 kΩ SCL  | 107.99  | 70.74   |   0     | F.Cu  | R_0402_1005Metric |

---

## 5 — Next Steps

1. **Route USB differential pair** (D+ / D−): route J1 pads 2–3 to MCU PA11/PA12 as a
   matched-length pair; insert R3 in-line on D+. Aim for trace width ≈ 0.2 mm and
   spacing ≈ 0.2 mm (50 Ω single-ended, ≈ 90 Ω differential; FR4 2-layer geometry).
2. **Route SWD/SWO signals** (J3 → PA13, PA14, PB3): straightforward low-speed traces;
   keep SWO (PB3) length < 50 mm to avoid reflections at higher SWO clock rates.
3. **Draw board outline** (Edge.Cuts) now that the USB connector and debug header are in
   their final positions — J1 rotation defines the connector edge cut direction.
