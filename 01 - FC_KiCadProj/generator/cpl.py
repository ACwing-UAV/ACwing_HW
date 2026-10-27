# JLCPCB pick-and-place file (CPL), same layout as the JLC sample: Designator, Mid X, Mid Y, Layer, Rotation.
# Coordinates from KiCad's position export with the drill/place origin at the board's lower-left corner
# (KiCad (130, 120) mm): X to the right, Y up, mm. Only assembled parts (the BoM placements); pads, holes,
# pogo pads and the DNP part are left out. Rotation 0-359 deg: KiCad rotation + JLC correction (bottom: see CORR).
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
    return p is not None and not p.get('dnp') and not (re.match(r'^(TP|H)\d', ref) or 'TestPoint_Pad_2.0x2.0mm' in parts[ref]['fp'])
key = lambda r: (re.sub(r'\d', '', r), int(re.sub(r'\D', '', r) or 0))
# JLC library zero orientation differs from KiCad's for these footprints (read from JLC's placement previews of this
# board, 2026-10-16 and 2026-10-27): angle added to the KiCad rotation of a top-side part.
# Bottom side: JLC mirrors the part about the Y axis and counts the angle as seen from below, so
# rotation = 180 - KiCad rotation + correction (checked on U10, U11, U13 in the 2026-10-27 preview).
CORR = {
 'QFN-48-1EP_7x7mm_P0.5mm_EP5.6x5.6mm': 270,   # U2
 'DFN-6_1.3x1.2mm_P0.4mm': 270,                # U5
 'ST_MLPF-WB55-01E3_CSP-6': 270,               # U8
 'Vishay_PowerPAK_1212-8_Single': 270,         # Q1-Q4 (AON7524)
 'SOT-23-6': 270,                              # U7
 'LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y': 180,  # U1
 'SOT-353_SC-70-5': 180,                       # U13 (SN74LV1T34, C78541): from the 2026-10-27 preview
 'SOT-23': 180,                                # Q5
 'Texas_DRC0010J': 0,                          # U12 (LM5166): pin 1 seen 90 deg off with 270 in the 2026-10-27 preview
 'CP_EIA-7343-31_Kemet-D': 180,                # C1 (tantalum polarity)
 'D_SMAflat': 180,                             # D5-D8 (cathode band)
 'WSON-8-1EP_6x5mm_P1.27mm_EP3.4x4mm': 270,    # U10 (W25Q128JVPIQ, bottom): from the 2026-10-27 preview
 'LED_WS2812B-2020_PLCC4_2.0x2.0mm': 180,      # D1-D4 (XL-2020RGBC-WS2812B, C5349955): DO/DI/+/- marks 180 deg off with 0
}
# JLC part origin != KiCad footprint origin: offset (mm, footprint frame, KiCad Y down) from the KiCad origin to the
# JLC origin (centre of the pad bounding box). USB-C C165948: KiCad origin = body centre, JLC origin 1.46 mm toward the
# pins; without it the 2026-10-27 preview showed the receptacle ~1.5 mm out of the board edge.
OFFSET = {
 'USB_C_Receptacle_HRO_TYPE-C-31-M-12': (0.0, -1.46),
}
import math
rows = []
for r in csv.DictReader(open(tmp)):
    if not assembled(r['Ref']):
        continue
    kr = float(r['Rot']); top = r['Side'] == 'top'
    rot = (round(kr) + CORR.get(r['Package'], 0)) % 360 if top else (180 - round(kr) + CORR.get(r['Package'], 0)) % 360
    x, y = float(r['PosX']), float(r['PosY'])
    if r['Package'] in OFFSET:
        assert top
        dx, dy = OFFSET[r['Package']]; dy = -dy                # to Y up
        a = math.radians(kr)
        x += dx * math.cos(a) - dy * math.sin(a); y += dx * math.sin(a) + dy * math.cos(a)
    rows.append((r['Ref'], '%.4fmm' % x, '%.4fmm' % y, 'Top' if top else 'Bottom', rot))
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
