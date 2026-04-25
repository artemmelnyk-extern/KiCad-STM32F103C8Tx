# 0001 — Power Decoupling Network (STM32F103C8T6)

**Date:** 2026-04-25
**Status:** Implemented
**References:** ST AN2834 — *How to achieve EMC compliance with STM32 microcontrollers*

---

## Bill of Materials (machine-readable)

| Ref | Value | lib_id | Footprint | Datasheet |
|-----|-------|--------|-----------|-----------|
| U1  | STM32F103C8T6 | MCU_ST_STM32F1:STM32F103C8Tx | Package_QFP:LQFP-48_7x7mm_P0.5mm | https://www.st.com/resource/en/datasheet/stm32f103c8.pdf |
| FB1 | 120R | Device:FerriteBead | Inductor_SMD:L_0402_1005Metric | ~ |
| C1  | 100n | Device:C | Capacitor_SMD:C_0402_1005Metric | ~ |
| C2  | 100n | Device:C | Capacitor_SMD:C_0402_1005Metric | ~ |
| C3  | 100n | Device:C | Capacitor_SMD:C_0402_1005Metric | ~ |
| C4  | 100n | Device:C | Capacitor_SMD:C_0402_1005Metric | ~ |
| C5  | 10u  | Device:C | Capacitor_SMD:C_0402_1005Metric | ~ |
| C6  | 10n  | Device:C | Capacitor_SMD:C_0402_1005Metric | ~ |
| C7  | 1u   | Device:C | Capacitor_SMD:C_0402_1005Metric | ~ |
| C8  | 1u   | Device:C | Capacitor_SMD:C_0402_1005Metric | ~ |

---

## Context

The STM32F103C8T6 (LQFP-48) has two separate supply domains that require independent
decoupling strategies:

| Domain | Pins | Description |
|---|---|---|
| VDD | pins 19, 32, 48 | Digital core and I/O supply |
| VDDA | pin 5 | Analog supply (ADC, DAC, PLL, RC oscillator) |
| VBAT | pin 1 | Backup domain (RTC, backup registers) |

ST strongly recommends isolating VDDA from VDD with a ferrite bead to prevent digital
switching noise from corrupting ADC measurements (AN2834, section 2.2).

---

## Decoupling Network — Component List

### Digital supply (VDD → +3.3V rail)

| Ref | Value | Purpose |
|---|---|---|
| C1 | 100 nF | Local HF decoupling, VDD pin 19 |
| C2 | 100 nF | Local HF decoupling, VDD pin 32 |
| C3 | 100 nF | Local HF decoupling, VDD pin 48 |
| C4 | 100 nF | Local HF decoupling, VBAT pin 1 |
| C5 | 10 µF  | Bulk reservoir capacitor for VDD rail |

> One 100 nF ceramic cap per VDD/VBAT pin, placed as close as possible to the pin.
> Bulk cap C5 handles slower load transients from GPIO toggling and peripheral startup.

### Analog supply (VDDA → +3.3VA filtered rail)

| Ref | Value | Purpose |
|---|---|---|
| FB1 | 120 Ω @ 100 MHz | Ferrite bead — isolates VDDA from VDD digital noise |
| C7  | 1 µF  | Low-frequency filtering on VDDA (after ferrite) |
| C8  | 1 µF  | Additional bulk on VDDA node |
| C6  | 10 nF | High-frequency filtering on VDDA |

> The ferrite bead FB1 (120 Ω at 100 MHz) creates a low-pass filter together with C6/C7/C8.
> This prevents digital switching transients on +3.3V from coupling into the ADC reference.

---

## Power Rail Topology

```
+3.3V ──────┬──── C5 (10µF) ──── GND       ← Bulk
            ├──── C1 (100n) ──── GND        ← VDD pin 19
            ├──── C2 (100n) ──── GND        ← VDD pin 32
            ├──── C3 (100n) ──── GND        ← VDD pin 48
            ├──── C4 (100n) ──── GND        ← VBAT pin 1
            │
            └── FB1 (120R) ─┬─ +3.3VA
                            ├── C7 (1µF)  ── GND
                            ├── C8 (1µF)  ── GND
                            └── C6 (10nF) ── GND   → VDDA pin 5
```

---

## Design Decisions

### Why 100 nF for VDD pins?
100 nF ceramic (X7R/X5R) provides low impedance in the 1–100 MHz range where MCU
switching transients occur. Per ST reference designs and AN2834.

### Why 10 µF bulk?
Handles slower load steps (e.g., when multiple GPIO ports switch simultaneously or a
peripheral is enabled). One bulk cap is sufficient for a single-supply LQFP-48 board.

### Why 120 Ω ferrite bead for VDDA?
The impedance at 100 MHz is high enough to block digital noise while DC resistance is
low enough (typically < 0.5 Ω) not to cause significant voltage drop at VDDA currents
(< 10 mA typical for ADC use). Higher impedance beads (600 Ω+) could cause supply
instability under transient load.

### Why 10 nF on VDDA in addition to 1 µF?
The two cap values cover different frequency bands. 1 µF handles lower frequencies;
10 nF maintains low impedance above ~10 MHz where ferrite bead effectiveness drops off.

### Footprints
All capacitors: 0402 (1005 metric). Selected for compact placement near MCU pins.
Ferrite bead FB1: 0402.

---

## Placement Notes

- All VDD decoupling caps must be placed on the **same side as the MCU**, within 1–2 mm
  of each VDD/GND pin pair.
- FB1 + VDDA caps form an island: route +3.3VA trace short and keep it away from
  high-speed signal traces (SPI, I2C, USART).
- GND via directly under each cap recommended (single via per cap, not shared).

---

## References

- ST AN2834 — *How to achieve EMC compliance with STM32 microcontrollers*
  https://www.st.com/resource/en/application_note/an2834-how-to-achieve-emc-compliance-with-stm32-microcontrollers-stmicroelectronics.pdf
- STM32F103C8T6 Datasheet — see `docs/datasheets/`
- ST Reference Manual RM0008
