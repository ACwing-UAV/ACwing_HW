# DimaQuadFlow rev A: optical-flow + ToF board for the DimaQuadFC expansion bus (Qwiic), KiCad 7 schematic generator.
import sys, json
sys.path.insert(0, '/home/claude/genE')
import kisch
from kisch import Schematic, POWER_LIB
from flow_syms import pmw3901

OUT = sys.argv[1]
PROJECT = 'DimaQuadFlow_A'
LIB = 'DimaQuadFlow'
POWER_LIB.update({'GND': 'power:GND', '+3V3': 'power:+3V3'})
sch = Schematic(PROJECT, 'A4', title=dict(
    title='DimaQuadFlow rev A - flow + ToF expansion',
    date='2026-10-18', rev='A', company='UAV Control - A. Cirillo',
    comments=['Mounted under the battery tray, sensor side facing the ground (handoff doc for the frame)',
              'Qwiic (JST SH 4P) in/out: daisy-chain with the GPS board; I2C 0x29 (ToF) and 0x3B (flow bridge)',
              'PixArt PMW3901MB (flow, SPI) behind an ST STM32C011 I2C bridge; ST VL53L1X ToF on the bus',
              'Generated automatically: run ERC before release']))
sch.add_lib(LIB + ':PMW3901MB', pmw3901())
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
def C(ref, val, x, y, a='+3V3', b='GND', rot=0, fp=FP_C, side='right', **kw):
    return sch.part(ref, 'Device:C', val, x, y, rot, {'1': a, '2': b}, fp=fp, field_pos=_fpos(x, y, rot, side), **kw)
def block(title, a, b):
    sch.rect(a, b); sch.text(title, (a[0] + 1.27, a[1] + 1.27), size=1.8, bold=True)
def note(s, p, size=1.27): sch.text(s, p, size=size)

# ---------------------------------------------------------------- A. bus + power
block('A - Qwiic in/out, 2.0 V for the flow sensor', (10.16, 10.16), (142.24, 78.74))
for k, ref in enumerate(('J1', 'J2')):
    x = 25.4 + 25.4 * k
    sch.part(ref, 'Connector_Generic:Conn_01x04', 'Qwiic', x, 33.02, 0,
             {'1': 'GND', '2': '+3V3', '3': 'I2C_SDA', '4': 'I2C_SCL'},
             fp='Connector_JST:JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal',
             fields={'Note': 'Qwiic / STEMMA QT: 1 GND, 2 3.3 V, 3 SDA, 4 SCL. %s' % ('In (from the FC or the GPS board)' if k == 0 else 'Out (daisy chain)')},
             field_pos={'Reference': (x + 3.81, 27.94), 'Value': (x + 3.81, 30.48), 'just': 'left'})
note('No I2C pull-ups here: they are on the FC (expansion bus).', (15.24, 58.42))
sch.part('U2', 'Regulator_Linear:LDK130-ADJ_DFN6', 'LDK130PU-R', 96.52, 35.56, 0,
         {'6': '+3V3', '4': '+3V3', '2': 'GND', '1': ('W', 'V2V0'), '3': ('W', 'VADJ'), '5': None},
         fp='Package_DFN_QFN:DFN-6_1.3x1.2mm_P0.4mm',
         fields={'Note': 'Adjustable LDO (DFN-6 1.2 x 1.3, LCSC C157446), VOUT = 0.8 V x (1 + R5/R6) = 2.0 V (PMW3901 VDD 1.8-2.1 V)'},
         field_pos={'Reference': (91.44, 27.94), 'Value': (99.06, 27.94), 'just': 'left'})
vo = sch.pin_end('U2', '1')[0]; va = sch.pin_end('U2', '3')[0]
sch.wire(vo, (121.92, vo[1])); sch.label('V2V0', (121.92, vo[1]), 0)
R('R5', '15k 1%', 111.76, vo[1] + 3.81, ('W', 'V2V0'), ('W', 'VADJ'))
R('R6', '10k 1%', 111.76, vo[1] + 11.43, ('W', 'VADJ'), 'GND')
sch.junction((111.76, vo[1]))
sch.wire(va, (106.68, va[1]), (106.68, vo[1] + 7.62), (111.76, vo[1] + 7.62)); sch.junction((111.76, vo[1] + 7.62))
C('C8', '1uF', 78.74, 39.37, '+3V3', 'GND', side='left', fields={'Note': 'U2 input'})
C('C9', '1uF', 132.08, 39.37, 'V2V0', 'GND', fields={'Note': 'U2 output'})
sch.pwr_flag('GND', (134.62, 63.5))
def flag(net, p, n):
    sch._instance('power:PWR_FLAG', '#FLG%02d' % n, 'PWR_FLAG', p[0], p[1], 0); sch.label(net, p, 0)
flag('+3V3', (60.96, 63.5), 10)
note('+3V3 from the Qwiic bus (FC VEXP LDO).\nTotal draw about 35 mA (flow 9 mA, ToF up to 20 mA, MCU 3 mA).', (60.96, 68.58))

# ---------------------------------------------------------------- B. flow sensor
block('B - Optical flow PixArt PMW3901MB (SPI 2 MHz)', (146.05, 10.16), (287.02, 78.74))
sch.part('U1', LIB + ':PMW3901MB', 'PMW3901MB-TXQT', 215.9, 50.8, 0,
         {'2': 'PMW_VDD', '3': '+3V3', '4': 'PMW_VREG', '7': 'PMW_NRESET',
          '19': 'PMW_NCS', '17': 'SPI_SCK', '16': 'SPI_MOSI', '18': 'SPI_MISO', '15': 'PMW_MOTION',
          '1': 'GND', '21': 'GND', '29': 'GND'},
         fields={'Note': 'Sensor side (faces the ground). Lens LN03 on the package: keep the 42 deg field of view clear'},
         field_pos={'Reference': (205.74, 36.83), 'Value': (220.98, 36.83), 'just': 'left'})
R('R1', '3R', 157.48, 22.86, 'V2V0', 'PMW_VDD', fields={'Note': 'Datasheet reference RC filter on VDD'})
C('C1', '22uF', 167.64, 22.86, 'PMW_VDD', 'GND', fp=FP_C0603)
C('C2', '22uF', 177.8, 22.86, 'PMW_VDD', 'GND', fp=FP_C0603)
C('C3', '100nF', 187.96, 22.86, 'PMW_VDD', 'GND')
C('C4', '10uF', 157.48, 66.04, '+3V3', 'GND', fp=FP_C0603, fields={'Note': 'VDDIO'})
C('C5', '100nF', 167.64, 66.04, '+3V3', 'GND', fields={'Note': 'VDDIO'})
C('C6', '4.7uF', 177.8, 66.04, 'PMW_VREG', 'GND', fp=FP_C0603, fields={'Note': 'VREG'})
C('C7', '100nF', 187.96, 66.04, 'PMW_VREG', 'GND', fields={'Note': 'VREG'})
R('R4', '10k', 256.54, 25.4, '+3V3', 'PMW_NRESET', fields={'Note': 'NRESET pull-up'})
R('R2', '10k', 269.24, 25.4, '+3V3', 'PMW_NCS', fields={'Note': 'NCS pull-up: deselected at boot'})
R('R3', '10k', 281.94, 25.4, '+3V3', 'PMW_MOTION', fields={'Note': 'MOTION pull-up'})
note('Datasheet reference schematic (Fig. 8): VDD 3 ohm + 2 x 22 uF + 100 nF,\nVDDIO 10 uF + 100 nF, VREG 4.7 uF + 100 nF, all next to the pins.\nWorking range 80 mm to infinity, >= 110 lux, 7.4 rad/s max.', (203.2, 63.5))

# ---------------------------------------------------------------- C. ToF + bridge MCU
block('C - ToF ST VL53L1X (bus 0x29) and bridge MCU ST STM32C011 (bus 0x3B)', (10.16, 82.55), (176.53, 190.5))
block('D - Status LED, SWD pads, mounting', (180.34, 82.55), (287.02, 158.75))
sch.part('U3', 'Sensor_Distance:VL53L1CXV0FY1', 'VL53L1CXV0FY/1', 45.72, 132.08, 0,
         {'1': '+3V3', '11': '+3V3', '2': 'GND', '3': 'GND', '4': 'GND', '6': 'GND', '12': 'GND',
          '5': 'TOF_XSHUT', '7': 'TOF_INT', '8': None, '9': 'I2C_SDA', '10': 'I2C_SCL'},
         fields={'Note': 'Sensor side, next to the flow sensor. 27 deg field of view. Cover: ST AN cover-glass rules, or no cover'},
         field_pos={'Reference': (53.34, 116.84), 'Value': (53.34, 119.38), 'just': 'left'})
C('C10', '100nF', 22.86, 111.76, '+3V3', 'GND', side='left', fields={'Note': 'ToF AVDD'})
C('C11', '4.7uF', 30.48, 111.76, '+3V3', 'GND', fp=FP_C0603, fields={'Note': 'ToF AVDDVCSEL'})
R('R9', '10k', 78.74, 116.84, '+3V3', 'TOF_XSHUT', fields={'Note': 'XSHUT pull-up (ToF on unless the bridge resets it)'})
R('R10', '10k', 88.9, 116.84, '+3V3', 'TOF_INT', fields={'Note': 'GPIO1 open-drain pull-up'})
mcu = {'2': '+3V3', '3': 'GND', '4': 'MCU_NRST',
       '9': 'PMW_NCS', '10': 'SPI_SCK', '11': 'SPI_MISO', '12': 'SPI_MOSI', '8': 'PMW_MOTION', '7': 'PMW_NRESET',
       '5': 'TOF_XSHUT', '6': 'TOF_INT', '18': 'I2C_SCL', '19': 'I2C_SDA', '16': 'SWDIO', '17': 'SWCLK',
       '13': 'LED_K', '1': None, '14': None, '15': None, '20': None}
sch.part('U4', 'MCU_ST_STM32C0:STM32C011F4Ux', 'STM32C011F4U6', 132.08, 139.7, 0, mcu,
         fp='Package_DFN_QFN:ST_UFQFPN-20_3x3mm_P0.5mm',
         fields={'Note': 'Flow bridge: SPI1 PA4-PA7 to the PMW3901, I2C1 PB6/PB7 slave 0x3B on the Qwiic bus. Firmware: read motion at 100 Hz, publish dX/dY/SQUAL/shutter'},
         field_pos={'Reference': (147.32, 116.84), 'Value': (147.32, 119.38), 'just': 'left'})
C('C12', '100nF', 104.14, 116.84, '+3V3', 'GND', side='left', fields={'Note': 'MCU VDD'})
C('C13', '4.7uF', 111.76, 116.84, '+3V3', 'GND', fp=FP_C0603, fields={'Note': 'MCU VDD bulk'})
C('C14', '100nF', 104.14, 165.1, 'MCU_NRST', 'GND', side='left', fields={'Note': 'NRST'})
R('R11', '1k', 195.58, 95.25, '+3V3', ('W', 'LED_A'), side='left')
sch.part('D1', 'Device:LED', 'green', 195.58, 102.87, 90, {'2': ('W', 'LED_A'), '1': 'LED_K'},
         fp='LED_SMD:LED_0402_1005Metric', fields={'Note': 'Status LED (PA8 low = on)'},
         field_pos={'Reference': (198.12, 101.6), 'Value': (198.12, 104.14), 'just': 'left'})
for k, (tp, net, nt) in enumerate([('TP1', 'SWDIO', 'SWDIO (PA13)'), ('TP2', 'SWCLK', 'SWCLK (PA14)'), ('TP3', 'MCU_NRST', 'NRST'),
                                   ('TP4', '+3V3', '3.3 V'), ('TP5', 'GND', 'GND')]):
    x = 213.36 + 12.7 * k
    sch.part(tp, 'Connector:TestPoint', net, x, 104.14, 0, {'1': net}, fp='TestPoint:TestPoint_Pad_D1.0mm',
             fields={'Note': nt + ' - SWD programming pad'}, stub=2.54,
             field_pos={'Reference': (x + 1.27, 97.79), 'Value': (x + 1.27, 95.25), 'just': 'left'})
for k in range(2):
    x = 220.98 + 12.7 * k
    sch.part('H%d' % (k + 1), 'Mechanical:MountingHole', 'M2', x, 139.7, 0, {}, fp='MountingHole:MountingHole_2.2mm_M2',
             fields={'Note': 'M2 mounting hole (frame boss, see handoff)'},
             field_pos={'Reference': (x, 133.35), 'Value': (x, 135.89)}, in_bom=False)
note('Bus map: ToF 0x29 (VL53L1X default), flow bridge 0x3B.\nThe bridge can hold the ToF in reset (XSHUT) to change its address.', (12.7, 175.26))

sch.write(OUT)
json.dump({'%s.%s' % k: v for k, v in sch.expected.items()}, open(OUT + '.expected.json', 'w'), indent=0)
json.dump(sorted('%s.%s' % k for k in sch.nc), open(OUT + '.nc.json', 'w'))
parts = {ref: dict(lib_id=P['lib_id'], value=P['value'], fp=P['fp'], fields=P['fields'], dnp=P['dnp']) for ref, P in sch.parts.items()}
json.dump(parts, open(OUT + '.parts.json', 'w'), indent=1)
print('ok', len(sch.parts), 'parts')
