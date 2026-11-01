import pickle, re, collections, sys, numpy as np, cv2
sys.path.insert(0, '/tmp/dub')
M = pickle.load(open('/tmp/dub/merged.pkl','rb')); S = 1.1111
HS = pickle.load(open('/tmp/dub/notes_H.pkl','rb'))
for _pi, _li, _wi, _t in pickle.load(open('/tmp/dub/pfix.pkl','rb')):
    if _pi < 483 or _pi > 582: continue
    _w = M[_pi]['lines'][_li]['words'][_wi]
    if _w[4] == _t:
        _w[4] = re.sub(r',([”’)\]]*)$', r'.\1', _t)
        M[_pi]['lines'][_li]['text'] = ' '.join(w[4] for w in M[_pi]['lines'][_li]['words'])
items_n = pickle.load(open('/tmp/dub/titems_n.pkl','rb'))
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
        gw = [w for w in l['words'] if re.search(r'[A-Za-z0-9“‘"(\[]', w[4])]
        ox = (gw[0][0] if gw else l['x0']) * S
        out.append(min(float(sel[:,0].min()), ox + 2) if len(sel) else ox)
    return out
# decisions: (pi, li) -> list of (old, new)
DEC = collections.defaultdict(list)
for line in open('/tmp/dub/tdec_n.txt'):
    line = line.rstrip('\n')
    if not line: continue
    idx, rest = line.split(' ', 1)
    it = items_n[int(idx)]
    a, b = rest[1:].split('=>')
    DEC[(it['pi'], it['li'])].append((a, b))
TABLE1 = """                    1933       1936       1939
    Northeast       15–68%     39–73%     42–58%
    South           5–23%      7–13%      9–12%
    Middle West     2–9%       3–6%       10–14%
    West            0          3–6%       8–11%
    Foreign         0          1–2%       4–5%"""
TABLE2 = """                    Indifferent   Unfavorable   Favorable   Highly Favorable
    Students
      Female        1             2             11          15
      Male          2             9             11          16
    Faculty
      Female        1             0             6           1
      Male          3             2             6           4
                                                (Courtesy Forbes)"""
TABLES = {(501, 12): (17, TABLE1), (517, 17): (25, TABLE2)}
SKIPLINES = {(571, 35)}   # OCR junk ("eto")
seq = []   # entries: ('chap', n, title) / ('start'|'cont'|'para'|'table', text)
for pi in range(483, 583):
    L = M[pi]['lines']
    if not L: continue
    start = 1 if (re.search(r'Pages?\s+\d|^\d{3}\s|\s\d{3}$', L[0]['text']) and L[0]['y0'] < 80) else 0
    lines = L[start:]
    xs = ink_left(pi, lines)
    H = HS[pi]
    skip_until = -1
    for k, (x, l) in enumerate(zip(xs, lines)):
        li = k + start
        if li <= skip_until or (pi, li) in SKIPLINES: continue
        if (pi, li) in TABLES:
            end, tab = TABLES[(pi, li)]
            seq.append(('table', tab)); skip_until = end; continue
        t = re.sub(r'^[_;:~·•]+\s+', '', l['text'])
        m = re.match(r'^CHAPTER\s+(\d+):\s*(.*)$', t)
        if m: seq.append(('chap', int(m.group(1)), m.group(2).strip())); continue
        d = x - H
        kind = 'start' if d < -15 else ('para' if d > 14 else 'cont')
        if kind == 'start':
            ws = [w for w in l['words'] if not (w[2] * S < H - 3)]
            t = ' '.join(w[4] for w in ws)
        if kind != 'start' and re.match(r'^[.,](?: [.,])?\s+(?=[\w“‘\[(])', t) and not t.startswith('. . .'):
            t = re.sub(r'^[.,](?: [.,])?\s+', '. . . ', t)
        for a, b in DEC.get((pi, li), []):
            if a in t: t = t.replace(a, b, 1)
            else: print('DEC MISS', pi, li, repr(a), repr(t))
        seq.append((kind, t))
pickle.dump(seq, open('/tmp/dub/notes_seq.pkl', 'wb'))
# assemble notes
notes = []   # (chap, n, [paragraph lists])
cur = None; ch = None; title = None; chapters = []; n = 0
for e in seq:
    if e[0] == 'chap':
        ch = e[1]; n = 0; chapters.append((ch, e[2])); cur = None; continue
    if e[0] == 'start':
        n += 1; cur = dict(ch=ch, n=n, paras=[[e[1]]]); notes.append(cur)
    elif e[0] == 'para':
        cur['paras'].append([e[1]])
    elif e[0] == 'table':
        cur['paras'].append(['\x00TABLE' + e[1]]); cur['paras'].append([])
    else:
        if cur['paras'][-1] == []: cur['paras'][-1].append(e[1])
        else: cur['paras'][-1].append(e[1])
pickle.dump((chapters, notes), open('/tmp/dub/notes_struct.pkl', 'wb'))
cnt = collections.Counter(x['ch'] for x in notes)
print(sorted(cnt.items()))
