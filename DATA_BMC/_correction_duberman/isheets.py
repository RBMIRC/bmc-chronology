import json, re, csv, difflib, pickle, cv2, numpy as np, sys
sys.path.insert(0,'/tmp/dub')
from index2 import page_split
P = json.load(open('/tmp/dub/pages.json')); S = 1.1111
def tess_words(pi):
    rows = list(csv.reader(open(f'/tmp/dub/tess/{pi+1:03d}.tsv'), delimiter='\t', quoting=csv.QUOTE_NONE))
    return [r[11] for r in rows[1:] if len(r) >= 12 and r[0] == '5' and r[11].strip()]
def core(w): return w.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"').replace('—', '-').replace('–', '-')
def alpha(s): return re.sub(r'[^A-Za-z0-9]', '', s)
items = []
for pi in range(585, 615):
    sp = page_split(pi)
    ws = [w for f in P[pi]['lines'] for w in f['words']]
    c1 = sorted([w for w in ws if (w[0]+w[2])/2 < sp], key=lambda w: (round((w[1]+w[3])/2/9), w[0]))
    c2 = sorted([w for w in ws if (w[0]+w[2])/2 >= sp], key=lambda w: (round((w[1]+w[3])/2/9), w[0]))
    W = c1 + c2
    A_ = [w[4] for w in W]; B_ = tess_words(pi)
    sm = difflib.SequenceMatcher(None, [core(x) for x in A_], [core(x) for x in B_], autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'equal' or i1 >= len(W): continue
        A = ' '.join(A_[i1:i2]); B = ' '.join(B_[j1:j2])
        nA, nB = core(A).replace('"','').replace("'",''), core(B).replace('"','').replace("'",'')
        if nA.replace(' ','') == nB.replace(' ',''): continue
        if op == 'insert' and ('INDEX' in B or not alpha(B)): continue
        if op == 'delete' and (not alpha(A) or 'INDEX' in A): continue
        ww = W[i1:max(i2, i1+1)]
        y = (ww[0][1]+ww[0][3])/2
        ww = [w for w in ww if abs((w[1]+w[3])/2 - y) < 9]
        items.append(dict(pi=pi, A=A, B=B, x0=min(w[0] for w in ww), x1=max(w[2] for w in ww), y0=min(w[1] for w in ww), y1=max(w[3] for w in ww)))
pickle.dump(items, open('/tmp/dub/titems_i.pkl','wb'))
CW, CH, COLS, ROWS = 660, 110, 3, 16; per = COLS*ROWS; cache = {}
for s in range(0, len(items), per):
    sheet = np.full((ROWS*CH, COLS*CW), 255, np.uint8)
    for j, it in enumerate(items[s:s+per]):
        pi = it['pi']
        if pi not in cache: cache.clear(); cache[pi] = cv2.imread(f'/tmp/dub/img/p-{pi:03d}.jpg', cv2.IMREAD_GRAYSCALE)
        im = cache[pi]
        y0 = int(it['y0']*S)-6; y1 = int(it['y1']*S)+6; xc0 = int(it['x0']*S)-120; xc1 = int(it['x1']*S)+120
        crop = cv2.resize(im[max(0,y0):y1, max(0,xc0):xc1], None, fx=1.6, fy=1.6, interpolation=cv2.INTER_CUBIC)[:CH-34, :CW-10]
        r, c = divmod(j, COLS); oy, ox = r*CH, c*CW
        sheet[oy:oy+crop.shape[0], ox+5:ox+5+crop.shape[1]] = crop
        wx = int((it['x0']*S - max(0,xc0))*1.6)+5; wx1 = int((it['x1']*S - max(0,xc0))*1.6)+5
        cv2.line(sheet, (ox+wx, oy+crop.shape[0]+1), (ox+min(wx1, CW-5), oy+crop.shape[0]+1), 0, 2)
        t = f"{s+j}  A:{it['A'][:30]}  |  B:{it['B'][:30]}".encode('ascii','replace').decode()
        cv2.putText(sheet, t, (ox+5, oy+CH-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 0, 1, cv2.LINE_AA)
        cv2.line(sheet, (ox, oy+CH-1), (ox+CW, oy+CH-1), 160, 1); cv2.line(sheet, (ox+CW-1, oy), (ox+CW-1, oy+CH), 160, 1)
    cv2.imwrite(f'/tmp/dub/sheets/i{s//per:02d}.png', sheet)
print(len(items))
