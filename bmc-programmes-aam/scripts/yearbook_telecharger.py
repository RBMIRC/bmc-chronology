"""Télécharge les biographies du BMC Yearbook (https://bmcyearbook.org/biographies), source de BlackMountainPeople.txt.

BMC Yearbook est un projet du Black Mountain College Museum + Arts Center (Amanda Hartman, Heron Studio), « compiled
from multiple archival collections » (Western Regional Archives surtout). Le site affiche « All rights reserved » :
copie de travail pour la recherche, à ne pas republier.

Texte et données seulement (pas d'images) : pour chaque biographie, la page /bio/<slug> (données Remix incluses dans la
page : window.__remixContext) → une ligne JSON : slug, url, personne (noms, rôle, discipline, dates au collège, naissance,
décès), crédit, texte de la notice bloc par bloc (style, puce, texte).
Liste : /biographies?page=N&_data=routes/biographies (32 par page).
Sortie : DATA_BMC/bmcyearbook/NNN_biographies.jsonl (numéro suivant, jamais écrasé) + NNN_telechargement.md.
Politesse : une requête toutes les 0,4 s ; reprise possible (--reprendre NNN : les slugs déjà présents sont sautés).
Usage : python3 scripts/yearbook_telecharger.py [--reprendre NNN]
"""
import datetime as dt, json, os, re, sys, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.join(os.path.dirname(ROOT), "DATA_BMC", "bmcyearbook")
SITE = "https://bmcyearbook.org"
UA = {"User-Agent": "Mozilla/5.0 (recherche historique, semainier du Black Mountain College)"}


def lire(url, essais=4):
    for k in range(essais):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read().decode("utf-8")
        except Exception as e:
            if k == essais - 1: raise
            time.sleep(2 ** (k + 1)); print(f"  nouvel essai ({e}) : {url}", file=sys.stderr)


def texte_bloc(b):
    return "".join(c.get("text", "") for c in b.get("children", []) if c.get("_type") == "span")


def main():
    os.makedirs(SORTIE, exist_ok=True)
    if "--reprendre" in sys.argv:
        num = sys.argv[sys.argv.index("--reprendre") + 1]
    else:
        nums = [int(f[:3]) for f in os.listdir(SORTIE) if re.match(r"\d{3}_", f)]
        num = f"{max(nums, default=0) + 1:03d}"
    p = os.path.join(SORTIE, f"{num}_biographies.jsonl")
    deja = set()
    if os.path.exists(p):
        deja = {json.loads(l)["slug"] for l in open(p, encoding="utf-8")}
    # 1. liste
    slugs, page, total, sans_lien = [], 1, None, []
    while True:
        d = json.loads(lire(f"{SITE}/biographies?page={page}&_data=routes%2Fbiographies"))
        total = d["totalCount"]
        for b in d["biographies"]:
            if (b.get("slug") or {}).get("current"): slugs.append((b["slug"]["current"], (b.get("person") or {}).get("fullName", "")))
            else: sans_lien.append(json.dumps({k: b.get(k) for k in ("_id", "person")}, ensure_ascii=False)[:200])
        if not d.get("hasNextPage"): break
        page += 1; time.sleep(0.4)
    print(f"{len(slugs)} biographies listées sur {page} pages (le site en annonce {total})")
    # 2. notices
    erreurs = []
    with open(p, "a", encoding="utf-8") as f:
        for i, (slug, nom) in enumerate(slugs, 1):
            if slug in deja: continue
            url = f"{SITE}/bio/{slug}"
            try:
                h = lire(url)
                m = re.search(r"window\.__remixContext = (\{.*?\});\s*</script>", h, re.S)
                ld = json.loads(m.group(1))["state"]["loaderData"]
                bio = json.loads(next(v for k, v in ld.items() if k.startswith("routes/bio"))["stringifiedBio"])
            except Exception as e:
                erreurs.append(f"{slug} : {e}"); continue
            pers = {k: v for k, v in (bio.get("person") or {}).items() if k not in ("image", "_id")}
            blocs = [{"style": b.get("style", ""), "puce": b.get("listItem", ""), "texte": texte_bloc(b)}
                     for b in bio.get("body") or [] if b.get("_type") == "block"]
            f.write(json.dumps({"slug": slug, "url": url, "nom_liste": nom, "personne": pers, "nom": bio.get("name"),
                                "auteur": bio.get("author"), "credit_image": bio.get("imageCredit"),
                                "blocs": [b for b in blocs if b["texte"].strip()],
                                "telecharge_le": dt.date.today().isoformat()}, ensure_ascii=False) + "\n")
            f.flush()
            if i % 100 == 0: print(f"  {i}/{len(slugs)}")
            time.sleep(0.4)
    n = sum(1 for _ in open(p, encoding="utf-8"))
    rapport = [f"# BMC Yearbook, biographies : téléchargement {num}", "",
               f"- Source : {SITE}/biographies (BMC Yearbook, Black Mountain College Museum + Arts Center), le {dt.date.today().isoformat()}.",
               f"- {len(slugs)} biographies listées (le site en annonce {total}) ; {n} notices dans `{os.path.basename(p)}`.",
               f"- Entrées de la liste sans page (pas de slug) : {len(sans_lien)}"] + [f"  - {e}" for e in sans_lien] + [
               f"- Erreurs : {len(erreurs)}"] + [f"  - {e}" for e in erreurs]
    open(os.path.join(SORTIE, f"{num}_telechargement.md"), "w", encoding="utf-8").write("\n".join(rapport) + "\n")
    print("\n".join(rapport))


if __name__ == "__main__":
    main()
