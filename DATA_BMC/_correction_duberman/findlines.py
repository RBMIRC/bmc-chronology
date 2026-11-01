import pickle, re, sys
M = pickle.load(open('/tmp/dub/merged.pkl','rb'))
def find(key):
    pat = re.compile(r'\s+'.join(re.escape(w) for w in key.split()))
    res = []
    for pi in range(len(M)):
        L = M[pi]['lines']
        txt = ''; starts = []
        for l in L: starts.append(len(txt)); txt += l['text'] + '\n'
        for m in pat.finditer(txt):
            li = max(i for i, s in enumerate(starts) if s <= m.start())
            res.append(f'{pi}:{li}')
    return res
if __name__ == '__main__':
    out = []
    for k in sys.argv[1:]:
        r = find(k); print(k, r); out += r[:1]
    print(' '.join(out))
