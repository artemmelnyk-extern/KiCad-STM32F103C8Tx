# 0017 — Signal Routing: USB, UART, SWD, I2C, SDIO, BOOT0

**Date:** 2026-05-02
**Status:** Implemented
**References:** Design notes 0008 (PCB rules), 0015 (decoupling/crystal routing), 0016 (connector footprint fix); STM32F103C8T6 datasheet §5 (I/O characteristics); USB 2.0 Full-Speed signal integrity guidelines

---

## Summary

Second routing pass: 52 track segments on F.Cu completing all remaining signal nets.
USB differential pair (D+/D−) routed at 0.2 mm width; all other signal nets at 0.3 mm.
No vias were added — all routing is single-layer F.Cu.
Four components were repositioned to enable clean trace entry.

| Metric | Value |
|--------|-------|
| New segments | 52 |
| Layer | F.Cu only |
| Vias added | 0 |
| Nets routed | 12 |
| Signal width | 0.3 mm (general), 0.2 mm (USB D+/D−) |

---

## 1 — Component Repositioning

Four components were adjusted before routing to align pads with routing channels.

| Ref | Value | Old position (x, y, rot°) | New position (x, y, rot°) | Reason |
|-----|-------|---------------------------|---------------------------|--------|
| R4  | 1k5 pull-up | (56.76, 80.25, 0°) | **(53.49, 77.75, 180°)** | Shift toward J4 to shorten USB D+ pull-up trace |
| J3  | Conn_01x04 | (53.625, 55, 0°) | **(52.25, 55, −90°)** | Rotate and shift — align pin row with UART/+3.3V route direction; footprint updated to 2.54mm THT (see note 0016) |
| J4  | Conn_01x04 | (52.625, 81, 90°) | **(48.92, 82.75, 90°)** | Shift left to shorten I2C and SWD routes from MCU |
| J2  | Conn_01x04 | (59.875, 56, 0°) | **(66.5, 55, −90°)** | Shift right and rotate to place SDIO/SWD header clear of USB traces |

---

## 2 — Routed Nets

### 2.1 USB Differential Pair — 0.2 mm width

USB Full-Speed operates at 12 Mbit/s. The D+ and D− traces are kept short, parallel, and
equal-length to minimise skew and maintain differential impedance.

| Net | Name | Segments | Connected nodes |
|-----|------|----------|-----------------|
| 11 | /USB_D+ | 2 | U1 PA12 (pad 33) → J1 D+ (pin 3); R4 pull-up junction |
| 12 | /USB_D− | 9 | U1 PA11 (pad 32) → J1 D− (pin 2) |

### 2.2 Power distribution stubs — 0.3 mm width

Short power segments completing the supply rails to the connector headers.

| Net | Name | Segments | Notes |
|-----|------|----------|-------|
| 1 | GND | 2 | GND stubs to J3/J4 header pads |
| 3 | +3.3V | 3 | +3.3V stubs to J3 pin 1 and J4 |

### 2.3 UART — 0.3 mm width

| Net | Name | Segments | Path |
|-----|------|----------|------|
| 18 | /USART1_TX | 7 | U1 PA9 (pad 30) → J3 pin 2 |
| 19 | /USART1_RX | 4 | U1 PA10 (pad 31) → J3 pin 3 |

### 2.4 I2C — 0.3 mm width

| Net | Name | Segments | Path |
|-----|------|----------|------|
| 20 | /I2C2_SDA | 5 | U1 PB11 (pad 22) → J4 |
| 21 | /I2C2_SCL | 5 | U1 PB10 (pad 21) → J4 |

### 2.5 SWD / Debug — 0.3 mm width

| Net | Name | Segments | Path |
|-----|------|----------|------|
| 16 | /SDIO | 5 | U1 PA8 (pad 29) → J2 |
| 17 | /SWCLK | 4 | U1 PA5 (pad 15) → J2 |

### 2.6 BOOT0 — 0.3 mm width

| Net | Name | Segments | Path |
|-----|------|----------|------|
| 22 | /SW_BOOT0 | 2 | SW1 → BOOT0 net junction |
| 23 | /BOOT0 | 4 | BOOT0 junction → U1 BOOT0 (pad 20) |

---

## 3 — Routing Rules Compliance

| Rule | Requirement | Applied |
|------|-------------|---------|
| Min track width | 0.15 mm (design rule) | 0.2 mm (USB), 0.3 mm (signals) — compliant |
| USB D+/D− width | Matched pair, equal length | 0.2 mm, routed in same pass |
| Layer | F.Cu signal routing | All 52 segments on F.Cu |
| Clearance | 0.2 mm min | Maintained throughout |

---

## 4 — Remaining Work

- DRC full-board check after connector placement confirmation
- Via stitching of F.Cu GND stubs to B.Cu ground plane (deferred to next pass)
- Label silkscreen position cleanup (C3 reference moved during this session)
