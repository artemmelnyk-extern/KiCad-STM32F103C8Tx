# 0012 — Switch, Connector, and Peripheral Circuit Placement Refinement

**Date:** 2026-04-29
**Status:** Implemented
**References:** Design notes 0002 (BOOT0/NRST), 0009 (initial floorplan), 0010 (USB/SWD), 0011 (PCM12 switch)

---

## Summary

Eight components were relocated from their initial parking positions to their final
pre-routing positions, grouped into three functional clusters around U1 (STM32F103C8T6):

| Cluster | Components moved |
|---------|-----------------|
| BOOT0 / switch circuit | SW1, R2 |
| Expansion connectors | J2, J3, J4 |
| MCU peripheral passives | R4, R5, C11 |

Twenty components remain at their positions from design notes 0009–0011 (U1, J1, Y1,
C1–C13, FB1, D1, R1, R3, U2).

---

## 1 — Component Position Changes

| Ref  | Value          | Footprint                    | Old (x, y) rot°     | New (x, y) rot°      |
|------|----------------|------------------------------|---------------------|----------------------|
| SW1  | SW_SPDT        | SW_SPDT_PCM12 (SMD)          | (99.60, 46.46) r=0  | **(40.43, 56.65) r=−90°** |
| R2   | 10 kΩ BOOT0    | R_0402                       | (108.54, 63.71) r=0 | **(47.24, 57.25) r=0**    |
| J2   | Conn_01x04_Pin | PinHeader_1x04_P1.00mm_SMD   | (114.14, 55.11) r=0 | **(59.375, 54.0) r=0**    |
| J3   | Conn_01x04_Pin | PinHeader_1x04_P1.00mm_SMD   | (62.875, 58.0) r=0  | **(52.125, 54.0) r=0**    |
| J4   | Conn_01x04_Pin | PinHeader_1x04_P1.00mm_SMD   | (125.24, 55.11) r=0 | **(52.625, 81.0) r=90°**  |
| R4   | 1.5 kΩ I2C SCL | R_0402                       | (107.99, 70.74) r=0 | **(56.76, 80.25) r=0**    |
| R5   | 1.5 kΩ I2C SDA | R_0402                       | (39.70, 68.32) r=0  | **(46.74, 79.0) r=0**     |
| C11  | 100 nF NRST    | C_0402                       | (125.52, 71.0) r=0  | **(54.0, 74.0) r=0**      |

---

## 2 — Placement Rationale

### 2.1 BOOT0 Circuit — SW1 and R2

**SW1** (CK PCM12 SMD slide switch) relocated from the top-right parking area to
**(40.43, 56.65) r=−90°**, placing it to the left of the MCU body.

- The PCM12 is rotated −90° so its slide travel aligns with the board edge, making it
  accessible after PCB assembly.
- New position is ~15 mm left of U1 centre, keeping the BOOT0 trace (SW1 → BOOT0 pin 44
  via R2) short and avoiding the USB / crystal routing areas.
- **R2** (10 kΩ BOOT0 series resistor) follows SW1 to **(47.24, 57.25)**, placed inline
  between SW1 and U1 pin 44 (BOOT0, left side of LQFP-48).

```
SW1 (40.43, 56.65) ──R2 (47.24, 57.25)──► U1 pin 44 (BOOT0)
       ↑
  PCM12, slide
  accessible from
  board left edge
```

### 2.2 Expansion Connectors — J2, J3, J4

All three 4-pin 1.00 mm SMD pin headers were relocated from the right-side parking
cluster to positions flanking U1:

| Ref | New position     | Assignment |
|-----|-----------------|------------|
| J3  | (52.125, 54.0)  | SWD/SWO debug header — above-left of U1, ~13 mm from MCU centre |
| J2  | (59.375, 54.0)  | Expansion connector — above-right of U1 |
| J4  | (52.625, 81.0) r=90° | Expansion connector — below U1, rotated 90° to align pads vertically |

J2 and J3 are placed in a row at Y=54, ~5 mm above U1 (centre Y=67.25), providing a
horizontal connector strip above the MCU. Pitch between J3 and J2 is 7.25 mm, leaving
routing channels between them. J4 is placed below U1, rotated 90° to route signals
downward off the MCU's lower pads.

### 2.3 MCU Peripheral Passives — R4, R5, C11

**R4** (1.5 kΩ I2C2 SCL pull-up) and **R5** (1.5 kΩ I2C2 SDA pull-up) moved from their
scattered parking positions to the area immediately below U1:

- **R4** at (56.76, 80.25) — below U1, aligned with PB10/PB11 (I2C2_SCL/SDA, pins 29–30
  on the bottom of the LQFP-48).
- **R5** at (46.74, 79.0) — adjacent to R4, both at Y ≈ 79–80, giving a short pull-up
  trace to the I2C bus pads.

**C11** (100 nF NRST filter capacitor) moved from its right-side parking position to
**(54.0, 74.0)**, placing it near U1 pin 7 (NRST) on the left side of the LQFP-48.
This minimises the stub length on the NRST net, which is important for correct MCU reset
filtering (RC time constant with R_internal and C11 ≈ 100 ns at 100 nF per design note 0002).

---

## 3 — Updated Cluster Layout (Approximate, mm)

```
X →   40       47       52  54  56  59       70
      |        |        |   |   |   |        |
  54  .        .        J3  .   .   J2       .
      .        .        .   .   .   .        .
  57  SW1      R2       .   .   .   .        .
      .        .        .   .   .   .        .
  63  .        .        .   .   .   .        .
      .        .        .   .   .   .        J1
  67  .        .        .   U1(56,67.25)     .
      .        .        .   .   .   .        .
  74  .        .        C11 .   .   .        .
      .        .        .   .   .   .        .
  79  .        .        R5  .   .   .        .
  80  .        .        .   .   R4  .        .
  81  .        .        J4  .   .   .        .
```

---

## 4 — Unchanged Components (20)

U1, J1, Y1, C1, C2, C3, C4, C5, C6, C7, C8, C9, C10, C12, C13, D1, FB1, R1, R3, U2 —
all retain positions from design notes 0009–0011.

---

## 5 — Next Steps

1. **Draw board outline** (Edge.Cuts) — all components are now in final pre-routing
   positions; the left-side extent is defined by SW1 at X≈40, right side by U2/D1 at
   X≈125, top by J1 USB connector.
2. **Run DRC courtyard check** — verify PCM12 (SW1) and J4 (rotated 90°) clear adjacent
   components.
3. **Begin copper routing** — recommended order:
   - Power (GND / +3.3 V pours on B.Cu)
   - USB differential pair (J1 → R3 → U1 PA11/PA12)
   - SWD/SWO (J3 → U1 PA13/PA14/PB3)
   - BOOT0 (SW1 → R2 → U1 pin 44)
   - NRST (C11 → U1 pin 7)
   - I2C (R4/R5 → U1 PB10/PB11)
