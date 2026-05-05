# 0020 — BOM and Gerber Export — Final Stage

**Date:** 2026-05-05
**Status:** Complete — **This is the final design note. The board is ready for fabrication.**
**References:** All previous design notes 0001–0019; KiCad 9 Gerber export documentation

---

## Summary

All manufacturing outputs have been generated from the completed PCB design and committed
to the `manufacturing/` directory. This marks the end of the design cycle for the
STM32F103C8T6 development board. The board is ready to be submitted to a PCB fabrication
house.

---

## 1 — Bill of Materials (`manufacturing/tproject.csv`)

Exported from KiCad Schematic Editor → **File → Export → BOM**.

| Ref(s) | Qty | Value | Footprint | Datasheet |
|--------|-----|-------|-----------|-----------|
| C1, C2 | 2 | 22 µF | C_0805_2012Metric | — |
| C3 | 1 | 10 µF | C_0603_1608Metric | — |
| C4, C5, C6, C7, C11 | 5 | 100 nF | C_0402_1005Metric | — |
| C8 | 1 | 10 nF | C_0402_1005Metric | — |
| C9, C10 | 2 | 1 µF | C_0402_1005Metric | — |
| C12, C13 | 2 | 10 pF | C_0402_1005Metric | — |
| D1 | 1 | RED LED | LED_0603_1608Metric | — |
| FB1 | 1 | 120 Ω ferrite bead | L_0603_1608Metric | — |
| H1–H4 | 4 | Mounting hole M2 | MountingHole_2.2mm_M2 | — (excluded from BOM) |
| J1 | 1 | USB Micro-B | USB_Micro-B_Wuerth_629105150521 | — |
| J2, J3, J4 | 3 | Conn_01x04 | PinHeader_1x04_P2.54mm_Vertical | — |
| R1, R3, R4, R5 | 4 | 1k5 | R_0402_1005Metric | — |
| R2 | 1 | 10k | R_0402_1005Metric | — |
| SW1 | 1 | SW_SPDT | SW_SPDT_PCM12 | — |
| U1 | 1 | STM32F103C8T6 | LQFP-48_7x7mm_P0.5mm | ST datasheet |
| U2 | 1 | AMS1117-3.3 | SOT-223-3_TabPin2 | AMS datasheet |
| Y1 | 1 | 16 MHz crystal | Crystal_SMD_3225-4Pin_3.2x2.5mm | — |

**Total unique line items:** 17 (excluding mounting holes)
**Total component placements:** 29 (excluding H1–H4)

---

## 2 — Gerber and Drill Files (`manufacturing/`)

Exported from KiCad PCB Editor → **File → Fabrication Outputs → Gerbers** and
**Drill Files**. All files are also bundled in `tproject.zip` for direct submission
to a fab house.

### 2.1 — Gerber layers

| File | Layer | Size |
|------|-------|------|
| `tproject-F_Cu.gbr` | Front copper | 28 KB |
| `tproject-B_Cu.gbr` | Back copper (GND plane) | 74 KB |
| `tproject-F_Mask.gbr` | Front solder mask | 6.9 KB |
| `tproject-B_Mask.gbr` | Back solder mask | 1.5 KB |
| `tproject-F_Paste.gbr` | Front solder paste (stencil) | 6.0 KB |
| `tproject-B_Paste.gbr` | Back solder paste | 491 B |
| `tproject-F_Silkscreen.gbr` | Front silkscreen | 46 KB |
| `tproject-B_Silkscreen.gbr` | Back silkscreen | 9.9 KB |
| `tproject-Edge_Cuts.gbr` | Board outline (38.54 × 33.17 mm) | 1012 B |
| `tproject-job.gbrjob` | Gerber job file (layer stack description) | — |

### 2.2 — Drill files

| File | Type | Content |
|------|------|---------|
| `tproject-PTH.drl` | Plated through-holes | Pin header holes (J2, J3, J4), crystal pads |
| `tproject-NPTH.drl` | Non-plated through-holes | M2 mounting holes (H1–H4) |

### 2.3 — Pick-and-place (centroid) files

| File | Side | Components |
|------|------|------------|
| `tproject-top-pos.csv` | Top (F.Cu) | All 29 placed components |
| `tproject-bottom-pos.csv` | Bottom | Empty — no bottom-side components |

---

## 3 — Board Summary

| Parameter | Value |
|-----------|-------|
| Board dimensions | 38.54 × 33.17 mm |
| Layers | 2 (F.Cu signal + B.Cu GND plane) |
| Min track width | 0.2 mm (USB D+/D−), 0.3 mm (all other signals) |
| Min clearance | 0.2 mm |
| Drill sizes | 1.0 mm (PTH pin headers), 2.2 mm (NPTH M2) |
| Surface finish | As ordered (HASL or ENIG recommended) |
| MCU | STM32F103C8T6, LQFP-48 |
| Supply | 5 V via USB Micro-B → AMS1117-3.3 → 3.3 V |

---

## 4 — Design Cycle Summary

| Note | Stage |
|------|-------|
| 0001 | Decoupling strategy |
| 0002 | NRST / BOOT0 configuration |
| 0003 | HSE crystal circuitry |
| 0004 | USB Micro-B connector |
| 0005 | Power supply and connectors |
| 0006 | ERC and annotations |
| 0007 | Footprint assignment |
| 0008 | PCB setup and design rules |
| 0009 | Initial component placement |
| 0010 | USB / SWO placement refinement |
| 0011 | SMD switch and USB STEP model |
| 0012 | Switch / connector placement refinement |
| 0013 | Power supply cluster placement |
| 0014 | Board outline and mounting holes |
| 0015 | Routing — decoupling caps and HSE crystal |
| 0016 | Connector footprint fix (J2, J3, J4) |
| 0017 | Routing — signal nets (UART, I2C, SWD, USB, BOOT0) |
| 0018 | Routing — power nets |
| 0019 | Silkscreen and zone fill |
| **0020** | **BOM and Gerber export — final stage** |
