import re, pickle, sys, csv, difflib
sys.path.insert(0, '/tmp/dub')
from index2 import col_lines
entries = []   # dict(level, lines[list], src)
seq = []
for pi in range(585, 615):
    r, s = col_lines(pi)
    def good(l): return not (l['y'] < 75 and 'INDEX' in l['text']) and len(re.sub(r'\W', '', l['text'])) >= 1
    c1 = [l for l in r[0] if good(l)]; c2 = [l for l in r[1] if good(l)]
    def clus(ls):
        xs = sorted(l['x0'] for l in ls if len(l['text']) > 3)
        for x in xs:
            if sum(1 for y in xs if x <= y <= x + 6) >= 3: return x
        return xs[0]
    a = clus(c1); b = clus(c2)
    M1 = min(a, b - 387); M2 = M1 + 387
    for c, lines, Mx in ((0, c1, M1), (1, c2, M2)):
        for li, l in enumerate(lines):
            d = l['x0'] - Mx
            lev = 0 if d < 14 else (1 if d < 38 else 2)
            seq.append(dict(pi=pi, col=c, li=li, d=round(d), lev=lev, text=l['text']))
pickle.dump(seq, open('/tmp/dub/index_seq.pkl', 'wb'))
import collections
print(collections.Counter(s['lev'] for s in seq))
print(sorted(collections.Counter(s['d'] for s in seq).items())[:80])
