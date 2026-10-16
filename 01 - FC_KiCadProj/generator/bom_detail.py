# Detailed (assembly) BoM for DimaQuadFC rev C2: quantity, references, MPN, manufacturer, package, description,
# side, notes. Groups come from the schematic (parts.json); the assembly side comes from the routed PCB.
import sys, json, re, pcbnew
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

PARTS, BOARD, OUT = sys.argv[1:4]
parts = json.load(open(PARTS))
side = {f.GetReference(): ('Bottom' if f.IsFlipped() else 'Top') for f in pcbnew.LoadBoard(BOARD).GetFootprints()}

# (value, footprint name) -> (MPN, manufacturer, package, description, notes)
Y = lambda v: 'RC0402FR-07%sL' % v
MPN = {
 ('470uF 6.3V polymer', 'CP_EIA-7343-31_Kemet-D'): ('T520D477M006ATE015', 'KEMET', '7343-31 (EIA D), h 2.8 mm',
     'Capacitor, tantalum polymer, 470 uF, 6.3 V, 20%, ESR 15 mOhm', 'Bulk at the battery input. Alternative: Panasonic 6TPE470MI'),
 ('10uF 10V', 'C_0603_1608Metric'): ('GRM188R61A106KE69D', 'Murata', '0603 (1608 metric)',
     'Capacitor, MLCC, 10 uF, 10 V, X5R, 10%', 'Motor-stage local decoupling, next to each MOSFET'),
 ('100uF 6.3V', 'C_1206_3216Metric'): ('GRM31CR60J107ME39L', 'Murata', '1206 (3216 metric), h 1.6 mm',
     'Capacitor, MLCC, 100 uF, 6.3 V, X5R, 20%', 'RC filter capacitor (VBAT_F)'),
 ('4.7uF', 'C_0603_1608Metric'): ('GRM188R61A475KE15D', 'Murata', '0603 (1608 metric), h 0.8 mm',
     'Capacitor, MLCC, 4.7 uF, 10 V, X5R, 10%', 'VSYS (C7) and MCU VDD bulk (C9)'),
 ('4.7uF 10V', 'C_0603_1608Metric'): ('GRM188R61A475KE15D', 'Murata', '0603 (1608 metric), h 0.8 mm',
     'Capacitor, MLCC, 4.7 uF, 10 V, X5R, 10%', 'Charger RC (with R7), bottom side'),
 ('1uF', 'C_0402_1005Metric'): ('GRM155R61A105KE15D', 'Murata', '0402 (1005 metric)',
     'Capacitor, MLCC, 1 uF, 10 V, X5R, 10%', 'LDO output (C8), VDDA (C22)'),
 ('1uF 10V', 'C_0402_1005Metric'): ('GRM155R61A105KE15D', 'Murata', '0402 (1005 metric)',
     'Capacitor, MLCC, 1 uF, 10 V, X5R, 10%', 'Charger input'),
 ('100nF', 'C_0402_1005Metric'): ('GRM155R71C104KA88D', 'Murata', '0402 (1005 metric)',
     'Capacitor, MLCC, 100 nF, 16 V, X7R, 10%', 'Decoupling (MCU, sensors, NRST)'),
 ('220nF', 'C_0402_1005Metric'): ('GRM155R71C224KA12D', 'Murata', '0402 (1005 metric)',
     'Capacitor, MLCC, 220 nF, 16 V, X7R, 10%', 'IIS2MDC C1 (ESR < 200 mOhm)'),
 ('10uF 6.3V', 'C_0603_1608Metric'): ('GRM188R60J106ME47D', 'Murata', '0603 (1608 metric), h 0.8 mm',
     'Capacitor, MLCC, 10 uF, 6.3 V, X5R, 20%', 'VDD bulk, bottom side'),
 ('white', 'LED_0402_1005Metric'): ('IN-S42ATUW', 'Inolux', '0402 (1005 metric)',
     'LED, white, 0402, Vf 3.1 V typ', 'Front navigation LEDs (supplied from VSYS)'),
 ('red', 'LED_0402_1005Metric'): ('IN-S42ATR', 'Inolux', '0402 (1005 metric)',
     'LED, red 631 nm, 0402, Vf 2.1 V typ', 'Rear navigation LEDs'),
 ('green', 'LED_0402_1005Metric'): ('IN-S42ATG', 'Inolux', '0402 (1005 metric)',
     'LED, green, 0402', 'Charge indicator (on = charging)'),
 ('STPS3L45AF', 'D_SMAflat'): ('STPS3L45AF', 'STMicroelectronics', 'SMAflat (DO-221AC)',
     'Diode, Schottky, 45 V, 3 A, low Vf', 'Motor freewheeling diode'),
 ('PMEG2010AEH', 'D_SOD-123F'): ('PMEG2010AEH,115', 'Nexperia', 'SOD-123F',
     'Diode, Schottky, 20 V, 1 A, Vf ~0.35 V', 'USB VBUS -> VSYS'),
 ('USB-C (HRO TYPE-C-31-M-12)', 'USB_C_Receptacle_HRO_TYPE-C-31-M-12'): ('TYPE-C-31-M-12', 'HRO (Korea Hroparts)', 'USB-C receptacle, 16 pin, SMD + THT shell',
     'Connector, USB Type-C receptacle, USB 2.0, top mount', 'Mouth 0.35 mm past the right-corner chamfer'),
 ('AON7524', 'Vishay_PowerPAK_1212-8_Single'): ('AON7524', 'Alpha & Omega Semiconductor', 'DFN 3x3 EP (DFN3x3A_8L_EP1)',
     'MOSFET, N-channel, 30 V, logic level, 5.8 mOhm @ VGS 2.5 V', 'Footprint is a PowerPAK 1212-8 approximation: check the AOS land pattern before ordering'),
 ('AO3401A', 'SOT-23'): ('AO3401A', 'Alpha & Omega Semiconductor', 'SOT-23',
     'MOSFET, P-channel, 30 V, 4 A', 'Battery/USB load sharing'),
 ('2N7002DW', 'SOT-363_SC-70-6'): ('2N7002DW-7-F', 'Diodes Inc.', 'SOT-363 (SC-70-6)',
     'MOSFET, dual N-channel, 60 V, 115 mA', 'LED drivers'),
 ('1R', 'R_0603_1608Metric'): ('RC0603FR-071RL', 'Yageo', '0603 (1608 metric)',
     'Resistor, 1 Ohm, 1%, 0.1 W', 'RC filter (VBAT -> VBAT_F)'),
 ('100k', 'R_0402_1005Metric'): (Y('100K'), 'Yageo', '0402 (1005 metric)', 'Resistor, 100 kOhm, 1%, 1/16 W', 'Pull-downs and VBUS divider'),
 ('287k 1%', 'R_0402_1005Metric'): (Y('287K'), 'Yageo', '0402 (1005 metric)', 'Resistor, 287 kOhm, 1%, 1/16 W', 'LDO feedback (VOUT = 3.10 V)'),
 ('100k 1%', 'R_0402_1005Metric'): (Y('100K'), 'Yageo', '0402 (1005 metric)', 'Resistor, 100 kOhm, 1%, 1/16 W', 'LDO feedback'),
 ('3.3k 1%', 'R_0402_1005Metric'): (Y('3K3'), 'Yageo', '0402 (1005 metric)', 'Resistor, 3.3 kOhm, 1%, 1/16 W', 'Charger PROG: I_BAT ~300 mA'),
 ('1k', 'R_0402_1005Metric'): (Y('1K'), 'Yageo', '0402 (1005 metric)', 'Resistor, 1 kOhm, 1%, 1/16 W', 'Charge LED'),
 ('1R', 'R_0402_1005Metric'): (Y('1R'), 'Yageo', '0402 (1005 metric)', 'Resistor, 1 Ohm, 1%, 1/16 W', 'Charger RC (STC4054 DS sec. 6.13)'),
 ('470k 1%', 'R_0402_1005Metric'): (Y('470K'), 'Yageo', '0402 (1005 metric)', 'Resistor, 470 kOhm, 1%, 1/16 W', 'VBAT sense divider'),
 ('5.1k', 'R_0402_1005Metric'): (Y('5K1'), 'Yageo', '0402 (1005 metric)', 'Resistor, 5.1 kOhm, 1%, 1/16 W', 'USB-C CC pull-downs'),
 ('10k', 'R_0402_1005Metric'): (Y('10K'), 'Yageo', '0402 (1005 metric)', 'Resistor, 10 kOhm, 1%, 1/16 W', 'BOOT0 pull-down (PH3-BOOT0)'),
 ('2.2k', 'R_0402_1005Metric'): (Y('2K2'), 'Yageo', '0402 (1005 metric)', 'Resistor, 2.2 kOhm, 1%, 1/16 W', 'I2C1 pull-ups'),
 ('4.7k', 'R_0402_1005Metric'): (Y('4K7'), 'Yageo', '0402 (1005 metric)', 'Resistor, 4.7 kOhm, 1%, 1/16 W', 'Sensor hub pull-ups'),
 ('22R', 'R_0402_1005Metric'): (Y('22R'), 'Yageo', '0402 (1005 metric)', 'Resistor, 22 Ohm, 1%, 1/16 W', 'MOSFET gate resistors'),
 ('220R', 'R_0402_1005Metric'): (Y('220R'), 'Yageo', '0402 (1005 metric)', 'Resistor, 220 Ohm, 1%, 1/16 W', 'White LED current'),
 ('470R', 'R_0402_1005Metric'): (Y('470R'), 'Yageo', '0402 (1005 metric)', 'Resistor, 470 Ohm, 1%, 1/16 W', 'Red LED current'),
 ('LSM6DSV16X', 'LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y'): ('LSM6DSV16XTR', 'STMicroelectronics', 'LGA-14, 2.5 x 3 x 0.83 mm',
     'IMU, 6-axis (accelerometer + gyroscope), I2C/I3C/SPI, sensor hub', 'Board centre; I2C address 0x6B'),
 ('STM32WB55CGU6', 'QFN-48-1EP_7x7mm_P0.5mm_EP5.6x5.6mm'): ('STM32WB55CGU6', 'STMicroelectronics', 'UFQFPN-48, 7 x 7 x 0.55 mm, EP 5.6 mm',
     'MCU, Cortex-M4 + M0+ radio core, BLE 5 / 802.15.4, 1 MB flash, 256 KB RAM, SMPS', 'EP to GND through a 3x3 via array'),
 ('MLPF-WB55-01E3', 'ST_MLPF-WB55-01E3_CSP-6'): ('MLPF-WB55-01E3', 'STMicroelectronics', 'CSP-6 (bumps), 1.0 x 1.6 mm approx., pitch 0.5 mm',
     '2.4 GHz low-pass filter with integrated impedance matching for STM32WB55 RF1', 'Between U2 RF1 and the antenna feed (AN5290 IPD BoM)'),
 ('2450AT18A0100001E', 'Johanson_2450AT18x100'): ('2450AT18A0100001E', 'Johanson Technology', '1206 (3.2 x 1.6 x 1.3 mm)',
     'Chip antenna, 2.4 GHz, 0.5 dBi, 50 Ohm', 'Johanson global P/N of the legacy 2450AT18A100E (same part). Left board edge, in the copper keep-out; R34 = 0R, C36 not fitted'),
 ('32MHz', 'Crystal_SMD_2016-4Pin_2.0x1.6mm'): ('NX2016SA-32M-EXS00A-CS06654', 'NDK', 'SMD 2016, 4 pad, 2.0 x 1.6 mm',
     'Crystal, 32 MHz, HSE for the STM32WB radio', 'No load capacitors: internal HSE trimming (AN5042). Also the RF wake-up (HSE/1024) and RTC (HSE/32) clock: no LSE'),
 ('2.2uH', 'L_0805_2012Metric'): ('74479774222', 'Wurth Elektronik', '0805 (2012 metric), h 0.6 mm',
     'Inductor, multilayer (WE-PMI), 2.2 uH, 20%, Isat 250 mA, DCR 0.34 Ohm', 'SMPS inductor for the 8 MHz SMPS clock (DS13252 table 6)'),
 ('10nH', 'L_0402_1005Metric'): ('LQG15WZ10NJ02D', 'Murata', '0402 (1005 metric)',
     'Inductor, multilayer, 10 nH, 5%', 'SMPS output filter, AN5290'),
 ('4.7uF', 'C_0402_1005Metric'): ('GRM155R61A475MEAAD', 'Murata', '0402 (1005 metric)',
     'Capacitor, MLCC, 4.7 uF, 10 V, X5R, 20%', 'SMPS output (VFBSMPS)'),
 ('100pF', 'C_0402_1005Metric'): ('GRM1555C1H101JA01D', 'Murata', '0402 (1005 metric)',
     'Capacitor, MLCC, 100 pF, 50 V, C0G, 5%', 'VDDRF high-frequency decoupling'),
 ('0R', 'R_0402_1005Metric'): ('RC0402JR-070RL', 'Yageo', '0402 (1005 metric)',
     'Resistor, 0 Ohm jumper, 1/16 W', 'Antenna tuning, series position (replace with L/C after tuning)'),
 ('DNP', 'C_0402_1005Metric'): ('-', '-', '0402 (1005 metric)',
     'Not populated: antenna tuning, shunt position', 'Leave empty; fit only after VNA tuning'),
 ('IIS2MDC', 'LGA-12_2x2mm_P0.5mm'): ('IIS2MDCTR', 'STMicroelectronics', 'LGA-12, 2 x 2 x 0.7 mm',
     'Magnetometer, 3-axis, +-50 gauss, 16 bit, I2C/SPI, industrial grade (LIS2MDL-compatible)', 'Front corner; read through the LSM6DSV16X sensor hub, address 0x1E'),
 ('LPS22HB', 'ST_HLGA-10_2x2mm_P0.5mm_LayoutBorder3x2y'): ('LPS22HBTR', 'STMicroelectronics', 'HLGA-10, 2 x 2 x 0.76 mm',
     'Pressure sensor (barometer), 260-1260 hPa, I2C/SPI', 'Altitude hold; address 0x5D. Keep the vent hole clear'),
 ('LD39130SPUR', 'DFN-6_1.3x1.2mm_P0.4mm'): ('LD39130SPUR', 'STMicroelectronics', 'DFN-6, 1.2 x 1.3 mm',
     'LDO regulator, adjustable, 300 mA, 1 uA quiescent', 'Set to 3.10 V by R3/R4'),
 ('STC4054GR', 'TSOT-23-5'): ('STC4054GR', 'STMicroelectronics', 'TSOT-23-5',
     'Battery charger, linear, single-cell Li-ion/LiPo, 4.2 V, up to 800 mA', 'Charge current set to ~300 mA by R5'),
 ('USBLC6-2SC6', 'SOT-23-6'): ('USBLC6-2SC6', 'STMicroelectronics', 'SOT-23-6',
     'ESD protection, 2-line, low capacitance, for USB 2.0', 'Next to the USB-C connector'),
}
# not-assembled items: (value, MPN, manufacturer, package, description, notes)
NOT_ASSEMBLED = {
 'J2': ('BATT 1S', 'N/A (PCB feature)', 'N/A', 'BattPads_1x02_SMD: 2 SMD pads, rear corner',
        'Battery lead solder pads, 1S LiPo, AWG 22-24',
        'Solder a BT2.0 or PH2.0 pigtail (male, 22 AWG) to the pads. Pad 1 = VBAT (+), pad 2 = GND'),
 'M': ('coreless 8520', 'N/A (PCB feature)', 'N/A', 'MotorPads_1x02_SMD: 2 SMD pads per motor',
       'Motor lead solder pads for 8.5 x 20 mm coreless brushed motors, 3.7 V',
       'Motors sit in the frame ducts and are soldered by hand; "+" pad to VBAT, "-" pad to the MOSFET drain. Motors supplied with the frame'),
 'TP': ('pogo pad', 'N/A (PCB feature)', 'N/A', 'TestPoint_Pad_D1.0mm: 1.0 mm round SMD pad',
        'Programming / debug pads, 2 x 4 grid at 2.54 mm pitch',
        'Row 1: SWDIO, SWCLK, NRST, BOOT0; row 2: VDD, GND, UART_TX, UART_RX. Use a 2.54 mm pogo-pin fixture'),
 'H': ('D3.2 PTH', 'N/A (PCB feature)', 'N/A', 'Grommet_PTH_3.2mm_Pad5.0mm: plated 3.2 mm hole, 5.0 mm ring',
       'Mounting holes for M2 anti-vibration grommets, 16 x 16 mm pattern',
       'Exposed 5.0 mm GND copper ring on both sides (grommet seat). Grommets supplied with the frame'),
}
DNP_INFO = ('Not populated (tuning)', 'TBD after VNA tuning (C0G capacitor or chip inductor)', 'Murata (GRM1555C1H C0G or LQG15HS series)',
            '0402 (1005 metric)', 'Antenna tuning, shunt position at the antenna side',
            'Do not populate. Fit only if the VNA measurement asks for it; R34 (series) is the other tuning spot')

key = lambda r: (re.sub(r'\d', '', r), int(re.sub(r'\D', '', r) or 0))
groups = {}
skipped = []
dnp = []
for ref, v in parts.items():
    fpn = v['fp'].split(':')[1]
    if ref == 'J2' or ref.startswith(('M', 'TP', 'H')):
        skipped.append(ref); continue
    if v.get('dnp'):
        dnp.append(ref); continue
    k = (v['value'], fpn)
    if k not in MPN:
        raise SystemExit('no MPN for %s %s' % (ref, k))
    # split groups that are mounted on both sides
    groups.setdefault((MPN[k][0], v['value'], fpn, side[ref]), []).append(ref)

FONT = 'Arial'
wb = Workbook(); ws = wb.active; ws.title = 'BoM'
hdr = ['Item', 'Quantity', 'Part Reference', 'Value', 'MPN', 'Manufacturer', 'Package', 'Description', 'Side', 'Notes']
ws.append(['DimaQuadFC rev C2 - assembly BoM (1 board)'])
ws.append(['Source: DimaQuadFC_C2.kicad_sch / DimaQuadFC_C2.kicad_pcb. MPNs are proposals: confirm stock and equivalents with the assembler.'])
ws.append([])
ws.append(hdr)
H = 4
thin = Side(style='thin', color='BFBFBF')
rows = sorted(groups.items(), key=lambda kv: key(sorted(kv[1], key=key)[0]))
for i, ((mpn, val, fpn, sd), refs) in enumerate(rows, 1):
    m = MPN[(val, fpn)]
    refs = sorted(refs, key=key)
    note = m[4]
    if val == '100k' and sd == 'Top':
        note = 'Motor MOSFET gate pull-downs'
    elif val == '100k':
        note = 'Q5 gate pull-down (R2), VBUS sense divider (R10, R11), LED driver gate pull-downs (R32, R33)'
    if sd == 'Bottom' and 'h ' not in m[2] and fpn.startswith(('C_0603', 'C_1206')):
        note += '; bottom side, height <= 1.2 mm'
    ws.append([i, len(refs), ', '.join(refs), val, m[0], m[1], m[2], m[3], sd, note])
last = ws.max_row
ws.append([])
ws.append(['Total', '=SUM(B%d:B%d)' % (H + 1, last), 'Total placements (assembled parts)', '-', '=COUNTA(E%d:E%d)' % (H + 1, last), 'line items (unique MPN / side)', '-', '-', '-', 'Not-assembled items listed below'])
tot = ws.max_row

ws.append([])
ws.append(['Not assembled (PCB features / off-board)'])
na0 = ws.max_row
ws.append(hdr)
NA_H = ws.max_row
k = 0
for pref, (val, mpn, man, pkg, desc, note) in NOT_ASSEMBLED.items():
    refs = sorted([r for r in skipped if (r == pref if pref == 'J2' else (r.startswith(pref) and r != 'J2'))], key=key)
    if pref == 'M':
        refs = [r for r in refs if re.match(r'M\d', r)]
    k += 1
    ws.append(['NA%d' % k, len(refs), ', '.join(refs), val, mpn, man, pkg, desc, ('Both (plated through)' if pref == 'H' else ', '.join(sorted({side[r] for r in refs}))), note])
for r in sorted(dnp, key=key):
    k += 1
    ws.append(['NA%d' % k, 1, r, parts[r]['value']] + list(DNP_INFO[1:5]) + [side[r], DNP_INFO[5]])
end = ws.max_row

# formatting
for row in ws.iter_rows(min_row=1, max_row=end):
    for c in row:
        c.font = Font(name=FONT, size=10)
        c.alignment = Alignment(wrap_text=True, vertical='top')
ws['A1'].font = Font(name=FONT, size=13, bold=True)
ws['A2'].font = Font(name=FONT, size=9, italic=True, color='595959')
for c in ws[H]:
    c.font = Font(name=FONT, size=10, bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='305496')
    c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
for r in range(H + 1, last + 1):
    for c in ws[r]:
        c.border = Border(top=thin, bottom=thin, left=thin, right=thin)
        if r % 2 == 0:
            c.fill = PatternFill('solid', fgColor='F2F2F2')
    ws.cell(r, 1).alignment = Alignment(horizontal='center', vertical='top')
    ws.cell(r, 2).alignment = Alignment(horizontal='center', vertical='top')
for c in ws[tot]:
    c.font = Font(name=FONT, size=10, bold=True)
ws.cell(tot, 2).alignment = Alignment(horizontal='center')
ws.cell(tot, 5).alignment = Alignment(horizontal='right')
ws.cell(na0, 1).font = Font(name=FONT, size=11, bold=True)
ws.cell(na0, 1).alignment = Alignment(wrap_text=False, vertical='top')
ws.merge_cells(start_row=na0, start_column=1, end_row=na0, end_column=10)
for c in ws[NA_H]:
    c.font = Font(name=FONT, size=10, bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='7F7F7F')
    c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
for r in range(NA_H + 1, end + 1):
    for c in ws[r]:
        c.border = Border(top=thin, bottom=thin, left=thin, right=thin)
    ws.cell(r, 1).alignment = Alignment(horizontal='center', vertical='top')
    ws.cell(r, 2).alignment = Alignment(horizontal='center', vertical='top')
for col, w in zip(range(1, 11), (6, 9, 30, 20, 24, 22, 28, 48, 8, 50)):
    ws.column_dimensions[get_column_letter(col)].width = w
ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=10)
ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=10)
ws.freeze_panes = 'A%d' % (H + 1)
ws.auto_filter.ref = 'A%d:J%d' % (H, last)
ws.page_setup.orientation = 'landscape'; ws.page_setup.fitToWidth = 1; ws.sheet_properties.pageSetUpPr.fitToPage = True
ws.page_setup.fitToHeight = 0
wb.save(OUT)
print('line items', len(rows), 'placements', sum(len(v) for v in groups.values()), 'not assembled', len(skipped)+len(dnp))
