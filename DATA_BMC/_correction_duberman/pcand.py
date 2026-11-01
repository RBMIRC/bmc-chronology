import sys, pickle, re
sys.path.insert(0, '/tmp/dub')
from punct2 import feature, M
res = pickle.load(open('/tmp/dub/punct.pkl','rb'))
A, B = [], []
for pi, li, wi, t, g in res:
    o = re.search(r'([.,])[”’)\]]*$', t).group(1)
    ws = M[pi]['lines'][li]['words']
    nxt = ws[wi+1][4] if wi + 1 < len(ws) else (M[pi]['lines'][li+1]['words'][0][4] if li + 1 < len(M[pi]['lines']) and M[pi]['lines'][li+1]['words'] else '')
    if o == ',' and re.match(r'^[“‘(]?[A-Z]', nxt):
        f = feature(pi, li, wi)
        if f and f['desc'] <= 1 and f['h'] <= 5: A.append((pi, li, wi, t, nxt, f))
    if o == '.' and re.match(r'^[“‘(]?[a-z]', nxt) and not re.search(r'\b(etc|vs|p|pp|cf|ed|Mr|Mrs|Dr|St|Jr|Sr|al|ibid|op|cit|i\.e|e\.g|n\.d|No|Vol|U\.S|Mt)\.', t):
        f = feature(pi, li, wi)
        if f and f['desc'] >= 2.5: B.append((pi, li, wi, t, nxt, f))
pickle.dump((A, B), open('/tmp/dub/pcand.pkl', 'wb'))
print(len(A), len(B))
