# ACwing Flow rev A – KiCad project

**Project:** ACwing · **Author:** Andrea Cirillo

KiCad 7 sources of the ACwing Flow rev A board (they also open in KiCad 8/9). The board description, schematic PDF, BoM,
JLCPCB files, Gerber, STEP and board views are in [`00 - Docs/03 - FLOW_Docs`](../00%20-%20Docs/03%20-%20FLOW_Docs/).

| File / folder | What |
|---|---|
| `ACwing_Flow_A.kicad_pro`, `.kicad_sch`, `.kicad_pcb` | project, schematic, routed PCB |
| `*.kicad_sym`, `*.pretty/`, `fp-lib-table`, `sym-lib-table` | project library (symbols, footprints, ACwing logos) |
| `3d/` | STEP models, referenced as `${KIPRJMOD}/3d/...` |
| `generator/` | scripts that generated, routed and checked the design (run_sch.sh, gen_pcb_flow.py, loop_route.sh, post_route.sh) |
