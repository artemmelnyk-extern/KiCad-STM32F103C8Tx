# DRC Fix Plan

All errors come from the `kicad-cli pcb drc` run in CI.  
Target: **0 errors** so the pipeline passes on `main`.

---

## Error Summary

| # | Rule | Count | Severity | Root cause |
|---|------|-------|----------|------------|
| 1 | `via_diameter` | 28 | Error | All vias placed at 0.6 mm; board min is 0.7 mm |
| 2 | `unconnected_items` | 20 | Error | GND and +3.3V net segments have broken connections |
| 3 | `starved_thermal` | 2 | Error | VBUS zone thermal relief has only 1 spoke; min is 2 |

---

## Fix 1 — Via diameter (28 errors)

**All vias are 0.6 mm drill / 0.6 mm annular; board minimum is 0.7 mm.**

### Option A — Resize all vias to 0.7 mm (recommended for JLCPCB 2-layer)

1. Open `tproject.kicad_pcb` in KiCad PCB Editor.
2. `Edit → Find` or press `T` to open inspector; alternatively use `Edit → Change Footprint`.
3. Better: use **Scripting Console** (`Tools → Scripting Console`):
   ```python
   import pcbnew
   board = pcbnew.GetBoard()
   for track in board.GetTracks():
       if track.GetClass() == 'PCB_VIA':
           track.SetWidth(pcbnew.FromMM(0.8))   # outer diameter
           track.SetDrillValue(pcbnew.FromMM(0.4))  # drill
   pcbnew.Refresh()
   ```
   This sets all vias to 0.8 mm / 0.4 mm drill — well within JLCPCB standard rules (min via 0.3 mm drill, 0.6 mm pad).
4. Run DRC again to confirm `via_diameter` errors are gone.
5. Save → commit.

### Option B — Lower board minimum (only if fab supports it)

1. `File → Board Setup → Design Rules → Constraints`
2. Change **Minimum via diameter** from `0.7 mm` to `0.6 mm`.
3. Save → run DRC → commit.
> ⚠ JLCPCB standard process minimum is 0.6 mm pad (0.3 mm drill), so Option B is technically valid but leaves no margin. Option A is safer.

---

## Fix 2 — Unconnected items (20 errors)

**Net segments on GND and +3.3V are not electrically joined — ratsnest lines visible in PCB editor.**

Affected nets: `GND` (17 gaps), `+3.3V` (2 gaps), `VBUS` (1 gap to U2 pad 3).

### Step-by-step

1. Open `tproject.kicad_pcb`.
2. Run `Inspect → Design Rules Checker` (or press `D` shortcut).
3. In the DRC dialog click **Run DRC** → switch to the **Unconnected** tab.
4. Double-click each entry — the PCB editor will zoom to and highlight the two disconnected endpoints.
5. For each gap:
   - If the gap is tiny (< 0.1 mm): the track ends do not quite touch — use `Route → Interactive Router` (`X`) to draw a short closing segment, or drag the track endpoint to snap it.
   - If the gap is a missing segment: route the ratsnest manually with `X`.
   - If the gap crosses layers: add a via and route on B.Cu.
6. Specific items to check:
   | Net | From | To | Note |
   |-----|------|----|------|
   | GND | `C1 pad 2` | track near J1 | Short stub, re-route |
   | GND | `C2 pad 2` | track near U2 | Re-route via B.Cu GND plane |
   | GND | multiple track stubs | adjacent tracks | Drag endpoints to merge |
   | +3.3V | track stubs near decoupling caps | power rail | Route closing segment |
   | VBUS | Zone on F.Cu | `U2 pad 3` | Add a short track from U2 pad 3 to VBUS zone |
7. After routing, re-run DRC and confirm **0 unconnected items**.
8. Refill copper zones: `Edit → Fill All Zones` (`B`).

---

## Fix 3 — Starved thermal (2 errors)

**VBUS zone has thermal relief pads connected by only 1 spoke; zone requires 2.**

Affected pads:
- `J1 pad 1 [VBUS]` at (68.9, 67.325)
- `C1 pad 1 [VBUS]` at (63.35, 70.5)

### Option A — Reduce zone min spoke count to 1

1. Click on the **VBUS zone** (filled copper area on F.Cu).
2. Press `E` → Zone Properties.
3. Under **Thermal relief** → **Minimum thermal relief spoke count** → change from `2` to `1`.
4. Refill zones (`B`) → run DRC.

### Option B — Override to solid connection on those pads

1. Double-click `J1` → open footprint properties → select **Pad 1**.
2. In **Pad Properties → Connection** → override to **Solid**.
3. Repeat for `C1 pad 1`.
4. Refill zones (`B`) → run DRC.

> Option A is simpler. Option B gives better thermal/electrical performance for a power pad but is overkill for a small VBUS decoupling cap.

---

## Verification checklist

- [ ] DRC reports **0 errors** locally
- [ ] `git add tproject.kicad_pcb && git commit -m "pcb: fix DRC errors (via size, unconnected, thermals)"`
- [ ] Push to `main` — CI pipeline passes
- [ ] Re-export Gerbers and replace files in `manufacturing/`
- [ ] Re-export pick-and-place `tproject-top-pos.csv`
- [ ] Commit updated manufacturing files
