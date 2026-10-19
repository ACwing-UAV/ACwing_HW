# Project symbols for DimaQuadFlow (not in the KiCad 7 library): PixArt PMW3901MB-TXQT.
import sys
sys.path.insert(0, '/home/claude/genE')
from custom_syms import _pin, S, eff

def pmw3901():
    n = 'PMW3901MB'
    body = [S('symbol'), n + '_0_1',
            [S('rectangle'), [S('start'), -10.16, 10.16], [S('end'), 10.16, -10.16],
             [S('stroke'), [S('width'), 0.254], [S('type'), S('default')]], [S('fill'), [S('type'), S('background')]]]]
    pins = [S('symbol'), n + '_1_1',
            _pin('power_in', -12.7, 7.62, 0, 'VDD', '2'),
            _pin('power_in', -12.7, 5.08, 0, 'VDDIO', '3'),
            _pin('power_out', -12.7, 2.54, 0, 'VREG', '4'),
            _pin('input', -12.7, -2.54, 0, 'NRESET', '7'),
            _pin('input', 12.7, 7.62, 180, 'NCS', '19'),
            _pin('input', 12.7, 5.08, 180, 'SCLK', '17'),
            _pin('input', 12.7, 2.54, 180, 'MOSI', '16'),
            _pin('output', 12.7, 0, 180, 'MISO', '18'),
            _pin('output', 12.7, -2.54, 180, 'MOTION', '15'),
            _pin('power_in', -2.54, -12.7, 90, 'GND', '1'),
            _pin('passive', 0, -12.7, 90, 'GND', '21'),
            _pin('passive', 2.54, -12.7, 90, 'GND_PAD', '29')]
    for k in [5, 6] + list(range(8, 15)) + [20] + list(range(22, 29)):
        pins.append(_pin('no_connect', -12.7, -10.16, 0, 'NC', str(k), hide=True))
    s = [S('symbol'), n, [S('in_bom'), S('yes')], [S('on_board'), S('yes')],
         [S('property'), 'Reference', 'U', [S('at'), -10.16, 11.43, 0], eff(justify='left')],
         [S('property'), 'Value', n, [S('at'), 0, -15.24, 0], eff()],
         [S('property'), 'Footprint', 'DimaQuadFlow:PixArt_PMW3901MB_COB-28_6x6mm', [S('at'), 0, 0, 0], eff(hide=True)],
         [S('property'), 'Datasheet', 'PMW3901MB-TXQT-DS-R1.00 (PixArt, 2017-03-20)', [S('at'), 0, 0, 0], eff(hide=True)],
         [S('property'), 'ki_keywords', 'optical flow motion sensor far field', [S('at'), 0, 0, 0], eff(hide=True)],
         [S('property'), 'ki_description', 'Optical motion tracking chip, 80 mm to infinity, 4-wire SPI 2 MHz, VDD 1.8-2.1 V, VDDIO 1.8-3.6 V, 28-pin COB 6x6x2.28 mm with lens', [S('at'), 0, 0, 0], eff(hide=True)],
         body, pins]
    return s
