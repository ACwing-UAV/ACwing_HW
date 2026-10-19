# ACwing FC rev H - full regeneration (KiCad 7 + pcbnew, Freerouting 1.9 with xvfb, shapely, openpyxl, cadquery)
# paths: /home/claude/genH (scripts), /home/claude/outH (project); helpers from the rev E generator (genE)
set -e
bash /home/claude/genH/run_sch_h.sh        # schematic, netlist check, PDF
bash /home/claude/genH/prep_h.sh           # outline, placement, planes, RF / LDO / MCU details, pogo stubs, GND fan-out, crystal (A*)
bash /home/claude/genH/routeall_h.sh       # Freerouting (20 min cap), import, cleanup, A* for leftovers, DRC
bash /home/claude/genH/finish_h.sh         # silkscreen, library, DRC, BoM / costing / JLC BoM / CPL, Gerber, STEP, renders
