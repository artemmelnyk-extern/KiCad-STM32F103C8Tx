# 0003 — HSE Crystal Oscillator Circuit (STM32F103C8T6)

**Date:** 2026-04-26
**Status:** Implemented
**References:**
- ST AN2867 — *Oscillator design guide for STM8S, STM8A and STM32 microcontrollers*
- `docs/datasheets/16MHz-SMD-Crystal-oscillator.png`
- `docs/datasheets/Oscillator-design-guide-for-STM8S-STM8A-and-STM32-microcontrollers-ST-MICRO-1.pdf`

---

## Bill of Materials (machine-readable)

| Ref | Value | lib_id | Footprint | Datasheet |
|-----|-------|--------|-----------|-----------|
| Y1  | 16MHz | Device:Crystal_GND24 | Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm | ~ |
| C10 | 10p   | Device:C | Capacitor_SMD:C_0402_1005Metric | ~ |
| C11 | 10p   | Device:C | Capacitor_SMD:C_0402_1005Metric | ~ |

---

## Context

The STM32F103C8T6 has two high-speed external oscillator pins that support a crystal
resonator circuit for generating the HSE (High Speed External) clock:

| MCU pin | Name        | Net label | Description                          |
|---------|-------------|-----------|--------------------------------------|
| 12      | PD0/OSC_IN  | HSE_IN    | Crystal input / amplifier output     |
| 13      | PD1/OSC_OUT | HSE_OUT   | Crystal output / amplifier input     |

A 16 MHz HSE crystal is the preferred clock source because it allows the internal PLL
to reach the maximum 72 MHz SYSCLK (via the /2 HSE prescaler and ×9 PLL multiplier),
while remaining more stable and accurate than the internal RC oscillator (HSI, ±1 %
over temperature vs < ±50 ppm for a crystal).

The symbol used is `Device:Crystal_GND24` — a four-pin crystal package where pins 2 and
4 are the grounded case pads. This matches common 4-pad SMD crystal packages (e.g.
3225, 5032) in which the two long-side case pads are tied to GND for shielding.

---

## Circuit

### Topology

The STM32 integrates a Pierce oscillator amplifier on the OSC_IN/OSC_OUT pin pair.
Two external load capacitors (C10, C11) complete the resonant tank circuit:

```
MCU PD0 (OSC_IN)                                           MCU PD1 (OSC_OUT)
    │                                                               │
[HSE_IN net] ──────────────────────────────────────────── [HSE_OUT net]
    │                                                               │
    ├── Y1 pin 1 ──────── [crystal Y1 16 MHz] ────── Y1 pin 3 ────┤
    │                      Y1 pins 2, 4 → GND                      │
    │                                                               │
   C11 10p                                                        C10 10p
    │                                                               │
   GND ──────────────────────────────────────────────────────────GND
```

Y1 pins 2 and 4 (case/GND pads) are tied together and connected to the same GND node
as the bottom plates of C10 and C11.

### Net Labels

| Label   | Connects                              |
|---------|---------------------------------------|
| HSE_IN  | Y1 pin 1 ↔ MCU OSC_IN (PD0, pin 12)  |
| HSE_OUT | Y1 pin 3 ↔ MCU OSC_OUT (PD1, pin 13) |

Net labels are used rather than direct wires to keep the schematic readable; the
crystal sub-circuit and the MCU symbol are on different areas of the sheet.

---

## Component Rationale

### Y1 — 16 MHz crystal

A 16 MHz fundamental-mode crystal is chosen as the HSE source:

- 16 MHz is within the HSE frequency range of the STM32F103 (4–16 MHz for the
  internal oscillator drive circuit in the default gain mode).
- 16 MHz → SYSCLK 72 MHz path: HSE/2 = 8 MHz feeds the PLL; PLL ×9 = 72 MHz.
- Fundamental mode at 16 MHz avoids the overtone circuit complexity needed above
  ~30 MHz.

The 4-pin GND24 package provides EMI shielding through the grounded case pads, which
is preferred on a compact PCB where the crystal sits near the MCU.

### C10, C11 — 10 pF load capacitors

The two load capacitors form the feedback network of the Pierce oscillator. The
effective load capacitance seen by the crystal is:

$$C_{L,\text{eff}} = \frac{C_{10} \times C_{11}}{C_{10} + C_{11}} + C_{\text{stray}}$$

With C10 = C11 = 10 pF and an estimated PCB stray capacitance of ~3 pF per node on a
compact 0402 layout:

$$C_{L,\text{eff}} = \frac{10 \times 10}{10 + 10} + 3 \approx 8 \text{ pF}$$

This targets a crystal with a specified load capacitance of **8 pF**, which is common
for small SMD 16 MHz crystals. Verify the selected crystal's CL specification and
adjust C10/C11 if required:

$$C_{\text{ext}} = 2 \times (C_L - C_{\text{stray}})$$

| Crystal CL | Cstray (est.) | C10 = C11 required |
|------------|---------------|--------------------|
| 8 pF       | 3 pF          | 10 pF              |
| 12 pF      | 3 pF          | 18 pF              |
| 16 pF      | 3 pF          | 26 pF (→ 27 pF std value) |

Per ST AN2867 §3.2, using values lower than required reduces startup reliability;
values higher than required increase drive level and may violate the crystal's maximum
drive power (typically 100–500 µW for SMD 16 MHz parts).

---

## Placement Notes

- Place Y1 and C10/C11 as a tightly grouped cluster, as close to MCU pins 12/13 as
  possible (< 5 mm recommended).
- Route HSE_IN and HSE_OUT traces short and direct; minimise trace length to reduce
  stray capacitance and loop area.
- The GND connection for C10, C11 and Y1 case pads must use a short, direct via to the
  ground plane — do **not** share a single via between all three; each component should
  have its own GND via.
- Keep the crystal circuit away from high-frequency switching traces (SPI, I2C, USB
  D+/D−). A keep-out zone under the crystal is recommended on dense boards.
- Do **not** route any signal traces under the crystal body.
