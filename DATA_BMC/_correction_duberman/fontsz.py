import pickle, numpy as np, cv2, statistics
M = pickle.load(open('/tmp/dub/merged.pkl','rb')); S = 1.1111
def line_metrics(pi):
    im = cv2.imread(f'/tmp/dub/img/p-{pi:03d}.jpg', cv2.IMREAD_GRAYSCALE)
    _, bw = cv2.threshold(im, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    n, lab, st, cen = cv2.connectedComponentsWithStats(bw, 8)
    st = st[1:]
    st = st[st[:,4] >= 6]
    cx = st[:,0] + st[:,2]/2; cy = st[:,1] + st[:,3]/2
    res = []
    for l in M[pi]['lines']:
        ya, yb = l['y0']*S, l['y1']*S; xa, xb = l['x0']*S, l['x1']*S
        sel = (cx >= xa) & (cx <= xb) & (cy >= ya - 4) & (cy <= yb + 2)
        cs = st[sel]
        if len(cs) < 8: res.append(None); continue
        hs = cs[:,3]; bots = cs[:,1] + cs[:,3]
        base = np.median(bots)
        onb = cs[np.abs(bots - base) <= 2]
        if len(onb) < 5: res.append(None); continue
        h = onb[:,3]
        # x-height: mode of heights of small letters -> use 30th percentile of on-baseline heights
        xh = np.percentile(h, 35)
        cap = np.percentile(h, 92)
        res.append((round(float(xh),1), round(float(cap),1)))
    return res
if __name__ == '__main__':
    import sys
    for pi in map(int, sys.argv[1:]):
        r = line_metrics(pi)
        for l, m in list(zip(M[pi]['lines'], r))[1:30]:
            print(m, l['text'][:50])
