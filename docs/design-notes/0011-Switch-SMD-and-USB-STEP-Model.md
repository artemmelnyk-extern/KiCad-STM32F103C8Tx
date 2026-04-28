# 0011 — Switch Footprint Change (THT → SMD) and USB Connector STEP Model

**Date:** 2026-04-28
**Status:** Implemented
**References:** Design note 0002 (BOOT0 circuit), 0010 (USB placement); CK PCM12 datasheet (https://www.ckswitches.com/media/1424/pcm.pdf); Würth 629105150521 STEP rev1

---

## Summary

Two independent changes were made in this session:

1. **SW1 footprint replaced**: the large through-hole angled slide switch
   (`SW_E-Switch_EG1224_SPDT_Angled`) was replaced with the SMD ultraminiature slide
   switch (`SW_SPDT_PCM12`) from the CK PCM12 series. Both the schematic `Footprint`
   field and the PCB footprint were updated. Position is unchanged (99.595, 46.455).

2. **USB connector STEP model replaced**: the KiCad built-in placeholder STEP model for
   J1 (USB Micro-B Würth 629105150521) was replaced with the manufacturer-supplied STEP
   file added to the project's `step/` directory.

---

## 1 — Switch Footprint Change (SW1)

### Before / After

| Property         | Before                                           | After                                             |
|------------------|--------------------------------------------------|---------------------------------------------------|
| Footprint        | `Button_Switch_THT:SW_E-Switch_EG1224_SPDT_Angled` | `Button_Switch_SMD:SW_SPDT_PCM12`              |
| Mount type       | Through-hole (THT)                               | Surface mount (SMD)                               |
| Datasheet        | E-Switch EG series (right angle)                 | CK PCM12 (right angle) — ckswitches.com           |
| 3D model         | `Button_Switch_THT.3dshapes/SW_E-Switch_EG1224_SPDT_Angled.step` | `Button_Switch_SMD.3dshapes/SW_SPDT_PCM12.step` |
| PCB position     | (99.595, 46.455) rot=0°                          | (99.595, 46.455) rot=0° *(unchanged)*             |

### PCM12 footprint geometry

Courtyard bounding box (from KiCad `F.CrtYd` data):

| Dimension | Value |
|-----------|-------|
| Width (X) | 8.8 mm (−4.4 to +4.4) |
| Height (Y) | 5.85 mm (−2.45 to +3.4) |
| Body approx. | 4.0 mm × 2.5 mm (PCM12 series per datasheet) |

The EG1224 THT footprint had a significantly larger courtyard (≈ 11 × 7 mm plus
through-hole barrel clearances). The PCM12 SMD footprint reduces the occupied board area
by approximately **50 %** and eliminates the need for drilled through-holes.

### Schematic change

The `Footprint` property of symbol SW1 was updated in `tproject.kicad_sch`:

```
- (property "Footprint" "Button_Switch_THT:SW_E-Switch_EG1224_SPDT_Angled" ...)
+ (property "Footprint" "Button_Switch_SMD:SW_SPDT_PCM12" ...)
```

Net connections (GND, BOOT0, +3.3V via R2) are unchanged — the PCM12 is also an SPDT
slide switch with equivalent pin-out for this application.

### Rationale

The EG1224 is a 5-pin right-angle THT slide switch. Its through-hole barrels would have
required drilling on a 2-layer board and occupied a large courtyard zone, conflicting with
SMD component routing around the BOOT0 pull-up resistor (R2) cluster. The CK PCM12:

- Is fully SMD, consistent with the rest of the board (except J1 mounting tabs).
- Has the same SPDT topology required by the BOOT0 select circuit (design note 0002).
- Fits within the existing (99.595, 46.455) placement without repositioning.
- Requires no additional drilling.

---

## 2 — USB Connector STEP Model (J1)

### Change

The 3D model reference for J1 (USB Micro-B, Würth 629105150521) was changed from the
KiCad built-in placeholder to the manufacturer-supplied STEP file added to the project:

| | Before | After |
|---|--------|-------|
| Model path | `${KICAD9_3DMODEL_DIR}/Connector_USB.3dshapes/USB_Micro-B_Wuerth_629105150521.step` | `${KIPRJMOD}/step/629105150521 (rev1).stp` |
| Source | KiCad built-in library | Manufacturer STEP, rev1 (804 KB) |
| File added | — | `step/629105150521 (rev1).stp` |

`${KIPRJMOD}` resolves to the project root directory, making the reference portable
across machines that have the project checked out.

### Why use the manufacturer STEP

- The KiCad built-in model for this connector is a generic approximation.
- The Würth 629105150521 STEP (rev1) is the exact mechanical model from the manufacturer,
  including the through-hole mounting tabs, shell dimensions, and USB port opening.
- Using the exact model ensures accurate DRC 3D collision checks and correct board-edge
  alignment for the USB connector panel cut-out that will be defined in Edge.Cuts.

### File added to repository

```
step/
└── 629105150521 (rev1).stp   804 KB   Würth USB Micro-B 629105150521 STEP rev1
```

---

## 3 — File Changes Summary

| File | Change |
|------|--------|
| `tproject.kicad_sch` | SW1 `Footprint` property updated (1 line) |
| `tproject.kicad_pcb` | SW1 footprint block replaced; J1 `model` path updated |
| `step/629105150521 (rev1).stp` | New file — manufacturer STEP model for J1 |

---

## 4 — Next Steps

1. Verify SW1 PCM12 courtyard does not overlap with neighbouring components after DRC.
2. Draw board outline (Edge.Cuts) — J1 rotation (90°) and position (70.8, 65.875) define
   the required USB connector panel cut-out location.
3. Begin copper routing: USB differential pair first (J1 → R3 → U1 PA11/PA12), then
   SWD/SWO (J3 → U1 PA13/PA14/PB3).
