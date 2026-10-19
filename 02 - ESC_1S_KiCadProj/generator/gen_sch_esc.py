# ACwing ESC 1S rev A: ACwing 1S power board (brushed) for ACwing FC rev A (KiCad 7 schematic generator).
# Rev B adds: USB-C 1S charger (STC4054), charge switch Q5
# (motors and FC off while charging), current shunt after the battery as rev A.
# Takes the place of the FC in frame C: battery pads, current shunt + amplifier, bulk capacitor, four low-side MOSFET
# motor stages at the edge midpoints, standard 4-in-1 ESC connector (JST SH 8-pin) to the FC.
import sys, json
sys.path.insert(0, '/home/claude/genESCB')
import kisch
from kisch import Schematic, POWER_LIB
from custom_syms import all_symbols, LIB

OUT = sys.argv[1]
PROJECT = 'ACwing_ESC1S_A'
POWER_LIB.update({'GND': 'power:GND', 'VBAT': LIB + ':VBAT'})
sch = Schematic(PROJECT, 'A3', title=dict(
    title='ACwing ESC 1S rev A - ACwing 1S power board (brushed) for ACwing FC rev A',
    date='2026-10-18', rev='B', company='ACwing - Andrea Cirillo',
    comments=['40 x 40 mm, 2 layers, 1.0 mm; frame C outline; 20 x 20 mm M2 holes (hard mount)',
              'FC link: standard 4-in-1 ESC connector, JST SH 8-pin, 1:1 cable',
              'Larger drones: a commercial 4-in-1 ESC replaces this board on the same FC cable',
              'Generated automatically: run ERC before release']))
for name, node in all_symbols().items():
    sch.add_lib(LIB + ':' + name, node)

FP_R = 'Resistor_SMD:R_0402_1005Metric'
FP_C = 'Capacitor_SMD:C_0402_1005Metric'
FP_C0603 = 'Capacitor_SMD:C_0603_1608Metric'

def _fpos(x, y, rot, side='right'):
    if rot in (0, 180):
        if side == 'left':
            return {'Reference': (x - 2.54, y - 1.27), 'Value': (x - 2.54, y + 1.27), 'just': 'right'}
        return {'Reference': (x + 2.54, y - 1.27), 'Value': (x + 2.54, y + 1.27), 'just': 'left'}
    return {'Reference': (x, y - 2.54), 'Value': (x, y + 3.81)}
def R(ref, val, x, y, a, b, rot=0, fp=FP_R, side='right', **kw):
    return sch.part(ref, 'Device:R', val, x, y, rot, {'1': a, '2': b}, fp=fp, field_pos=_fpos(x, y, rot, side), **kw)
def C(ref, val, x, y, a='VBAT', b='GND', rot=0, fp=FP_C, pol=False, side='right', **kw):
    return sch.part(ref, 'Device:C_Polarized' if pol else 'Device:C', val, x, y, rot, {'1': a, '2': b},
                    fp=fp, field_pos=_fpos(x, y, rot, side), **kw)
def block(title, a, b):
    sch.rect(a, b); sch.text(title, (a[0] + 1.27, a[1] + 1.27), size=1.8, bold=True)
def note(s, p, size=1.27):
    sch.text(s, p, size=size)

# ================================================================ A. BATTERY, SHUNT, CURRENT SENSE
block('A - Battery entry, current shunt, current sense', (10.16, 10.16), (142.24, 86.36))
sch.part('J2', 'Connector_Generic:Conn_01x02', 'BATT 1S', 20.32, 35.56, 0,
         {'1': 'VBAT_RAW', '2': 'GND'}, fp=LIB + ':BattPads_1x02_SMD', mirror=True,
         fields={'Note': 'Battery solder pads: a JST PH 2.0 pigtail (plug-in batteries, 2 A rated) or a soldered battery lead (above 2 A). Rear corner, leads exit off the corner tip, as frame C'},
         field_pos={'Reference': (17.78, 30.48), 'Value': (17.78, 41.91), 'just': 'right'})
note('Battery connector: JST PH 2.0 pigtail (30-40 mm, 24 AWG, 2 A rated)\nsoldered to J2 (no room for a board-mounted PH 2.0:\n9 mm deep against 7.3 mm between the 20 x 20 holes and the edges)', (15.24, 50.8))
R('R9', '2m', 45.72, 38.1, 'VBAT_RAW', 'VBAT_SH', fp='Resistor_SMD:R_1206_3216Metric',
  fields={'Note': 'Current shunt 2 mOhm 1 W 1206 (battery + -> R9 -> VBAT_SH -> Q5 -> VBAT), Kelvin sense to U1'})
C('C1', '470uF 6.3V polymer', 66.04, 38.1, 'VBAT', 'GND', pol=True, fp='Capacitor_Tantalum_SMD:CP_EIA-7343-31_Kemet-D',
  fields={'Note': 'Low-ESR bulk next to the battery pads (e.g. Panasonic 6TPE470MI)'})
sch.part('U1', LIB + ':TSC213', 'TSC213', 104.14, 40.64, 0,
         {'4': 'VBAT_RAW', '5': 'VBAT_SH', '3': 'VBAT', '2': 'GND', '1': 'GND', '6': ('W', 'CUR_A')},
         fp='Package_TO_SOT_SMD:SOT-363_SC-70-6',
         fields={'Note': 'TSC213ICT, gain 50: CUR = 50 x 2 mOhm x I = 0.1 V/A (unidirectional, REF = GND). VCC from VBAT (after the charge switch, as rev A; the inputs work up to 26 V whatever VCC is). The charge current does not flow through R9 (CUR reads 0)'},
         field_pos={'Reference': (96.52, 31.75), 'Value': (109.22, 50.8), 'just': 'left'})
R('R10', '1k', 120.65, 40.64, ('W', 'CUR_A'), 'CUR', rot=90, fields={'Note': 'RC 1k/100nF to the FC ADC, fc 1.6 kHz'})
C('C6', '100nF', 128.27, 44.45, 'CUR', 'GND')
p6 = sch.pin_end('U1', '6')[0]; p10 = sch.pin_end('R10', '1')[0]
sch.wire(p6, (p10[0] - 1.27, p6[1]), (p10[0] - 1.27, p10[1]), p10) if abs(p6[1] - p10[1]) > 0.01 else sch.wire(p6, p10)
C('C7', '100nF', 91.44, 27.94, 'VBAT', 'GND', side='left', fields={'Note': 'U1 VCC'})
sch.pwr_flag('GND', (30.48, 60.96))
sch.pwr_flag('VBAT', (55.88, 60.96))
def flag_label(net, p, n):
    sch._instance('power:PWR_FLAG', '#FLG%02d' % n, 'PWR_FLAG', p[0], p[1], 0)
    sch.label(net, p, 0)
flag_label('VBAT_RAW', (30.48, 25.4), 10)
flag_label('VBAT_SH', (66.04, 25.4), 11)
note('Battery current: CUR = 0.1 V/A on J1 pin 3 (FC ADC PA4); discharge only.\n'
     'Motor peak about 8 A -> 0.8 V; full scale 31 A at 3.1 V.\n'
     'Shunt loss at 6 A: 72 mW. U1 senses R9 through two Kelvin tracks.', (15.24, 72.39))

# ================================================================ B. FC LINK
block('B - Link to the flight controller (standard 4-in-1 ESC connector)', (146.05, 10.16), (287.02, 86.36))
sch.part('J1', 'Connector_Generic:Conn_01x08', 'ESC link', 172.72, 38.1, 0,
         {'1': 'GND', '2': 'VBAT', '3': 'CUR', '4': None, '5': 'PWM_M1', '6': 'PWM_M2', '7': 'PWM_M3', '8': 'PWM_M4'},
         fp='Connector_JST:JST_SH_SM08B-SRSS-TB_1x08-1MP_P1.00mm_Horizontal',
         fields={'Note': 'JST SH 8-pin side entry, top side, rear-right edge: 1 GND, 2 VBAT, 3 CUR, 4 TLM (n.c.), 5-8 M1-M4. 1:1 cable to the FC'},
         field_pos={'Reference': (168.91, 25.4), 'Value': (168.91, 52.07), 'just': 'left'})
note('Common 4-in-1 ESC pinout. A brushless 20 x 20 1S 4-in-1 ESC plugs into the\n'
     'same FC cable: check its pinout first (some vendors swap VBAT/GND or CUR/TLM).\n'
     'TLM (pin 4) is not used by this brushed board.\n'
     'VBAT on pin 2 also supplies the whole FC (up to 0.5 A at 4.1 V).\n'
     'VBAT is off while the charge port is plugged in (Q5): FC and motors off.', (190.5, 30.48))

# ================================================================ C. MOTOR STAGES
block('C - Motor stages: 4 x low-side N-MOSFET, 8520 coreless on 1S', (10.16, 90.17), (287.02, 162.56))
INFO = [('M1', 'rear-right edge midpoint, CW'), ('M2', 'front-right edge midpoint, CCW'),
        ('M3', 'rear-left edge midpoint, CCW'), ('M4', 'front-left edge midpoint, CW')]
for i, (mref, where) in enumerate(INFO):
    n = i + 1
    ox, oy = 43.18 + 66.04 * i, 137.16
    net_n = 'M%d_N' % n
    sch.part('Q%d' % n, LIB + ':AON7524', 'AON7524', ox, oy, 0,
             {'4': ('W', 'GATE%d' % n), '1': 'GND', '5': ('W', net_n)},
             fields={'Note': 'DFN 3x3 EP: check the land pattern against the AOS DFN3x3A_8L_EP1_P package'},
             field_pos={'Reference': (ox + 5.08, oy - 1.27), 'Value': (ox + 5.08, oy + 1.27), 'just': 'left'})
    for k in ('2', '3'):
        sch.expected[('Q%d' % n, k)] = 'GND'
    d = sch.pin_end('Q%d' % n, '5')[0]
    gpin = sch.pin_end('Q%d' % n, '4')[0]
    sch.part(mref, 'Motor:Motor_DC', 'coreless 8520', d[0], oy - 30.48, 0,
             {'1': 'VBAT', '2': ('W', net_n)}, fp=LIB + ':MotorPads_1x02_SMD',
             fields={'Note': 'Motor pads, %s. Red/blue = +, black/white = - (check the direction)' % where},
             field_pos={'Reference': (d[0] - 5.08, oy - 31.75), 'Value': (d[0] - 5.08, oy - 29.21), 'just': 'right'})
    mneg = sch.pin_end(mref, '2')[0]
    sch.wire(d, mneg)
    jd = (d[0], d[1] - 2.54)
    dref = 'D%d' % n
    sch.part(dref, 'Device:D_Schottky', 'STPS3L45AF', d[0] + 10.16, jd[1] - 3.81, 270,
             {'1': 'VBAT', '2': ('W', net_n)}, fp=LIB + ':D_SMAflat',
             fields={'Note': 'Freewheel Schottky 45 V 3 A, SMAflat'},
             field_pos={'Reference': (d[0] + 12.7, jd[1] - 5.08), 'Value': (d[0] + 12.7, jd[1] - 2.54), 'just': 'left'})
    da = sch.pin_end(dref, '2')[0]
    sch.wire(da, (da[0], jd[1]), jd)
    sch.junction(jd)
    rg, rpd = 'R%d' % n, 'R%d' % (4 + n)
    sch.part(rg, 'Device:R', '22R', gpin[0] - 10.16, oy, 90, {'1': 'PWM_M%d' % n, '2': ('W', 'GATE%d' % n)},
             fp=FP_R, field_pos={'Reference': (gpin[0] - 10.16, oy - 2.54), 'Value': (gpin[0] - 10.16, oy + 2.54)})
    sch.wire(sch.pin_end(rg, '2')[0], gpin)
    jg = (gpin[0] - 2.54, oy)
    sch.part(rpd, 'Device:R', '100k', jg[0], oy + 6.35, 0, {'1': ('W', 'GATE%d' % n), '2': 'GND'},
             fp=FP_R, field_pos={'Reference': (jg[0] - 1.27, oy + 5.08), 'Value': (jg[0] - 1.27, oy + 7.62), 'just': 'right'})
    sch.wire(jg, sch.pin_end(rpd, '1')[0])
    sch.junction(jg)
    C('C%d' % (1 + n), '10uF 10V', d[0] + 22.86, oy - 22.86, 'VBAT', 'GND', fp=FP_C0603,
      fields={'Note': 'Channel %d local cap, VBAT to GND next to the MOSFET (hot loop)' % n})
    sch.label(net_n, (d[0], oy - 8.89), 0)
note('Rg 22 ohm limits the FC output peak current (Ciss 2250 pF). Rpd 100k keeps the MOSFETs off while the FC boots\n'
     'or when the cable is unplugged. Brushed PWM 32 kHz from the FC (TIM2 CH1-CH4).', (12.7, 154.94))
for k in range(4):
    x = 213.36 + 12.7 * k
    sch.part('H%d' % (k + 1), 'Mechanical:MountingHole', 'M2', x, 76.2, 0, {},
             fp='MountingHole:MountingHole_2.2mm_M2',
             fields={'Note': 'M2 hole, 20 x 20 pattern, hard mount to the frame bosses; FC grommet stack above'},
             field_pos={'Reference': (x, 69.85), 'Value': (x, 72.39)}, in_bom=False)

# ================================================================ D. CHARGE PORT, CHARGER, CHARGE SWITCH (rev B)
block('D - USB-C charge port (power only), 1S charger STC4054, charge switch Q5', (10.16, 166.37), (287.02, 254.0))
DY = 200.66
sch.part('J4', 'Connector:USB_C_Receptacle_USB2.0_16P', 'USB-C (HRO TYPE-C-31-M-12)', 30.48, DY, 0,
         {'A4': 'VBUS', 'A5': 'CC1', 'B5': 'CC2', 'A6': None, 'B6': None, 'A7': None, 'B7': None,
          'A8': None, 'B8': None, 'A1': 'GND', 'S1': 'GND'},
         fp='Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12',
         fields={'Note': 'Charge port, power only (D+/D- not connected). Top side, front edge, mouth toward the front: nothing of the FC above protrudes there'},
         field_pos={'Reference': (20.32, 172.72), 'Value': (20.32, 175.26), 'just': 'left'})
R('R12', '5.1k', 60.96, DY + 2.54, 'CC1', 'GND', fields={'Note': 'CC1 Rd: USB-C sink, 5 V up to 1.5 A from Type-C chargers'})
R('R13', '5.1k', 71.12, DY + 2.54, 'CC2', 'GND')
C('C8', '1uF', 78.74, DY + 2.54, 'VBUS', 'GND', fields={'Note': 'Charger input, at the USB-C VBUS pins'})
sch.part('U2', LIB + ':STC4054', 'STC4054GR', 116.84, DY, 0,
         {'4': 'VBUS', '2': 'GND', '3': 'VBAT_RAW', '1': ('W', 'CHG_LED'), '5': ('W', 'CHG_PROG')},
         fields={'Note': 'STC4054GR: 4.2 V Li-ion charger, I_BAT = 1000 V / R_PROG = 455 mA (about 1C on a 450 mAh 1S pack), thermal regulation. BAT straight to the battery terminal (before the shunt)'},
         field_pos={'Reference': (106.68, 191.77), 'Value': (119.38, 213.36), 'just': 'left'})
prog = sch.pin_end('U2', '5')[0]
sch.wire(prog, (101.6, prog[1]))
R('R14', '2.2k 1%', 101.6, prog[1] + 3.81, ('W', 'CHG_PROG'), 'GND', fields={'Note': 'R_PROG: 1000 V / 2.2 k = 455 mA'})
chrg = sch.pin_end('U2', '1')[0]
sch.part('D6', 'Device:LED', 'green', chrg[0] - 3.81, chrg[1], 180, {'1': ('W', 'CHG_LED'), '2': ('W', 'CHG_LED_A')},
         fp='LED_SMD:LED_0402_1005Metric', fields={'Note': 'Charge LED, on = charging (top side, next to the charge port)'},
         field_pos={'Reference': (chrg[0] - 3.81, chrg[1] - 5.08), 'Value': (chrg[0] - 3.81, chrg[1] - 2.54)})
an = sch.pin_end('D6', '2')[0]
sch.wire(an, (93.98, an[1]))
R('R15', '1k', 93.98, an[1] - 3.81, 'VBUS', ('W', 'CHG_LED_A'), side='left')
R('R16', '1R', 144.78, DY + 2.54, 'VBAT_RAW', ('W', 'CHG_RC'), fields={'Note': 'R16 + C9: STC4054 stability with no battery (DS sec. 6.13)'})
C('C9', '4.7uF 10V', 144.78, DY + 10.16, ('W', 'CHG_RC'), 'GND', fp=FP_C0603)
# charge switch: Q5 P-MOSFET between the shunt and the board supply. Gate pulled to GND (on) by R11; with the charge
# port plugged in, D5 lifts the gate to VBUS - 0.3 V > VBAT: Q5 off, motors and FC unpowered, the charger sees the
# battery alone (clean CC/CV termination, no load current).
sch.part('Q5', LIB + ':AON7423', 'AON7423', 205.74, DY - 10.16, 90,
         {'1': 'VBAT_SH', '5': 'VBAT', '4': ('W', 'Q5_G')},
         fields={'Note': 'AON7423 P-MOSFET 20 V, 4.9 mOhm @ -2.5 V, Vgs +-8 V, DFN 3x3 (bottom side, next to R9). Source on the battery side: the body diode never feeds VBAT -> battery'},
         field_pos={'Reference': (210.82, DY - 21.59), 'Value': (210.82, DY - 19.05), 'just': 'left'})
for k in ('2', '3'):
    sch.expected[('Q5', k)] = 'VBAT_SH'
g = sch.pin_end('Q5', '4')[0]
sch.wire(g, (g[0], DY + 2.54))
sch.junction((g[0], DY + 2.54))
R('R11', '100k', g[0], DY + 6.35, ('W', 'Q5_G'), 'GND', fields={'Note': 'Q5 gate pull-down: on without USB'})
sch.part('D5', 'Device:D_Schottky', 'RB521S30', g[0] - 10.16, DY + 2.54, 180, {'2': 'VBUS', '1': ('W', 'Q5_G')},
         fp='Diode_SMD:D_SOD-523', fields={'Note': 'VBUS -> Q5 gate: gate at VBUS - 0.3 V turns Q5 off while charging'},
         field_pos={'Reference': (g[0] - 10.16, DY - 1.27), 'Value': (g[0] - 10.16, DY + 6.35)})
sch.wire(sch.pin_end('D5', '1')[0], (g[0], DY + 2.54))
flag_label('VBUS', (40.64, 236.22), 12)
note('Charging (power board USB-C): plug a 5 V USB charger. The LED is on while charging.\n'
     'Q5 cuts VBAT (FC + motors) while USB is plugged in: no motor can spin during charging and\n'
     'the charger terminates on the battery current alone. The FC can stay on its own USB for data.\n'
     'Battery: JST PH 2.0 pigtail on the pads J2 (rated 2 A), or a soldered lead (any current up to the shunt rating).', (60.96, 228.6))

sch.write(OUT)
json.dump({'%s.%s' % k: v for k, v in sch.expected.items()}, open(OUT + '.expected.json', 'w'), indent=0)
json.dump(sorted('%s.%s' % k for k in sch.nc), open(OUT + '.nc.json', 'w'))
parts = {}
for ref, P in sch.parts.items():
    parts[ref] = dict(lib_id=P['lib_id'], value=P['value'], fp=P['fp'], fields=P['fields'], dnp=P['dnp'])
json.dump(parts, open(OUT + '.parts.json', 'w'), indent=1)
print('ok', len(sch.parts), 'parts')
