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
ROWS = [
 ('AE1', 1, '2450AT18A0100001E', 'LCSC C89334 (legacy P/N)', 0.849, 0.6343, Q, 'Same part as legacy 2450AT18A100E (Johanson global P/N). LCSC sells it under the legacy P/N (1,416 in stock); factory lead time 17 weeks'),
 ('C1', 1, 'T520D477M006ATE015', 'LCSC C696809', 1.6307, 1.2652, Q, 'Only 78 in stock at LCSC'),
 ('C2, C3, C4, C5', 4, 'GRM188R61A106KE69D', 'LCSC C77044', 0.0351, 0.0246, Q, ''),
 ('C6', 1, 'GRM31CR60J107ME39L', 'LCSC C77085', 0.1257, 0.1023, Q, ''),
 ('C7, C9', 2, 'GRM188R61A475KE15D', 'LCSC (0603 X5R 10 V)', 0.03, 0.022, E, 'Priced as 0603 X5R MLCC, same series as C77044'),
 ('C8, C22', 2, 'GRM155R61A105KE15D', 'LCSC (0402 X5R)', 0.008, 0.006, E, ''),
 ('C10', 1, 'GRM155R61A105KE15D', 'LCSC (0402 X5R)', 0.008, 0.006, E, ''),
 ('C11', 1, 'GRM188R61A475KE15D', 'LCSC (0603 X5R 10 V)', 0.03, 0.022, E, ''),
 ('C12, C14, C15, C16, C17, C19, C21, C23, C24, C25, C26, C28', 12, 'GRM155R71C104KA88D', 'LCSC C71629', 0.0052, 0.0047, Q, 'MOQ 100 pcs'),
 ('C18', 1, 'GRM155R71C224KA12D', 'LCSC (0402 X7R)', 0.006, 0.005, E, ''),
 ('C20', 1, 'GRM188R60J106ME47D', 'LCSC (0603 X5R)', 0.035, 0.028, E, 'Priced as C77044'),
 ('C27', 1, 'GRM1555C1H101JA01D', 'LCSC (0402 C0G)', 0.004, 0.003, E, ''),
 ('C29', 1, 'GRM155R61A475MEAAD', 'LCSC (0402 X5R 4.7 uF)', 0.02, 0.015, E, ''),
 ('D1, D2', 2, 'IN-S42ATUW', 'DigiKey / LCSC (0402 LED)', 0.05, 0.04, E, 'Any 0402 white LED, Vf ~3 V'),
 ('D3, D4', 2, 'IN-S42ATR', 'DigiKey / LCSC (0402 LED)', 0.04, 0.03, E, 'Any 0402 red LED'),
 ('D5, D6, D7, D8', 4, 'STPS3L45AF', 'LCSC C2969832', 0.4322, 0.3802, Q, 'Only 3 in stock at LCSC: buy from Mouser/DigiKey or the ST eStore'),
 ('D9', 1, 'PMEG2010AEH,115', 'LCSC C110921', 0.1082, 0.0851, Q, ''),
 ('D10', 1, 'IN-S42ATG', 'DigiKey / LCSC (0402 LED)', 0.04, 0.03, E, 'Any 0402 green LED'),
 ('J1', 1, 'TYPE-C-31-M-12', 'LCSC C165948', 0.1729, 0.1365, Q, 'MOQ 5 pcs'),
 ('L1', 1, '74479774222', 'Mouser / DigiKey', 0.80, 0.66, E, 'Mouser 0.86 USD @1, 0.548 USD @10k: intermediate breaks estimated. Active, 3,438 at Mouser'),
 ('L2', 1, 'LQG15WZ10NJ02D', 'LCSC (LQG15 series)', 0.03, 0.02, E, 'LQG15HS10NJ02D (LCSC C77103) is a stocked alternative'),
 ('Q1, Q2, Q3, Q4', 4, 'AON7524', 'LCSC (via Octopart)', 0.232, 0.178, Q, ''),
 ('Q5', 1, 'AO3401A', 'LCSC C15127', 0.1028, 0.0831, Q, 'MOQ 5 pcs'),
 ('Q6', 1, '2N7002DW-7-F', 'LCSC C83571', 0.0879, 0.0714, Q, 'MOQ 5 pcs'),
 ('R1', 1, 'RC0603FR-071RL', 'LCSC (Yageo 0603)', 0.003, 0.002, E, ''),
 ('R2, R10, R11, R32, R33', 5, 'RC0402FR-07100KL', 'LCSC (Yageo 0402)', 0.0024, 0.0019, E, 'Priced as RC0402FR-0710KL (C60490), MOQ 100'),
 ('R3', 1, 'RC0402FR-07287KL', 'LCSC (Yageo 0402)', 0.0024, 0.0019, E, ''),
 ('R4', 1, 'RC0402FR-07100KL', 'LCSC (Yageo 0402)', 0.0024, 0.0019, E, ''),
 ('R5', 1, 'RC0402FR-073K3L', 'LCSC (Yageo 0402)', 0.0024, 0.0019, E, ''),
 ('R6', 1, 'RC0402FR-071KL', 'LCSC (Yageo 0402)', 0.0024, 0.0019, E, ''),
 ('R7', 1, 'RC0402FR-071RL', 'LCSC (Yageo 0402)', 0.0024, 0.0019, E, ''),
 ('R8, R9', 2, 'RC0402FR-07470KL', 'LCSC (Yageo 0402)', 0.0024, 0.0019, E, ''),
 ('R12, R13', 2, 'RC0402FR-075K1L', 'LCSC (Yageo 0402)', 0.0024, 0.0019, E, ''),
 ('R14', 1, 'RC0402FR-0710KL', 'LCSC C60490', 0.0024, 0.0019, Q, 'MOQ 100 pcs'),
 ('R15, R16', 2, 'RC0402FR-072K2L', 'LCSC (Yageo 0402)', 0.0024, 0.0019, E, ''),
 ('R17, R18', 2, 'RC0402FR-074K7L', 'LCSC (Yageo 0402)', 0.0024, 0.0019, E, ''),
 ('R20, R21, R22, R23', 4, 'RC0402FR-0722RL', 'LCSC (Yageo 0402)', 0.0024, 0.0019, E, ''),
 ('R24, R25, R26, R27', 4, 'RC0402FR-07100KL', 'LCSC (Yageo 0402)', 0.0024, 0.0019, E, ''),
 ('R28, R29', 2, 'RC0402FR-07220RL', 'LCSC (Yageo 0402)', 0.0024, 0.0019, E, ''),
 ('R30, R31', 2, 'RC0402FR-07470RL', 'LCSC (Yageo 0402)', 0.0024, 0.0019, E, ''),
 ('R34', 1, 'RC0402JR-070RL', 'LCSC (Yageo 0402)', 0.0024, 0.0019, E, ''),
 ('U1', 1, 'LSM6DSV16XTR', 'LCSC C5267406', 3.0014, 2.4748, Q, ''),
 ('U2', 1, 'STM32WB55CGU6', 'LCSC C404023', 7.8102, 5.8543, Q, 'Mouser/DigiKey: 7.22 USD @10, 6.16-6.31 USD @100'),
 ('U3', 1, 'IIS2MDCTR', 'LCSC C2655002', 3.6906, 2.981, Q, '6,902 in stock at LCSC'),
 ('U4', 1, 'LPS22HBTR', 'LCSC C94049', 2.6466, 2.0382, Q, 'Out of stock at LCSC: reference price; buy where you found stock'),
 ('U5', 1, 'LD39130SPUR', 'TME (GBP 0.45 / 0.36)', 0.60, 0.48, Q, 'Converted at 1.33 USD/GBP; out of stock at TME: check ST eStore / Mouser'),
 ('U6', 1, 'STC4054GR', 'LCSC C262930', 1.4469, 1.0963, Q, ''),
 ('U7', 1, 'USBLC6-2SC6', 'LCSC C7519', 0.1786, 0.1375, Q, 'MOQ 5 pcs'),
 ('U8', 1, 'MLPF-WB55-01E3', 'LCSC C2651048', 0.368, 0.2711, Q, ''),
 ('Y1', 1, 'NX2016SA-32M-EXS00A-CS06654', 'LCSC (NX2016SA series)', 0.4632, 0.3565, E, 'Priced as NX2016SA (LCSC C910048); ST-specified 32 MHz part via NDK distributors'),
]

wb = load_workbook(BOM)
if 'Costing' in wb.sheetnames:
    del wb['Costing']
ws = wb.create_sheet('Costing')
FONT = 'Arial'
BLUE = Font(name=FONT, size=10, color='0000FF')
ws.append(['DimaQuadFC rev C2 - component costing (assembled parts, USD)'])
ws.append(['Prices from distributors on 2026-10-15 (LCSC unless noted). "Quote" = price read for that exact MPN; '
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
iu = lambda u: H + 1 + [x[0] for x in ROWS].index(u)
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
ws.append(['Not included: C36 (DNP), pads/holes (PCB features), motors, battery, grommets. JLCPCB PCBA adds a setup fee '
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
