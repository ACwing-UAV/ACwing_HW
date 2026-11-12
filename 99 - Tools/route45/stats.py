import sys,pcbnew,math
for f in sys.argv[1:]:
    b=pcbnew.LoadBoard(f)
    tr=[t for t in b.GetTracks() if t.GetClass()=='PCB_TRACK']
    L=[t.GetLength()/1e6 for t in tr]
    bad=0
    for t in tr:
        s,e=t.GetStart(),t.GetEnd(); dx,dy=e.x-s.x,e.y-s.y
        if not(dx==0 or dy==0 or abs(dx)==abs(dy)): bad+=1
    print(f.split('/')[-2]+'/'+f.split('/')[-1], 'segs',len(tr),'non45(exact)',bad,'micro<20um',sum(1 for l in L if 0<l<0.02),'<5um',sum(1 for l in L if 0<l<0.005),'zero',sum(1 for l in L if l==0),'total len',round(sum(L),1),'vias',sum(1 for t in b.GetTracks() if t.GetClass()=='PCB_VIA'))
