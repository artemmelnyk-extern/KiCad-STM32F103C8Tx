# 0006 — Electrical Rules Check and Annotations (STM32F103C8T6)

**Date:** 2026-04-26
**Status:** Implemented
**References:** KiCad ERC documentation

---

## Summary of Changes

This revision makes no functional or component changes. It resolves all KiCad Electrical
Rules Check (ERC) violations, adds schematic title block metadata, adds in-schematic
annotation text, and repositions several components within the power supply area for
improved readability.

---

## 1 — PWR_FLAG: Resolving ERC "Power Pin Not Driven" Errors

### Problem

KiCad's ERC checks that every power net has a **driver** — a pin with type `power_out`.
Passive power symbols (`power:+3.3V`, `power:VBUS`, `power:GND`, etc.) have a pin of
type `power_in`, not `power_out`. When a power net is supplied by an external source
(e.g. via a connector or an off-sheet regulator) rather than an on-sheet `power_out` pin,
KiCad cannot resolve the driver and reports:

```
ERC error: Pin not connected / Power pin not driven
```

### Solution: PWR_FLAG (#FLG01)

A `power:PWR_FLAG` symbol was placed on the **+3.3VA** (VDDA) net at position (215.9, 36.83).

```
+3.3VA ──┬── [VDDA filter network] ── MCU VDDA
         │
        #FLG01 (PWR_FLAG)
```

`PWR_FLAG` is a zero-footprint, no-BOM symbol whose sole purpose is to expose a
`power_out` pin onto the net, satisfying the ERC driver rule. It has no electrical
effect in the circuit — it is an annotation artefact only.

| Reference | lib_id          | Net    | Purpose                                |
|-----------|-----------------|--------|----------------------------------------|
| #FLG01    | power:PWR_FLAG  | +3.3VA | Suppresses "power pin not driven" ERC on VDDA net |

> **Why VDDA?** The VDDA net is derived from +3.3V through an LC filter (see note 0001).
> Because its driver (the +3.3V regulator VO pin) is on a different net name, KiCad
> cannot automatically trace the supply chain. PWR_FLAG makes the VDDA net self-consistent
> from the ERC perspective.

---

## 2 — Title Block Metadata

The schematic title block was populated for the first time:

| Field    | Value              |
|----------|--------------------|
| Title    | UDEMY STM32 Demo   |
| Date     | 2026-04-26         |
| Revision | 0.0.1              |

This information appears in the sheet border/title block printed on schematic exports
(PDF, SVG). It provides version traceability and identifies the project.

---

## 3 — Schematic Annotation Text

Eight in-schematic text labels were added to document design intent directly on the
schematic sheet. These are non-electrical drawing annotations (no reference, no BOM
entry, no ERC participation).

| Text                                                                       | Location (approx.) | Purpose |
|----------------------------------------------------------------------------|--------------------|---------|
| `Power supply`                                                             | Power supply area  | Section heading |
| `VBUS from USB connector. Normally it is +5V. Minimum 22uF inp./outp caps`| Near U2/C12/C13    | Reminds the designer of input/output bulk cap requirement |
| `Microcontroller and USB`                                                  | MCU area heading   | Section heading |
| `1x 100nF capacitor per VDD pin`                                           | Decoupling area    | States the decoupling rule (see note 0001) |
| `VDDA Filtering`                                                           | VDDA filter area   | Section heading for the VDDA LC filter |
| `CL=2*(CLO-Cs)=2*(10-5)pF=10pF`                                           | Crystal area       | Documents the crystal load capacitor calculation (see note 0003) |
| `USB Application Note AN 4879`                                             | USB area           | Cross-reference to the ST USB hardware guidelines |
| `Pin-out using STM32CubeIDE`                                               | Connector area     | Documents that MCU pin assignments were configured in CubeIDE |

The crystal load capacitance annotation formalises the calculation already implicit in
note 0003:

$$C_L = 2 \times (C_{L,osc} - C_s) = 2 \times (10 - 5)\,\text{pF} = 10\,\text{pF}$$

where $C_{L,osc}$ is the crystal's specified load capacitance and $C_s$ is the estimated
PCB stray capacitance per pin.

---

## 4 — Component Repositioning (Power Supply Area)

Several components in the power supply and power LED circuits were shifted to improve
schematic readability and wire routing cleanliness. No values, footprints, or net
connections changed — only (x, y) placement coordinates.

| Reference | Old position (mm)   | New position (mm)   | Description |
|-----------|---------------------|---------------------|-------------|
| VBUS #PWR | (25.4, 41.91)       | (30.48, 40.64)      | VBUS power symbol |
| C13       | (25.4, 53.34)       | (30.48, 53.34)      | +3.3V output bulk cap |
| +3.3V #PWR (C13 side) | (62.23, 41.91) | (55.88, 40.64) | +3.3V power symbol |
| C12       | (62.23, 52.07)      | (55.88, 52.07)      | VBUS input bulk cap |
| D1        | (86.36, 48.26)      | (66.04, 48.26)      | Power LED |
| R3        | (97.79, 53.34)      | (77.47, 53.34)      | LED current-limiting resistor |
| PWR_LED_K label | (92.71, 48.26) | (72.39, 48.26)  | Cathode net label |
| GND (U2 output) | (45.72, 76.2) | (45.72, 64.77)   | GND symbol on regulator output side |
| +3.3VA #PWR | (200.66, 26.67) | (200.66, 30.48)   | VDDA power symbol |

The LED chain (R3 → D1) was shifted approximately 20 mm to the left, shortening the
horizontal span of the power supply section. Wire segments and junction points were
updated accordingly throughout.

---

## 5 — ngspice Settings Added to Project File

The `.kicad_pro` project file gained an `ngspice` settings block:

```json
"ngspice": {
  "fix_include_paths": true,
  "meta": { "version": 0 },
  "model_mode": 4,
  "workbook_filename": ""
}
```

This was added automatically by KiCad when the schematic editor was opened with the
ngspice simulation plugin active. It has no effect on the PCB or BOM — it is a UI
preference block only.

---

## Checklist: Changes with No Functional Impact

| Change type                | Functional impact | BOM impact | PCB footprint impact |
|----------------------------|:-----------------:|:----------:|:--------------------:|
| PWR_FLAG (#FLG01) placed   | None              | No (DNP / no footprint) | None |
| Title block filled         | None              | No         | None |
| Schematic text annotations | None              | No         | None |
| Component repositioning    | None              | No         | None (only schematic coords) |
| Wire/junction rerouting    | None              | No         | None |
| ngspice project settings   | None              | No         | None |
