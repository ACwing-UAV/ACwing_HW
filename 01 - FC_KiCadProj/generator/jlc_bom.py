# JLCPCB assembly BoM: Comment, Designator, Footprint, JLCPCB Part # (one line per part number, assembled parts only).
# With the JLCPCB Part # filled in, JLC's BOM tool matches every line exactly instead of guessing from the comment.
import sys, os, re, json
from openpyxl import Workbook
from openpyxl.styles import Font
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jlc_parts import LCSC
PARTS, OUT = sys.argv[1:3]
parts = json.load(open(PARTS))
key = lambda r: (re.sub(r'\d', '', r), int(re.sub(r'\D', '', r) or 0))
PKG = {'C_0402_1005Metric': '0402', 'R_0402_1005Metric': '0402', 'LED_0402_1005Metric': '0402', 'L_0402_1005Metric': '0402',
       'C_0603_1608Metric': '0603', 'R_0603_1608Metric': '0603', 'C_1206_3216Metric': '1206', 'L_0805_2012Metric': '0805',
       'CP_EIA-7343-31_Kemet-D': '7343-31 (EIA D)', 'D_SMAflat': 'SMAF (DO-221AC)', 'D_SOD-123F': 'SOD-123F',
       'SOT-23': 'SOT-23', 'SOT-23-6': 'SOT-23-6', 'SOT-363_SC-70-6': 'SOT-363', 'TSOT-23-5': 'TSOT-23-5',
       'Vishay_PowerPAK_1212-8_Single': 'DFN-8 (3x3)', 'QFN-48-1EP_7x7mm_P0.5mm_EP5.6x5.6mm': 'UFQFPN-48 (7x7)',
       'LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y': 'LGA-14 (2.5x3)', 'LGA-12_2x2mm_P0.5mm': 'LGA-12 (2x2)',
       'ST_HLGA-10_2x2mm_P0.5mm_LayoutBorder3x2y': 'HLGA-10 (2x2)', 'DFN-6_1.3x1.2mm_P0.4mm': 'DFN-6 (1.2x1.3)',
       'ST_MLPF-WB55-01E3_CSP-6': 'CSP-6 (1.0x1.6)', 'Crystal_SMD_2016-4Pin_2.0x1.6mm': 'SMD2016-4P',
       'Johanson_2450AT18x100': '1206', 'USB_C_Receptacle_HRO_TYPE-C-31-M-12': 'USB-C 16P SMD',
       'JST_SH_SM06B-SRSS-TB_1x06-1MP_P1.00mm_Horizontal': 'SMD,P=1mm,Side entry (JST SH 6P)',
       'JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal': 'SMD,P=1mm,Side entry (JST SH 4P)',
       'LED_WS2812B-2020_PLCC4_2.0x2.0mm': '2020 (WS2812B-2020)', 'D_SOD-523': 'SOD-523', 'R_1206_3216Metric': '1206',
       'WSON-8-1EP_6x5mm_P1.27mm_EP3.4x4mm': 'WSON-8 (6x5)',
       'JST_SH_SM08B-SRSS-TB_1x08-1MP_P1.00mm_Horizontal': 'SMD,P=1mm,Side entry (JST SH 8P)',
       'C_0805_2012Metric': '0805', 'Texas_DRC0010J': 'VSON-10 (3x3)', 'L_Sunlord_SWPA5040S': 'SMD 5x5 (SWPA5040S)',
       'C_1206_3216Metric': '1206'}
groups = {}
for ref, v in parts.items():
    if v.get('dnp') or (re.match(r'^(TP|H)\d', ref) or 'TestPoint_Pad_2.0x2.0mm' in parts[ref]['fp']):
        continue
    fpn = v['fp'].split(':')[1]
    o = LCSC[(v['value'], fpn)]
    g = groups.setdefault(o[2], {'refs': [], 'comment': o[3], 'fp': PKG[fpn]})
    g['refs'].append(ref)
wb = Workbook(); ws = wb.active; ws.title = 'BOM'
ws.append(['Comment', 'Designator', 'Footprint', 'JLCPCB Part #'])
for lcsc, g in sorted(groups.items(), key=lambda kv: key(sorted(kv[1]['refs'], key=key)[0])):
    ws.append([g['comment'], ','.join(sorted(g['refs'], key=key)), g['fp'], lcsc])
for row in ws.iter_rows():
    for c in row:
        c.font = Font(name='Arial', size=10, bold=(c.row == 1))
for col, w in zip('ABCD', (36, 60, 20, 16)):
    ws.column_dimensions[col].width = w
wb.save(OUT)
print('JLC BoM lines:', len(groups), 'placements:', sum(len(g['refs']) for g in groups.values()))
