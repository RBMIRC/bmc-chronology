import pickle, sys, cv2, numpy as np
Q = pickle.load(open('/tmp/dub/annotated_fixed.pkl','rb'))
M = pickle.load(open('/tmp/dub/merged.pkl','rb'))
S = 1.1111
def find(w, maxn=2):
    res = []
    for pi in range(len(Q)):
        for li, l in enumerate(Q[pi]['lines']):
            if w in l['text']: res.append((pi, li))
            if len(res) >= maxn: return res
    return res
words = sys.argv[2:]
out = sys.argv[1]
cells = []
for w in words:
    for pi, li in find(w):
        l = M[pi]['lines'][li]
        im = cv2.imread(f'/tmp/dub/img/p-{pi:03d}.jpg', cv2.IMREAD_GRAYSCALE)
        c = im[int(l['y0']*S)-6:int(l['y1']*S)+6, max(0,int(l['x0']*S)-5):int(l['x1']*S)+30]
        lab = np.full((24, c.shape[1]), 255, np.uint8)
        cv2.putText(lab, f'{w.encode("ascii","replace").decode()}  p{pi} l{li}', (4, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.55, 0, 1)
        cells.append(np.vstack([lab, c]))
W = max(c.shape[1] for c in cells)
cells = [np.pad(c, ((0, 4), (0, W - c.shape[1])), constant_values=200) for c in cells]
cv2.imwrite(out, np.vstack(cells))
