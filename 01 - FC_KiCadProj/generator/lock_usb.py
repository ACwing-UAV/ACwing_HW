# locks the USB tracks routed by A* before Freerouting (finish.py keeps only locked copper)
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); n = 0
for t in b.GetTracks():
    if t.GetNetname() in ('USB_DP', 'USB_DM'):
        t.SetLocked(True); n += 1
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(sys.argv[1], b); print('USB items locked:', n)
