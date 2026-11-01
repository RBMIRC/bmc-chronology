"""Aspire les fiches BMC de collection.ashevilleart.org (eMuseum 4D) : texte OCR des descriptions.
Relançable : saute les pages déjà en cache. Sortie : cache/<requete>_<n>.html + fiches.json"""
import re, html, json, time, sys, urllib.request, urllib.parse, os
from concurrent.futures import ThreadPoolExecutor
BASE = "https://collection.ashevilleart.org"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "cache")
REQUETES = {"bm": 'mfs any "Black Mountain"', "bmc": 'mfs any "BMC"',
            "dreier": 'mfs any "Dreier"', "lakeeden": 'mfs any "Lake Eden"',
            "schedule": 'mfs any "schedule"'}
UA = {"User-Agent": "Mozilla/5.0 (research; BMC programme index)"}

def get(url):
    for essai in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read().decode("utf-8", "ignore")
        except Exception as e:
            time.sleep(3 * (essai + 1))
    raise RuntimeError(url)

def total(q):
    s = get(f"{BASE}/objects-1/thumbnails?records=5000&query={urllib.parse.quote(q)}&sort=9&page=1")
    p = [int(x) for x in re.findall(r"page&#61;(\d+)", s)]
    return max(p) if p else 0

def fetch(args):
    key, q, n = args
    f = os.path.join(CACHE, f"{key}_{n:04d}.html")
    if os.path.exists(f) and os.path.getsize(f) > 5000:
        return f
    s = get(f"{BASE}/objects-1/info?query={urllib.parse.quote(q)}&sort=9&page={n}")
    open(f, "w", encoding="utf-8").write(s)
    time.sleep(0.3)
    return f

def champ(s, label):
    m = re.search(r'heading-small">\s*' + re.escape(label) + r'\s*</span>\s*</div>\s*<div class="object-info-section">(.*?)</div>', s, re.S)
    return texte(m.group(1)) if m else ""

def texte(h):
    h = re.sub(r"<br\s*/?>", "\n", h)
    h = re.sub(r"</p>", "\n", h)
    h = html.unescape(re.sub(r"<[^>]+>", "", h))
    return "\n".join(l.strip() for l in h.splitlines()).strip()

def titre(s):
    m = re.search(r'heading-small">Title</span>\s*</div>\s*<h1>(.*?)</h1>', s, re.S)
    return texte(m.group(1)) if m else ""

def parse(f):
    s = open(f, encoding="utf-8").read()
    ids = re.findall(r"/objects-1/info/(\d+)", s)
    # l'id de la fiche courante : lien canonique / images
    acc = champ(s, "Accession Number")
    d = re.search(r'Description</span>\s*</div>\s*<div class="embarkInfoNotes">(.*?)</div>', s, re.S)
    imgs = sorted(set(re.findall(r'/Media/images/[^"\']+?\.jpg', s)))
    return {"accession": acc, "title": titre(s), "date": champ(s, "Date"),
            "artist": champ(s, "Artist"), "object_type": champ(s, "Object Type"),
            "credit": champ(s, "Credit Line"), "medium": champ(s, "Medium & Support"),
            "description": texte(d.group(1)) if d else "", "images": imgs,
"cache": os.path.basename(f)}

if __name__ == "__main__":
    taches = []
    for key, q in REQUETES.items():
        n = total(q); print(key, n, flush=True)
        taches += [(key, q, i) for i in range(1, n + 1)]
    with ThreadPoolExecutor(4) as ex:
        for i, _ in enumerate(ex.map(fetch, taches)):
            if i % 100 == 0: print(i, "/", len(taches), flush=True)
    # id d'objet : déduit des liens précédent/suivant des pages voisines
    ids = {}
    for f in os.listdir(CACHE):
        if f.endswith(".html"):
            key = f.rsplit("_", 1)[0]
            for oid, pg in re.findall(r"/objects-1/info/(\d+)\?query=[^\"']*?page=(\d+)", open(os.path.join(CACHE, f), encoding="utf-8").read()):
                ids[(key, int(pg))] = oid
    fiches = {}
    for f in sorted(os.listdir(CACHE)):
        if f.endswith(".html"):
            r = parse(os.path.join(CACHE, f))
            key, n = f[:-5].rsplit("_", 1)
            oid = ids.get((key, int(n)))
            r["object_id"] = oid
            r["url"] = f"{BASE}/objects-1/info/{oid}" if oid else None
            if r["accession"]:
                fiches.setdefault(r["accession"], r)
    json.dump(sorted(fiches.values(), key=lambda r: r["accession"]),
              open(os.path.join(ROOT, "fiches.json"), "w"), ensure_ascii=False, indent=1)
    print("fiches uniques:", len(fiches))
