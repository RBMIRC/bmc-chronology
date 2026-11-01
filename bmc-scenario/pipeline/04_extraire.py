"""04 — Extraction structurée, morceau par morceau (voir moteurs.py pour les moteurs).

  python3 04_extraire.py --estimer
  python3 04_extraire.py --moteur zai --test 8
  python3 04_extraire.py --moteur claude --lot --priorite A        # envoi (API Batches)
  python3 04_extraire.py --moteur claude --relever                 # récupération
Chaque morceau fini = extractions/<id>.json ; tout se reprend là où ça s'est arrêté.
"""
import argparse
import csv
import json
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import moteurs
from config import CONSIGNE_ROLE, ETAT, EXTRACTIONS, INVENTAIRE, MORCEAUX
from schema import CATEGORIES, SCHEMA

PROMPT = (Path(__file__).parent / "prompt_extraction.md").read_text()
JOURNAL_LOTS = ETAT / "lots_extraction.jsonl"


def charger():
    with open(INVENTAIRE, newline="") as f:
        sources = {r["id"]: r for r in csv.DictReader(f)}
    morceaux = [json.loads(l) for l in open(MORCEAUX / "morceaux.jsonl", encoding="utf-8")]
    return sources, morceaux


def systeme(source):
    titre = Path(source["fichier"]).stem.split(" -- ")[0].replace("_", ":")
    return PROMPT.format(source=f"{source['court']} — {titre}", role=source["role"],
                         consigne=CONSIGNE_ROLE.get(source["role"], ""))


def message(m):
    return f"Passage {m['id']} (pages {m['pages'][0]} à {m['pages'][-1]}) :\n\n{m['texte']}"


def fait(m):
    return (EXTRACTIONS / f"{m['id']}.json").exists()


def valider(d):
    if not isinstance(d, dict):
        raise moteurs.ReponseInvalide("pas un objet")
    for k in CATEGORIES:
        d.setdefault(k, [])
        if not isinstance(d[k], list):
            raise moteurs.ReponseInvalide(f"{k} n'est pas une liste")
    d.setdefault("motifs", [])
    d.setdefault("resume", "")
    d.setdefault("pertinence", "utile")
    d.setdefault("cadre_temporel", {"debut": None, "fin": None, "justification": ""})
    return d


def enregistrer(m, source, modele, donnees, usage):
    EXTRACTIONS.mkdir(exist_ok=True)
    sortie = {"morceau": m["id"], "source": m["source"], "source_court": source["court"],
              "role": source["role"], "pages": m["pages"], "modele": modele, "usage": usage,
              "donnees": donnees}
    tmp = EXTRACTIONS / f"{m['id']}.tmp"
    tmp.write_text(json.dumps(sortie, ensure_ascii=False, indent=1))
    tmp.rename(EXTRACTIONS / f"{m['id']}.json")
    with open(ETAT / "extraction.jsonl", "a") as f:
        f.write(json.dumps({"t": time.strftime("%Y-%m-%d %H:%M:%S"), "morceau": m["id"],
                            "modele": modele, **usage}) + "\n")


def selection(args, sources, morceaux):
    sel = [m for m in morceaux if sources[m["source"]]["priorite"] in args.priorite.split(",")]
    if args.ids:
        sel = [m for m in morceaux if any(m["id"].startswith(i) for i in args.ids.split(","))]
    if args.test:
        # un échantillon varié : un morceau par rôle, pris au milieu des livres
        par_role = {}
        for m in sel:
            par_role.setdefault(sources[m["source"]]["role"], []).append(m)
        rng = random.Random(1933)
        sel = [rng.choice(v[len(v) // 4: 3 * len(v) // 4] or v) for v in par_role.values()]
        rng.shuffle(sel)
        sel = sel[:args.test]
    return [m for m in sel if not fait(m)]


def estimer(sources, morceaux):
    car_sys = len(systeme(next(iter(sources.values())))) + len(json.dumps(SCHEMA))
    for prio in ("A", "A,B", "A,B,C"):
        sel = [m for m in morceaux if sources[m["source"]]["priorite"] in prio.split(",")]
        reste = [m for m in sel if not fait(m)]
        entree = sum(len(m["texte"]) for m in reste) / 3.6 + len(reste) * car_sys / 3.6
        sortie = len(reste) * 11000  # mesuré au test : 7 à 15 k tokens par morceau
        print(f"priorité {prio:6s} {len(reste):5d} morceaux à faire  ≈ {entree/1e6:.1f} M tokens entrée, "
              f"{sortie/1e6:.1f} M sortie")
        for mod, (pe, ps) in moteurs.PRIX.items():
            c = (entree * pe + sortie * ps) / 1e6
            print(f"     {mod:18s} direct {c:7.0f} $   lot {c/2:7.0f} $")


def direct(args, sources, sel):
    cl = moteurs.client(args.moteur)
    print(f"{len(sel)} morceaux, moteur {args.moteur}, modèle {args.modele}, {args.parallele} fils", flush=True)

    def un(m):
        d, u = moteurs.appeler(args.moteur, cl, args.modele, systeme(sources[m["source"]]), message(m),
                               SCHEMA, args.effort)
        return valider(d), u

    ok = 0
    with ThreadPoolExecutor(args.parallele) as ex:
        futurs = {ex.submit(un, m): m for m in sel}
        for f in as_completed(futurs):
            m = futurs[f]
            try:
                d, u = f.result()
            except Exception as e:
                print(f"  {m['id']} ÉCHEC {type(e).__name__}: {str(e)[:200]}", flush=True)
                with open(ETAT / "echecs.jsonl", "a") as j:
                    j.write(json.dumps({"morceau": m["id"], "erreur": str(e)[:500]}) + "\n")
                continue
            enregistrer(m, sources[m["source"]], args.modele, d, u)
            ok += 1
            n = sum(len(d[k]) for k in CATEGORIES)
            print(f"  {m['id']} {n:3d} entrées  ({u['entree']}→{u['sortie']} tokens)  {d['pertinence']}", flush=True)
    print(f"{ok}/{len(sel)} faits")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--moteur", choices=["claude", "zai"], default="claude")
    ap.add_argument("--modele")
    ap.add_argument("--effort", default="medium", choices=["low", "medium", "high"])
    ap.add_argument("--priorite", default="A,B,C")
    ap.add_argument("--ids", help="préfixes de morceaux, ex. 006,041-003")
    ap.add_argument("--test", type=int, help="N morceaux variés, en direct")
    ap.add_argument("--parallele", type=int, default=4)
    ap.add_argument("--lot", action="store_true")
    ap.add_argument("--relever", action="store_true")
    ap.add_argument("--estimer", action="store_true")
    args = ap.parse_args()
    args.modele = args.modele or moteurs.MODELE_DEFAUT[args.moteur]
    ETAT.mkdir(exist_ok=True)
    sources, morceaux = charger()
    if args.estimer:
        return estimer(sources, morceaux)
    if args.relever:
        par_id = {m["id"]: m for m in morceaux}
        for cid, modele, d, u, err in moteurs.relever(moteurs.client("claude"), JOURNAL_LOTS):
            m = par_id.get(cid)
            if not m or fait(m):
                continue
            if err:
                print(f"  {cid} {err} → sera renvoyé au prochain --lot")
                continue
            enregistrer(m, sources[m["source"]], modele, valider(d), u)
        print(f"{sum(fait(m) for m in morceaux)}/{len(morceaux)} morceaux extraits")
        return
    sel = selection(args, sources, morceaux)
    if args.lot:
        moteurs.soumettre(moteurs.client("claude"), [
            (m["id"], moteurs.params(args.modele, systeme(sources[m["source"]]), message(m), SCHEMA, args.effort))
            for m in sel], JOURNAL_LOTS, args.modele)
        print("Relever plus tard : python3 04_extraire.py --moteur claude --relever")
        return
    direct(args, sources, sel)


if __name__ == "__main__":
    main()
