# 0021 — USB Hub Integration (Microchip USB2514B)

**Date:** 2026-05-06
**Status:** Proposed — Rev B design
**References:**
- Phil's Lab #86 — *(Sponsored) USB Hub Design Walkthrough* — `docs/feature-notes/NoteGPT_TRANSCRIPT_(Sponsored) USB Hub Design Walkthrough - Phil's Lab #86.txt`
- Microchip USB2514B datasheet
- Design notes 0004 (USB Micro-B), 0005 (Power Supply), 0017 (Signal Routing), 0020 (BOM)

---

## 1 — Motivation

The Rev A board (0001–0020) exposes the STM32F103C8T6 USB Full Speed device interface
directly through one Micro-B connector (J1). This gives the board a single USB interface
to the host PC with no ability to simultaneously attach USB peripherals.

Adding a USB hub IC between the host PC and the two MCUs provides:

1. **Dual-MCU capability** — Two independent STM32F103C8T6 MCUs are visible simultaneously
   to the host PC as two distinct USB Full Speed devices on one cable.
2. **Two free USB-A ports** — Downstream ports 3 and 4 expose USB-A female connectors with
   MIC2099 load switches for bench peripherals (logic analyser, USB-serial, USB storage).
3. **Self-contained multi-device board** — No USB hub dongle needed on the bench.
4. **Learning outcome** — Full implementation of the USB2514B design covered in Phil's Lab #86.

---

## 2 — Architecture Decision

### 2.1 — Options considered

| Option | Description | Decision |
|--------|-------------|----------|
| A | 1 STM32 on port 1, three USB-A on ports 2–4 | Superseded |
| **B** | **2 STM32s on ports 1–2, two USB-A on ports 3–4** | ✅ **Selected** |
| C | STM32 as USB host via OTG | ✗ Not possible: F103C8T6 has no USB Host / OTG |

### 2.2 — Selected topology

```
PC / USB Host
     │
  [Micro-B J1]  ← existing connector; repurposed as hub upstream
     │   VBUS_DET
     ▼
┌──────────────────────────────────────────┐
│        USB2514B  (USB 2.0 HS Hub)        │
│  24 MHz crystal (Y2)  │  3.3 V LDO (U4) │
│  Strapping resistors (no EEPROM)         │
└──┬──────────┬──────────┬──────────┬──────┘
   │ Port 1   │ Port 2   │ Port 3   │ Port 4
   ▼          ▼          ▼          ▼
STM32 #1   STM32 #2   USB-A J6   USB-A J7
(U1)       (U_MCU2)   +MIC2099   +MIC2099
PA11/PA12  PA11/PA12  (U5)       (U6)
(via D6)   (via D7)
```

> Both STM32 MCUs connect to hub downstream ports via USBLC6-2SC6 ESD arrays.
> Each STM32 appears as an independent USB Full Speed (12 Mbps) device to the host PC.
> The two USB-A connectors (J6, J7) each have a MIC2099 500 mA load switch and
> 100 µF bulk capacitance per the USB standard.

---

## 3 — New Components (Rev B BOM additions)

### 3.1 — Hub IC

| Ref | Value | Package | Description |
|-----|-------|---------|-------------|
| U3  | USB2514B-I/MG | QFN-36 (5 × 5 mm, 0.5 mm pitch) | Microchip 4-port USB 2.0 HS Hub |

### 3.2 — Hub power supply

| Ref | Value | Footprint | Notes |
|-----|-------|-----------|-------|
| U4  | AMS1117-3.3 (or MCP1700-3302) | SOT-223-3 | Dedicated 3.3 V LDO for hub IC; keeps hub supply independent from MCU rail |
| C20 | 22 µF | C_0805 | U4 input bulk cap |
| C21 | 22 µF | C_0805 | U4 output bulk cap |
| FB2 | 600 Ω / 1 A ferrite bead | L_0603 | Pi-filter series element (5 V input to U4) |
| C22 | 10 µF | C_0603 | Pi-filter input cap |
| C23 | 10 µF | C_0603 | Pi-filter output cap |

> The Rev A AMS1117-3.3 (U2) is rated 1 A. Its load budget (MCU + crystal + LEDs) is
> ≈ 120 mA. Adding hub VDD (≈ 100 mA) would be within its rating but a separate LDO
> cleanly isolates noise paths and preserves margin.

### 3.3 — Hub crystal

| Ref | Value | Footprint | Notes |
|-----|-------|-----------|-------|
| Y2  | 24 MHz | Crystal_SMD_3225-4Pin_3.2x2.5mm | Hub clock source (USB2514B requires 24 MHz) |
| C24 | 10 pF | C_0402 | Load cap Y2 (CL = 9 pF, ~4 pF stray → 10 pF per leg) |
| C25 | 10 pF | C_0402 | Load cap Y2 |
| R6  | DNP (1 MΩ) | R_0402 | Feedback resistor — do not place; USB2514B has internal 1 MΩ |

### 3.4 — Hub IC passives

| Ref | Value | Footprint | Notes |
|-----|-------|-----------|-------|
| R7  | 12 kΩ | R_0402 | RBIAS pin to GND (bias current reference) |
| R8  | 100 kΩ | R_0402 | VBUS_DET divider top (5 V → 2.5 V) |
| R9  | 100 kΩ | R_0402 | VBUS_DET divider bottom (2.5 V → GND) |
| R10 | 100 kΩ | R_0402 | CFG_SEL0 pull-down (self-powered, individual port switching) |
| R11 | 100 kΩ | R_0402 | CFG_SEL1 pull-down |
| R12 | 100 kΩ | R_0402 | NON_REM0 pull-down (all ports removable) |
| R13 | 100 kΩ | R_0402 | NON_REM1 pull-down |
| C26–C33 | 100 nF | C_0402 | VDD / VDDA bypass (one per power pin, per datasheet) |
| C34 | 2.2 µF | C_0402 | Bulk bypass across hub VDD |
| C35, C36 | Per datasheet | C_0402 | PLL filter caps (values from USB2514B datasheet §5) |

### 3.5 — Hub upstream ESD (host-side)

| Ref | Value | Footprint | Notes |
|-----|-------|-----------|-------|
| D2  | USBLC6-2SC6 | SOT-23-6 | ESD on J1 D+/D− and VBUS; place ≤ 2 mm from J1 |

### 3.6 — USB-A downstream connectors + ESD + load switches (×3, ports 2–4)

Each port (P2, P3, P4) requires identical circuitry:

| Ref | Value | Footprint | Notes |
|-----|-------|-----------|-------|
| J5/J6/J7 | USB_A_Female | USB_A_Amphenol_61729-0010BLF | USB-A female downstream |
| D3/D4/D5 | USBLC6-2SC6 | SOT-23-6 | ESD on D+/D− of each downstream port |
| U5/U6/U7 | MIC2099 | SOT-23-5 | Load switch, 500 mA current limit |
| R14/R16/R18 | 330 Ω | R_0402 | ILIM resistor → ~500 mA current limit |
| R15/R17/R19 | DNP (100 kΩ) | R_0402 | OC# pull-up — DNP (USB2514B has internal pull-up) |
| C37–C42 | 100 µF / 6.3 V | C_1206 | Bulk capacitance at each USB-A VBUS pin (USB 2.0 standard) |
| LED2/3/4 | GREEN | LED_0402 | Per-port "power-on" indicator |
| R20/R21/R22 | 1 kΩ | R_0402 | LED current limit resistors |

### 3.7 — Port 1 downstream ESD (STM32 side)

| Ref | Value | Footprint | Notes |
|-----|-------|-----------|-------|
| D6  | USBLC6-2SC6 | SOT-23-6 | ESD on hub P1 D+/D− lines (between hub IC and STM32 PA11/PA12) |

> No load switch is needed on port 1: the STM32 draws < 150 mA and is permanently powered
> from the board supply, not USB VBUS.

---

## 4 — Schematic Modifications (Rev B)

### 4.1 — Changes to existing nets

| Change | Detail |
|--------|--------|
| **Remove** J1 → MCU USB direct connection | Traces from J1 pin 2 (D−) and pin 3 (D+) no longer go to PA11/PA12; they now terminate at USB2514B UPSTREAM port pins (DP_UP, DM_UP) via D2 ESD array |
| **Retain** J1 VBUS → VBUS power net | VBUS net unchanged; J1 pin 1 still powers the board |
| **Retain** R2 (1.5 kΩ D+ pull-up on PA12) | Removed from J1 D+ net; re-attached to hub downstream port 1 D+ if needed — check USB2514B datasheet: internal pull-ups on downstream port DP/DM are managed by the hub; R2 is removed or re-purposed |
| **Add** VBUS_DET net | R8/R9 divider from J1 VBUS to USB2514B VBUS_DET pin and U4 enable pin |

### 4.2 — New schematic sheet (recommended)

Add **Sheet 2: USB Hub** containing:

1. **Power section** — J1 VBUS → FB2 pi-filter → U4 LDO → HUB_3V3 net
2. **Hub IC (U3)** — All pins labelled with net names
3. **Crystal section** — Y2, C24, C25, R6(DNP)
4. **Strapping / config** — R10–R13 with annotation comments
5. **VBUS_DET divider** — R8, R9
6. **Upstream port** — D2 ESD array → U3 UPSTREAM port; net labels /HUB_DM_UP, /HUB_DP_UP routed from J1
7. **Downstream port 1** — D6 ESD array → net labels /USB_D−, /USB_D+ (existing MCU nets rejoined here)
8. **Downstream ports 2–4** — D3–D5, U5–U7, J5–J7, bulk caps, LEDs

### 4.3 — Net name updates on Sheet 1

| Old net | New net | Reason |
|---------|---------|--------|
| USB_D+ (J1 pin 3) | HUB_DP_UP | D+ now goes to hub upstream, not MCU directly |
| USB_D− (J1 pin 2) | HUB_DM_UP | Same |
| USB_D+ (MCU PA12) | USB_D+ retained | Now connected from hub P1 downstream via D6 |
| USB_D− (MCU PA11) | USB_D− retained | Same |

---

## 5 — PCB Design Considerations

### 5.1 — Layer stack upgrade (2-layer → 4-layer)

The existing Rev A PCB is **2-layer**. The USB2514B handles USB 2.0 **High Speed (480 Mbps)**.
At HS speeds controlled-impedance differential pairs and a solid unbroken ground reference
plane are mandatory.

| Requirement | 2-layer | 4-layer |
|-------------|---------|---------|
| Solid continuous GND plane | ✗ Difficult (power + signal share B.Cu) | ✅ Layer 2 dedicated GND |
| Controlled impedance (90 Ω diff) | ✗ Prepreg thickness varies without inner layer | ✅ Layer 1–2 dielectric fixed by stack-up |
| Return path under every HS trace | ✗ Cannot guarantee | ✅ Guaranteed by layer 2 GND |
| Routing density for QFN-36 | Marginal | ✅ Comfortable fan-out |

**Decision: Rev B moves to 4-layer.**

Recommended stack-up (JLCPCB JLC04161H-7628 standard):

| Layer | Name | Usage |
|-------|------|-------|
| 1 | F.Cu | Signal + routed power |
| 2 | In1.Cu | Solid GND plane |
| 3 | In2.Cu | Solid GND plane (or +3.3V/VBUS pours) |
| 4 | B.Cu | Signal + routed power |

### 5.2 — Controlled impedance targets

| Trace type | Target | Width | Gap | Layer |
|------------|--------|-------|-----|-------|
| Single-ended signal | 50 Ω | 0.17 mm | — | L1 or L4 (above GND) |
| USB HS differential pair | 90 Ω diff / 50 Ω SE | 0.17 mm | 0.22 mm | L1 or L4 |
| USB FS differential pair (STM32 side) | 90 Ω diff | 0.17 mm | 0.22 mm | L1 |

> Verify with PCB fab impedance calculator using their actual Dk and dielectric thickness.
> Saturn PCB Toolkit or Altium / KiCad impedance calculator can be used for cross-check.

### 5.3 — Component placement guidelines

| Component | Placement rule |
|-----------|----------------|
| D2 (ESD — upstream) | ≤ 2 mm from J1 pins 2/3; between J1 and U3 in signal path |
| D3–D5 (ESD — downstream) | ≤ 2 mm from J5/J6/J7; between connector and U3 |
| D6 (ESD — MCU side) | Between U3 port 1 and STM32 PA11/PA12 |
| Y2 (24 MHz crystal) | ≤ 5 mm from U3 XTALIN/XTALOUT pins; avoid crossing HS diff pairs |
| U4 (LDO) | Near U3 VDD pins; keep away from crystal area |
| C26–C33 (100 nF bypass) | One per VDD pin, on bottom side under QFN if double-sided assembly allowed |
| C37–C42 (100 µF bulk) | At each USB-A VBUS pin; helps meet USB inrush requirements |
| U5–U7 (load switches) | Between U3 OC#/EN signals and USB-A VBUS pins |

### 5.4 — Routing rules (add to KiCad Design Rules)

```
# USB HS differential pairs
Min clearance between diff pairs:  0.5 mm (3× trace width)
Intra-pair skew matching:          ≤ 5 ps (≈ 1 mm length difference)
Max via count on HS diff pair:     2 (add ground via beside each signal via)
Transient via (stitching via):     Place adjacent to every HS signal via
```

### 5.5 — Power trace widths

| Net | Max current | Min trace width |
|-----|-------------|-----------------|
| VBUS (main trunk) | 600 mA (MCU + hub + 3×500 mA ports) → 2.1 A | 0.5 mm |
| HUB_3V3 | 200 mA | 0.3 mm |
| USB-A VBUS (per port) | 500 mA | 0.3 mm |

---

## 6 — Step-by-Step Implementation Plan

### Step 1 — Schematic

- [ ] Add Sheet 2 "USB Hub" to `tproject.kicad_sch`
- [ ] Place U3 (USB2514B), U4 (LDO), Y2 (24 MHz), D2–D6, U5–U7, J5–J7 and all passives
- [ ] Wire all nets; add net labels matching the table in §4.2
- [ ] Modify Sheet 1: re-route J1 D+/D− to HUB_DM_UP / HUB_DP_UP labels
- [ ] Remove R2 (1.5 kΩ pull-up on J1 D+) — pull-up is no longer needed at J1 level
- [ ] Run ERC → target 0 errors

### Step 2 — Footprint assignment

- [ ] USB2514B → `Package_QFN:QFN-36-1EP_5x5mm_P0.5mm_EP3.65x3.65mm` (or Microchip ECAD model)
- [ ] USB-A connectors → `Connector_USB:USB_A_Amphenol_61729-0010BLF_Horizontal` (or vertical variant)
- [ ] MIC2099 → `Package_TO_SOT_SMD:SOT-23-5`
- [ ] USBLC6-2SC6 → `Package_TO_SOT_SMD:SOT-23-6`
- [ ] Y2 → `Crystal_SMD_3225-4Pin_3.2x2.5mm`

### Step 3 — PCB setup (Rev B)

- [ ] `File → Board Setup → Board Stackup` — change from 2-layer to 4-layer using JLCPCB JLC04161H stack-up
- [ ] Layer 2 = In1.Cu → assign net GND as copper fill (solid plane)
- [ ] Layer 3 = In2.Cu → assign net GND or split +3.3V / GND pours
- [ ] Update Design Rules Constraints: min via 0.3 mm drill / 0.6 mm pad (4-layer JLCPCB standard)
- [ ] Add impedance profiles in Board Setup: SE-50 (0.17 mm), DIFF-90 (0.17 mm / 0.22 mm gap)

### Step 4 — Component placement

- [ ] Keep existing MCU, crystal Y1, power, connector area from Rev A as reference
- [ ] Place USB hub sub-circuit block (U3, Y2, D2, U4) in a dedicated region near J1
- [ ] Place USB-A connector row (J5–J7) on board edge opposite J1
- [ ] Place load switches U5–U7 between hub IC and USB-A connectors
- [ ] Place bulk caps C37–C42 directly at J5–J7 VBUS pins

### Step 5 — Routing

1. **HS differential pairs** — route first; use diff-pair rule (0.17 mm / 0.22 mm)
2. **ESD arrays** — confirm D2–D5 are in the signal path (between connector and hub IC)
3. **Crystal traces** — route Y2 short and isolated from HS diff pairs
4. **Power** — route VBUS trunk (0.5 mm), HUB_3V3 (0.3 mm), per-port VBUS (0.3 mm)
5. **Control signals** — hub EN/OC# lines to U5–U7 (not critical, 0.2 mm OK)
6. **Intra-pair skew matching** — squiggles on mismatched leg to achieve ≤ 5 ps
7. **Ground stitching vias** — add beside every HS signal via (transovia pattern)
8. **Copper fills** — fill In1.Cu with GND; fill In2.Cu with GND; fill F.Cu/B.Cu with GND

### Step 6 — DRC

- [ ] Run DRC → 0 errors
- [ ] Verify controlled impedance nets are flagged correctly in rules
- [ ] Check 3D view for USB-A connector overhang at board edge

### Step 7 — BOM update

- [ ] Regenerate `manufacturing/tproject.csv` (or produce `tproject-revB.csv`)
- [ ] Re-export Gerbers to `manufacturing/revB/`

---

## 7 — Strapping Pin Configuration Summary

All strapping pins sampled at power-on. Using resistors (not shorts) for all pulls
to allow future rework.

| Pin | Pull | Value | Meaning |
|-----|------|-------|---------|
| CFG_SEL0 | Low | R10 = 100 kΩ to GND | Use strapping resistor config (no EEPROM) |
| CFG_SEL1 | Low | R11 = 100 kΩ to GND | Self-powered mode |
| NON_REM0 | Low | R12 = 100 kΩ to GND | All downstream ports removable |
| NON_REM1 | Low | R13 = 100 kΩ to GND | All downstream ports removable |

> CFG_SEL[1:0] = 00 → self-powered, individual port power switching, individual OC sensing.
> See USB2514B datasheet Table 3-1 for all combinations.

---

## 8 — VBUS Detect Circuit

The USB2514B VBUS_DET pin is a 3.3 V logic input. J1 VBUS is 5 V.
A simple resistor divider scales VBUS to ≈ 2.5 V, safely within the 3.3 V device logic.

```
VBUS (5 V)
    │
   R8  100 kΩ
    │
    ├──── VBUS_DET (USB2514B pin)     → also ── EN (U4 LDO enable)
    │
   R9  100 kΩ
    │
   GND
```

VBUS_DET voltage with 5 V present: `5 V × (100k / 200k) = 2.5 V` ✅
VBUS_DET voltage with no host: `0 V` → hub remains in reset; U4 LDO disabled.

This ensures the hub (and its dedicated 3.3 V rail) only activates once a USB host
cable is connected, matching the behaviour described in Phil's Lab #86.

---

## 9 — Summary of Rev A → Rev B Differences

| Aspect | Rev A | Rev B |
|--------|-------|-------|
| USB connectivity | 1× Micro-B (MCU device only) | 1× Micro-B upstream + 3× USB-A downstream + MCU on hub P1 |
| PCB layers | 2 | 4 |
| USB speed | FS 12 Mbps only | HS 480 Mbps hub; FS STM32 on one port |
| Power supply | 1× AMS1117 | 2× AMS1117 (MCU + hub independent) |
| ESD protection | None (Rev A has no ESD on J1) | USBLC6-2SC6 on every USB port |
| Component count | 29 | ≈ 65 |
| Approximate board area increase | — | +30–40% (USB-A connectors + hub IC region) |
