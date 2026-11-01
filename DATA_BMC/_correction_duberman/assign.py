import pickle, re
idx = pickle.load(open('/tmp/dub/sheet_index.pkl','rb'))
allm = pickle.load(open('/tmp/dub/markers2.pkl','rb'))
chap = pickle.load(open('/tmp/dub/chap.pkl','rb'))
vals = {}
for line in open('/tmp/dub/supvals.txt'):
    line = line.strip()
    if not line or line.startswith('#'): continue
    a, b = line.split()
    if '-' in a:
        a0, a1 = map(int, a.split('-')); b0, b1 = map(int, b.split('-'))
        assert a1 - a0 == b1 - b0, line
        for k in range(a1 - a0 + 1): vals[a0 + k] = b0 + k
    else:
        vals[int(a)] = None if b.startswith('X') else int(b.rstrip('?'))
assert sorted(vals) == list(range(len(idx))), (len(vals), len(idx), set(range(len(idx))) - set(vals))
# per chapter sequence
seq = {}
for j, (pi, k) in enumerate(idx):
    v = vals[j]
    if v is None: continue
    seq.setdefault(chap[pi], []).append((v, pi, k))
missing = {}
for c, s in seq.items():
    nums = [v for v, _, _ in s]
    bad = [(a, b) for a, b in zip(nums, nums[1:]) if b <= a]
    mx = max(nums)
    miss = sorted(set(range(1, mx + 1)) - set(nums))
    missing[c] = miss
    print(c, 'max', mx, 'n', len(nums), 'order errors', bad, 'missing', miss)
pickle.dump((vals, seq, missing), open('/tmp/dub/assign.pkl', 'wb'))
