import json, re, numpy as np, pickle
P = json.load(open('/tmp/dub/pages.json'))
def page_split(pi):
    p = P[pi]; W = int(p['W'])
    cov = np.zeros(W + 1)
    for f in p['lines']:
        for w in f['words']:
            cov[int(w[0]):int(w[2]) + 1] += 1
    lo, hi = int(W * 0.33), int(W * 0.66)
    seg = cov[lo:hi]
    # choose center of the longest run of minimal coverage
    m = seg.min()
    best, cur, bs = 0, 0, 0
    for i, v in enumerate(seg):
        if v <= m + 1: cur += 1
        else: cur = 0
        if cur > best: best, bs = cur, i - cur + 1
    return lo + bs + best / 2
def col_lines(pi):
    p = P[pi]; split = page_split(pi)
    cols = {0: [], 1: []}
    for f in p['lines']:
        for w in f['words']:
            cols[0 if (w[0] + w[2]) / 2 < split else 1].append(w)
    res = {}
    for c, ws in cols.items():
        ws.sort(key=lambda w: (w[1] + w[3]) / 2)
        rows = []
        for w in ws:
            yc = (w[1] + w[3]) / 2
            if rows and abs(rows[-1]['yc'] - yc) < 9: rows[-1]['w'].append(w); continue
            rows.append(dict(yc=yc, w=[w]))
        res[c] = [dict(x0=min(w[0] for w in r['w']), y=r['yc'], text=' '.join(w[4] for w in sorted(r['w'], key=lambda w: w[0]))) for r in rows]
    return res, split
if __name__ == '__main__':
    for pi in range(585, 615):
        r, s = col_lines(pi)
        a = sorted(l['x0'] for l in r[0] if 'INDEX' not in l['text']); b = sorted(l['x0'] for l in r[1] if 'INDEX' not in l['text'])
        print(pi, round(s), round(a[1]), round(b[1]), round(b[1] - a[1]))
