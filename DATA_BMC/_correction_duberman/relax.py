import pickle, numpy as np, cv2, statistics
from sup2 import comps_for, P, S
gaps = pickle.load(open('/tmp/dub/gaps.pkl','rb'))
def relaxed(pi, li_from, li_to):
    im, comps = comps_for(pi)
    out = []
    for li, l in enumerate(P[pi]['lines']):
        if li < li_from or li > li_to: continue
        ya, yb = l['y0']*S, l['y1']*S
        xa, xb = l['x0']*S - 5, l['x1']*S + 40
        cs = [c for c in comps if xa <= c[0] + c[2]/2 <= xb and ya - 10 <= c[1] + c[3]/2 <= yb]
        big = [c for c in cs if c[3] >= 6]
        if len(big) < 5: continue
        base = statistics.median([c[1]+c[3] for c in big])
        cap = float(np.percentile([base - c[1] for c in big if c[1]+c[3] <= base + 2], 90))
        raised = sorted([c for c in cs if c[1]+c[3] < base - 0.2*cap and c[1] >= base - 1.5*cap and c[3] >= 0.3*cap and c[3] <= cap], key=lambda c: c[0])
        groups = []
        for c in raised:
            if groups and c[0] - groups[-1][1] <= 9:
                g = groups[-1]; groups[-1] = [g[0], max(g[1], c[0]+c[2]), g[2] + [c]]
            else: groups.append([c[0], c[0]+c[2], [c]])
        for g in groups:
            hs = [c[3] for c in g[2]]
            if max(hs) < 0.5*cap and all(c[2] <= 6 for c in g[2]) : continue  # quotes
            out.append((li, g[0], g[1], base, cap))
    return out, im
SC=3; CW, CH = 330, 90; COLS = 6
cells = []
for gi, (c, n, a, b) in enumerate(gaps):
    pages = []
    if a is None: a = (b[0], 0)
    for pi in range(a[0], b[0] + 1):
        lf = a[1] if pi == a[0] else 0
        lt = b[1] if pi == b[0] else 999
        cand, im = relaxed(pi, lf, lt)
        for (li, x0, x1, base, cap) in cand:
            # skip already-detected markers
            if any(m['li'] == li and abs(m['x0'] - x0) < 6 for m in pickle.load(open('/tmp/dub/markers2.pkl','rb'))[pi]): continue
            crop = im[int(base-1.6*cap):int(base+0.35*cap), max(0, x0-45):x1+14]
            cells.append((f'{gi}', pi, li, x0, x1, cv2.resize(crop, None, fx=SC, fy=SC, interpolation=cv2.INTER_CUBIC)))
rows = (len(cells) + COLS - 1)//COLS
sheet = np.full((rows*CH, COLS*CW), 255, np.uint8)
for j, (lab, pi, li, x0, x1, cr) in enumerate(cells):
    r, cc = divmod(j, COLS); oy, ox = r*CH, cc*CW
    cr = cr[:CH-4, :CW-70]
    sheet[oy:oy+cr.shape[0], ox+66:ox+66+cr.shape[1]] = cr
    cv2.putText(sheet, f'{j}', (ox+2, oy+30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 0, 2)
    cv2.putText(sheet, f'g{lab}', (ox+2, oy+60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 0, 1)
    cv2.line(sheet, (ox, oy+CH-1), (ox+CW, oy+CH-1), 180, 1)
cv2.imwrite('/tmp/dub/sheets/relax.png', sheet)
pickle.dump([(lab, pi, li, x0, x1) for lab, pi, li, x0, x1, _ in cells], open('/tmp/dub/relax_cells.pkl', 'wb'))
print(len(cells), len(gaps))
