import re,statistics as st,collections
from hl import lines
def blocks(n):
    L=lines(n)
    B=collections.OrderedDict()
    for l in L: B.setdefault(l['k'][0],[]).append(l)
    out=[]
    for b,ls in B.items():
        xs=[l['xh'] for l in ls if l['xh']]
        txt='\n'.join(l['text'] for l in ls)
        alpha=sum(ch.isalpha() for ch in txt)/max(1,len(txt))
        conf=st.mean(w['c'] for l in ls for w in l['ws'])
        out.append(dict(b=b,lines=ls,xh=st.median(xs) if xs else None,x0=min(l['x0'] for l in ls),x1=max(l['x1'] for l in ls),
                        y0=min(l['y0'] for l in ls),y1=max(l['y1'] for l in ls),text=txt,alpha=alpha,conf=conf))
    return out
def classe(bk,top):
    t=bk['text'].strip(); xh=bk['xh']
    if bk['alpha']<0.45 or bk['conf']<45 or len(re.sub(r'[^A-Za-z]','',t))<3: return 'bruit'
    if bk['y0']<=top+5 and len(bk['lines'])==1 and re.search(r'\b\d{1,3}\b',t): return 'entete'
    if xh and xh>=27: return 'grand'
    if all(re.sub(r'[^A-Za-z]','',l['text']).isupper() for l in bk['lines'] if re.sub(r'[^A-Za-z]','',l['text'])) and len(t)<60: return 'titre'
    if xh and xh<=20.5: return 'legende'
    return 'corps'
