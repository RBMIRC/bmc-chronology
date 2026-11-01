import pickle, re, difflib, csv, collections
Q = pickle.load(open('/tmp/dub/merged.pkl','rb'))
def tess_words(pi):
    rows = list(csv.reader(open(f'/tmp/dub/tess/{pi+1:03d}.tsv'), delimiter='\t', quoting=csv.QUOTE_NONE))
    ws = []
    for r in rows[1:]:
        if len(r) < 12 or r[0] != '5': continue
        if r[11].strip(): ws.append((r[11], float(r[10])))
    return ws
def norm(w):
    w = w.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"').replace('—', '-').replace('–', '-')
    return w
diffs = []
for pi in range(21, 477):
    a = [w[4] for l in Q[pi]['lines'][1:] for w in l['words']]
    tw = tess_words(pi)
    b = [w for w, c in tw]
    sm = difflib.SequenceMatcher(None, [norm(x) for x in a], [norm(x) for x in b], autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op != 'equal':
            diffs.append((pi, op, ' '.join(a[i1:i2]), ' '.join(b[j1:j2])))
pickle.dump(diffs, open('/tmp/dub/tdiffs.pkl','wb'))
print(len(diffs))
c = collections.Counter(op for _, op, _, _ in diffs); print(c)
import random; random.seed(1)
for d in random.sample(diffs, 60): print(d)
