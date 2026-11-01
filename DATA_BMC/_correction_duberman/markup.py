"""Apply footnote markers to merged page lines -> annotated.pkl (pages: list of lines with 'text')."""
import pickle, re, copy
P = pickle.load(open('/tmp/dub/merged.pkl','rb'))
idx = pickle.load(open('/tmp/dub/sheet_index.pkl','rb'))
allm = pickle.load(open('/tmp/dub/markers2.pkl','rb'))
vals, seq, missing = pickle.load(open('/tmp/dub/assign.pkl','rb'))
chap = pickle.load(open('/tmp/dub/chap.pkl','rb'))
S = 1.1111
G = set('0123456789?°*®¢§%&^™•¹²³#+>')
SUP = str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹')
def mk(n): return '⟦' + str(n) + '⟧'
def clean_word(w):
    """split trailing OCR garbage of a superscript off a word"""
    k = len(w)
    while k > 0 and w[k-1] in G: k -= 1
    body, suf = w[:k], w[k:]
    if suf.startswith('?') and body and body[-1].isalpha() and len(suf) > 1:
        body, suf = body + '?', suf[1:]
    if suf.endswith('t') : pass
    return body, suf
Q = copy.deepcopy(P)
log = []
for j, (pi, k) in enumerate(idx):
    v = vals[j]
    if v is None: continue
    m = allm[pi][k]
    line = Q[pi]['lines'][m['li']]
    ws = line['words']
    # candidate words starting left of marker
    cands = [i for i, w in enumerate(ws) if w[0]*S < m['x0'] + 1]
    if not cands: log.append(('NOWORD', pi, m['li'], v)); continue
    i = max(cands, key=lambda i: ws[i][0])
    w = ws[i][4]
    if ws[i][2]*S >= m['x0'] + 2:  # marker glyphs inside OCR word
        body, suf = clean_word(w)
        if body == '' or re.fullmatch(r'[.,;:!?”’"\')\]]+', body or ''):
            # standalone garbage token -> glue to previous word
            if i > 0:
                ws[i-1][4] = ws[i-1][4] + body + mk(v); ws[i][4] = ''
            else:
                ws[i][4] = body + mk(v)
        else:
            ws[i][4] = body + mk(v)
        if suf == '' : log.append(('NOSUF', pi, m['li'], v, w))
    else:
        ws[i][4] = w + mk(v)
    line['text'] = ' '.join(x[4] for x in ws if x[4] != '')
# extras
for l in open('/tmp/dub/extras.txt'):
    if not l[0].isdigit(): continue
    c, n, pi, rest = l.rstrip('\n').split(' ', 3)
    n, pi = int(n), int(pi)
    old, new = rest.split('|')
    old = old.replace('\\n', '\n'); new = new.replace('\\n', '\n').replace('^', mk(n))
    L = Q[pi]['lines']
    full = '\n'.join(x['text'] for x in L)
    cnt = full.count(old)
    if cnt != 1:
        log.append(('EXTRA_NOT_UNIQUE', c, n, pi, old, cnt)); continue
    full = full.replace(old, new)
    parts = full.split('\n')
    assert len(parts) == len(L)
    for x, t in zip(L, parts): x['text'] = t
pickle.dump(Q, open('/tmp/dub/annotated.pkl', 'wb'))
for e in log: print(e)
# verify sequence per chapter
import collections
found = collections.defaultdict(list)
for pi in range(len(Q)):
    for x in Q[pi]['lines']:
        for n in re.findall(r'⟦(\d+)⟧', x['text']):
            found[chap.get(pi)].append(int(n))
for c in sorted(k for k in found if k):
    s = found[c]
    ok = s == list(range(1, len(s)+1))
    print(c, len(s), 'OK' if ok else [ (a,b) for a,b in zip(s, s[1:]) if b != a+1 ])
print('None:', found.get(None))
