import pickle
vals, seq, missing = pickle.load(open('/tmp/dub/assign.pkl','rb'))
allm = pickle.load(open('/tmp/dub/markers2.pkl','rb'))
gaps = []
for c, miss in missing.items():
    s = seq[c]
    for n in miss:
        prev = max([x for x in s if x[0] < n], default=None, key=lambda x: x[0])
        nxt = min([x for x in s if x[0] > n], default=None, key=lambda x: x[0])
        a = (prev[1], allm[prev[1]][prev[2]]['li']) if prev else None
        b = (nxt[1], allm[nxt[1]][nxt[2]]['li']) if nxt else None
        gaps.append((c, n, a, b))
pickle.dump(gaps, open('/tmp/dub/gaps.pkl','wb'))
for g in gaps: print(g)
