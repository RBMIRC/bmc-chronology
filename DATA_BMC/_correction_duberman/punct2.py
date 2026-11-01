import pickle, numpy as np, cv2, re
M = pickle.load(open('/tmp/dub/merged.pkl','rb')); S = 1.1111
_cache = {}
def img(pi):
    if pi not in _cache:
        _cache.clear()
        im = cv2.imread(f'/tmp/dub/img/p-{pi:03d}.jpg', cv2.IMREAD_GRAYSCALE)
        _, bw = cv2.threshold(im, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        n, lab, st, cen = cv2.connectedComponentsWithStats(bw, 8)
        _cache[pi] = (im, bw, lab, st)
    return _cache[pi]
def feature(pi, li, wi):
    im, bw, lab, st = img(pi)
    l = M[pi]['lines'][li]; w = l['words'][wi]
    ya, yb = int(l['y0']*S) - 4, int(l['y1']*S) + 8
    wx0, wx1 = w[0]*S, w[2]*S
    nx = l['words'][wi+1][0]*S - 1 if wi + 1 < len(l['words']) else wx1 + 18
    # baseline: median bottom of letter components within the word
    sub = lab[ya:yb, int(wx0):int(min(nx, wx1 + 18))]
    ids = [i for i in np.unique(sub) if i]
    comps = [st[i] for i in ids]
    letters = [c for c in comps if c[3] >= 9]
    if not letters: return None
    base = np.median([c[1] + c[3] for c in letters])
    xh = np.median([c[3] for c in letters if c[3] < 18] or [13])
    lastx = max(c[0] + c[2] for c in letters if c[0] < wx1 - 2) if any(c[0] < wx1 - 2 for c in letters) else wx1 - 4
    # punctuation candidates: small comps right of last letter, bottom near/below baseline
    cand = [c for c in comps if c[0] >= lastx - 2 and c[3] < 0.9 * xh and c[1] + c[3] >= base - 3 and c[1] >= base - 0.6 * xh]
    if not cand: return None
    c = min(cand, key=lambda c: c[0])
    # grayscale sensitive bottom: scan columns of this comp, find lowest pixel darker than 170
    x0, y0, cw, ch = int(c[0]), int(c[1]), int(c[2]), int(c[3])
    region = im[y0:y0 + ch + 6, x0:x0 + cw]
    rows = np.where((region < 170).any(axis=1))[0]
    bottom = y0 + (rows.max() if len(rows) else ch - 1)
    desc = bottom - base
    return dict(desc=float(desc), h=ch, w=cw, xh=float(xh), ratio=ch / max(cw, 1))
