import pickle, numpy as np, cv2, statistics, re
from concurrent.futures import ProcessPoolExecutor
M = pickle.load(open('/tmp/dub/merged.pkl','rb')); S = 1.1111
def run(pi):
    im = cv2.imread(f'/tmp/dub/img/p-{pi:03d}.jpg', cv2.IMREAD_GRAYSCALE)
    _, bw = cv2.threshold(im, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    n, lab, st, cen = cv2.connectedComponentsWithStats(bw, 8)
    st = st[1:]
    st = st[st[:,4] >= 3]
    cx = st[:,0] + st[:,2]/2; cy = st[:,1] + st[:,3]/2
    out = []
    for li, l in enumerate(M[pi]['lines']):
        ya, yb = l['y0']*S, l['y1']*S
        sel = (cy >= ya - 4) & (cy <= yb + 8) & (cx >= l['x0']*S - 3) & (cx <= l['x1']*S + 3)
        cs = st[sel]
        big = cs[cs[:,3] >= 8]
        if len(big) < 5: continue
        base = np.median(big[:,1] + big[:,3])
        xh = np.percentile(big[:,3], 30)
        for wi, w in enumerate(l['words']):
            t = w[4]
            m = re.search(r'[A-Za-z0-9)\]”’]([.,])([”’)\]]*)$', t)
            if not m: continue
            # candidate glyphs inside word box right part, small
            wx0, wx1 = w[0]*S, w[2]*S
            nx = l['words'][wi+1][0]*S - 2 if wi + 1 < len(l['words']) else wx1 + 16
            c = cs[(cs[:,0] + cs[:,2]/2 >= wx0) & (cs[:,0] + cs[:,2]/2 <= min(nx, wx1 + 16))]
            small = c[(c[:,3] <= 0.95 * xh) & (c[:,2] <= 0.6 * xh) & (c[:,1] + c[:,3] >= base - 0.35 * xh)]
            if len(small) == 0: out.append((pi, li, wi, t, None)); continue
            # rightmost small near-baseline glyph (punctuation before closing quotes)
            g = small[np.argmax(small[:,0])]
            if m.group(2):
                # closing quote/paren after: pick the small low glyph that is lowest-right but before quote glyphs (quotes are high)
                g = small[np.argmax(small[:,0])]
            desc = (g[1] + g[3]) - base
            ratio = g[3] / max(g[2], 1)
            kind = ',' if (desc >= 0.18 * xh or ratio >= 1.45) else '.'
            out.append((pi, li, wi, t, (kind, round(float(desc),1), round(float(ratio),2), float(xh))))
    return out
if __name__ == '__main__':
    pages = list(range(11, 16)) + list(range(17, 20)) + list(range(21, 615))
    res = []
    with ProcessPoolExecutor(8) as ex:
        for r in ex.map(run, pages): res += r
    pickle.dump(res, open('/tmp/dub/punct.pkl', 'wb'))
    import collections
    c = collections.Counter()
    for pi, li, wi, t, g in res:
        o = re.search(r'([.,])[”’)\]]*$', t).group(1)
        c[(o, g[0] if g else None)] += 1
    print(c)
