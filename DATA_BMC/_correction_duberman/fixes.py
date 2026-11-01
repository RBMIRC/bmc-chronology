import pickle, re
Q = pickle.load(open('/tmp/dub/annotated.pkl','rb'))
items = pickle.load(open('/tmp/dub/titems.pkl','rb'))
MK = re.compile(r'⟦\d+⟧')
todo, fails = [], []
for line in open('/tmp/dub/tdec.txt'):
    line = line.rstrip('\n')
    if not line.strip(): continue
    idx, dec = line.split(' ', 1) if ' ' in line else (line, '')
    it = items[int(idx)]
    todo.append((int(idx), it, dec))
def replace_tokens(pi, li, A, new):
    for L in ([li], [li, li+1], [li-1, li]):
        if min(L) < 0 or max(L) >= len(Q[pi]['lines']): continue
        toks = []
        for l in L: toks += [(l, t) for t in Q[pi]['lines'][l]['text'].split(' ')]
        plain = [MK.sub('', t) for _, t in toks]
        At = A.split(' ')
        for s in range(len(plain) - len(At) + 1):
            if plain[s:s+len(At)] == At:
                marks = ''.join(m for _, t in toks[s:s+len(At)] for m in MK.findall(t))
                # rebuild: put new text in first token's line, remove other tokens
                newtoks = [list(x) for x in toks]
                newtoks[s][1] = new + marks
                for k in range(s+1, s+len(At)): newtoks[k][1] = None
                for l in L:
                    Q[pi]['lines'][l]['text'] = ' '.join(t for ll, t in newtoks if ll == l and t)
                return True
    return False
review = []
for idx, it, dec in todo:
    pi, li, A, B = it['pi'], it['li'], it['A'], it['B']
    if dec == '?': review.append(idx); continue
    if dec.startswith('~'):
        a, b = dec[1:].split('=>')
        ok = False
        for l in (li, li+1, li-1):
            if 0 <= l < len(Q[pi]['lines']) and a in Q[pi]['lines'][l]['text']:
                Q[pi]['lines'][l]['text'] = Q[pi]['lines'][l]['text'].replace(a, b, 1); ok = True; break
        if not ok: fails.append((idx, dec, A, Q[pi]['lines'][li]['text']))
        continue
    new = B if dec == 'B' else dec[1:]
    if not replace_tokens(pi, li, A, new):
        fails.append((idx, dec, A, Q[pi]['lines'][li]['text']))
pickle.dump(Q, open('/tmp/dub/annotated_fixed.pkl','wb'))
print('fails', len(fails))
for f in fails: print(f)
print('review', review)
# line-level fixes
lf_fail = []
for l in open('/tmp/dub/linefix.txt'):
    l = l.rstrip('\n')
    if not l: continue
    pi, li, a, b = l.split('|')
    pi, li = int(pi), int(li)
    t = Q[pi]['lines'][li]['text']
    if a not in t: lf_fail.append(l); continue
    Q[pi]['lines'][li]['text'] = t.replace(a, b, 1)
pickle.dump(Q, open('/tmp/dub/annotated_fixed.pkl','wb'))
print('linefix fails', lf_fail)
# marker cleanup
GARB = '#?>®°¢*+|=«$%&^™•!'
def mclean(t):
    # garbage between punctuation and marker:  word.*°⟦56⟧ / it.7⟦7⟧ / revolution.5”⟦57⟧
    t = re.sub(r'([.,;:!?”’)\]])[0-9*°®¢#?%&^™•!+]+[”’"]?(?=⟦)', r'\1', t)
    t = re.sub(r'([.,;:!?”’)\]]) [*°®¢#%&^™•+]+(?=⟦)', r'\1', t)
    # glued after marker
    def glued(m):
        mk, g = m.group(1), m.group(2)
        if any(c in GARB for c in g) or re.search(r'\d', g): return mk
        return mk + g
    t = re.sub(r'(⟦\d+⟧)([^\s]+)', glued, t)
    # closing quotes glued after marker -> before
    t = re.sub(r'(⟦\d+⟧)([”’)]+)', r'\2\1', t)
    # garbage token after marker at end of line
    t = re.sub(r'(⟦\d+⟧)\s+[^\sA-Za-z“‘(\[—]{1,5}\s*$', r'\1', t)
    return t
n = 0
for pi in range(len(Q)):
    for l in Q[pi]['lines']:
        t2 = mclean(l['text'])
        if t2 != l['text']: n += 1; l['text'] = t2
pickle.dump(Q, open('/tmp/dub/annotated_fixed.pkl','wb'))
print('marker cleanup', n)
# punctuation: OCR comma that is a printed period (geometric check + visual review)
A, B = pickle.load(open('/tmp/dub/pcand.pkl','rb'))
keep = set(int(x) for x in open('/tmp/dub/pkeep.txt').read().split())
MK2 = re.compile(r'⟦\d+⟧')
pfail = []
PFIX = []
for j, (pi, li, wi, t, nxt, f) in enumerate(A):
    if j in keep: continue
    PFIX.append((pi, li, wi, t))
    if pi >= 483: continue
    line = Q[pi]['lines'][li]
    toks = line['text'].split(' ')
    core = re.sub(r'[.,][”’)\]]*$', '', t)
    cands = [k for k, tk in enumerate(toks) if MK2.sub('', tk).startswith(core) and re.search(r',[”’)\]]*$', MK2.sub('', tk))]
    if not cands: pfail.append((pi, li, t, line['text'][:80])); continue
    k = min(cands, key=lambda k: abs(k - wi))
    tk = toks[k]
    m = re.search(r',([”’)\]]*)((?:⟦\d+⟧)?)$', tk)
    toks[k] = tk[:m.start()] + '.' + m.group(1) + m.group(2)
    line['text'] = ' '.join(toks)
pickle.dump(PFIX, open('/tmp/dub/pfix.pkl', 'wb'))
pickle.dump(Q, open('/tmp/dub/annotated_fixed.pkl','wb'))
print('punct fixes', len(PFIX), 'fails', pfail)
