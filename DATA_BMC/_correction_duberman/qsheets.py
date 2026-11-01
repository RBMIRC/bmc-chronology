import pickle, re, cv2, numpy as np
t = open('/tmp/dub/out/draft.txt').read()
body = t[:t.index('\nNOTES\n')]
INV = {v: k for k, v in zip('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹')}
ch = 0; want = set()
for p in body.split('\n\n'):
    m = re.match(r'\s*CHAPTER (\d+)', p)
    if m: ch = int(m.group(1)); continue
    unbal = p.count('“') != p.count('”')
    for mm in re.finditer(r'([”’"\']*)([⁰¹²³⁴⁵⁶⁷⁸⁹]+)', p):
        q = mm.group(1); n = int(''.join(INV[c] for c in mm.group(2)))
        if q not in ('', '”') or (unbal and q in ('', '”')):
            want.add((ch, n))
Q = pickle.load(open('/tmp/dub/annotated_fixed.pkl','rb'))
chap = pickle.load(open('/tmp/dub/chap.pkl','rb'))
M = pickle.load(open('/tmp/dub/merged.pkl','rb')); S = 1.1111
cells = []
for pi in range(21, 477):
    for li, l in enumerate(Q[pi]['lines']):
        for m in re.finditer(r'⟦(\d+)⟧', l['text']):
            key = (chap.get(pi), int(m.group(1)))
            if key in want:
                # locate x: count words before
                before = l['text'][:m.start()].split(' ')
                ml = M[pi]['lines'][li]; ws = ml['words']
                k = min(len([w for w in before if w]) - 1, len(ws) - 1)
                k = max(k, 0)
                cells.append((key, pi, li, ws[k][0], ws[k][2], l['text'][max(0, m.start()-25):m.end()]))
cells.sort(key=lambda c: c[1:3])
pickle.dump(cells, open('/tmp/dub/qcells.pkl', 'wb'))
CW, CH, COLS, ROWS = 660, 100, 3, 18; per = COLS * ROWS
for s in range(0, len(cells), per):
    sheet = np.full((ROWS * CH, COLS * CW), 255, np.uint8)
    for j, (key, pi, li, x0, x1, txt) in enumerate(cells[s:s+per]):
        im = cv2.imread(f'/tmp/dub/img/p-{pi:03d}.jpg', cv2.IMREAD_GRAYSCALE)
        l = M[pi]['lines'][li]
        crop = im[int(l['y0']*S) - 8:int(l['y1']*S) + 4, max(0, int(x0*S) - 200):int(x1*S) + 60]
        crop = cv2.resize(crop, None, fx=1.4, fy=1.4, interpolation=cv2.INTER_CUBIC)[:CH - 30, :CW - 10]
        r, c = divmod(j, COLS); oy, ox = r * CH, c * CW
        sheet[oy:oy + crop.shape[0], ox + 5:ox + 5 + crop.shape[1]] = crop
        lab = f"{s+j} c{key[0]}n{key[1]} | {txt}".encode('ascii', 'replace').decode()
        cv2.putText(sheet, lab, (ox + 5, oy + CH - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 0, 1, cv2.LINE_AA)
        cv2.line(sheet, (ox, oy + CH - 1), (ox + CW, oy + CH - 1), 160, 1); cv2.line(sheet, (ox + CW - 1, oy), (ox + CW - 1, oy + CH), 160, 1)
    cv2.imwrite(f'/tmp/dub/sheets/q{s // per:02d}.png', sheet)
print(len(want), len(cells))
