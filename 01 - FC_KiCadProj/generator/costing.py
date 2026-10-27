# Adds a "Costing" sheet to the assembly BoM: component cost per board for a 10-board and a 100-board batch.
# Prices: LCSC (USD) unless noted, looked up on 2026-10-15; "Estimate" rows use the price of an equivalent part in the
# same series/size. The price tier is the one reached by the batch quantity (qty per board x boards).
import sys
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

BOM = sys.argv[1]
Q, E = 'Quote', 'Estimate'
# (refs, qty/board, MPN, source / part #, unit @ 10 boards, unit @ 100 boards, basis, notes)
E_ROWS = [   # rev E: parts as assembled by JLCPCB (jlc_parts.py); LCSC prices of 2026-10-16/17
 ('AE1', 1, '2450AT18A0100001E', 'LCSC C17430588', 0.69, 0.65, Q, 'Price from the JLC BOM tool (5 boards)'),
 ('C1', 1, 'T520D477M006ATE015', 'LCSC C696809', 1.6307, 1.2652, Q, 'Only 78 in stock at LCSC'),
 ('C2, C3, C4, C5', 4, 'CL10A106KP8NNNC', 'LCSC C19702 (JLC Basic)', 0.0287, 0.0287, Q, ''),
 ('C6', 1, 'CL31A107MQHNNNE', 'LCSC C15008', 0.1319, 0.0968, Q, ''),
 ('C7, C9', 2, 'CL10A475KO8NNNC', 'LCSC C19666 (JLC Basic)', 0.0205, 0.0159, Q, ''),
 ('C8, C22, C43', 3, 'CL05A105KA5NQNC', 'LCSC C52923 (JLC Basic)', 0.0068, 0.0068, Q, 'MOQ 100'),
 ('C10', 1, 'CL05A105KA5NQNC', 'LCSC C52923 (JLC Basic)', 0.0068, 0.0068, Q, ''),
 ('C11', 1, 'CL10A475KO8NNNC', 'LCSC C19666 (JLC Basic)', 0.0205, 0.0159, Q, ''),
 ('C12, C14, C15, C16, C17, C19, C21, C23, C24, C25, C26, C28, C37, C38, C39, C40, C41', 17, 'CL05B104KO5NNNC', 'LCSC C1525 (JLC Basic)', 0.0049, 0.0049, Q, 'MOQ 100'),
 ('C18', 1, 'CL05B224KO5NNNC', 'LCSC C16772', 0.0054, 0.0054, Q, ''),
 ('C20', 1, 'CL10A106KP8NNNC', 'LCSC C19702 (JLC Basic)', 0.0287, 0.0287, Q, '10 V part'),
 ('C27', 1, '0402CG101J500NT', 'LCSC C1546 (JLC Basic)', 0.0032, 0.0032, Q, ''),
 ('C29', 1, 'CL05A475MP5NRNC', 'LCSC C23733', 0.0168, 0.0168, Q, 'Out of stock at LCSC on 2026-10-16: check JLC stock'),
 ('C44', 1, 'CL05A225MQ5NSNC', 'LCSC C12530 (JLC Basic)', 0.004, 0.004, E, ''),
 ('D1, D2', 2, 'WS2812B-2020', 'LCSC C965555', 0.10, 0.08, E, 'Worldsemi RGB LED, price estimated'),
 ('D5, D6, D7, D8', 4, 'SS34F', 'LCSC C908669', 0.0326, 0.0326, Q, 'GOODWORK, SMAF (DO-221AC); replaces STPS3L45AF'),
 ('D9', 1, 'PMEG2010AEH,115', 'LCSC C110921', 0.1082, 0.0851, Q, ''),
 ('D10', 1, 'XL-1005UGC', 'LCSC C965793', 0.012, 0.008, E, 'XINGLIGHT 0402 green'),
 ('D11', 1, 'RB521S30T1G', 'LCSC C8523', 0.03, 0.02, E, ''),
 ('J1', 1, 'TYPE-C-31-M-12', 'LCSC C165948', 0.1729, 0.1365, Q, 'MOQ 5 pcs'),
 ('J3, J5', 2, 'SM04B-SRSS-TB(LF)(SN)', 'LCSC C160404', 0.25, 0.18, E, 'JST SH 4P side entry (Qwiic, ELRS); price estimated'),
 ('L1', 1, 'MPH201210S2R2MT', 'LCSC C55755', 0.0467, 0.0388, Q, ''),
 ('L2', 1, 'LQG15HS10NJ02D', 'LCSC C77103', 0.0185, 0.0185, Q, 'MOQ 50'),
 ('Q1, Q2, Q3, Q4', 4, 'AON7524', 'LCSC C431195', 0.232, 0.178, Q, ''),
 ('Q5', 1, 'AO3401A', 'LCSC C15127', 0.1028, 0.0831, Q, 'MOQ 5 pcs'),
 ('R1', 1, 'HRC0603F1R00ENTN', 'LCSC C54920875', 0.005, 0.004, E, ''),
 ('R2, R10, R11, R24, R25, R26, R27', 7, '0402WGF1003TCE', 'LCSC C25741 (JLC Basic)', 0.002, 0.002, E, ''),
 ('R3', 1, 'RC-02K2873FT', 'LCSC C42921050', 0.003, 0.002, E, ''),
 ('R4', 1, '0402WGF1003TCE', 'LCSC C25741 (JLC Basic)', 0.002, 0.002, E, ''),
 ('R5', 1, '0402WGF3301TCE', 'LCSC C25890 (JLC Basic)', 0.002, 0.002, E, ''),
 ('R6, R36', 2, '0402WGF1001TCE', 'LCSC C11702 (JLC Basic)', 0.002, 0.002, E, ''),
 ('R7', 1, 'FRC0402F1R00TS', 'LCSC C2909329', 0.003, 0.002, E, ''),
 ('R8, R9', 2, '0402WGF4703TCE', 'LCSC C25790 (JLC Basic)', 0.002, 0.002, E, ''),
 ('R12, R13', 2, '0402WGF5101TCE', 'LCSC C25905 (JLC Basic)', 0.002, 0.002, E, ''),
 ('R14, R37, R38', 3, '0402WGF1002TCE', 'LCSC C25744 (JLC Basic)', 0.002, 0.002, E, ''),
 ('R15, R16', 2, '0402WGF2201TCE', 'LCSC C25879 (JLC Basic)', 0.002, 0.002, E, ''),
 ('R17, R18', 2, '0402WGF4701TCE', 'LCSC C25900 (JLC Basic)', 0.002, 0.002, E, ''),
 ('R20, R21, R22, R23', 4, '0402WGF220JTCE', 'LCSC C25092 (JLC Basic)', 0.002, 0.002, E, ''),
 ('R34', 1, '0402WGF0000TCE', 'LCSC C17168 (JLC Basic)', 0.002, 0.002, E, ''),
 ('R35', 1, 'RLM12FTCMR002', 'LCSC C710257', 0.0476, 0.0389, Q, '2 mOhm 1 W shunt, 145k in stock'),
 ('R39', 1, '0402WGF330JTCE', 'LCSC C25105 (JLC Basic)', 0.002, 0.002, E, ''),
 ('R40', 1, '0402WGF4702TCE', 'LCSC C25792 (JLC Basic)', 0.002, 0.002, E, ''),
 ('R41', 1, '0402WGF1502TCE', 'LCSC C25756 (JLC Basic)', 0.002, 0.002, E, ''),
 ('U1', 1, 'LSM6DSV16XTR', 'LCSC C5267406', 3.0014, 2.4748, Q, ''),
 ('U2', 1, 'STM32WB55CGU6', 'LCSC C404023', 7.8102, 5.8543, Q, 'Out of stock at LCSC/JLC (2026-10-27): consigned part; Mouser/DigiKey 7.22 USD @10, 6.16-6.31 USD @100'),
 ('U3', 1, 'IIS2MDCTR', 'LCSC C2655002', 3.6906, 2.981, Q, ''),
 ('U4', 1, 'LPS22HHTR', 'LCSC C2827824', 3.9895, 3.9895, Q, 'Replaces LPS22HBTR (out of stock); 70 pcs at LCSC on 2026-10-27'),
 ('U5', 1, 'LD39130SPUR', 'LCSC C2798213', 0.60, 0.48, E, ''),
 ('U6', 1, 'STC4054GR', 'LCSC C262930', 1.4469, 1.0963, Q, ''),
 ('U7', 1, 'USBLC6-2SC6', 'LCSC C7519', 0.1786, 0.1375, Q, 'MOQ 5 pcs'),
 ('U8', 1, 'MLPF-WB55-01E3', 'LCSC C2651048', 0.368, 0.2711, Q, ''),
 ('U9', 1, 'TSC213ICT', 'LCSC C1858319', 0.60, 0.45, E, 'Current-sense amplifier, price estimated'),
 ('U10', 1, 'W25Q128JVPIQ', 'LCSC C190862', 1.60, 1.30, E, '16 MB log flash, price estimated'),
 ('U11', 1, 'LDK130PU-R', 'LCSC C157446', 0.4186, 0.3181, Q, '1,162 in stock on 2026-10-17'),
 ('Y1', 1, 'NX2016SA-32MHZ-STD-CZS-5', 'LCSC C843260', 0.3534, 0.3534, Q, 'NDK 32 MHz 8 pF +-10 ppm'),
]


# rev F: rows built from the BoM sheet (one per MPN), prices looked up by MPN in the rev E table above
PRICE = {}
for refs_, q_, mpn_, src_, p10_, p100_, basis_, note_ in E_ROWS:
    PRICE.setdefault(mpn_, (src_, p10_, p100_, basis_, note_))
PRICE.update({
    '0402WGF1000TCE': ('LCSC C25076 (JLC Basic)', 0.002, 0.002, E, ''),
    'SM08B-SRSS-TB(LF)(SN)': ('LCSC C160407', 0.35, 0.25, E, 'JST SH 8P side entry (ESC link); price estimated'),
    'WS2812B-2020': ('LCSC C965555', 0.10, 0.08, E, 'Worldsemi RGB LED, price estimated'),
    'TPS62160DSGR': ('LCSC C324077', 0.8073, 0.6494, Q, '1,236 in stock on 2026-10-18'),
    'AO3407A': ('LCSC C5379096', 0.0482, 0.0393, Q, 'MSKSEMI'),
    '2N7002': ('LCSC C8545', 0.012, 0.008, E, ''),
    'CL21A226MAQNNNE': ('LCSC C45783 (JLC Basic)', 0.1953, 0.1953, Q, 'MOQ 20'),
    'CL21A106KAYNNNE': ('LCSC C15850 (JLC Basic)', 0.02, 0.016, E, ''),
    '0402WGF4023TCE': ('LCSC C25785', 0.002, 0.002, E, ''),
    # rev H
    'LM5166DRCT': ('LCSC C181495', 3.6923, 3.3626, Q, '350 in stock on 2026-10-18 (30+ tier used for 100 boards)'),
    'SWPA5040S220MT': ('LCSC C68434', 0.12, 0.09, E, 'Sunlord 22 uH 5x5x4, price estimated (same series)'),
    '1206B475K500NT': ('LCSC C29823 (JLC Basic)', 0.03, 0.025, E, ''),
    '0402WGF2003TCE': ('LCSC C25764 (JLC Basic)', 0.002, 0.002, E, ''),
    'CL05B103KB5NNNC': ('LCSC C15195 (JLC Basic)', 0.002, 0.002, E, '10 nF 50 V X7R'),
})
_wb0 = load_workbook(BOM)
_rows = {}
for row in _wb0['BoM'].iter_rows(min_row=5, values_only=True):
    if isinstance(row[0], int) and row[2]:
        g = _rows.setdefault(row[4], [])
        g += [x.strip() for x in str(row[2]).split(',')]
import re as _re
_key = lambda r: (_re.sub(r'\d', '', r), int(_re.sub(r'\D', '', r) or 0))
ROWS = []
for mpn_, refs_ in _rows.items():
    if mpn_ not in PRICE:
        raise SystemExit('no price for ' + mpn_)
    src_, p10_, p100_, basis_, note_ = PRICE[mpn_]
    refs_ = sorted(refs_, key=_key)
    ROWS.append((', '.join(refs_), len(refs_), mpn_, src_, p10_, p100_, basis_, note_))
ROWS.sort(key=lambda x: _key(x[0].split(',')[0]))

wb = load_workbook(BOM)
if 'Costing' in wb.sheetnames:
    del wb['Costing']
ws = wb.create_sheet('Costing')
FONT = 'Arial'
BLUE = Font(name=FONT, size=10, color='0000FF')
ws.append(['ACwing FC rev A - component costing (assembled parts as ordered at JLCPCB, USD)'])
ws.append(['Prices from distributors on 2026-10-15/17 (LCSC unless noted). "Quote" = price read for that exact MPN; '
           '"Estimate" = price of an equivalent part of the same series and size. PCB fabrication, assembly, '
           'stencil, shipping and duties are not included.'])
ws.append(['', 'USD -> EUR exchange rate (edit):', 0.92])
RATE = 'C3'
ws.append([])
hdr = ['Item', 'Part Reference', 'Qty / board', 'MPN', 'Source / part #', 'Unit price @ 10 boards (USD)',
       'Cost / board @ 10 boards (USD)', 'Unit price @ 100 boards (USD)', 'Cost / board @ 100 boards (USD)', 'Price basis', 'Notes']
ws.append(hdr)
H = ws.max_row
for i, (refs, q, mpn, src, p10, p100, basis, note) in enumerate(ROWS, 1):
    r = ws.max_row + 1
    ws.append([i, refs, q, mpn, src, p10, '=C%d*F%d' % (r, r), p100, '=C%d*H%d' % (r, r), basis, note or '-'])
last = ws.max_row
ws.append([''] * 11)                       # spacer (a real row, so the indices below are exact)
iu = lambda u: H + 1 + [x[0] for x in ROWS].index(u)   # single-part rows only
ws.append(['', 'Components per board (USD)', '=SUM(C%d:C%d)' % (H + 1, last), 'placements', '', '',
           '=SUM(G%d:G%d)' % (H + 1, last), '', '=SUM(I%d:I%d)' % (H + 1, last), '', 'Sum of the cost per board'])
r1 = ws.max_row
ws.append(['', 'Components per board (EUR)', '', '', '', '', '=G%d*%s' % (r1, RATE), '', '=I%d*%s' % (r1, RATE), '', 'At the exchange rate in C3'])
ws.append(['', 'Whole batch (USD)', '', '', '', '', '=G%d*10' % r1, '', '=I%d*100' % r1, '', '10 boards / 100 boards'])
ws.append(['', 'Share of U2 + sensors (U1, U3, U4)', '', '', '', '',
           '=(G%d+G%d+G%d+G%d)/G%d' % (iu('U2'), iu('U1'), iu('U3'), iu('U4'), r1), '',
           '=(I%d+I%d+I%d+I%d)/I%d' % (iu('U2'), iu('U1'), iu('U3'), iu('U4'), r1), '', 'MCU and MEMS sensors'])
r4 = ws.max_row
end = ws.max_row
ws.append([''] * 11)
ws.append(['Not included: C36 (DNP), pads/holes (PCB features), the ESC / power board and its cable, grommets. JLCPCB PCBA adds a setup fee '
           'per unique "extended" part (most ICs here) on top of the component price.'])
note_r = ws.max_row

thin = Side(style='thin', color='BFBFBF')
for row in ws.iter_rows(min_row=1, max_row=note_r):
    for c in row:
        c.font = Font(name=FONT, size=10)
        c.alignment = Alignment(wrap_text=True, vertical='top')
ws['A1'].font = Font(name=FONT, size=13, bold=True)
ws['A2'].font = Font(name=FONT, size=9, italic=True, color='595959')
ws['B3'].font = Font(name=FONT, size=10, bold=True)
ws[RATE].font = BLUE; ws[RATE].fill = PatternFill('solid', fgColor='FFFF00'); ws[RATE].number_format = '0.00'
for c in ws[H]:
    c.font = Font(name=FONT, size=10, bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='305496')
    c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
for r in range(H + 1, last + 1):
    for c in ws[r]:
        c.border = Border(top=thin, bottom=thin, left=thin, right=thin)
        if r % 2 == 0:
            c.fill = PatternFill('solid', fgColor='F2F2F2')
    for col in (6, 8):
        ws.cell(r, col).font = BLUE; ws.cell(r, col).number_format = '0.0000'
    for col in (7, 9):
        ws.cell(r, col).number_format = '0.0000'
    for col in (1, 3):
        ws.cell(r, col).alignment = Alignment(horizontal='center', vertical='top')
for r in range(r1, end + 1):
    for c in ws[r]:
        c.font = Font(name=FONT, size=10, bold=True)
        c.border = Border(top=thin, bottom=thin)
    for col in (7, 9):
        ws.cell(r, col).number_format = '0.00'
    ws.cell(r, 3).alignment = Alignment(horizontal='center')
for col in (7, 9):
    ws.cell(r4, col).number_format = '0%'
ws.cell(r1, 2).fill = ws.cell(r1, 7).fill = ws.cell(r1, 9).fill = PatternFill('solid', fgColor='DDEBF7')
ws.cell(note_r, 1).font = Font(name=FONT, size=9, italic=True, color='595959')
for col, w in zip(range(1, 12), (6, 30, 9, 26, 24, 14, 14, 14, 14, 10, 52)):
    ws.column_dimensions[get_column_letter(col)].width = w
for rr in (1, 2, note_r):
    ws.merge_cells(start_row=rr, start_column=1, end_row=rr, end_column=11)
ws.row_dimensions[2].height = 40
ws.freeze_panes = 'A%d' % (H + 1)
ws.page_setup.orientation = 'landscape'; ws.page_setup.fitToWidth = 1; ws.sheet_properties.pageSetUpPr.fitToPage = True
ws.page_setup.fitToHeight = 0
# check: every BoM line is costed
bom = wb['BoM']
bom_refs = set()
for row in bom.iter_rows(min_row=5, values_only=True):
    if isinstance(row[0], int) and row[2]:
        bom_refs |= {x.strip() for x in str(row[2]).split(',')}
cost_refs = set()
for x in ROWS:
    cost_refs |= {y.strip() for y in x[0].split(',')}
qty = sum(x[1] for x in ROWS)
assert bom_refs == cost_refs, (sorted(bom_refs - cost_refs), sorted(cost_refs - bom_refs))
assert all(len([y for y in x[0].split(',')]) == x[1] for x in ROWS), 'qty mismatch'
wb.save(BOM)
print('costed lines', len(ROWS), 'placements', qty)
