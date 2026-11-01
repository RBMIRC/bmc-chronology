import re, collections, sys
from wordfreq import zipf_frequency
txt = open(sys.argv[1]).read()
words = re.findall(r"[A-Za-zÀ-ÿ’'\-]+", txt)
cnt = collections.Counter(words)
unk = collections.Counter()
for w, c in cnt.items():
    core = w.strip("’'-")
    if not core: continue
    parts = core.split('-')
    bad = False
    for p in parts:
        p2 = re.sub(r"(’s|'s|’)$", '', p)
        if not p2: continue
        if zipf_frequency(p2.lower(), 'en') >= 1.0: continue
        bad = True
    if bad: unk[core] += c
print(len(unk))
for w, c in sorted(unk.items(), key=lambda x: (-x[1], x[0])): print(c, w)
