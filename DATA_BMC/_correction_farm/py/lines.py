import csv,re,glob,os,collections,statistics as st
def lines(n):
    L=collections.OrderedDict()
    for r in csv.DictReader(open(f'/tmp/farm/ocr/{n}.tsv'),delimiter='\t',quoting=csv.QUOTE_NONE):
        if r['level']!='5' or not (r['text'] or '').strip(): continue
        k=(r['block_num'],r['par_num'],r['line_num'])
        L.setdefault(k,[]).append(dict(t=r['text'],x=int(r['left']),y=int(r['top']),w=int(r['width']),h=int(r['height']),c=float(r['conf'])))
    out=[]
    for k,ws in L.items():
        x0=min(w['x'] for w in ws); y0=min(w['y'] for w in ws); x1=max(w['x']+w['w'] for w in ws); y1=max(w['y']+w['h'] for w in ws)
        # hauteur typique : médiane des mots de 3+ lettres minuscules sans jambage
        hs=[w['h'] for w in ws if re.fullmatch(r'[acemnorsuvwxz]{2,}[.,]?',w['t'])]
        out.append(dict(k=k,ws=ws,text=' '.join(w['t'] for w in ws),x0=x0,y0=y0,x1=x1,y1=y1,
                        h=st.median(hs) if hs else None,conf=st.mean(w['c'] for w in ws)))
    return out
