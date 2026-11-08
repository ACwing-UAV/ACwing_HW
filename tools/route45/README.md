# route45 – 45° routing check and fix

House rule for all ACwing boards: **every track segment at 0, 45 or 90°** (checked on the exact coordinates, nm).

These scripts make an existing routed board compliant without moving any pad, via or track end point:

| Script | What |
|---|---|
| `down2.py k10.kicad_pcb k7.kicad_pcb [extra tokens]` | converts a KiCad 10 board to a KiCad 7 copy (only to check and edit it with the KiCad 7 `pcbnew` Python API) |
| `oct45.py k7.kicad_pcb board.kicad_pro` | removes duplicated / zero-length segments, splits T joints, then replaces every off-angle run by (1) a straight line sliding a free end inside its pad, (2) a two- or three-segment octilinear dogleg, or (3) an octilinear A* detour on the same layer. Clearances from the net classes of the `.kicad_pro`, edge and hole clearances, keep-outs; never tighter than the original route |
| `postclean.py k7.kicad_pcb` | removes dangling stubs reported by the DRC while the board stays fully connected |
| `k10write.py k10.kicad_pcb k7.kicad_pcb out.kicad_pcb [--rmfp J7,J8] [--movefp J1] ...` | writes the tracks, vias and zone fills back into the original KiCad 10 file (text level; everything else untouched) |
| `drc.py`, `stats.py` | KiCad 7 DRC with zone refill; segment statistics (off-45 count, micro segments) |

Needs KiCad 7 `pcbnew` (Python 3.12 on Ubuntu 24.04: `python3.12`), shapely, numpy, Pillow.
The final check is always a DRC in KiCad 10.

For new routing: Freerouting in its default any-angle mode breaks the rule. Use the 45° mode (or route in KiCad with
the 45° constraint, which is the KiCad default) and run `oct45.py` + `stats.py` as a check before release.
