"""generic OCR-disagreement sheet generator for a page range: python tsheets_gen.py name first last"""
import pickle, re, difflib, csv, cv2, numpy as np, sys
Q = pickle.load(open('/tmp/dub/merged.pkl','rb')); S = 1.1111
name, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
def tess_words(pi):
    rows = list(csv.reader(open(f'/tmp/dub/tess/{pi+1:03d}.tsv'), delimiter='\t', quoting=csv.QUOTE_NONE))
    return [r[11] for r in rows[1:] if len(r) >= 12 and r[0] == '5' and r[11].strip()]
def core(w):
    return w.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"').replace('—', '-').replace('–', '-')
def alpha(s): return re.sub(r'[^A-Za-z0-9]', '', s)
HS = pickle.load(open('/tmp/dub/notes_H.pkl','rb')) if name == 'n' else {}
items = []
for pi in range(a, b + 1):
    W = [(li, w) for li, l in enumerate(Q[pi]['lines']) if li > 0 for w in l['words']]
    A_ = [w[4] for _, w in W]; B_ = tess_words(pi)
    ca = [core(x) for x in A_]; cb = [core(x) for x in B_]
    sm = difflib.SequenceMatcher(None, ca, cb, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'equal': continue
        A = ' '.join(A_[i1:i2]); B = ' '.join(B_[j1:j2])
        nA = ' '.join(ca[i1:i2]).replace('"','').replace("'",''); nB = ' '.join(cb[j1:j2]).replace('"','').replace("'",'')
        if nA == nB or nA.replace(' ','') == nB.replace(' ',''): continue
        if re.fullmatch(r'[. ]*', nA) and re.fullmatch(r'[. ]*', nB): continue
        if alpha(nA).lower() == alpha(nB).lower() and alpha(nA) and re.search(r'[A-Z]{2}|[a-z][A-Z]', A + B) and not re.search(r'\d', A+B): continue
        if op == 'insert' and re.search(r'Pages? \d|INDEX|^\d{3}$', B): continue
        if op == 'insert' and not alpha(B) and len(B) <= 2: continue
        if op == 'delete' and not alpha(A) and len(A) <= 2 and not re.search(r'[.,;:]', A): continue
        if i1 >= len(W): continue
        k0 = i1; k1 = min(max(i1, i2 - 1), len(W) - 1); li = W[k0][0]
        ws = [W[k][1] for k in range(k0, k1 + 1) if W[k][0] == li]
        if pi in HS and ws and max(w[2] for w in ws) * S < HS[pi] - 3: continue
        if op == 'insert' and pi in HS and all(re.search(r'\d', t) or not re.search(r'[A-Za-z]', t) for t in B.split()): continue
        items.append(dict(pi=pi, li=li, A=A, B=B, x0=min(w[0] for w in ws), x1=max(w[2] for w in ws)))
pickle.dump(items, open(f'/tmp/dub/titems_{name}.pkl', 'wb'))
CW, CH, COLS, ROWS = 660, 110, 3, 16
per = COLS * ROWS; cache = {}
for s in range(0, len(items), per):
    sheet = np.full((ROWS * CH, COLS * CW), 255, np.uint8)
    for j, it in enumerate(items[s:s+per]):
        pi = it['pi']
        if pi not in cache: cache.clear(); cache[pi] = cv2.imread(f'/tmp/dub/img/p-{pi:03d}.jpg', cv2.IMREAD_GRAYSCALE)
        im = cache[pi]; l = Q[pi]['lines'][it['li']]
        y0 = int(l['y0'] * S) - 6; y1 = int(l['y1'] * S) + 6
        xc0 = int(it['x0'] * S) - 120; xc1 = int(it['x1'] * S) + 120
        crop = im[max(0, y0):y1, max(0, xc0):xc1]
        crop = cv2.resize(crop, None, fx=1.6, fy=1.6, interpolation=cv2.INTER_CUBIC)[:CH - 34, :CW - 10]
        r, c = divmod(j, COLS); oy, ox = r * CH, c * CW
        sheet[oy:oy + crop.shape[0], ox + 5:ox + 5 + crop.shape[1]] = crop
        wx = int((it['x0'] * S - max(0, xc0)) * 1.6) + 5; wx1 = int((it['x1'] * S - max(0, xc0)) * 1.6) + 5
        cv2.line(sheet, (ox + wx, oy + crop.shape[0] + 1), (ox + min(wx1, CW - 5), oy + crop.shape[0] + 1), 0, 2)
        t = f"{s+j}  A:{it['A'][:30]}  |  B:{it['B'][:30]}".encode('ascii', 'replace').decode()
        cv2.putText(sheet, t, (ox + 5, oy + CH - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 0, 1, cv2.LINE_AA)
        cv2.line(sheet, (ox, oy + CH - 1), (ox + CW, oy + CH - 1), 160, 1)
        cv2.line(sheet, (ox + CW - 1, oy), (ox + CW - 1, oy + CH), 160, 1)
    cv2.imwrite(f'/tmp/dub/sheets/{name}{s // per:02d}.png', sheet)
print(len(items), (len(items) + per - 1) // per)
