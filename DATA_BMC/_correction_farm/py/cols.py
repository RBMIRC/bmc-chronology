"""Pages à deux colonnes (notes, index, crédits) : mots → colonnes → lignes."""
import csv, statistics as st
def mots(n, base='/tmp/farm/hd/ocr'):
    W=[]
    for r in csv.DictReader(open(f'{base}/{n}.tsv'),delimiter='\t',quoting=csv.QUOTE_NONE):
        if r['level']=='5' and (r['text'] or '').strip():
            W.append(dict(t=r['text'],x=int(r['left']),y=int(r['top']),w=int(r['width']),h=int(r['height']),c=float(r['conf'])))
    return W
def colonnes(W, x_min, x_max, nb=2):
    """Coupe en nb colonnes au plus grand creux de l'histogramme horizontal entre x_min et x_max."""
    import numpy as np
    occ=np.zeros(x_max+1)
    for w in W:
        if x_min<=w['x']<=x_max: occ[w['x']:min(x_max,w['x']+w['w'])]+=1
    mid=(x_min+x_max)//2; zone=occ[mid-300:mid+300]
    # creux le plus large
    best=(0,mid); run=0
    for i,v in enumerate(zone):
        run = run+1 if v==0 else 0
        if run>best[0]: best=(run, mid-300+i-run//2)
    return best[1]
def lignes(W, tol=None):
    W=sorted(W,key=lambda w:(w['y'],w['x']))
    if not W: return []
    hs=st.median(w['h'] for w in W); tol=tol or hs*0.6
    L=[]
    for w in W:
        cy=w['y']+w['h']/2
        for l in L:
            if abs(l['cy']-cy)<tol: l['ws'].append(w); break
        else: L.append({'cy':cy,'ws':[w]})
    for l in L:
        l['ws'].sort(key=lambda w:w['x']); l['x0']=l['ws'][0]['x']; l['y']=min(w['y'] for w in l['ws'])
        l['text']=' '.join(w['t'] for w in l['ws'])
    return sorted(L,key=lambda l:l['cy'])
