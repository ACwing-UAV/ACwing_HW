import re
TOK=re.compile(r'\s*(?:(\()|(\))|("(?:[^"\\]|\\.)*")|([^\s()"]+))')
class Sym(str): pass
def parse(s):
    pos=0; stack=[[]]
    while True:
        m=TOK.match(s,pos)
        if not m or m.end()==pos: break
        pos=m.end()
        if m.group(1): stack.append([])
        elif m.group(2):
            t=stack.pop(); stack[-1].append(t)
        elif m.group(3): stack[-1].append(m.group(3)[1:-1].replace('\\"','"').replace('\\\\','\\'))
        else: stack[-1].append(Sym(m.group(4)))
    return stack[0]
def q(s): return '"'+str(s).replace('\\','\\\\').replace('"','\\"').replace('\n','\\n')+'"'
def dump(x,ind=0):
    if isinstance(x,list):
        if not x: return '()'
        simple=all(not isinstance(e,list) for e in x)
        if simple: return '('+' '.join(dump(e) for e in x)+')'
        out='('+' '.join(dump(e) for e in x[:1])
        for e in x[1:]:
            if isinstance(e,list): out+='\n'+'  '*(ind+1)+dump(e,ind+1)
            else: out+=' '+dump(e)
        return out+')'
    if isinstance(x,Sym): return str(x)
    if isinstance(x,(int,float)):
        v=round(float(x),4)
        return ('%d'%v) if v==int(v) else ('%.4f'%v).rstrip('0').rstrip('.')
    return q(x)
def find(node,key):
    return [e for e in node if isinstance(e,list) and e and e[0]==key]
def find1(node,key):
    r=find(node,key); return r[0] if r else None
_libcache={}
def lib_symbol(lib,name):
    if lib not in _libcache:
        _libcache[lib]=parse(open('/usr/share/kicad/symbols/%s.kicad_sym'%lib).read())[0]
    L=_libcache[lib]
    for s in find(L,'symbol'):
        if s[1]==name: return s
    raise KeyError(lib+':'+name)
def pins(sym):
    out=[]
    def walk(n):
        for e in n:
            if isinstance(e,list) and e:
                if e[0]=='pin':
                    at=find1(e,'at'); nm=find1(e,'name'); nu=find1(e,'number')
                    out.append(dict(type=str(e[1]),num=nu[1],name=nm[1],x=float(at[1]),y=float(at[2]),a=int(float(at[3])) if len(at)>3 else 0,
                                    length=float(find1(e,'length')[1]),hide=any(isinstance(z,Sym) and z=='hide' for z in e)))
                else: walk(e)
    walk(sym); return out
