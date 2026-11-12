# outputs – KiCad 10 checks, fabrication outputs, renders and the stack check page

Used on 2026-11-08 to bring every board to KiCad 10.0.6 and regenerate everything in `00 - Docs`.
Paths inside the scripts are those of the build environment (`/work/acwing_hw`, `/work/stack`, `/home/claude/stack`): adapt them.

| Script | What |
|---|---|
| `k10_outputs.sh` | per board: DRC report, ERC, Gerber + drill zip, STEP, schematic PDF, position file (kicad-cli 10) |
| `k10_renders.sh`, `compose_board_renders.py` | `kicad-cli pcb render` (high quality, floor) top / bottom / isometric, composed into `*_pcb.png` and `*_3D.png` |
| `stack_check.py` | stack interference check (courtyard prisms, mated-plug envelopes, grommets / standoffs); per-part heights from the previous check |
| `step_mesh.py`, `build_page_data.py` | STEP (with silkscreen and pads) → triangle mesh → `stack_data.js` for `ACwing_stack_check.html` |
| `render_stack.py`, `compose_stack.py` | KiCad GLB exports + grommets, standoffs, mated plugs and cables → Blender Cycles → `ACwing_stack_3D.png` |
| `escpads.py` | one-off edit of 2026-11-08: ESC 1S battery pads J2 across the rear-left corner (pours, vias, polarity marks) |

Environment: KiCad 10.0.6 from the Ubuntu 26.10 archive (a chroot is enough). Its `pcbnew` Python module needs
`SwigPyIterator.next = SwigPyIterator.__next__` with Python 3.13. Meshes: `cadquery-ocp < 7.9`. Renders: `bpy` 5.0 (Python 3.11).
