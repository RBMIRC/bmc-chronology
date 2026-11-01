"""Ajoute des corrections (ancien → nouveau) à post.json : python fix.py 'ancien' 'nouveau' ['ancien' 'nouveau' ...]"""
import json, sys
p = json.load(open('/tmp/farm/post.json'))
a = sys.argv[1:]
for i in range(0, len(a), 2):
    p.append([a[i], a[i + 1]])
json.dump(p, open('/tmp/farm/post.json', 'w'), ensure_ascii=False, indent=0)
print(len(p), "corrections")
