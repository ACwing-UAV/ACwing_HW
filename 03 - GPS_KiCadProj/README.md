# ACwing GPS rev A – KiCad project

**Project:** ACwing · **Author:** Andrea Cirillo

KiCad 7 sources of the ACwing GPS rev A board (they also open in KiCad 8/9). The board description, schematic PDF, BoM,
JLCPCB files, Gerber, STEP and board views are in [`00 - Docs/02 - GPS_Docs`](../00%20-%20Docs/02%20-%20GPS_Docs/).

| File / folder | What |
|---|---|
| `ACwing_GPS_A.kicad_pro`, `.kicad_sch`, `.kicad_pcb` | project, schematic, routed PCB |
| `*.kicad_sym`, `*.pretty/`, `fp-lib-table`, `sym-lib-table` | project library (symbols, footprints, ACwing logos) |
| `3d/` | STEP models, referenced as `${KIPRJMOD}/3d/...` |
| `generator/` | scripts that generated, routed and checked the design (build_all_gps.sh) |
