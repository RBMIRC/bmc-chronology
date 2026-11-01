import pickle, re, difflib, csv, collections
from wordfreq import zipf_frequency
Q = pickle.load(open('/tmp/dub/merged.pkl','rb'))
def tess_lines(pi):
    rows = list(csv.reader(open(f'/tmp/dub/tess/{pi+1:03d}.tsv'), delimiter='\t', quoting=csv.QUOTE_NONE))
    ws = []
    for r in rows[1:]:
        if len(r) < 12 or r[0] != '5' or not r[11].strip(): continue
        ws.append(r[11])
    return ws
def core(w):
    w = w.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"').replace('—', '-').replace('–', '-')
    w = re.sub(r'[0-9?°*®¢§%&\^™•#+>]+$', '', w) if re.search(r'[a-z][.,;:!?"\')]+[0-9?°*®¢§%&\^™•#+>]+$', w) else w
    return w
pages = list(range(11,16)) + list(range(17,20)) + list(range(21,480))
pairs = []
for pi in pages:
    a = [w[4] for l in Q[pi]['lines'][1:] for w in l['words']]
    b = tess_lines(pi)
    ca = [core(x) for x in a]; cb = [core(x) for x in b]
    sm = difflib.SequenceMatcher(None, ca, cb, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'equal': continue
        A = ' '.join(a[i1:i2]); B = ' '.join(b[j1:j2])
        cA = ' '.join(ca[i1:i2]); cB = ' '.join(cb[j1:j2])
        if cA.replace('"', '').replace("'", '') == cB.replace('"', '').replace("'", ''): continue
        if op == 'insert' and re.search(r'BLACK MOUNTAIN|[A-Z]{4,} \d+$|^\d+$', B): continue
        pairs.append((pi, A, B))
pickle.dump(pairs, open('/tmp/dub/tpairs.pkl', 'wb'))
print(len(pairs))
for p in pairs: print(p)
