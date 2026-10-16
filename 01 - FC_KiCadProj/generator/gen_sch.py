# Generates DimaQuadFC.kicad_sch (KiCad 7 format) for the DimaMiniQuad flight controller.
import sys, json
import kisch
from kisch import Schematic, POWER_LIB, vec, g
from custom_syms import all_symbols, LIB

OUT = sys.argv[1] if len(sys.argv) > 1 else 'DimaQuadFC.kicad_sch'
PROJECT = 'DimaQuadFC_C2'

POWER_LIB.update({'GND': 'power:GND', 'VDD': 'power:VDD', 'VBUS': 'power:VBUS',
                  'VBAT': LIB + ':VBAT', 'VBAT_F': LIB + ':VBAT_F', 'VSYS': LIB + ':VSYS'})

sch = Schematic(PROJECT, 'A3', title=dict(
    title='DimaQuadFC rev C2 - 1S flight controller for frame C (STM32WB55CGU6)',
    date='2026-10-15', rev='C2',
    company='UAV Control - A. Cirillo',
    comments=['Outline and keep-outs: DimaQuadFC_C_Edge_Cuts.dxf, DimaQuadFC_C_Keepouts.dxf (frame C)',
              'Placement: DimaQuadFC_C_Placement.csv (mechanical handoff)',
              'Motor stage: BoM_motori.xlsx',
              'Generated automatically: run ERC before release']))

for name, node in all_symbols().items():
    sch.add_lib(LIB + ':' + name, node)

# ---------------------------------------------------------------- helpers
FP_R = 'Resistor_SMD:R_0402_1005Metric'
FP_C = 'Capacitor_SMD:C_0402_1005Metric'
FP_C0603 = 'Capacitor_SMD:C_0603_1608Metric'
FP_C1206 = 'Capacitor_SMD:C_1206_3216Metric'
FP_R0603 = 'Resistor_SMD:R_0603_1608Metric'
FP_LED = 'LED_SMD:LED_0402_1005Metric'

def R(ref, val, x, y, a, b, rot=0, fp=FP_R, side='right', **kw):
    """Vertical (rot 0: pin1 top) or horizontal (rot 90: pin1 left) resistor."""
    fpos = _fpos(x, y, rot, side)
    return sch.part(ref, 'Device:R', val, x, y, rot, {'1': a, '2': b}, fp=fp, field_pos=fpos, **kw)

def C(ref, val, x, y, a='VDD', b='GND', rot=0, fp=FP_C, pol=False, side='right', **kw):
    fpos = _fpos(x, y, rot, side)
    return sch.part(ref, 'Device:C_Polarized' if pol else 'Device:C', val, x, y, rot, {'1': a, '2': b},
                    fp=fp, field_pos=fpos, **kw)

def _fpos(x, y, rot, side='right'):
    if rot in (0, 180):
        if side == 'left':
            return {'Reference': (x - 2.54, y - 1.27), 'Value': (x - 2.54, y + 1.27), 'just': 'right'}
        return {'Reference': (x + 2.54, y - 1.27), 'Value': (x + 2.54, y + 1.27), 'just': 'left'}
    return {'Reference': (x, y - 2.54), 'Value': (x, y + 3.81)}

def block(title, a, b):
    sch.rect(a, b)
    sch.text(title, (a[0] + 1.27, a[1] + 1.27), size=2.0, bold=True)

def note(s, p, size=1.27):
    sch.text(s, p, size=size)

# ================================================================ A. POWER
block('A - 1S battery, RC filter, USB/battery power path, LDO', (12, 12), (178, 118))
Y0 = 35.56

def node(net, p, j=True):
    sch.power(net, p, 90 if net != 'GND' else 270)
    if j:
        sch.junction(p)

def divider(ra, rb, va, vb, x, y, top, mid, bot, cref=None, cval='100nF', note_=None, label_dx=7.62):
    """Vertical divider: ra top (pin1 at y), rb directly below; mid node wired to the right with a label."""
    R(ra, va, x, y + 3.81, top, ('W', mid))
    R(rb, vb, x, y + 11.43, ('W', mid), bot)
    m = (x, y + 7.62)
    sch.junction(m)
    sch.wire(m, (x + label_dx, m[1]))
    sch.label(mid, (x + label_dx, m[1]), 0)
    if cref:
        cx = x + 10.16
        C(cref, cval, cx, m[1] + 3.81, ('W', mid), 'GND')
        sch.junction((cx, m[1]))

# battery pads (J2, rear edge) -> VBAT
sch.part('J2', 'Connector_Generic:Conn_01x02', 'BATT 1S', 20.32, Y0, 0,
         {'1': ('W', 'VBAT'), '2': ('W', 'GND')}, fp=LIB + ':BattPads_1x02_SMD', mirror=True,
         fields={'Note': 'Solder pads for the battery lead (BT2.0 / PH2.0 on the pigtail). Rear corner, leads exit off the corner tip'},
         field_pos={'Reference': (19.05, 31.75), 'Value': (19.05, 40.64)})
j1p = sch.pin_end('J2', '1')[0]; j2p = sch.pin_end('J2', '2')[0]
sch.wire(j1p, (35.56, Y0))
node('VBAT', (30.48, Y0))
sch.wire(j2p, (27.94, j2p[1]))
sch.power('GND', (27.94, j2p[1]), 270)

# RC filter (BoM): 1 ohm + 100 uF
R('R1', '1R', 39.37, Y0, ('W', 'VBAT'), ('W', 'VBAT_F'), rot=90, fp=FP_R0603,
  fields={'Note': 'RC filter (BoM): 1 ohm + 100 uF, isolates MCU/sensors from motor sags'})
sch.wire((43.18, Y0), (55.88, Y0))
node('VBAT_F', (46.99, Y0))
C('C6', '100uF 6.3V', 50.8, Y0 + 3.81, ('W', 'VBAT_F'), 'GND', fp=FP_C1206)
sch.junction((50.8, Y0))

# power path: battery through P-MOSFET (body diode toward VSYS), USB through Schottky
sch.part('Q5', 'Transistor_FET:AO3401A', 'AO3401A', 60.96, Y0 + 2.54, 90,
         {'3': ('W', 'VBAT_F'), '2': ('W', 'VSYS'), '1': ('W', 'VBUS')},
         fields={'Note': 'Load sharing: ON on battery only, OFF with USB (gate = VBUS)'},
         field_pos={'Reference': (58.42, Y0 - 6.35), 'Value': (58.42, Y0 - 3.81)})
gq = sch.pin_end('Q5', '1')[0]                      # (60.96, Y0+7.62)
yb = gq[1] + 5.08
sch.wire(gq, (gq[0], yb))
sch.junction((gq[0], yb))
R('R2', '100k', gq[0], yb + 3.81, ('W', 'VBUS'), 'GND', fields={'Note': 'Gate pull-down: Q5 on when VBUS is absent'})
sch.wire((66.04, Y0), (109.22, Y0))
node('VSYS', (71.12, Y0))
sch.part('D9', 'Device:D_Schottky', 'PMEG2010AEH', 76.2, Y0 + 3.81, 270,
         {'1': ('W', 'VSYS'), '2': ('W', 'VBUS')}, fp='Diode_SMD:D_SOD-123F',
         fields={'Note': 'VBUS -> VSYS, 1 A, Vf ~0.35 V'},
         field_pos={'Reference': (78.74, Y0 + 2.54), 'Value': (78.74, Y0 + 5.08), 'just': 'left'})
sch.junction((76.2, Y0))
sch.wire((76.2, Y0 + 7.62), (76.2, yb))
sch.wire((gq[0], yb), (83.82, yb))
sch.junction((76.2, yb))
sch.power('VBUS', (83.82, yb), 0)
C('C7', '4.7uF', 93.98, Y0 + 3.81, ('W', 'VSYS'), 'GND', fp=FP_C0603)
sch.junction((93.98, Y0))

# LDO LD39130S adjustable (DFN6): VOUT = 0.8 V * (1 + R3/R4)
sch.part('U5', LIB + ':LD39130S-ADJ', 'LD39130SPUR', 119.38, Y0 + 2.54, 0,
         {'4': ('W', 'VSYS'), '3': ('W', 'VSYS'), '1': ('W', 'VSYS'), '6': ('W', 'VDD'),
          '5': ('W', 'LDO_ADJ'), '2': 'GND'},
         fp='Package_DFN_QFN:DFN-6_1.3x1.2mm_P0.4mm',
         fields={'Note': 'BoM: LD39130S 3.0 V. The fixed 3.0 V part exists only as a 0.69 mm flip chip (LD39130SJ30R): '
                         'ADJ version in DFN6 used here, set to 3.1 V to keep VDDUSB >= 3.0 V'},
         field_pos={'Reference': (111.76, Y0 - 3.81), 'Value': (124.46, Y0 + 11.43), 'just': 'left'})
en = sch.pin_end('U5', '3')[0]; gm = sch.pin_end('U5', '1')[0]
sch.wire(en, (106.68, en[1])); sch.wire(gm, (106.68, gm[1]), (106.68, Y0))
sch.junction((106.68, Y0)); sch.junction((106.68, en[1]))
out_ = sch.pin_end('U5', '6')[0]; adj = sch.pin_end('U5', '5')[0]
sch.wire(out_, (152.4, Y0))
node('VDD', (134.62, Y0))
R('R3', '287k 1%', 139.7, Y0 + 3.81, ('W', 'VDD'), ('W', 'LDO_ADJ'))
R('R4', '100k 1%', 139.7, Y0 + 11.43, ('W', 'LDO_ADJ'), 'GND')
sch.junction((139.7, Y0))
sch.wire(adj, (132.08, adj[1]), (132.08, Y0 + 7.62), (139.7, Y0 + 7.62))
sch.junction((139.7, Y0 + 7.62))
C('C8', '1uF', 149.86, Y0 + 3.81, ('W', 'VDD'), 'GND')
sch.junction((149.86, Y0))
note('VOUT = 0.8 V x (1 + R3/R4) = 3.10 V\nGM high: green mode off\nEN = VSYS: always on', (109.22, 54.61))

sch.pwr_flag('VBUS', (154.94, 58.42)); sch.pwr_flag('VSYS', (165.1, 58.42)); sch.pwr_flag('GND', (172.72, 50.8))
note('J2: solder pads\n(a JST-SH connector is rated\n1 A, the motors draw 6-8 A)', (15.24, 48.26))

# Charger STC4054 (USB -> battery)
sch.text('USB charger (STC4054, 4.2 V)', (15.24, 66.04), size=1.5, bold=True)
sch.part('U6', LIB + ':STC4054', 'STC4054GR', 58.42, 86.36, 0,
         {'4': ('W', 'VBUS'), '2': 'GND', '3': ('W', 'VBAT'), '1': ('W', 'CHG_LED'), '5': ('W', 'CHG_PROG')},
         fields={'Note': 'I_BAT = 1000 V / R_PROG'},
         field_pos={'Reference': (48.26, 80.01), 'Value': (60.96, 99.06), 'just': 'left'})
vcc = sch.pin_end('U6', '4')[0]
sch.wire(vcc, (vcc[0], 73.66), (73.66, 73.66))
sch.wire((53.34, 73.66), (vcc[0], 73.66))
sch.junction((vcc[0], 73.66))
sch.power('VBUS', (53.34, 73.66), 90)
C('C10', '1uF 10V', 73.66, 77.47, ('W', 'VBUS'), 'GND')
chrg = sch.pin_end('U6', '1')[0]
sch.part('D10', 'Device:LED', 'green', chrg[0] - 3.81, chrg[1], 180, {'1': ('W', 'CHG_LED'), '2': ('W', 'CHG_LED_A')},
         fp=FP_LED, fields={'Note': 'On = charging'},
         field_pos={'Reference': (chrg[0] - 3.81, chrg[1] - 6.35), 'Value': (chrg[0] - 3.81, chrg[1] - 3.81)})
an = sch.pin_end('D10', '2')[0]
sch.wire(an, (35.56, an[1]))
R('R6', '1k', 35.56, an[1] - 3.81, 'VBUS', ('W', 'CHG_LED_A'), side='left')
prog = sch.pin_end('U6', '5')[0]
sch.wire(prog, (43.18, prog[1]))
R('R5', '3.3k 1%', 43.18, prog[1] + 3.81, ('W', 'CHG_PROG'), 'GND',
  fields={'Note': 'I_BAT ~ 300 mA (0.7C on 400-450 mAh)'})
bat = sch.pin_end('U6', '3')[0]
sch.wire(bat, (83.82, bat[1]))
sch.power('VBAT', (83.82, bat[1]), 90)
R('R7', '1R', 83.82, bat[1] + 3.81, ('W', 'VBAT'), ('W', 'CHG_RC'))
C('C11', '4.7uF 10V', 83.82, bat[1] + 11.43, ('W', 'CHG_RC'), 'GND', fp=FP_C0603)
note('R7 + C11: STC4054 DS\nsec. 6.13 (stability\nwith no battery)', (99.06, 93.98))

# Sense: battery voltage and USB presence
sch.text('Sensing', (124.46, 66.04), size=1.5, bold=True)
divider('R8', 'R9', '470k 1%', '470k 1%', 127.0, 76.2, 'VBAT', 'VBAT_SNS', 'GND', cref='C12', label_dx=15.24)
divider('R10', 'R11', '100k', '100k', 154.94, 76.2, 'VBUS', 'VBUS_DET', 'GND', label_dx=5.08)
note('VBAT_SNS = VBAT/2 (ADC, PC5)\nVBUS_DET = VBUS/2 (PC2):\nmotors inhibited with USB plugged in', (124.46, 101.6))

# ================================================================ B. USB-C
block('B - USB-C (charging + DFU/CDC), ESD protection', (12, 122), (178, 188))
sch.part('J1', 'Connector:USB_C_Receptacle_USB2.0_16P', 'USB-C (HRO TYPE-C-31-M-12)', 30.48, 152.4, 0,
         {'A4': 'VBUS', 'A5': 'USB_CC1', 'B5': 'USB_CC2', 'A6': 'USB_DP', 'B6': 'USB_DP',
          'A7': 'USB_DM', 'B7': 'USB_DM', 'A8': None, 'B8': None, 'A1': 'GND', 'S1': 'GND'},
         fp='Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12',
         fields={'Note': 'Right-corner chamfer, plug from the frame side'},
         field_pos={'Reference': (20.32, 129.54), 'Value': (20.32, 132.08), 'just': 'left'})
R('R12', '5.1k', 63.5, 154.94, 'USB_CC1', 'GND')
R('R13', '5.1k', 76.2, 154.94, 'USB_CC2', 'GND')
sch.part('U7', 'Power_Protection:USBLC6-2SC6', 'USBLC6-2SC6', 101.6, 152.4, 0,
         {'1': 'USB_DP', '6': 'USB_DP', '3': 'USB_DM', '4': 'USB_DM', '5': 'VBUS', '2': 'GND'},
         field_pos={'Reference': (106.68, 144.78), 'Value': (106.68, 162.56), 'just': 'left'})
note('CC1/CC2 5.1k: USB 2.0 sink\n(5 V, 500 mA / 1.5 A with Type-C chargers)\n'
     'D+/D- straight to PA12/PA11,\nUSBLC6 close to the connector\n'
     'Shield tied directly to GND\n(no metal frame)', (119.38, 140.97))

# ================================================================ C. MCU (rev C2: STM32WB55CGU6 QFN48 + RF front end)
block('C - STM32WB55CGU6 (QFN48), RF front end, clocks', (182, 12), (282, 188))
MX, MY = 240.03, 86.36
mcu = {
    '1': ('W', 'VDD'), '8': ('W', 'VDD'), '20': ('W', 'VDD'), '23': ('W', 'VDD'), '34': ('W', 'VDD'),
    '35': ('W', 'VDD'), '40': ('W', 'VDD'), '48': ('W', 'VDD'),
    '22': ('W', 'GND'), '32': ('W', 'GND'), '49': ('W', 'GND'),
    '21': 'RF_IN',                                     # RF1 -> MLPF-WB55 IN (62 ohm line)
    '24': 'HSE_OUT', '25': 'HSE_IN',                   # 32 MHz crystal, internal trimming caps
    '33': 'SMPS_LX', '31': 'VFBSMPS',                  # SMPS network (bypass at reset)
    '4': 'BOOT0', '7': 'NRST',
    # rev C2 pin map: the row facing the top board edge (pins 1-12) has room for three 0.1 mm lanes per side only,
    # so it carries just BOOT0/I2C (east) and NRST/VDDA/PA0 (west); no LSE (RF wake-up and RTC from HSE)
    '9': 'PWM_M1',                                     # PA0  TIM2_CH1
    '43': 'PWM_M2',                                    # PB3  TIM2_CH2
    '15': 'PWM_M3',                                    # PA6  TIM16_CH1
    '36': 'PWM_M4',                                    # PA10 TIM1_CH3
    '13': 'VBUS_DET', '14': 'VBAT_SNS',                # PA4 ADC1_IN9, PA5 ADC1_IN10
    '30': 'LED_FRONT', '29': 'LED_REAR',               # PE4, PB1 (GPIO)
    '5': 'I2C_SCL', '6': 'I2C_SDA',                    # PB8/PB9 I2C1
    '37': 'USB_DM', '38': 'USB_DP',                    # PA11/PA12 USB FS
    '39': 'SWDIO', '41': 'SWCLK',                      # PA13/PA14
    '42': 'IMU_INT1', '44': 'IMU_INT2', '45': 'MAG_DRDY', '28': 'BARO_INT',   # PA15, PB4, PB5, PB0
    '46': 'UART_TX', '47': 'UART_RX',                  # PB6/PB7 USART1
    '2': None, '3': None, '10': None, '11': None, '12': None, '16': None, '17': None, '18': None, '19': None,
}
sch.part('U2', 'MCU_ST_STM32WB:STM32WB55CGUx', 'STM32WB55CGU6', MX, MY, 0, mcu,
         fp='Package_DFN_QFN:QFN-48-1EP_7x7mm_P0.5mm_EP5.6x5.6mm',
         fields={'Note': 'Top-left, next to the chip antenna. Exposed pad to GND with a via array (RF ground)'},
         field_pos={'Reference': (MX + 22.86, MY - 43.18), 'Value': (MX + 22.86, MY + 41.91)})
sch.tie('U2', ['1', '20', '35', '48', '8', '23', '34', '40'], 'VDD')
sch.tie('U2', ['22', '49', '32'], 'GND', sym_at=1)
note('Pin map (IEKF firmware), rev C2:\n'
     'Motor PWM: M1 PA0 TIM2_CH1, M2 PB3 TIM2_CH2,\n'
     '  M3 PA6 TIM16_CH1, M4 PA10 TIM1_CH3\n'
     'LED: front PE4, rear PB1 (GPIO)\n'
     'No LSE: RF wake-up HSE/1024, RTC HSE/32\n'
     'ADC: PA5 VBAT_SNS (IN10), PA4 VBUS_DET (IN9)\n'
     'I2C1 PB8/PB9 -> LSM6DSV16X (Mode 3)\n'
     'IMU_INT1 PA15, IMU_INT2 PB4, MAG_DRDY PB5, BARO_INT PB0\n'
     'USART1 PB6/PB7 -> TP1/TP2 (pogo), USB PA11/PA12\n'
     'SWD PA13/PA14, BOOT0 = PH3 (pull-down 10k)', (186.69, 17.78))

# decoupling (one 100 nF per supply pin, VDDA 1 uF, VDDRF 100 nF + 100 pF), row under the MCU
DEC = [('C23', '100nF', FP_C, 'VDD pin 20'), ('C24', '100nF', FP_C, 'VDD pin 35'), ('C25', '100nF', FP_C, 'VDD pin 48 / VBAT pin 1'),
       ('C14', '100nF', FP_C, 'VDDA pin 8'), ('C22', '1uF', FP_C, 'VDDA pin 8'),
       ('C26', '100nF', FP_C, 'VDDRF pin 23 (DS: 100 nF // 100 pF)'), ('C27', '100pF', FP_C, 'VDDRF pin 23, C0G'),
       ('C28', '100nF', FP_C, 'VDDUSB pin 40'), ('C9', '4.7uF', FP_C0603, 'VDD bulk')]
for k, (ref, val, fp_, nt) in enumerate(DEC):
    C(ref, val, 187.96 + 11.43 * (k % 2), 48.26 + 17.78 * (k // 2), 'VDD', 'GND', fp=fp_, fields={'Note': nt})
C('C15', '100nF', 199.39, 119.38, 'NRST', 'GND', fields={'Note': 'DS13252: 100 nF on NRST'})
R('R14', '10k', 187.96, 137.16, 'BOOT0', 'GND', fields={'Note': 'Boot from flash; TP3 to VDD for the USB DFU bootloader'})

# SMPS network (DS13252 table 6): VLXSMPS - 10 uH - 10 nH - VFBSMPS, 4.7 uF; works in bypass (reset default) and SMPS mode
sch.part('L1', 'Device:L', '2.2uH', 196.85, 172.72, 90, {'1': 'SMPS_LX', '2': ('W', 'SMPS_L2')},
         fp='Inductor_SMD:L_0805_2012Metric', fields={'Note': 'SMPS inductor, 8 MHz mode (Wurth 74479774222, DS13252 table 6): set the SMPS clock to 8 MHz in firmware'},
         field_pos={'Reference': (196.85, 168.91), 'Value': (196.85, 176.53)})
sch.part('L2', 'Device:L', '10nH', 207.01, 172.72, 90, {'1': ('W', 'SMPS_L2'), '2': 'VFBSMPS'},
         fp='Inductor_SMD:L_0402_1005Metric', fields={'Note': 'Series 10 nH for receiver performance (DS13252 table 6)'},
         field_pos={'Reference': (207.01, 168.91), 'Value': (207.01, 176.53)})
sch.wire(sch.pin_end('L1', '2')[0], sch.pin_end('L2', '1')[0])
C('C29', '4.7uF', 219.71, 176.53, 'VFBSMPS', 'GND', fields={'Note': 'SMPS output (DS13252 table 6)'})

# HSE 32 MHz (internal trimming caps, no external load caps)
sch.part('Y1', 'Device:Crystal_GND24', '32MHz', 240.03, 175.26, 0,
         {'1': 'HSE_IN', '3': 'HSE_OUT', '2': 'GND', '4': 'GND'}, fp='Crystal:Crystal_SMD_2016-4Pin_2.0x1.6mm',
         fields={'Note': 'NDK NX2016SA 32 MHz (DS13252 table 5); load caps integrated in the MCU (trimmed in firmware)'},
         field_pos={'Reference': (243.84, 168.91), 'Value': (243.84, 171.45), 'just': 'left'})
# no LSE crystal: BLE RF wake-up clock = HSE/1024, RTC = HSE/32 (pins 2/3 PC14/PC15 not connected)

# RF: RF1 -> MLPF-WB55-01E3 -> pi network (tuning) -> chip antenna
sch.part('U8', LIB + ':MLPF-WB55-01E3', 'MLPF-WB55-01E3', 207.01, 152.4, 0, {'A3': 'RF_IN', 'A1': ('W', 'RF_ANT'), 'B2': 'GND'},
         fields={'Note': 'Directly at RF1: 62 ohm line from the MCU, 50 ohm to the antenna'},
         field_pos={'Reference': (205.74, 147.32), 'Value': (203.2, 160.02), 'just': 'right'})
ra = sch.pin_end('U8', 'A1')[0]
sch.wire(ra, (ra[0] + 10.16, ra[1]))
R('R34', '0R', ra[0] + 13.97, ra[1], ('W', 'RF_ANT'), ('W', 'RF_ANT2'), rot=90, fields={'Note': 'Antenna tuning: series position, 0 ohm until tuned'})
rb = sch.pin_end('R34', '2')[0]
sch.wire(rb, (rb[0] + 10.16, rb[1]))
C('C36', 'DNP', rb[0] + 5.08, rb[1] + 3.81, ('W', 'RF_ANT2'), 'GND', dnp=True, side='left', fields={'Note': 'Antenna tuning: shunt position at the antenna side (C0G or inductor), DNP until tuned'})
sch.junction((rb[0] + 5.08, rb[1]))
sch.part('AE1', 'Device:Antenna_Chip', '2450AT18A0100001E', rb[0] + 12.7, rb[1] - 2.54, 0, {'1': ('W', 'RF_ANT2'), '2': None},
         fp='RF_Antenna:Johanson_2450AT18x100',
         fields={'Note': 'Johanson 2.4 GHz chip antenna at the left board edge; pad 2 NC; copper-free area around it'},
         field_pos={'Reference': (rb[0] + 15.24, rb[1] - 8.89), 'Value': (rb[0] + 15.24, rb[1] - 6.35), 'just': 'left'})
sch.wire(sch.pin_end('AE1', '1')[0], (rb[0] + 10.16, rb[1]))


# ================================================================ D. SENSORS
block('D - Sensors: LSM6DSV16X (I2C1) + sensor hub -> IIS2MDC, LPS22HB', (286, 12), (408, 150))
sch.part('U1', LIB + ':LSM6DSV16X', 'LSM6DSV16X', 335.28, 50.8, 0,
         {'1': 'VDD', '2': 'SHUB_SDA', '3': 'SHUB_SCL', '4': 'IMU_INT1', '5': ('W', 'VDD'), '6': 'GND',
          '8': ('W', 'VDD'), '9': 'IMU_INT2', '10': None, '11': None, '12': 'VDD', '13': 'I2C_SCL', '14': 'I2C_SDA'},
         fields={'Note': 'Board centre (frame CG), axes 45 deg to the airframe. SA0 = 1 -> 0x6B. CS = 1 -> I2C'},
         field_pos={'Reference': (340.36, 33.02), 'Value': (340.36, 68.58), 'just': 'left'})
sch.tie('U1', ['5', '8'], 'VDD', sym_at=0)
C('C16', '100nF', 360.68, 30.48, 'VDD', 'GND', fields={'Note': 'Vdd (pin 8)'})
C('C17', '100nF', 370.84, 30.48, 'VDD', 'GND', fields={'Note': 'Vdd_IO (pin 5)'})
R('R15', '2.2k', 297.18, 25.4, 'VDD', 'I2C_SCL', fields={'Note': 'I2C1 pull-up (up to 1 MHz Fm+)'})
R('R16', '2.2k', 309.88, 25.4, 'VDD', 'I2C_SDA')
R('R17', '4.7k', 381, 25.4, 'VDD', 'SHUB_SCL', fields={'Note': 'Sensor hub bus pull-up (or the internal SHUB_PU_EN)'})
R('R18', '4.7k', 393.7, 25.4, 'VDD', 'SHUB_SDA')

sch.part('U3', 'Sensor_Magnetic:LIS2MDL', 'IIS2MDC', 327.66, 109.22, 0,
         {'1': 'SHUB_SCL', '3': 'VDD', '4': 'SHUB_SDA', '5': 'MAG_C1', '6': 'GND', '7': 'MAG_DRDY',
          '9': ('W', 'VDD'), '10': ('W', 'VDD')},
         fields={'Note': 'IIS2MDCTR (industrial grade of the LIS2MDL: same LGA-12 pinout and registers). Front corner, farthest from battery and motor currents. No motor current under it'},
         field_pos={'Reference': (332.74, 93.98), 'Value': (332.74, 124.46), 'just': 'left'})
sch.tie('U3', ['9', '10'], 'VDD', sym_at=0)
C('C18', '220nF', 350.52, 121.92, 'MAG_C1', 'GND', fields={'Note': 'IIS2MDC C1: 220 nF, ESR < 200 mOhm, close to pins 5-6'})
C('C19', '100nF', 297.18, 88.9, 'VDD', 'GND')
C('C20', '10uF 6.3V', 309.88, 88.9, 'VDD', 'GND', fp=FP_C0603, fields={'Note': 'IIS2MDC DS: 100 nF + 10 uF on Vdd'})

sch.part('U4', 'Sensor_Pressure:LPS22DF', 'LPS22HB', 377.19, 109.22, 0,
         {'1': ('W', 'VDD'), '10': ('W', 'VDD'), '2': 'SHUB_SCL', '4': 'SHUB_SDA', '5': 'VDD', '6': 'VDD',
          '7': 'BARO_INT', '8': ('W', 'GND'), '9': ('W', 'GND')},
         fields={'Note': 'LPS22HBTR on the LPS22DF symbol/footprint (same HLGA-10 pinout, pin 3 to GND). Optional. SA0 = 1 -> 0x5D'},
         stub=7.62,
         field_pos={'Reference': (382.27, 93.98), 'Value': (382.27, 124.46), 'just': 'left'})
sch.tie('U4', ['1', '10'], 'VDD', sym_at=1)
sch.tie('U4', ['8', '9'], 'GND', sym_at=1)
C('C21', '100nF', 355.6, 88.9, 'VDD', 'GND')
note('Topology = IKS4A1 Mode 3: the IEKF firmware\n'
     'reads the IIS2MDC through the LSM6DSV16X\n'
     'sensor hub (samples aligned in the FIFO).\n'
     'Addresses: LSM6DSV16X 0x6B, IIS2MDC 0x1E, LPS22HB 0x5D', (289.56, 134.62))

# ================================================================ E. MOTORS
block('E - Motor stage: 4 x low-side N-MOSFET (BoM_motori.xlsx), 8520 coreless on 1S', (12, 192), (282, 285))
motors = [('M1', 'CW, rear right', 'BLACK prop'), ('M2', 'CCW, front right', 'GREEN prop'),
          ('M3', 'CCW, rear left', 'BLACK prop'), ('M4', 'CW, front left', 'GREEN prop')]
for i, (mref, spin, prop) in enumerate(motors):
    n = i + 1
    ox, oy = 43.18 + 55.88 * i, 254.0
    net_n = 'M%d_N' % n
    # MOSFET
    sch.part('Q%d' % n, LIB + ':AON7524', 'AON7524', ox, oy, 0,
             {'4': ('W', 'GATE%d' % n), '1': 'GND', '5': ('W', net_n)},
             fields={'Note': 'DFN 3x3 EP: check the land pattern against the AOS DFN3x3A_8L_EP1_P package'},
             field_pos={'Reference': (ox + 5.08, oy - 1.27), 'Value': (ox + 5.08, oy + 1.27), 'just': 'left'})
    for k in ('2', '3'):
        sch.expected[('Q%d' % n, k)] = 'GND'
    d = sch.pin_end('Q%d' % n, '5')[0]
    gpin = sch.pin_end('Q%d' % n, '4')[0]
    # motor
    sch.part(mref, 'Motor:Motor_DC', 'coreless 8520', d[0], oy - 22.86, 0,
             {'1': 'VBAT', '2': ('W', net_n)}, fp=LIB + ':MotorPads_1x02_SMD',
             fields={'Note': '%s, %s. Red/blue = +, black/white = - (check the direction)' % (spin, prop)},
             field_pos={'Reference': (d[0] - 5.08, oy - 24.13), 'Value': (d[0] - 5.08, oy - 21.59), 'just': 'right'})
    mneg = sch.pin_end(mref, '2')[0]
    sch.wire(d, mneg)
    jd = (d[0], d[1] - 2.54)
    # freewheel Schottky across the motor
    dref = 'D%d' % (4 + n)
    sch.part(dref, 'Device:D_Schottky', 'STPS3L45AF', d[0] + 10.16, jd[1] - 3.81, 270,
             {'1': 'VBAT', '2': ('W', net_n)}, fp=LIB + ':D_SMAflat',
             fields={'Note': 'Schottky 45 V 3 A, SMAflat'},
             field_pos={'Reference': (d[0] + 12.7, jd[1] - 5.08), 'Value': (d[0] + 12.7, jd[1] - 2.54), 'just': 'left'})
    da = sch.pin_end(dref, '2')[0]
    sch.wire(da, (da[0], jd[1]), jd)
    sch.junction(jd)
    # gate resistor + pull-down
    rg = 'R%d' % (19 + n)
    rpd = 'R%d' % (23 + n)
    sch.part(rg, 'Device:R', '22R', gpin[0] - 10.16, oy, 90, {'1': 'PWM_M%d' % n, '2': ('W', 'GATE%d' % n)},
             fp=FP_R, field_pos={'Reference': (gpin[0] - 10.16, oy - 2.54), 'Value': (gpin[0] - 10.16, oy + 2.54)})
    rgp = sch.pin_end(rg, '2')[0]
    sch.wire(rgp, gpin)
    jg = (gpin[0] - 2.54, oy)
    sch.part(rpd, 'Device:R', '100k', jg[0], oy + 6.35, 0, {'1': ('W', 'GATE%d' % n), '2': 'GND'},
             fp=FP_R, field_pos={'Reference': (jg[0] - 1.27, oy + 5.08), 'Value': (jg[0] - 1.27, oy + 7.62), 'just': 'right'})
    sch.wire(jg, sch.pin_end(rpd, '1')[0])
    sch.junction(jg)
    # local decoupling
    C('C%d' % (1 + n), '10uF 10V', d[0] + 30.48, oy - 15.24, 'VBAT', 'GND', fp=FP_C0603,
      fields={'Note': 'Channel %d local cap, VBAT to GND next to the MOSFET' % n})
    sch.label(net_n, (d[0], oy - 8.89), 0)

C('C1', '470uF 6.3V polymer', 262.89, 238.76, 'VBAT', 'GND', pol=True,
  fp='Capacitor_Tantalum_SMD:CP_EIA-7343-31_Kemet-D',
  fields={'Note': 'Low-ESR bulk (e.g. Panasonic 6TPE470MI), next to the battery pads'})
note('Rg 22 ohm limits the GPIO peak current (Ciss 2250 pF);\n'
     'Rpd 100k keeps the MOSFETs off during reset/boot.\n'
     'PWM 32 kHz on TIM2 (ARR 2000 @ 64 MHz), same resolution as motors.c', (12.7, 276.86))

# ================================================================ F. LEDS, PROGRAMMING, HOLES
block('F - Navigation LEDs, programming pads, mounting', (286, 154), (408, 250))
for k, (ref, col, rr, val, net, where) in enumerate([
        ('D1', 'white', 'R28', '220R', 'LEDF_K', 'front corner, top edge'),
        ('D2', 'white', 'R29', '220R', 'LEDF_K', 'front corner, right edge'),
        ('D3', 'red', 'R30', '470R', 'LEDR_K', 'rear corner, bottom edge'),
        ('D4', 'red', 'R31', '470R', 'LEDR_K', 'rear corner, left edge')]):
    x = 300.99 + 12.7 * k
    R(rr, val, x, 172.72, 'VSYS', ('W', 'LED%d_A' % (k + 1)), side='left')
    sch.part(ref, 'Device:LED', col, x, 180.34, 90, {'2': ('W', 'LED%d_A' % (k + 1)), '1': net}, fp=FP_LED,
             fields={'Note': 'Navigation LED, ' + where},
             field_pos={'Reference': (x - 2.54, 179.07), 'Value': (x - 2.54, 181.61), 'just': 'right'})
for unit, (y, g_, d_, s_, net_g, net_d, rpd) in enumerate([(182.88, '2', '6', '1', 'LED_FRONT', 'LEDF_K', 'R32'),
                                                          (205.74, '5', '3', '4', 'LED_REAR', 'LEDR_K', 'R33')], 1):
    sch.part('Q6', 'Device:Q_Dual_NMOS_S1G1D2S2G2D1', '2N7002DW', 365.76, y, 0,
             {g_: ('W', net_g), d_: net_d, s_: 'GND'}, unit=unit, fp='Package_TO_SOT_SMD:SOT-363_SC-70-6',
             field_pos={'Reference': (370.84, y - 1.27), 'Value': (370.84, y + 1.27), 'just': 'left'})
    gp = sch.pin_end('Q6', g_, unit)[0]
    sch.wire(gp, (gp[0] - 7.62, gp[1]))
    sch.label(net_g, (gp[0] - 7.62, gp[1]), 180)
    R(rpd, '100k', gp[0] - 2.54, gp[1] + 3.81, ('W', net_g), 'GND', side='left')
    sch.junction((gp[0] - 2.54, gp[1]))
note('LEDs supplied from VSYS (3.3-4.7 V):\na white LED (Vf ~3 V) would not\nlight from a 3.1 V GPIO', (292.1, 200.66))

for k, (tp, net, nt) in enumerate([('TP6', 'SWDIO', 'SWDIO (PA13)'), ('TP7', 'SWCLK', 'SWCLK (PA14)'),
                                   ('TP8', 'NRST', 'NRST')]):
    x = 378.46 + 10.16 * k
    sch.part(tp, 'Connector:TestPoint', net, x, 175.26, 0, {'1': net}, fp='TestPoint:TestPoint_Pad_D1.0mm',
             fields={'Note': nt + ' - pogo pad, 2x4 grid at 2.54 mm pitch on the bottom'}, stub=2.54,
             field_pos={'Reference': (x - 1.27, 168.91), 'Value': (x - 1.27, 166.37), 'just': 'left'})
for k, (tp, net, nt) in enumerate([('TP1', 'UART_TX', 'USART1 TX (PB6)'), ('TP2', 'UART_RX', 'USART1 RX (PB7)'),
                                   ('TP3', 'BOOT0', 'BOOT0: bridge to TP4 for DFU'),
                                   ('TP4', 'VDD', 'VDD 3.1 V'), ('TP5', 'GND', 'GND')]):
    x = 330.2 + 10.16 * k
    sch.part(tp, 'Connector:TestPoint', net, x, 233.68, 0, {'1': net}, fp='TestPoint:TestPoint_Pad_D1.0mm',
             fields={'Note': nt + ' - pogo pad, 2x4 grid at 2.54 mm pitch on the bottom'}, stub=2.54,
             field_pos={'Reference': (x - 1.27, 227.33), 'Value': (x - 1.27, 224.79), 'just': 'left'})
for k in range(4):
    sch.part('H%d' % (k + 1), 'Mechanical:MountingHole_Pad', 'D3.2', 378.46 + 7.62 * k, 228.6, 0, {'1': 'GND'},
             fp='DimaQuad:Grommet_PTH_3.2mm_Pad5.0mm',
             fields={'Note': 'Plated 3.2 hole for an M2 anti-vibration grommet, 16x16 pattern (frame C). Exposed 5.0 mm copper ring on both sides, GND'},
             field_pos={'Reference': (378.46 + 7.62 * k, 220.98), 'Value': (378.46 + 7.62 * k, 223.52)},
             in_bom=False)
note('Grommet holes 3.2 PTH, 16x16\nfrom DimaQuadFC_C_Keepouts.dxf', (375.92, 210.82))

sch.write(OUT)
json.dump({'%s.%s' % k: v for k, v in sch.expected.items()}, open(OUT + '.expected.json', 'w'), indent=0)
json.dump(sorted('%s.%s' % k for k in sch.nc), open(OUT + '.nc.json', 'w'))
parts = {}
for ref, P in sch.parts.items():
    parts[ref] = dict(lib_id=P['lib_id'], value=P['value'], fp=P['fp'], fields=P['fields'], dnp=P['dnp'])
json.dump(parts, open(OUT + '.parts.json', 'w'), indent=1)
print('ok', len(sch.parts), 'parts')
