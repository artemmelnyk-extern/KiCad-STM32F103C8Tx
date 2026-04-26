# 0008 — PCB Setup (STM32F103C8T6)

**Date:** 2026-04-26
**Status:** Implemented
**References:** IPC-2221B, JLCPCB/PCBWay standard 2-layer spec

---

## Summary

The KiCad PCB editor was opened for the first time and the board setup was configured.
Changes span two files:

- `tproject.kicad_pcb` — board stackup, layer definition, and plot parameters (was essentially empty)
- `tproject.kicad_pro` — board design rules, DRC severities, track/via presets, teardrop settings

No copper, no components, no routes exist yet — this commit establishes the manufacturing
and electrical constraints that all subsequent layout work must satisfy.

---

## 1 — Board Stackup (`tproject.kicad_pcb`)

### Layer count and physical stack

| Layer       | Type               | Thickness (mm) | Material |
|-------------|--------------------|----------------|----------|
| F.SilkS     | Top Silk Screen    | —              | — |
| F.Paste     | Top Solder Paste   | —              | — |
| F.Mask      | Top Solder Mask    | 0.010          | — |
| **F.Cu**    | **Copper (signal)**| **0.035**      | — |
| dielectric 1| Core               | **1.510**      | FR4, εᵣ = 4.5, tan δ = 0.02 |
| **B.Cu**    | **Copper (power)** | **0.035**      | — |
| B.Mask      | Bottom Solder Mask | 0.010          | — |
| B.Paste     | Bottom Solder Paste| —              | — |
| B.SilkS     | Bottom Silk Screen | —              | — |

**Total board thickness:** 1.6 mm (standard)

Copper finish: **None** (bare copper / HASL by default at fab).
Tenting: via tenting **front and back** (soldermask over via holes).

### Layer roles

| KiCad layer | Role assigned |
|-------------|---------------|
| F.Cu (0)    | Signal — MCU, connectors, small-signal traces |
| B.Cu (2)    | Power — ground/power pours |

A 2-layer board is sufficient for this design given the component count (~30 parts)
and the relatively relaxed signal integrity requirements (USB FS 12 Mbit/s maximum).

### Enabled drawing/fab layers

F.Adhesive, B.Adhesive, F.Paste, B.Paste, F.Silkscreen, B.Silkscreen, F.Mask, B.Mask,
User.Drawings, User.Comments, User.Eco1/2, Edge.Cuts, Margin, F.Courtyard, B.Courtyard,
F.Fab, B.Fab, User.1–4.

---

## 2 — Design Rules (`tproject.kicad_pro`)

### Clearance and width constraints

| Rule                          | Value   | Notes |
|-------------------------------|---------|-------|
| `min_clearance`               | 0.20 mm | Copper-to-copper minimum; typical JLCPCB standard spec |
| `min_track_width`             | 0.20 mm | Minimum track width |
| `min_via_diameter`            | 0.70 mm | Minimum via pad diameter |
| `min_via_annular_width`       | 0.13 mm | Minimum annular ring (via drill to pad edge) |
| `min_through_hole_diameter`   | 0.30 mm | Minimum drill size |
| `min_hole_to_hole`            | 0.254 mm| Hole-to-hole spacing |
| `min_hole_clearance`          | 0.25 mm | Hole to copper clearance |
| `min_copper_edge_clearance`   | 0.0 mm  | (not yet constrained — set at layout) |
| `min_silk_clearance`          | 0.0 mm  | (not yet constrained) |
| `solder_mask_to_copper_clearance` | 0.0 mm | Fab-side mask expansion |
| `max_error`                   | 0.005 mm| Arc-to-chord approximation tolerance |
| `pad_to_mask_clearance`       | 0       | No extra mask clearance beyond footprint spec |

> The 0.2 mm / 0.2 mm (track width / clearance) rule set is the standard minimum for
> JLCPCB and most prototype fabs. It is also compatible with PCBWay, Aisler, and OSH Park.

### Track width presets (quick-select in router)

| Preset | Width   | Intended use |
|--------|---------|--------------|
| Default (auto) | —  | Net-class driven |
| 0.3 mm | 0.30 mm | General signal traces |
| 0.5 mm | 0.50 mm | Power traces (VBUS, +3.3V, GND stubs) |

### Via dimension presets

| Preset | Pad Ø   | Drill Ø | Notes |
|--------|---------|---------|-------|
| Default | —      | —       | Net-class driven |
| Standard | 0.70 mm | 0.30 mm | Smallest reliable via for standard fabs |

### Differential pair presets

| Preset | Trace width | Gap    | Via gap |
|--------|------------|--------|---------|
| Default | —          | —      | — |
| USB FS  | 0.30 mm    | 0.30 mm | 0.50 mm |

The USB differential pair preset (0.3 mm / 0.3 mm gap) is sized for the USB_D+ / USB_D−
traces. At USB Full Speed (12 Mbit/s) the signal rise time is ~4 ns; for a 2-layer FR4
board a 0.3 mm trace over 1.51 mm FR4 gives a characteristic impedance of approximately
90 Ω single-ended (≈ 90 Ω differential), close to the USB 90 Ω differential target.

---

## 3 — Teardrop Settings

Teardrops are enabled globally:

| Location              | Enabled |
|-----------------------|---------|
| PTH pads              | Yes |
| SMD pads              | Yes |
| Vias                  | Yes |
| Track ends            | No |

Teardrop geometry (all types):

| Parameter               | Value |
|-------------------------|-------|
| Height ratio            | 1.0 (100% of track width) |
| Length ratio            | 0.5 (50% of via/pad diameter) |
| Max height              | 2.0 mm |
| Max length              | 1.0 mm |
| Allow two-track teardrops | Yes |
| Curved segments         | 0 (straight chamfer) |

Teardrops reduce mechanical stress at the pad-to-trace junction and improve DFM
(manufacturing yield) by preventing drill-breakout from tearing the annular ring.

---

## 4 — DRC Rule Severities (selected)

| Rule                        | Severity  | Notes |
|-----------------------------|-----------|-------|
| `clearance`                 | error     | Hard stop |
| `unconnected_items`         | error     | All nets must be routed |
| `courtyards_overlap`        | error     | No component overlap |
| `solder_mask_bridge`        | error     | |
| `shorting_items`            | error     | |
| `missing_courtyard`         | ignore    | Some library parts lack courtyards |
| `footprint_type_mismatch`   | ignore    | |
| `duplicate_footprints`      | warning   | |
| `track_dangling`            | warning   | Acceptable during layout-in-progress |
| `missing_footprint`         | warning   | |
| `hole_to_hole`              | warning   | |
| `silk_over_copper`          | warning   | |

---

## 5 — Plot / Gerber Output Settings

Output format: **Gerber** (format 1).
Gerber extensions: **standard** (no non-standard extensions).
Gerber attributes: **enabled** (X2 attributes for fab).
Gerber job file: **enabled**.
Black & white plot: **yes** (drill map / PDF).
DNP parts on fab layer: **crossed out** (sketchDNP + crossoutDNP = yes).

---

## Checklist

| Item                                    | Functional impact | BOM impact |
|-----------------------------------------|:-----------------:|:----------:|
| Board stackup defined (1.6 mm, 2-layer) | None (no copper yet) | No |
| Design rules set                        | None (enforced at DRC time) | No |
| Track/via presets added                 | None | No |
| Teardrop settings configured            | None | No |
| DRC severities configured               | None | No |
| Plot/Gerber settings configured         | None | No |
