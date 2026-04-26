# 0007 — Footprint Assignment (STM32F103C8T6)

**Date:** 2026-04-26
**Status:** Implemented
**References:** KiCad footprint library (built-in)

---

## Summary

All schematic symbols that previously had an empty `Footprint` field were assigned PCB
footprints using **KiCad Tools → Assign Footprints**. This is the first full footprint
pass; U1 (STM32F103C8T6) and U2 (AMS1117-3.3) were already assigned in earlier commits
and are unchanged here.

A total of **26** footprint fields changed from `""` to a named KiCad library footprint.
No values, reference designators, or net connections were modified.

---

## Full Footprint Assignment Table

| Ref  | Value              | Footprint                                                               | Package / Notes |
|------|--------------------|-------------------------------------------------------------------------|-----------------|
| **Connectors** |
| J1   | USB Micro-B        | `Connector_USB:USB_Micro-B_Wuerth_629105150521`                        | Würth 629105150521, through-hole tabs |
| J2   | Conn_01x04         | `Connector_PinHeader_1.00mm:PinHeader_1x04_P1.00mm_Vertical_SMD_Pin1Right` | 1.00 mm pitch SMD, pin 1 right |
| J3   | Conn_01x04         | `Connector_PinHeader_1.00mm:PinHeader_1x04_P1.00mm_Vertical_SMD_Pin1Right` | 1.00 mm pitch SMD, pin 1 right |
| J4   | Conn_01x04         | `Connector_PinHeader_1.00mm:PinHeader_1x04_P1.00mm_Vertical_SMD_Pin1Right` | 1.00 mm pitch SMD, pin 1 right |
| **Passives — Capacitors** |
| C1   | 22 µF              | `Capacitor_SMD:C_0805_2012Metric`                                      | 0805 — +3.3V output bulk cap (U2 VO) |
| C2   | 22 µF              | `Capacitor_SMD:C_0805_2012Metric`                                      | 0805 — VBUS input bulk cap (U2 VI) |
| C3   | (VDD/VDDA bulk)    | `Capacitor_SMD:C_0603_1608Metric`                                      | 0603 — larger bypass (e.g. 1 µF); leftmost MCU supply cap |
| C4   | 100 nF             | `Capacitor_SMD:C_0402_1005Metric`                                      | 0402 — VDD decoupling |
| C5   | 100 nF             | `Capacitor_SMD:C_0402_1005Metric`                                      | 0402 — VDD decoupling |
| C6   | 100 nF             | `Capacitor_SMD:C_0402_1005Metric`                                      | 0402 — VDD decoupling |
| C7   | 100 nF             | `Capacitor_SMD:C_0402_1005Metric`                                      | 0402 — VDD decoupling |
| C8   | 100 nF             | `Capacitor_SMD:C_0402_1005Metric`                                      | 0402 — VDD decoupling |
| C9   | 100 nF             | `Capacitor_SMD:C_0402_1005Metric`                                      | 0402 — VDD decoupling |
| C10  | 100 nF             | `Capacitor_SMD:C_0402_1005Metric`                                      | 0402 — VDD decoupling |
| C11  | 100 nF             | `Capacitor_SMD:C_0402_1005Metric`                                      | 0402 — NRST filter cap |
| C12  | 22 pF              | `Capacitor_SMD:C_0402_1005Metric`                                      | 0402 — HSE crystal load cap |
| C13  | 22 pF              | `Capacitor_SMD:C_0402_1005Metric`                                      | 0402 — HSE crystal load cap |
| **Passives — Resistors** |
| R1   | 1.5 kΩ             | `Resistor_SMD:R_0402_1005Metric`                                       | 0402 — Power LED current limiter |
| R2   | 10 kΩ              | `Resistor_SMD:R_0402_1005Metric`                                       | 0402 — BOOT0 series resistor |
| R3   | 1.5 kΩ             | `Resistor_SMD:R_0402_1005Metric`                                       | 0402 — USB D+ pull-up |
| R4   | 1.5 kΩ             | `Resistor_SMD:R_0402_1005Metric`                                       | 0402 — I2C2 SCL pull-up |
| R5   | 1.5 kΩ             | `Resistor_SMD:R_0402_1005Metric`                                       | 0402 — I2C2 SDA pull-up |
| **Active / Semiconductor** |
| D1   | RED                | `LED_SMD:LED_0603_1608Metric`                                          | 0603 LED — power indicator |
| **Electromechanical** |
| SW1  | BOOT0 switch       | `Button_Switch_THT:SW_E-Switch_EG1224_SPDT_Angled`                    | THT, SPDT angled slide switch |
| Y1   | 16 MHz crystal     | `Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm`                             | 3.2 × 2.5 mm 4-pad SMD |
| FB1  | Ferrite bead       | `Inductor_SMD:L_0603_1608Metric`                                       | 0603 (standard ferrite bead SMD size) |

**Already assigned (unchanged):**

| Ref  | Footprint                                         |
|------|---------------------------------------------------|
| U1   | `Package_QFP:LQFP-48_7x7mm_P0.5mm`               |
| U2   | `Package_TO_SOT_SMD:SOT-223-3_TabPin2`            |

---

## Footprint Selection Rationale

### Capacitors

| Case | Footprint | Reason |
|------|-----------|--------|
| C1, C2 — 22 µF bulk | 0805 | 22 µF in X5R/X7R ceramic is readily available in 0805; 0402/0603 22 µF parts have very low voltage rating or poor capacitance derating |
| C3 — larger bypass | 0603 | Assigned a 0603 pad to accommodate a 1 µF (or higher) value bulk capacitor alongside the 100 nF 0402 decouplers; 0603 allows 1 µF X7R with good voltage margin |
| C4–C11 — 100 nF | 0402 | 100 nF 0402 is the industry standard for high-frequency VDD decoupling; small footprint enables placement directly under MCU body |
| C12, C13 — 22 pF crystal load | 0402 | 22 pF NP0/C0G in 0402 provides the required low-loss, temperature-stable capacitance for the HSE oscillator |

### Connectors

J2, J3, J4 use **1.00 mm pitch SMD** pin headers (`PinHeader_1x04_P1.00mm_Vertical_SMD_Pin1Right`).
This is a compact SMD footprint suitable for low-profile board-to-board or board-to-cable
connections.

> **Note:** If through-hole 2.54 mm pitch (standard 0.1") headers are preferred for hand
> soldering or breadboard use, replace with
> `Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical` at layout time.

### SW1 — BOOT0 Switch

`Button_Switch_THT:SW_E-Switch_EG1224_SPDT_Angled` is a through-hole SPDT angled slide
switch. THT was chosen for mechanical robustness — the BOOT0 switch is manipulated by
hand during firmware programming and benefits from stronger solder joints than SMD.

### Y1 — 16 MHz Crystal

`Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm` matches the 4-pad 3225 package standard for
the crystal specified in design note 0003. Pins 2 and 4 are GND (chassis) pads;
the symbol `Device:Crystal_GND24` reflects this.

### FB1 — Ferrite Bead

`Inductor_SMD:L_0603_1608Metric` is the standard 0603 pad used for ferrite beads in the
KiCad library. All common ferrite bead manufacturers (Murata BLM series, TDK MMZ series)
supply 0603-footprint parts for VDDA filtering.

---

## Checklist

| Item                                       | Functional impact | BOM impact |
|--------------------------------------------|:-----------------:|:----------:|
| 26 footprints assigned (was `""`)          | None              | No (values unchanged) |
| U1, U2 footprints unchanged                | None              | No |
