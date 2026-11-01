import pickle, numpy as np, cv2, statistics
P = pickle.load(open('/tmp/dub/merged.pkl','rb'))
S = 1.1111
def comps_for(pi):
    im = cv2.imread(f'/tmp/dub/img/p-{pi:03d}.jpg', cv2.IMREAD_GRAYSCALE)
    _, bw = cv2.threshold(im, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    n, lab, st, cen = cv2.connectedComponentsWithStats(bw, 8)
    return im, [tuple(int(v) for v in st[k]) for k in range(1, n) if st[k,4] >= 3]
def markers(pi):
    im, comps = comps_for(pi)
    out = []
    for li, l in enumerate(P[pi]['lines']):
        ya, yb = l['y0']*S, l['y1']*S
        xa, xb = l['x0']*S - 5, l['x1']*S + 30
        cs = [c for c in comps if xa <= c[0] + c[2]/2 <= xb and ya - 6 <= c[1] + c[3]/2 <= yb]
        big = [c for c in cs if c[3] >= 6]
        if len(big) < 5: continue
        base = statistics.median([c[1]+c[3] for c in big])
        cap = float(np.percentile([base - c[1] for c in big if c[1]+c[3] <= base + 2], 90))
        raised = [c for c in cs if c[1]+c[3] < base - 0.33*cap and c[1] >= base - 1.3*cap and c[3] <= 0.9*cap and c[3] >= 0.3*cap]
        strong = [c for c in raised if c[3] >= 0.52*cap]
        if not strong: continue
        raised.sort(key=lambda c: c[0])
        # group raised comps by adjacency
        groups = []
        for c in raised:
            if groups and c[0] - groups[-1]['x1'] <= 9:
                g = groups[-1]; g['x1'] = max(g['x1'], c[0]+c[2]); g['y0'] = min(g['y0'], c[1]); g['y1'] = max(g['y1'], c[1]+c[3]); g['c'].append(c)
            else:
                groups.append(dict(x0=c[0], x1=c[0]+c[2], y0=c[1], y1=c[1]+c[3], c=[c]))
        for g in groups:
            if any(c[3] >= 0.52*cap for c in g['c']):
                out.append(dict(li=li, x0=g['x0'], x1=g['x1'], y0=g['y0'], y1=g['y1'], base=base, cap=cap, n=len(g['c'])))
    return out
