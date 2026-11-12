import re
TOK=re.compile(r'\s*(\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+)')
def parse(t):
    st=[[]];i=0;n=len(t)
    for m in TOK.finditer(t):
        g=m.group(1)
        if g=='(': st.append([])
        elif g==')': x=st.pop(); st[-1].append(x)
        else: st[-1].append(g)
    return st[0][0]
def dump(x,ind=0):
    if not isinstance(x,list): return x
    if all(not isinstance(c,list) for c in x): return '('+' '.join(x)+')'
    s='('+' '.join(c for c in x[:1])
    for c in x[1:]:
        s+= ('\n'+'\t'*(ind+1)+dump(c,ind+1)) if isinstance(c,list) else ' '+c
    return s+'\n'+'\t'*ind+')'
