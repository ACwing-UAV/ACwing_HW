# JLCPCB pick-and-place file (CPL), same layout as the JLC sample: Designator, Mid X, Mid Y, Layer, Rotation.
# Coordinates from KiCad's position export with the drill/place origin at the board's lower-left corner
# (KiCad (130, 120) mm): X to the right, Y up, mm. Only assembled parts (the BoM placements); pads, holes,
# pogo pads and the DNP part are left out. Rotation = KiCad footprint rotation, 0-359 deg.
import sys, csv, subprocess, re, json
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
BOARD, PARTS, OUT = sys.argv[1:4]
tmp = '/tmp/claude-0/cpl_pos.csv'
subprocess.run(['kicad-cli', 'pcb', 'export', 'pos', '--format', 'csv', '--units', 'mm', '--side', 'both',
                '--use-drill-file-origin', '-o', tmp, BOARD], check=True, capture_output=True)
parts = json.load(open(PARTS))
def assembled(ref):
    p = parts.get(ref)
    return p is not None and not p.get('dnp') and ref != 'J2' and not re.match(r'^(M|TP|H)\d', ref)
key = lambda r: (re.sub(r'\d', '', r), int(re.sub(r'\D', '', r) or 0))
rows = []
for r in csv.DictReader(open(tmp)):
    if not assembled(r['Ref']):
        continue
    rot = round(float(r['Rot'])) % 360
    rows.append((r['Ref'], '%.4fmm' % float(r['PosX']), '%.4fmm' % float(r['PosY']), 'Top' if r['Side'] == 'top' else 'Bottom', rot))
rows.sort(key=lambda x: key(x[0]))
missing = sorted({r for r in parts if assembled(r)} - {x[0] for x in rows}, key=key)
assert not missing, missing
wb = Workbook(); ws = wb.active; ws.title = 'Sheet1'
ws.append(['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'])
for x in rows:
    ws.append(list(x))
for row in ws.iter_rows():
    for c in row:
        c.font = Font(name='Arial', size=10, bold=(c.row == 1))
for col, w in zip('ABCDE', (13.56, 16.22, 14.44, 12.33, 14.11)):
    ws.column_dimensions[col].width = w
wb.save(OUT)
print('CPL rows:', len(rows), '(top %d, bottom %d)' % (sum(x[3] == 'Top' for x in rows), sum(x[3] == 'Bottom' for x in rows)))
