import csv,re,collections,statistics as st
XO=re.compile(r'[acemnorsuvwxz]{2,}[.,;:]?')
def lines(n,base='/tmp/farm/hd/ocr'):
    L=collections.OrderedDict()
    for r in csv.DictReader(open(f'{base}/{n}.tsv'),delimiter='\t',quoting=csv.QUOTE_NONE):
        if r['level']!='5' or not (r['text'] or '').strip(): continue
        k=(int(r['block_num']),int(r['par_num']),int(r['line_num']))
        L.setdefault(k,[]).append(dict(t=r['text'],x=int(r['left']),y=int(r['top']),w=int(r['width']),h=int(r['height']),c=float(r['conf'])))
    out=[]
    for k,ws in L.items():
        x0=min(w['x'] for w in ws); y0=min(w['y'] for w in ws); x1=max(w['x']+w['w'] for w in ws); y1=max(w['y']+w['h'] for w in ws)
        xs=[w['h'] for w in ws if XO.fullmatch(w['t'])]
        bots=[w['y']+w['h'] for w in ws if re.fullmatch(r"[A-Za-z]*[acemnorsuvwxzbdfhiklt][A-Za-z]*[.,;:”’\"']?",w['t']) and not re.search(r'[gjpqy]',w['t'])]
        txt=' '.join(w['t'] for w in ws)
        alpha=sum(ch.isalpha() for ch in txt)/max(1,len(txt))
        out.append(dict(k=k,ws=ws,text=txt,x0=x0,y0=y0,x1=x1,y1=y1,xh=st.median(xs) if xs else None,
                        base=st.median(bots) if bots else y1,conf=st.mean(w['c'] for w in ws),alpha=alpha))
    return out
