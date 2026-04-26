# 0004 — USB Micro-B Interface (STM32F103C8T6)

**Date:** 2026-04-26
**Status:** Implemented
**References:**
- ST AN4879 — *Introduction to USB hardware and PCB guidelines using STM32 MCUs*
- `docs/datasheets/an4879-introduction-to-usb-hardware-and-pcb-guidelines-using-stm32-mcus-stmicroelectronics.pdf`

---

## Bill of Materials (machine-readable)

| Ref | Value        | lib_id                    | Footprint                                                      | Datasheet |
|-----|--------------|---------------------------|----------------------------------------------------------------|-----------|
| J1  | USB_B_Micro  | Connector:USB_B_Micro     | Connector_USB:USB_Micro-B_Molex_47589-0001                     | ~         |
| R2  | 1k5          | Device:R                  | Resistor_SMD:R_0402_1005Metric                                 | ~         |

---

## Context

The STM32F103C8T6 contains a built-in USB 2.0 Full Speed (FS) device controller
operating at 12 Mbps. Two dedicated pins expose the differential USB data lines:

| MCU pin | Name            | Net label | USB signal |
|---------|-----------------|-----------|------------|
| 21      | PA11 / USB_DM   | USB_D-    | D− (data minus) |
| 22      | PA12 / USB_DP   | USB_D+    | D+ (data plus)  |

These net labels were introduced in the schematic alongside the crystal circuit (0003)
to connect the MCU USB pins to the physical connector added in this change.

A USB Micro-B receptacle (J1) is used as the physical interface. Micro-B is the
prevalent connector on STM32 development boards and is consistent with the Blue Pill
form factor this project references.

---

## Circuit

### Connector pinout — J1 (`Connector:USB_B_Micro`)

| Pin | Name   | Connected to         | Notes                                   |
|-----|--------|----------------------|-----------------------------------------|
| 1   | VBUS   | VBUS power net       | 5 V supply from USB host                |
| 2   | D−     | USB_D− net label     | → MCU PA11 (pin 21)                     |
| 3   | D+     | USB_D+ net label     | → MCU PA12 (pin 22); also R2 pull-up    |
| 4   | ID     | No-connect           | OTG host/device detect — not used       |
| 5   | GND    | GND                  | USB signal return / power return        |
| 6   | Shield | No-connect           | Mechanical shell — tied to GND on PCB  |

> Pin 6 (shield) is left as no-connect on the schematic symbol; it should be connected
> to the GND copper pour on the PCB through a short trace or thermal relief to provide
> shielding without creating a ground loop.

### D+ pull-up — R2 (1.5 kΩ)

```
+3.3V
  │
 R2  1.5 kΩ
  │
  ├──── USB_D+ ──── J1 pin 3 ──── [cable] ──── host D+
  │
 MCU PA12 (USB_DP, pin 22)
```

```
J1 pin 2 ──── USB_D− ──── MCU PA11 (USB_DM, pin 21)

J1 pin 1 ──── VBUS
J1 pin 5 ──── GND
```

### Power net topology

| Net    | Source         | Voltage | Description                                       |
|--------|----------------|---------|---------------------------------------------------|
| VBUS   | J1 pin 1       | 5 V     | USB bus voltage, supplied by the USB host         |
| +3.3V  | Voltage reg.   | 3.3 V   | Regulated MCU supply (regulator fed from VBUS)    |

VBUS and +3.3V are separate nets. The 3.3 V regulator (not shown in this sub-circuit)
is powered from VBUS. The D+ pull-up R2 connects to the regulated +3.3V rail, not to
VBUS directly.

---

## Component Rationale

### J1 — USB Micro-B receptacle

USB Micro-B is chosen for physical compatibility with standard USB cables used on
Blue Pill-style STM32 boards. The 5-pin + shell connector provides VBUS, D−, D+, and
GND signals. The ID pin (pin 4) is unused because only USB device mode is implemented;
OTG host-detection (which requires reading the ID pin level) is not used.

### R2 — 1.5 kΩ D+ pull-up

USB Full Speed device enumeration is signalled to the host by pulling D+ to 3.3 V
through a 1.5 kΩ resistor. When the host detects this pull-up it identifies the
attached device as Full Speed (12 Mbps) and initiates enumeration.

USB 2.0 specification §7.1.5 defines:
- **Full Speed device:** 1.5 kΩ ± 5 % pull-up on D+ to V(OPR) (3.0–3.6 V).
- **Low Speed device:** 1.5 kΩ ± 5 % pull-up on D− to V(OPR).

The 1.5 kΩ value (E96 standard: 1500 Ω, E24 nearest: 1.5 kΩ) is specified directly;
0402 SMD footprint is consistent with the rest of the board passives.

> **Note on software-controlled pull-up:** The STM32F103 does not have an integrated
> programmable pull-up on USB_DP. The external resistor R2 is required. Some STM32
> designs add a GPIO-controlled transistor to disconnect R2 under software control (to
> force USB re-enumeration without a power cycle). This is not implemented here; if
> required, a small NPN or N-FET in series with R2 between D+ and +3.3V can be added.

---

## USB Clock Requirement

The USB peripheral requires a precise 48 MHz USB clock, which must be derived from
the PLL. With the 16 MHz HSE crystal added in 0003:

$$48\,\text{MHz} = \frac{16\,\text{MHz}}{2} \times 6 = 8\,\text{MHz} \times 6$$

This is configured in firmware via the RCC registers:
- `PLLSRC` = HSE / 2 (PREDIV1 = /2) → 8 MHz PLL input
- `PLLMUL` = × 6 → 48 MHz (USB clock via `USBPRE` = /1)
- `PLLMUL` = × 9 → 72 MHz SYSCLK (simultaneously)

> The USB peripheral cannot be clocked from the HSI RC oscillator (±1 % accuracy is
> insufficient for USB timing). The 16 MHz crystal in 0003 is therefore a prerequisite
> for USB operation.

---

## PCB Placement and Routing Notes

Per ST AN4879:

- Route D+ and D− as a **differential pair** with matched length (< 0.2 mm mismatch)
  and 90 Ω differential impedance (≈ 45 Ω single-ended on a standard 1.6 mm FR4 2-layer
  board: ~0.2 mm trace width, 0.2 mm spacing).
- Keep USB traces away from the crystal/oscillator circuit (0003), SPI clock lines, and
  switching regulator traces.
- Place R2 close to J1 pin 3, not near the MCU, to keep the stub length short.
- A ground pour or ground stitching vias along the D+/D− traces reduces EMI.
- The VBUS trace must be rated for 500 mA (USB 2.0 max) — a 0.3 mm trace is sufficient
  on 1 oz copper for short distances.
- Add a 100 nF decoupling capacitor on VBUS close to J1 pin 1 if the regulator input
  capacitor is far from the connector.
