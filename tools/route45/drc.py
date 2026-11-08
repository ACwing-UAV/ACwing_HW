import sys,pcbnew,re,collections
b=pcbnew.LoadBoard(sys.argv[1])
if len(sys.argv)>3 and sys.argv[3]=='fill':
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(sys.argv[1],b)
pcbnew.WriteDRCReport(b,sys.argv[2],pcbnew.EDA_UNITS_MILLIMETRES,True)
t=open(sys.argv[2]).read()
c=collections.Counter(re.findall(r'^\[(\w+)\]',t,re.M))
print({k:v for k,v in c.items() if k not in ('lib_footprint_mismatch','lib_footprint_issues','silk_overlap','silk_over_copper','text_height','text_thickness','silk_edge_clearance')}, re.findall(r'\*\* Found \d+ \w+ pads? \*\*|Found \d+ unconnected',t))
