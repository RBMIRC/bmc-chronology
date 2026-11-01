"""Sonde /objects-1/info/<id> sur une plage pour rattraper les fiches que la recherche du site ne renvoie pas.
Usage : sonder_ids.py debut fin. Cache : cache_id/<id>.html. Écrit fiches_sondees.json (fiches BMC seulement)."""
import sys, os, json, re
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aspirer as a
ROOT = a.ROOT; C = os.path.join(ROOT, "cache_id"); os.makedirs(C, exist_ok=True)
deb, fin = int(sys.argv[1]), int(sys.argv[2])
def go(i):
    fn = os.path.join(C, f"{i}.html")
    if not os.path.exists(fn):
        try: open(fn, "w", encoding="utf-8").write(a.get(f"{a.BASE}/objects-1/info/{i}"))
        except Exception: return
    return i
with ThreadPoolExecutor(4) as ex:
    for k, _ in enumerate(ex.map(go, range(deb, fin + 1))):
        if k % 250 == 0: print(k, flush=True)
out = []
for f in os.listdir(C):
    if not f.endswith(".html"): continue
    r = a.parse(os.path.join(C, f))
    if not r["accession"]: continue
    blob = " ".join([r["title"], r["credit"], r["description"][:3000]])
    if re.search(r"Black Mountain|BMC|Lake Eden|Dreier", blob):
        r["object_id"] = f[:-5]; r["url"] = f"{a.BASE}/objects-1/info/{f[:-5]}"
        out.append(r)
json.dump(sorted(out, key=lambda r: r["accession"]), open(os.path.join(ROOT, "fiches_sondees.json"), "w"), ensure_ascii=False, indent=1)
print("BMC sondées :", len(out))
