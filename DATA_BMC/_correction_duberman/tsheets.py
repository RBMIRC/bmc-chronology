import pickle, re, difflib, csv, cv2, numpy as np
Q = pickle.load(open('/tmp/dub/merged.pkl','rb'))
S = 1.1111
def tess_words(pi):
    rows = list(csv.reader(open(f'/tmp/dub/tess/{pi+1:03d}.tsv'), delimiter='\t', quoting=csv.QUOTE_NONE))
    return [r[11] for r in rows[1:] if len(r) >= 12 and r[0] == '5' and r[11].strip()]
def core(w):
    w = w.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"').replace('—', '-').replace('–', '-')
    w = re.sub(r'[0-9?°*®¢§%&\^™•#+>!]+$', '', w) if re.search(r'[a-z)][.,;:!?"\')]*[.,;:!?"\')][0-9?°*®¢§%&\^™•#+>!]+$', w) else w
    return w
def alpha(s): return re.sub(r'[^A-Za-z]', '', s)
PHOTO = set(range(217,225)) | set(range(393,401))
pages = list(range(11,16)) + list(range(17,20)) + [p for p in range(21,480) if p not in PHOTO]
items = []
for pi in pages:
    W = [(li, w) for li, l in enumerate(Q[pi]['lines']) if li > 0 for w in l['words']]
    a = [w[4] for _, w in W]
    b = tess_words(pi)
    ca = [core(x) for x in a]; cb = [core(x) for x in b]
    sm = difflib.SequenceMatcher(None, ca, cb, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'equal': continue
        A = ' '.join(a[i1:i2]); B = ' '.join(b[j1:j2])
        cA = ' '.join(ca[i1:i2]); cB = ' '.join(cb[j1:j2])
        nA = cA.replace('"', '').replace("'", ''); nB = cB.replace('"', '').replace("'", '')
        if nA == nB: continue
        if re.fullmatch(r'[. ]*', nA) and re.fullmatch(r'[. ]*', nB): continue        # ellipsis spacing
        if nA.replace(' ', '') == nB.replace(' ', ''): continue                       # spacing only
        if alpha(nA).lower() == alpha(nB).lower() and alpha(nA) and re.search(r'[A-Z]{2}|[a-z][A-Z]', A + B) : continue  # small caps case
        if alpha(nA) == alpha(nB) and re.sub(r'[A-Za-z.,;:\-\s]', '', nA + nB) and not re.search(r'[.,;:]', re.sub(r'[^.,;:]', '', nA) + re.sub(r'[^.,;:]', '', nB)) : continue
        if op == 'insert' and re.search(r'BLACK MOUNTAIN|[A-Z]{4,} \d+$|^[A-Z ]+$|^\d+$', B): continue
        if op == 'insert' and not alpha(B) and len(B) <= 2: continue
        if op == 'delete' and not alpha(A) and len(A) <= 2 and not re.search(r'[.,;:]', A): continue
        # locate bbox
        k0 = i1 if i1 < len(W) else len(W) - 1
        k1 = max(i1, i2 - 1) if i2 > i1 else k0
        k1 = min(k1, len(W) - 1)
        li = W[k0][0]
        ws = [W[k][1] for k in range(k0, k1 + 1) if W[k][0] == li]
        x0 = min(w[0] for w in ws); x1 = max(w[2] for w in ws)
        items.append(dict(pi=pi, li=li, A=A, B=B, x0=x0, x1=x1))
print(len(items))
pickle.dump(items, open('/tmp/dub/titems.pkl', 'wb'))
# sheets: each cell shows crop of line around word, plus labels
CW, CH, COLS, ROWS = 660, 110, 3, 16
font = cv2.FONT_HERSHEY_SIMPLEX
def put(img, text, org, scale=0.5):
    # ascii-only rendering for labels
    t = text.encode('ascii', 'replace').decode()
    cv2.putText(img, t, org, font, scale, 0, 1, cv2.LINE_AA)
per = COLS * ROWS
cache = {}
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
        # mark the word position with a small tick under the crop
        wx = int((it['x0'] * S - max(0, xc0)) * 1.6) + 5
        wx1 = int((it['x1'] * S - max(0, xc0)) * 1.6) + 5
        cv2.line(sheet, (ox + wx, oy + crop.shape[0] + 1), (ox + min(wx1, CW - 5), oy + crop.shape[0] + 1), 0, 2)
        put(sheet, f"{s+j}  A:{it['A'][:30]}  |  B:{it['B'][:30]}", (ox + 5, oy + CH - 10))
        cv2.line(sheet, (ox, oy + CH - 1), (ox + CW, oy + CH - 1), 160, 1)
        cv2.line(sheet, (ox + CW - 1, oy), (ox + CW - 1, oy + CH), 160, 1)
    cv2.imwrite(f'/tmp/dub/sheets/t{s // per:02d}.png', sheet)
