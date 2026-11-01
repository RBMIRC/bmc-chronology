import pickle, re
P = pickle.load(open('/tmp/dub/merged.pkl','rb'))
gaps = pickle.load(open('/tmp/dub/gaps.pkl','rb'))
allm = pickle.load(open('/tmp/dub/markers2.pkl','rb'))
S = 1.1111
pat = re.compile(r'[.,;:!?”’"\')\]]([0-9?°*®¢§%&\^™•¹²³\'’”"]*[0-9?°*®¢§%&\^™•¹²³][0-9?°*®¢§%&\^™•¹²³\'’”"]*)$')
for gi, (c, n, a, b) in enumerate(gaps):
    if a is None: a = (b[0], 0)
    cands = []
    for pi in range(a[0], b[0] + 1):
        L = P[pi]['lines']
        lf = a[1] if pi == a[0] else 1
        lt = b[1] if pi == b[0] else len(L) - 1
        for li in range(lf, lt + 1):
            for w in L[li]['text'].split():
                if pat.search(w) and not re.match(r'^[\d$,.\-–:]+$', w):
                    # skip if this line already has a detected marker at end of this word? keep simple
                    cands.append((pi, li, w))
    # remove candidates at the bounding markers themselves
    cands = [x for x in cands if not ((x[0], x[1]) == tuple(a) or (x[0], x[1]) == tuple(b))]
    print(gi, f'ch{c} #{n}', a, b, cands)
