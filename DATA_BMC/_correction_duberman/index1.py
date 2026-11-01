import json, statistics, re, pickle
P = json.load(open('/tmp/dub/pages.json'))
def col_lines(pi):
    p = P[pi]; W = p['W']
    frags = [f for f in p['lines']]
    # header removal: top line with INDEX
    out = {0: [], 1: []}
    xs = sorted(f['x0'] for f in frags)
    # split: biggest gap in x0 distribution between 0.3W and 0.6W
    cand = [x for x in xs if 0.3*W < x < 0.65*W]
    split = W * 0.47
    for f in frags:
        c = 0 if f['x0'] < split else 1
        out[c].append(f)
    res = {}
    for c, fs in out.items():
        fs.sort(key=lambda f: (f['y0'] + f['y1'])/2)
        rows = []
        for f in fs:
            yc = (f['y0'] + f['y1'])/2
            if rows and abs(rows[-1]['yc'] - yc) < 9: rows[-1]['f'].append(f); continue
            rows.append(dict(yc=yc, f=[f]))
        lines = []
        for r in rows:
            r['f'].sort(key=lambda f: f['x0'])
            lines.append(dict(x0=r['f'][0]['x0'], y=r['yc'], text=' '.join(f['text'] for f in r['f'])))
        res[c] = lines
    return res
if __name__ == '__main__':
    diffs = []
    for pi in range(585, 615):
        r = col_lines(pi)
        l1 = [l for l in r[0] if not re.search(r'INDEX', l['text'])]; l2 = [l for l in r[1] if not re.search(r'INDEX', l['text'])]
        a = sorted(l['x0'] for l in l1); b = sorted(l['x0'] for l in l2)
        if a and b: diffs.append((pi, round(a[2],1), round(b[2],1), round(b[2]-a[2],1)))
    for d in diffs: print(d)
