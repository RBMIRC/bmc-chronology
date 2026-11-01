"""07 — Le JSON final du scénario, à partir des fiches (05) et des synthèses (06).

Sans appel au modèle ; se relance à volonté. N'écrase rien : chaque assemblage
prend un nouveau numéro, sortie/NNN_bmc_scenario_1933-1957.json.

Structure :
  meta            sources, comptes, conventions (ancrage, certitude, refs)
  chronologie     annees{AAAA}, mois[AAAA-MM] (état du collège), dates[] (faits au jour/mois)
  personnages[]   dossiers (06) + fiche agrégée (05) + identifiants des fiches qui les citent
  enseignements[] cours reconstitués par enseignant
  fiches{}        toutes les fiches fusionnées par catégorie (evenements, scenes, …)
  motifs[]        images récurrentes, par fréquence
  index           par_mois, par_annee, par_personne, par_lieu → identifiants
  passages[]      résumé et cadre temporel de chaque morceau lu
"""
import csv
import json
import re
import time
from collections import defaultdict

from config import FUSION, INVENTAIRE, SORTIE, SYNTHESES
from schema import CATEGORIES


ID_FICHE = re.compile(r"^[A-Z]{2}-\d{5}$")
REDIRECTIONS = json.load(open(FUSION / "_redirections.json")) if (FUSION / "_redirections.json").exists() else {}


def rediriger(x):
    """Remplace, dans une synthèse, les identifiants de fiches absorbées par leur fiche d'accueil."""
    if isinstance(x, dict):
        return {k: rediriger(v) for k, v in x.items()}
    if isinstance(x, list):
        return [rediriger(v) for v in x]
    if isinstance(x, str) and ID_FICHE.match(x):
        return REDIRECTIONS.get(x, x)
    return x


def lire(passe):
    d = SYNTHESES / passe
    return {} if not d.exists() else {
        x["cle"]: rediriger(x["donnees"]) for x in (json.load(open(f)) for f in sorted(d.glob("*.json")))}


def rattacher_dossiers(dossiers, personnes):
    """Relie chaque dossier à sa personne, même si le nom a changé depuis sa rédaction
    (redirection de la fiche, ou personnage de roman désormais mis à part)."""
    noms = {p["nom"] for p in personnes}
    par_id = {p["id"]: p["nom"] for p in personnes}
    ref = FUSION / "_reference" / "personnes.json"
    id_ancien = {p["nom"]: p["id"] for p in json.load(open(ref))} if ref.exists() else {}
    relies, orphelins = {}, []
    for cle, d in dossiers.items():
        nom = cle if cle in noms else par_id.get(REDIRECTIONS.get(id_ancien.get(cle, ""), ""))
        if not nom:
            nom = next((n for n in noms if n.startswith(cle + " (personnage")), None)
        if nom and nom not in relies:
            relies[nom] = d
        else:
            orphelins.append(cle)
    return relies, orphelins


MOTS_MAX = 25  # citations : formules brèves, jamais des extraits


def ecourter(fiches):
    """Ramène chaque citation (et ses autres versions) à 25 mots au plus."""
    n = 0
    for c in fiches["citations"]:
        for v in [c] + c.get("autres_versions", []):
            mots = (v.get("texte_original") or "").split()
            if len(mots) > MOTS_MAX:
                v["texte_original"] = " ".join(mots[:MOTS_MAX]) + " […]"
                n += 1
    return n


def mois_entre(debut, fin):
    a, m = int(debut[:4]), int(debut[5:7]) if len(debut) >= 7 else 1
    fa, fm = int(fin[:4]), int(fin[5:7]) if len(fin) >= 7 else 12
    while (a, m) <= (fa, fm):
        yield f"{a}-{m:02d}"
        a, m = (a + 1, 1) if m == 12 else (a, m + 1)


def main():
    SORTIE.mkdir(exist_ok=True)
    fiches = {cat: json.load(open(FUSION / f"{cat}.json")) for cat in CATEGORIES}
    print(f"  citations écourtées à {MOTS_MAX} mots : {ecourter(fiches)}")
    with open(INVENTAIRE, newline="") as f:
        sources = [{k: r[k] for k in ("id", "court", "role", "priorite", "fichier")}
                   for r in csv.DictReader(f) if r["role"] != "doublon"]

    # ------------------------------------------------ index
    par_mois, par_annee = defaultdict(list), defaultdict(list)
    par_personne, par_lieu = defaultdict(list), defaultdict(list)
    dates = []
    for cat, liste in fiches.items():
        for e in liste:
            a = e["ancrage"]
            for p in e.get("personnes", []):
                par_personne[p].append(e["id"])
            if e.get("lieu") or (cat == "lieux" and e.get("nom")):
                par_lieu[e.get("lieu") or e["nom"]].append(e["id"])
            if not a["debut"]:
                continue
            fin = a["fin"] or a["debut"]
            annees = range(int(a["debut"][:4]), int(fin[:4]) + 1)
            if len(annees) <= 5:
                for an in annees:
                    par_annee[str(an)].append(e["id"])
            ms = list(mois_entre(a["debut"], fin))
            if a["precision"] in ("jour", "semaine", "mois", "saison", "session") and len(ms) <= 6:
                for m in ms:
                    par_mois[m].append(e["id"])
            if a["precision"] in ("jour", "semaine", "mois") and not a["deduit"]:
                dates.append({"date": a["debut"], "precision": a["precision"], "id": e["id"], "categorie": cat,
                              "titre": e.get("titre") or e.get("nom") or e.get("idee") or e.get("texte_original", "")[:80]})
    dates.sort(key=lambda d: d["date"])

    # ------------------------------------------------ personnages
    dossiers, orphelins = rattacher_dossiers(lire("personnes"), fiches["personnes"])
    if orphelins:
        print(f"  dossiers sans personne (écartés) : {', '.join(orphelins)}")
    personnages = []
    for p in fiches["personnes"]:
        personnages.append({
            "nom": p["nom"], "id": p["id"], "mentions": p["mentions"], "statut_bmc": p["statut_bmc"],
            "autres_noms": p["autres_noms"], "dossier": dossiers.get(p["nom"]),
            "traits_par_source": p["traits"], "fiches": sorted(set(par_personne.get(p["nom"], []))),
        })

    mois = lire("mois")
    sortie = {
        "meta": {
            "titre": "Black Mountain College 1933-1957 — matière de scénario à l'échelle 1",
            "assemble_le": time.strftime("%Y-%m-%d %H:%M"),
            "sources": sources,
            "comptes": {cat: len(v) for cat, v in fiches.items()} | {
                "dossiers_personnages": len(dossiers), "chapitres_annees": len(lire("annees")),
                "mois_decrits": len(mois), "enseignants": len(lire("enseignements"))},
            "conventions": {
                "ancrage": "debut/fin en ISO partiel ; precision réelle ; deduit=true si la date vient du "
                           "cadre du passage et non du fait lui-même",
                "certitude": "atteste · temoignage_direct · oui_dire · interpretation_auteur · conteste · hypothese",
                "refs": "identifiants de fiches (EV evenements, SC scenes, PE personnes, RE relations, CO cours, "
                        "ID idees, LI lieux, QU quotidien, CI citations, OE oeuvres, CF conflits, EC echos)",
                "sources": "chaque fiche garde sa source et ses folios ; autres_versions = même fait vu par "
                           "d'autres sources",
                "texte": "paraphrases en français ; citations brèves dans la langue d'origine",
            },
        },
        "chronologie": {
            "annees": lire("annees"),
            "mois": [{"mois": m, "etat": mois.get(m), "fiches": sorted(set(par_mois.get(m, [])))}
                     for m in mois_entre("1933-09", "1957-12")],
            "dates": dates,
        },
        "personnages": personnages,
        "enseignements": list(lire("enseignements").values()),
        "fiches": fiches,
        "motifs": json.load(open(FUSION / "motifs.json")),
        "index": {"par_annee": dict(sorted(par_annee.items())), "par_mois": dict(sorted(par_mois.items())),
                  "par_personne": dict(par_personne), "par_lieu": dict(par_lieu)},
        "passages": json.load(open(FUSION / "passages.json")),
    }

    n = 1 + max((int(p.name[:3]) for p in SORTIE.glob("[0-9][0-9][0-9]_*.json")), default=0)
    dest = SORTIE / f"{n:03d}_bmc_scenario_1933-1957.json"
    dest.write_text(json.dumps(sortie, ensure_ascii=False, indent=1))
    c = sortie["meta"]["comptes"]
    print(f"{dest}  ({dest.stat().st_size/1e6:.1f} Mo)")
    print("  " + ", ".join(f"{k} {v}" for k, v in c.items()))
    print(f"  mois avec fiches : {sum(1 for m in sortie['chronologie']['mois'] if m['fiches'])}/292, "
          f"dates précises : {len(dates)}")


if __name__ == "__main__":
    main()
