import sys,re,subprocess
import os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import sx
src,dst=sys.argv[1],sys.argv[2]
tree=sx.parse(open(src).read())
removed=set('generator_version tenting covering plugging capping filling pcbplotparams embedded_fonts embedded_files'.split())|set(sys.argv[3:])
def ncu(tree):
    lay=[c for c in tree if isinstance(c,list) and c[0]=='layers'][0]
    return sum(1 for l in lay[1:] if l[1].strip('"').endswith('.Cu'))
N=ncu(tree)
def k7layers(n):
    L=[['0','"F.Cu"','signal']]+[[str(i),f'"In{i}.Cu"','signal'] for i in range(1,n-1)]+[['31','"B.Cu"','signal']]
    tech="32 B.Adhes user \"B.Adhesive\";33 F.Adhes user \"F.Adhesive\";34 B.Paste user;35 F.Paste user;36 B.SilkS user \"B.Silkscreen\";37 F.SilkS user \"F.Silkscreen\";38 B.Mask user;39 F.Mask user;40 Dwgs.User user \"User.Drawings\";41 Cmts.User user \"User.Comments\";42 Eco1.User user \"User.Eco1\";43 Eco2.User user \"User.Eco2\";44 Edge.Cuts user;45 Margin user;46 B.CrtYd user \"B.Courtyard\";47 F.CrtYd user \"F.Courtyard\";48 B.Fab user;49 F.Fab user;50 User.1 user;51 User.2 user"
    for t in tech.split(';'):
        p=t.split(' ',3); L.append([p[0],'"'+p[1]+'"',p[2]]+([p[3]] if len(p)>3 else []))
    return ['layers']+L
def tr(x,parent=None):
    if not isinstance(x,list): return x
    out=[]
    for c in x:
        if isinstance(c,list) and c:
            if c[0] in removed: continue
            if c[0]=='uuid': c=['tstamp',c[1]]
            if c[0] in ('remove_unused_layers','keep_end_layers') and len(c)==2:
                if c[1]=='yes': out.append([c[0]])
                continue
            if c[0]=='attr': c=[a for a in c if a!='dnp']
            if c==['fill','no']: c=['fill','none']
            if c[0]=='property' and parent=='footprint' or (c[0]=='property' and x[0]=='footprint'):
                c=c[:3]
                if c[1] in ('"Reference"','"Value"'):
                    out.append(['fp_text', 'reference' if c[1]=='"Reference"' else 'value', c[2], ['at','0','0'],['layer','"F.Fab"'],'hide',['effects',['font',['size','0.5','0.5'],['thickness','0.1']]]])
                    continue
            if c[0] in ('hide','locked') and len(c)==2:
                if c[1]=='yes' and (c[0]=='hide' or x[0] in ('footprint','segment','via','arc')): out.append(c[0])
                continue
            c=tr(c,x[0])
        out.append(c)
    return out
t2=tr(tree)
nets=['""']
def coll(x):
    if isinstance(x,list):
        if x and x[0]=='net' and len(x)==2 and x[1] not in nets: nets.append(x[1])
        for c in x: coll(c)
coll(t2)
NID={n:i for i,n in enumerate(nets)}
def fixnet(x):
    if not isinstance(x,list): return x
    out=[]
    for c in x:
        if isinstance(c,list) and c and c[0]=='net' and len(c)==2:
            if x[0]=='pad': c=['net',str(NID[c[1]]),c[1]]
            elif x[0]=='zone': out.append(['net',str(NID[c[1]])]); c=['net_name',c[1]]
            else: c=['net',str(NID[c[1]])]
        out.append(fixnet(c))
    return out
t2=fixnet(t2)
pos=[i for i,c in enumerate(t2) if isinstance(c,list) and c[0]=='setup'][0]+1
for i,n in enumerate(nets): t2.insert(pos+i,['net',str(i),n])
for i,c in enumerate(t2):
    if isinstance(c,list) and c[0]=='version': t2[i]=['version','20221018']
    if isinstance(c,list) and c[0]=='layers': t2[i]=k7layers(N)
for it in range(80):
    def strip(x):
        if not isinstance(x,list): return x
        return [strip(c) for c in x if not (isinstance(c,list) and c and c[0] in removed)]
    open(dst,'w').write(sx.dump(strip(t2)))
    r=subprocess.run(['python3.12','-c',f"import pcbnew;b=pcbnew.LoadBoard('{dst}');print('LOADED',len(b.GetTracks()),len(b.GetFootprints()))"],capture_output=True,text=True)
    out=r.stdout+r.stderr
    if r.returncode==0 and 'LOADED' in r.stdout: print(r.stdout.strip(), sorted(removed-set('generator_version tenting covering plugging capping filling pcbplotparams'.split()))); break
    m=re.search(r"(?:Unknown token|Unexpected) '([^']+)'|Expecting '([^']+)' in '[^']+', line (\d+)",out)
    if not m: print(out[-600:]); break
    if m.group(1): removed.add(m.group(1)); print('rm',m.group(1))
    else:
        ln=int(m.group(3)); print('EXPECT',m.group(0)[:300]); print(open(dst).read().splitlines()[ln-4:ln+1]); break
