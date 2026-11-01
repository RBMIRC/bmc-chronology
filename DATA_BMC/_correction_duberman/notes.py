import pickle, re, statistics, numpy as np, cv2, collections
M = pickle.load(open('/tmp/dub/merged.pkl','rb')); S = 1.1111
def ink_left(pi, lines):
    im = cv2.imread(f'/tmp/dub/img/p-{pi:03d}.jpg', cv2.IMREAD_GRAYSCALE)
    _, bw = cv2.threshold(im, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    n, lab, st, cen = cv2.connectedComponentsWithStats(bw, 8)
    st = st[1:]; st = st[(st[:,4] >= 12) & (st[:,3] >= 11)]
    cy = st[:,1] + st[:,3]/2
    out = []
    for l in lines:
        ya, yb = l['y0']*S, l['y1']*S
        sel = st[(cy >= ya + 2) & (cy <= yb - 1) & (st[:,0] >= l['x0']*S - 80) & (st[:,0] <= l['x1']*S)]
        if len(sel) == 0: out.append(l['x0']*S); continue
        out.append(float(sel[:,0].min()))
    return out
NOTES = range(483, 583)
items = []   # (kind, text, page) kind: chap / start / cont / para
for pi in NOTES:
    L = M[pi]['lines']
    if not L: continue
    start = 0
    if re.search(r'Pages?\s+\d|^\d{3}\s|\s\d{3}$', L[0]['text']) and L[0]['y0'] < 80: start = 1
    lines = L[start:]
    xs = ink_left(pi, lines)
    cont = [x for x, l in zip(xs, lines) if not l['text'].startswith('CHAPTER')]
    # hanging indent = most common ink-left (rounded)
    c = collections.Counter(round(x / 4) * 4 for x in cont)
    H = c.most_common(1)[0][0]
    for x, l in zip(xs, lines):
        t = l['text']
        if re.match(r'^CHAPTER\s+\d+', t): items.append(('chap', t, pi)); continue
        d = x - H
        if d < -10: items.append(('start', t, pi, d))
        elif d > 14: items.append(('para', t, pi, d))
        else: items.append(('cont', t, pi, d))
pickle.dump(items, open('/tmp/dub/notes_items.pkl','wb'))
# count per chapter
cnt = collections.Counter(); ch = None
for it in items:
    if it[0] == 'chap': ch = int(re.match(r'CHAPTER\s+(\d+)', it[1]).group(1))
    elif it[0] == 'start': cnt[ch] += 1
print(sorted(cnt.items()))
# save H per page
HS = {}
for pi in NOTES:
    L = M[pi]['lines']
    if not L: continue
    start = 1 if (re.search(r'Pages?\s+\d|^\d{3}\s|\s\d{3}$', L[0]['text']) and L[0]['y0'] < 80) else 0
    lines = L[start:]
    xs = ink_left(pi, lines)
    cont = [x for x, l in zip(xs, lines) if not l['text'].startswith('CHAPTER')]
    HS[pi] = collections.Counter(round(x / 4) * 4 for x in cont).most_common(1)[0][0]
pickle.dump(HS, open('/tmp/dub/notes_H.pkl', 'wb'))
