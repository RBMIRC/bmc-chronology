import pickle, cv2, numpy as np, sys
P = pickle.load(open('/tmp/dub/merged.pkl','rb')); S = 1.1111
gaps = pickle.load(open('/tmp/dub/gaps.pkl','rb'))
def strip(pi, la, lb):
    L = P[pi]['lines']; lb = min(lb, len(L)-1)
    im = cv2.imread(f'/tmp/dub/img/p-{pi:03d}.jpg')
    y0 = int(L[la]['y0']*S) - 8; y1 = int(L[lb]['y1']*S) + 6
    return im[max(0,y0):y1]
for gi in map(int, sys.argv[1:]):
    c, n, a, b = gaps[gi]
    if a is None: a = (b[0], 0)
    parts = []
    for pi in range(a[0], b[0]+1):
        la = a[1] if pi == a[0] else 0
        lb = b[1] if pi == b[0] else 999
        parts.append(strip(pi, la, lb))
    w = max(p.shape[1] for p in parts)
    parts = [np.pad(p, ((0,4),(0,w-p.shape[1]),(0,0)), constant_values=0) for p in parts]
    im = np.vstack(parts)
    if im.shape[0] > 1900: im = cv2.resize(im, None, fx=0.85, fy=0.85, interpolation=cv2.INTER_AREA)
    cv2.imwrite(f'/tmp/dub/reg/gap{gi}.png', im)
    print(gi, im.shape)
