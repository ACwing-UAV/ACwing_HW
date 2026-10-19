import sys, json, xml.etree.ElementTree as ET
xml, exp, ncf = sys.argv[1], sys.argv[2], sys.argv[3]
t = ET.parse(xml).getroot()
pin_net = {}; nets = {}
for n in t.find('nets'):
    name = n.get('name').lstrip('/')
    nodes = [(nd.get('ref'), nd.get('pin'), nd.get('pintype')) for nd in n.findall('node')]
    nets[name] = nodes
    for r, p, ty in nodes:
        pin_net[(r, p)] = name
E = {tuple(k.split('.', 1)): v for k, v in json.load(open(exp)).items()}
NC = {tuple(k.split('.', 1)) for k in json.load(open(ncf))}
err = 0
m = {}
for k, v in E.items():
    got = pin_net.get(k)
    if got is None or got.startswith('unconnected'):
        print('UNCONNECTED', k, 'expected', v); err += 1; continue
    m.setdefault(v, set()).add(got)
inv = {}
for v, gots in m.items():
    if len(gots) > 1:
        print('SPLIT net', v, '->', gots); err += 1
    for gname in gots:
        inv.setdefault(gname, set()).add(v)
        if gname != v and not gname.startswith('Net-('):
            print('NAME', v, '->', gname); err += 1
for gname, vs in inv.items():
    if len(vs) > 1:
        print('SHORT', gname, '<-', vs); err += 1
for k, v in pin_net.items():
    if k not in E and k not in NC and not v.startswith('unconnected'):
        print('UNEXPECTED', k, v); err += 1
    if k in NC and not v.startswith('unconnected'):
        print('NC but connected', k, v); err += 1
for name, nodes in nets.items():
    if len(nodes) < 2 and not name.startswith('unconnected'):
        print('SINGLE-NODE net', name, nodes); err += 1
# power_in pins need a driver
drivers = {'GND', 'VBUS', 'VSYS', 'SMPS_LX', 'VLED', 'VBAT', 'VREG'}   # nets with PWR_FLAG (VBAT from the ESC link or the battery pads; VREG from the buck U12); SMPS_LX is driven by the MCU SMPS switch (VLXSMPS)
for name, nodes in nets.items():
    tys = [ty for _, _, ty in nodes]
    if 'power_in' in tys and name not in drivers and 'power_out' not in tys:
        print('UNDRIVEN power_in on', name, nodes); err += 1
    if tys.count('power_out') > 1:
        print('MULTIPLE power_out on', name); err += 1
    if 'output' in tys and tys.count('output') + tys.count('power_out') > 1:
        print('MULTIPLE outputs on', name, nodes); err += 1
print('nets:', len(nets), 'pins:', len(pin_net), 'errors:', err)
