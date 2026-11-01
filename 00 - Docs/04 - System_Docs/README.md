# ACwing – system documents

**Project:** ACwing · **Author:** Andrea Cirillo · **Overview:** [repository README](../../Readme.md)

Documents that concern the whole drone rather than one board: the interface between the electronics and the frame,
and the stack check of the boards with all connectors mated.

![ACwing stack](ACwing_stack_3D.png)

| File | What |
|---|---|
| [`ACwing_mechanical_handoff.md`](ACwing_mechanical_handoff.md) | electronics → frame handoff: hole patterns, stack heights, board outlines, connectors, cables, keep-outs (started with FC draft E, updated through the rev A boards) |
| [`ACwing_frame_preliminary_draft_mechanical_answer.md`](ACwing_frame_preliminary_draft_mechanical_answer.md) | mechanical answer on the preliminary draft frame: stack hardware, cables wire by wire, flow board mounting, vibration, weight budget |
| [`ACwing_frame_preliminary_draft_electronics_reply.md`](ACwing_frame_preliminary_draft_electronics_reply.md) | electronics reply: checks confirmed, non-magnetic stack screws requested |
| `ACwing_stack_check.html` + `stack_data.js` | interactive 3D stack check (ESC 1S A + FC A + GPS A, 6 mm FC → GPS gap): download both files and open the page in a browser |
| `ACwing_stack_3D.png` | render of the stack |

> The handoff and the two preliminary-draft frame documents are design logs from before the release: their *draft*
> letters are internal iterations, never manufactured. All current boards are rev A. The released mechanics is
> **Mech A1** (frame A1 + battery trays) in [ACwing_Mechs](https://github.com/ACwing-UAV/ACwing_Mechs).

## Baseline configuration (2026-10-19)

The 1S mini drone flies indoor: **ESC 1S rev A + FC rev A + Flow rev A**, no GPS board. The GPS board is the outdoor
extension and can be fitted on the same 20 × 20 stack (6 mm above the FC). Larger drones replace the ESC 1S with
commercial 4-in-1 ESCs on the same FC cable.
