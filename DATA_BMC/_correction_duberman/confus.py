import re, collections, sys
from wordfreq import zipf_frequency as zf
txt = open(sys.argv[1]).read()
cnt = collections.Counter(re.findall(r"[A-Za-zÀ-ÿ]+", txt))
pairs = [('y','v'),('v','y'),('c','e'),('e','c'),('t','r'),('r','t'),('rn','m'),('m','rn'),('li','h'),('h','li'),('cl','d'),('a','o'),('o','a'),('n','u'),('u','n'),('f','t'),('t','f'),('l','I'),('I','l'),('J','I'),('T','I'),('ii','u'),('é','e'),('è','e'),('í','i'),('ó','o'),('ö','o'),('i','l'),('l','i'),('s','g'),('g','s'),('a','e'),('e','a'),('o','e'),('e','o'),('b','h'),('h','b'),('k','h'),('h','k'),('n','m'),('m','n'),('i','t'),('fl','f'),('d','cl'),('j','i'),('q','g'),('z','t')]
out = []
for w, c in cnt.items():
    lw = w.lower()
    z0 = zf(lw, 'en')
    best = None
    for a, b in pairs:
        for m in re.finditer(re.escape(a), w):
            v = w[:m.start()] + b + w[m.end():]
            z = zf(v.lower(), 'en')
            if z - z0 >= 2.0 and z >= 3.0 and (best is None or z > best[1]):
                best = (v, z)
    if best and len(w) > 2:
        out.append((c, w, best[0], round(z0,1), round(best[1],1)))
out.sort(key=lambda x: x[3])
for o in out: print(*o)
