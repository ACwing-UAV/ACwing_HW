# Project symbol library "DimaQuad": parts missing from the KiCad 7 libraries.
import copy
from sexp import dump, find, find1, Sym
from kisch import flatten, rename_sym, set_prop, eff, S

LIB = 'DimaQuad'

def _pin(typ, x, y, a, name, num, length=2.54, hide=False):
    p = [S('pin'), S(typ), S('line'), [S('at'), x, y, a], [S('length'), length]]
    if hide:
        p.append(S('hide'))
    p += [[S('name'), name, eff()], [S('number'), num, eff()]]
    return p

def _props(sym, d):
    for k, v in d.items():
        set_prop(sym, k, v)

def power_sym(name):
    s = rename_sym(flatten('power', 'VCC'), 'VCC', name)
    _props(s, {'Value': name,
               'ki_description': 'Power symbol creates a global label with name "%s"' % name})
    for sub in find(s, 'symbol'):
        for e in sub:
            if isinstance(e, list) and e and e[0] == 'pin':
                find1(e, 'name')[1] = name
    return s

def lsm6dsv16x():
    s = rename_sym(flatten('Sensor_Motion', 'LSM6DSM'), 'LSM6DSM', 'LSM6DSV16X')
    _props(s, {'Value': 'LSM6DSV16X',
               'Footprint': 'Package_LGA:LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y',
               'Datasheet': 'https://www.st.com/resource/en/datasheet/lsm6dsv16x.pdf',
               'ki_keywords': 'IMU accelerometer gyroscope 6-axis sensor hub',
               'ki_description': '6-axis IMU, I2C/I3C/SPI, sensor hub (Mode 2), LGA-14 2.5x3 mm'})
    ren = {'2': ('SDx', 'bidirectional'), '3': ('SCx', 'bidirectional'),
           '10': ('OCS_Aux', 'passive'), '11': ('SDO_Aux', 'passive')}
    for sub in find(s, 'symbol'):
        for e in sub:
            if isinstance(e, list) and e and e[0] == 'pin':
                n = find1(e, 'number')[1]
                if n in ren:
                    find1(e, 'name')[1] = ren[n][0]
                    e[1] = S(ren[n][1])
    return s

def stc4054():
    s = rename_sym(flatten('Battery_Management', 'LTC4054ES5-4.2'), 'LTC4054ES5-4.2', 'STC4054')
    _props(s, {'Value': 'STC4054',
               'Footprint': 'Package_TO_SOT_SMD:TSOT-23-5',
               'Datasheet': 'https://www.st.com/resource/en/datasheet/stc4054.pdf',
               'ki_keywords': 'li-ion charger linear 4.2V',
               'ki_description': '800 mA standalone linear Li-Ion charger, 4.2 V, TSOT23-5 (pinout LTC4054)'})
    return s

def ld39130s_adj():
    n = 'LD39130S-ADJ'
    body = [S('symbol'), n + '_0_1',
            [S('rectangle'), [S('start'), -7.62, 5.08], [S('end'), 7.62, -5.08],
             [S('stroke'), [S('width'), 0.254], [S('type'), S('default')]], [S('fill'), [S('type'), S('background')]]]]
    pins = [S('symbol'), n + '_1_1',
            _pin('power_in', -10.16, 2.54, 0, 'IN', '4'),
            _pin('input', -10.16, 0, 0, 'EN', '3'),
            _pin('input', -10.16, -2.54, 0, 'GM', '1'),
            _pin('power_out', 10.16, 2.54, 180, 'OUT', '6'),
            _pin('input', 10.16, 0, 180, 'ADJ', '5'),
            _pin('power_in', 0, -7.62, 90, 'GND', '2')]
    s = [S('symbol'), n, [S('in_bom'), S('yes')], [S('on_board'), S('yes')],
         [S('property'), 'Reference', 'U', [S('at'), -7.62, 6.35, 0], eff(justify='left')],
         [S('property'), 'Value', n, [S('at'), 0, -10.16, 0], eff()],
         [S('property'), 'Footprint', 'Package_DFN_QFN:DFN-6_1.3x1.2mm_P0.4mm', [S('at'), 0, 0, 0], eff(hide=True)],
         [S('property'), 'Datasheet', 'https://www.st.com/resource/en/datasheet/ld39130s.pdf', [S('at'), 0, 0, 0], eff(hide=True)],
         [S('property'), 'ki_keywords', 'LDO regulator low quiescent adjustable', [S('at'), 0, 0, 0], eff(hide=True)],
         [S('property'), 'ki_description', '300 mA LDO, 1 uA green mode, adjustable (VADJ 0.8 V), DFN6 1.2x1.3 mm', [S('at'), 0, 0, 0], eff(hide=True)],
         body, pins]
    return s

def aon7423():
    return _dfn_fet('Q_PMOS_GSD', 'AON7423', {'Value': 'AON7423',
               'Footprint': 'Package_SO:Vishay_PowerPAK_1212-8_Single',
               'Datasheet': 'https://www.aosmd.com/sites/default/files/res/datasheets/AON7423.pdf',
               'ki_keywords': 'P-MOSFET logic level 20V',
               'ki_description': '20 V P-MOSFET, 4.9 mOhm @ VGS -2.5 V, Vgs +-8 V, DFN 3x3 EP: 1-3 S, 4 G, 5-8 + EP D'})

def aon7524():
    return _dfn_fet('Q_NMOS_GSD', 'AON7524', {'Value': 'AON7524',
               'Footprint': 'Package_SO:Vishay_PowerPAK_1212-8_Single',
               'Datasheet': 'https://www.aosmd.com/sites/default/files/res/datasheets/AON7524.pdf',
               'ki_keywords': 'N-MOSFET logic level 30V',
               'ki_description': '30 V N-MOSFET, 5.8 mOhm @ VGS 2.5 V, DFN 3x3 EP: 1-3 S, 4 G, 5-8 + EP D'})

def _dfn_fet(base, name, props):
    s = rename_sym(flatten('Device', base), base, name)
    _props(s, props)
    for sub in find(s, 'symbol'):
        new = []
        for e in sub:
            if isinstance(e, list) and e and e[0] == 'pin':
                num = find1(e, 'number')
                nm = find1(e, 'name')[1]
                if nm == 'G':
                    num[1] = '4'
                elif nm == 'D':
                    num[1] = '5'
                elif nm == 'S':
                    num[1] = '1'
                    for extra in ('2', '3'):
                        c = copy.deepcopy(e)
                        find1(c, 'number')[1] = extra
                        c.insert(5, S('hide'))
                        new.append(c)
            new.append(e) if e not in new else None
        sub[:] = new
    return s

def mlpf_wb55():
    n = 'MLPF-WB55-01E3'
    body = [S('symbol'), n + '_0_1',
            [S('rectangle'), [S('start'), -5.08, 2.54], [S('end'), 5.08, -2.54],
             [S('stroke'), [S('width'), 0.254], [S('type'), S('default')]], [S('fill'), [S('type'), S('background')]]]]
    pins = [S('symbol'), n + '_1_1',
            _pin('passive', -7.62, 0, 0, 'IN', 'A3'),
            _pin('passive', 7.62, 0, 180, 'OUT', 'A1'),
            _pin('power_in', 0, -5.08, 90, 'GND', 'B2'),
            _pin('passive', 0, -5.08, 90, 'GND', 'A2', hide=True),
            _pin('passive', 0, -5.08, 90, 'GND', 'B1', hide=True),
            _pin('passive', 0, -5.08, 90, 'GND', 'B3', hide=True)]
    s = [S('symbol'), n, [S('in_bom'), S('yes')], [S('on_board'), S('yes')],
         [S('property'), 'Reference', 'U', [S('at'), -5.08, 3.81, 0], eff(justify='left')],
         [S('property'), 'Value', n, [S('at'), 0, -7.62, 0], eff()],
         [S('property'), 'Footprint', 'DimaQuad:ST_MLPF-WB55-01E3_CSP-6', [S('at'), 0, 0, 0], eff(hide=True)],
         [S('property'), 'Datasheet', 'https://www.st.com/resource/en/datasheet/mlpf-wb55-01e3.pdf', [S('at'), 0, 0, 0], eff(hide=True)],
         [S('property'), 'ki_keywords', 'RF low pass filter matching STM32WB', [S('at'), 0, 0, 0], eff(hide=True)],
         [S('property'), 'ki_description', '2.4 GHz low-pass filter with integrated matching for STM32WB55 (IN = RF1, OUT = 50 ohm antenna), 6-bump CSP', [S('at'), 0, 0, 0], eff(hide=True)],
         body, pins]
    return s

def tsc213():
    n = 'TSC213'
    body = [S('symbol'), n + '_0_1',
            [S('rectangle'), [S('start'), -7.62, 5.08], [S('end'), 7.62, -5.08],
             [S('stroke'), [S('width'), 0.254], [S('type'), S('default')]], [S('fill'), [S('type'), S('background')]]]]
    pins = [S('symbol'), n + '_1_1',
            _pin('input', -10.16, 2.54, 0, 'VIN+', '4'),
            _pin('input', -10.16, -2.54, 0, 'VIN-', '5'),
            _pin('power_in', 0, 7.62, 270, 'VCC', '3'),
            _pin('power_in', 0, -7.62, 90, 'GND', '2'),
            _pin('input', 2.54, -7.62, 90, 'REF', '1'),
            _pin('output', 10.16, 0, 180, 'OUT', '6')]
    s = [S('symbol'), n, [S('in_bom'), S('yes')], [S('on_board'), S('yes')],
         [S('property'), 'Reference', 'U', [S('at'), -7.62, 6.35, 0], eff(justify='left')],
         [S('property'), 'Value', n, [S('at'), 0, -10.16, 0], eff()],
         [S('property'), 'Footprint', 'Package_TO_SOT_SMD:SOT-363_SC-70-6', [S('at'), 0, 0, 0], eff(hide=True)],
         [S('property'), 'Datasheet', 'https://www.st.com/resource/en/datasheet/tsc210.pdf', [S('at'), 0, 0, 0], eff(hide=True)],
         [S('property'), 'ki_keywords', 'current sense amplifier zero drift bidirectional', [S('at'), 0, 0, 0], eff(hide=True)],
         [S('property'), 'ki_description', 'Zero-drift current sense amplifier, gain 50 V/V, CM -0.3...26 V, SC70-6 (DS13237: 1 REF, 2 GND, 3 VCC, 4 VIN+, 5 VIN-, 6 OUT)', [S('at'), 0, 0, 0], eff(hide=True)],
         body, pins]
    return s

def all_symbols():
    syms = {
        'LSM6DSV16X': lsm6dsv16x(),
        'STC4054': stc4054(),
        'LD39130S-ADJ': ld39130s_adj(),
        'AON7524': aon7524(),
        'AON7423': aon7423(),
        'MLPF-WB55-01E3': mlpf_wb55(),
        'TSC213': tsc213(),
    }
    for p in ('VBAT', 'VBAT_F', 'VSYS'):
        syms[p] = power_sym(p)
    return syms

def write_lib(path):
    lib = [S('kicad_symbol_lib'), [S('version'), 20220914], [S('generator'), S('kicad_symbol_editor')]]
    lib += list(all_symbols().values())
    with open(path, 'w') as f:
        f.write(dump(lib) + '\n')
