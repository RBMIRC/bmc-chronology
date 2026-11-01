import pickle, numpy as np, cv2, statistics, sys
P = pickle.load(open('/tmp/dub/merged.pkl','rb'))
S = 1.1111
def detect(pi, debug=False):
    """pi: 0-based pdf page index. returns list of (line_idx, x_img, y_img, w, h, word_idx_in_line)"""
    im = cv2.imread(f'/tmp/dub/img/p-{pi:03d}.jpg', cv2.IMREAD_GRAYSCALE)
    _, bw = cv2.threshold(im, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    n, lab, st, cen = cv2.connectedComponentsWithStats(bw, 8)
    comps = [(st[k,0], st[k,1], st[k,2], st[k,3], st[k,4]) for k in range(1, n) if st[k,4] >= 3]
    lines = P[pi]['lines']
    res = []
    for li, l in enumerate(lines):
        ya, yb = l['y0']*S, l['y1']*S
        xa, xb = l['x0']*S - 5, l['x1']*S + 30
        cs = [c for c in comps if xa <= c[0] + c[2]/2 <= xb and ya - 6 <= c[1] + c[3]/2 <= yb]
        big = [c for c in cs if c[3] >= 6]
        if len(big) < 5: continue
        base = statistics.median([c[1]+c[3] for c in big])
        cap = np.percentile([base - c[1] for c in big if c[1]+c[3] <= base + 2], 90)
        xh = statistics.median([c[3] for c in big if c[1]+c[3] <= base+2 and c[3] < 0.8*cap] or [cap*0.65])
        for c in cs:
            x, y, w, h, a = c
            bot = y + h
            if bot < base - 0.33*cap and h >= 0.42*cap and h <= 0.9*cap and y >= base - 1.25*cap:
                res.append((li, x, y, w, h, round(base,1), round(cap,1)))
    return res
if __name__ == '__main__':
    for pg in map(int, sys.argv[1:]):
        r = detect(pg-1)
        L = P[pg-1]['lines']
        for li, x, y, w, h, b, cap in r:
            # find word whose image x1 near x
            print(pg, li, x, y, w, h, 'cap', cap, '|', L[li]['text'][-50:])

def markers(pi):
    """grouped superscript markers: list of (li, x0, x1, y0, y1)"""
    raw = [r for r in detect(pi) if r[4] >= 0.52*r[6]]
    raw.sort(key=lambda r: (r[0], r[1]))
    groups = []
    for li, x, y, w, h, b, cap in raw:
        if groups and groups[-1][0] == li and x - groups[-1][2] <= 6:
            g = groups[-1]; groups[-1] = (li, g[1], max(g[2], x+w), min(g[3], y), max(g[4], y+h))
        else:
            groups.append((li, x, x+w, y, y+h))
    return groups
