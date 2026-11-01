import pickle, numpy as np, cv2
from concurrent.futures import ProcessPoolExecutor
M = pickle.load(open('/tmp/dub/merged.pkl','rb')); S = 1.1111
def metrics(pi):
    im = cv2.imread(f'/tmp/dub/img/p-{pi:03d}.jpg', cv2.IMREAD_GRAYSCALE)
    _, bw = cv2.threshold(im, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    n, lab, st, cen = cv2.connectedComponentsWithStats(bw, 8)
    st = st[1:]; st = st[st[:,4] >= 6]
    cx = st[:,0] + st[:,2]/2; cy = st[:,1] + st[:,3]/2
    res = []
    for l in M[pi]['lines']:
        ya, yb = l['y0']*S, l['y1']*S; xa, xb = l['x0']*S, l['x1']*S
        sel = (cx >= xa) & (cx <= xb) & (cy >= ya - 4) & (cy <= yb + 2)
        cs = st[sel]
        if len(cs) < 8: res.append(None); continue
        bots = cs[:,1] + cs[:,3]; base = np.median(bots)
        onb = cs[np.abs(bots - base) <= 2]
        if len(onb) < 5: res.append(None); continue
        h = np.sort(onb[:,3])
        lo, hi = np.percentile(h, 15), np.percentile(h, 60)
        xs = h[(h >= lo) & (h <= hi)]
        xh = float(xs.mean()) if len(xs) else float(np.median(h))
        cap = float(np.percentile(h, 92))
        res.append((xh, cap, len(onb)))
    return pi, res
if __name__ == '__main__':
    with ProcessPoolExecutor(8) as ex:
        out = dict(ex.map(metrics, range(11, 480)))
    pickle.dump(out, open('/tmp/dub/fontm.pkl', 'wb'))
    import collections
    c = collections.Counter()
    for pi, r in out.items():
        for m in r:
            if m and m[2] >= 20: c[round(m[0] + m[1], 0)] += 1
    print(sorted(c.items()))
