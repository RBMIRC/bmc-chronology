"""06 — Synthèses à partir des fiches fusionnées (05).

  personnes      un dossier par personnage (psychologie, voix, arc, avant / après)
  annees         un chapitre par année 1933-1957
  mois           l'état du collège mois par mois (sept. 1933 → déc. 1957) ; lit les années
  enseignements  les cours reconstitués, par enseignant

  python3 06_synthese.py personnes --moteur zai --test 2
  python3 06_synthese.py annees --moteur claude --lot      puis   --relever
Ordre conseillé : personnes, annees, enseignements, puis mois.
Résultats : syntheses/<passe>/<clé>.json (une passe se reprend là où elle s'est arrêtée).
"""
import argparse
from pathlib import Path
import json
import re
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

import moteurs
from unidecode import unidecode
from config import ETAT, FUSION, SYNTHESES
from schema import CATEGORIES
from schema_syntheses import ANNEE, ENSEIGNEMENT, MOIS, PERSONNE

PREMIER, DERNIER = (1933, 9), (1957, 12)
LIMITE_CARACTERES = 600_000  # ≈ 150 k tokens par requête, au-delà on garde le plus daté

CONSIGNES = """Tu prépares la matière d'un scénario sur Black Mountain College (1933-1957), suivi à l'échelle 1, avec flash-back et flash-forward.
On te donne des fiches déjà extraites de livres et d'articles, chacune avec son identifiant, sa date (ancrage) et sa source. « ≈ » signale une date déduite du contexte, à manier avec prudence.
Règles : n'utilise que ces fiches ; cite les identifiants dans « refs » ; distingue ce qui est attesté de ce que tu déduis ; quand les sources se contredisent, dis-le. Rédige en français, dense et concret ; paraphrase, ne recopie pas. Ne donne jamais un jour précis que les fiches ne donnent pas.
"""
TACHE = {
    "personnes": "Rédige le dossier de personnage de {cle} : ce qu'un scénariste doit savoir pour le faire vivre, parler et changer au fil des années, avec sa vie avant et après le collège.",
    "annees": "Rédige le chapitre de l'année {cle} au collège : sessions, gens présents, arrivées et départs, crises, intrigues en cours, climat. Les fiches d'années voisines servent de contexte.",
    "enseignements": "Reconstitue l'enseignement de {cle} : chaque cours, son déroulé type, les exercices exacts, ce qu'il ou elle disait, et les idées de son œuvre qui pouvaient nourrir une séance (en marquant ce qui n'est pas attesté au collège).",
    "mois": "Décris le collège en {cle} : la session en cours, qui est probablement là, ce qui arrive, la vie ordinaire, les tensions, des scènes possibles tirées des fiches, et les flash-back / flash-forward qui s'ouvrent depuis ce mois.",
}
SCHEMAS = {"personnes": PERSONNE, "annees": ANNEE, "mois": MOIS, "enseignements": ENSEIGNEMENT}


# ---------------------------------------------------------------- fiches

def charger():
    return {cat: json.load(open(FUSION / f"{cat}.json")) for cat in CATEGORIES}


def resume_fiche(e, cat):
    a = e["ancrage"]
    quand = "?" if not a["debut"] else (a["debut"] if a["fin"] in (None, a["debut"]) else f"{a['debut']}→{a['fin']}")
    if a["deduit"]:
        quand = "≈" + quand
    src = "; ".join(f"{s['titre']} p.{','.join(s['pages'][:3])}" for s in e["sources"][:3])
    if cat == "personnes":
        corps = " | ".join(f"{k}: " + " / ".join(t["texte"] for t in v[:6]) for k, v in e["traits"].items())
    else:
        champs = [k for k in e if k not in ("id", "sources", "ancrage", "personnes", "autres_versions", "date",
                                            "date_fin", "precision", "epoque", "pages")]
        corps = " | ".join(f"{k}: {e[k]}" for k in champs if e[k] not in (None, "", []))
        for v in e.get("autres_versions", [])[:3]:
            corps += f" || autre version ({v['sources'][0]['titre']}): " + str(v.get("description") or v.get("deroule") or "")[:400]
    return f"[{e['id']}] ({quand}) {corps} — {src}"


def annee_de(e):
    d = e["ancrage"]["debut"]
    return int(d[:4]) if d else None


def couvre(e, debut, fin):
    """L'ancrage de e chevauche-t-il [debut, fin] (chaînes AAAA-MM) ?"""
    a = e["ancrage"]
    if not a["debut"]:
        return False
    d, f = a["debut"][:7], (a["fin"] or a["debut"])[:7]
    if len(f) == 4:
        f += "-12"
    return d <= fin and f >= debut


def duree_mois(e):
    """Nombre de mois couverts par l'ancrage (une année seule compte pour 12)."""
    a = e["ancrage"]
    d, f = a["debut"], a["fin"] or a["debut"]
    md = int(d[5:7]) if len(d) >= 7 else 1
    mf = int(f[5:7]) if len(f) >= 7 else 12
    return (int(f[:4]) - int(d[:4])) * 12 + mf - md + 1


def assembler(blocs):
    """Concatène des blocs (titre, lignes) en respectant la limite de taille."""
    texte, total = [], 0
    for titre, lignes in blocs:
        texte.append(f"\n## {titre}\n")
        for l in lignes:
            if total + len(l) > LIMITE_CARACTERES:
                texte.append("… (fiches suivantes omises, limite atteinte)")
                return "\n".join(texte)
            texte.append(l)
            total += len(l)
    return "\n".join(texte)


def nom_dans(e, nom):
    return nom in e.get("personnes", []) or nom == e.get("nom")


# ---------------------------------------------------------------- passes

def taches_personnes(f, args):
    for p in f["personnes"]:
        if p["mentions"] < args.min_mentions:
            continue
        nom = p["nom"]
        blocs = [("Fiche agrégée", [resume_fiche(p, "personnes")])]
        for cat in ("relations", "scenes", "evenements", "citations", "echos", "conflits", "cours", "idees",
                    "quotidien", "oeuvres"):
            lignes = [resume_fiche(e, cat) for e in f[cat] if nom_dans(e, nom)
                      or (cat in ("echos", "quotidien") and nom in json.dumps(e, ensure_ascii=False))]
            if lignes:
                blocs.append((cat, lignes))
        yield nom, assembler(blocs)


def taches_annees(f, args):
    for an in range(1933, 1958):
        blocs = []
        for cat in CATEGORIES:
            if cat == "personnes":
                continue
            exacts = [e for e in f[cat] if annee_de(e) == an and not e["ancrage"]["deduit"]]
            larges = [e for e in f[cat] if e not in exacts and couvre(e, f"{an}-01", f"{an}-12")
                      and int((e["ancrage"]["fin"] or e["ancrage"]["debut"])[:4]) - annee_de(e) <= 3]
            if exacts or larges:
                blocs.append((cat, [resume_fiche(e, cat) for e in exacts + larges]))
        if blocs:
            yield str(an), assembler(blocs)


def taches_enseignements(f, args):
    par_ens = defaultdict(list)
    for e in f["cours"]:
        par_ens[e["enseignant"]].append(("cours", e))
    for e in f["idees"]:
        par_ens[e["auteur"]].append(("idees", e))
    for nom, fiches in par_ens.items():
        if len(fiches) < args.min_mentions:
            continue
        blocs = [("cours et idées", [resume_fiche(e, c) for c, e in fiches])]
        scenes = [resume_fiche(e, "scenes") for e in f["scenes"] if nom_dans(e, nom)]
        if scenes:
            blocs.append(("scènes où il ou elle apparaît", scenes))
        yield nom, assembler(blocs)


def mois_suivants():
    a, m = PREMIER
    while (a, m) <= DERNIER:
        yield a, m
        a, m = (a + 1, 1) if m == 12 else (a, m + 1)


def taches_mois(f, args):
    for a, m in mois_suivants():
        cle = f"{a}-{m:02d}"
        blocs = []
        chap = SYNTHESES / "annees" / f"{a}.json"
        if chap.exists():
            d = json.load(open(chap))["donnees"]
            blocs.append((f"chapitre de l'année {a} (synthèse)", [d["recit"], "Fils : " + " ; ".join(
                f"{x['titre']} ({x['debut']}→{x['fin']})" for x in d["fils"])]))
        for cat in CATEGORIES:
            if cat == "personnes":
                continue
            precis = [e for e in f[cat] if couvre(e, cle, cle) and e["ancrage"]["precision"] in
                      ("jour", "semaine", "mois", "saison", "session") and duree_mois(e) <= 4]
            if precis:
                blocs.append((f"{cat} datés de ce mois ou de sa saison", [resume_fiche(e, cat) for e in precis]))
        ouvertures = [resume_fiche(e, "echos") for e in f["echos"] if couvre(e, cle, cle) and duree_mois(e) <= 12]
        if ouvertures:
            blocs.append(("échos signalés par les sources", ouvertures))
        if len(blocs) <= 1 and not chap.exists():
            continue
        yield cle, assembler(blocs)


PASSES = {"personnes": taches_personnes, "annees": taches_annees, "mois": taches_mois,
          "enseignements": taches_enseignements}


# ---------------------------------------------------------------- exécution

def ident(cle):
    """Nom de fichier et custom_id de lot (64 caractères au plus)."""
    return re.sub(r"[^\w\-]+", "_", cle).strip("_")[:64]


DOSSIER = SYNTHESES  # --sortie le change (essais comparatifs à part)


def id_lot(cle, pris):
    """custom_id de lot : ASCII seulement (l'API refuse les accents), unique, 64 caractères."""
    base = re.sub(r"[^A-Za-z0-9_-]+", "_", unidecode(cle)).strip("_")[:56] or "x"
    i, cid = 1, base
    while cid in pris:
        i += 1
        cid = f"{base}_{i}"
    pris.add(cid)
    return cid


def fichier(passe, cle):
    return DOSSIER / passe / (ident(cle) + ".json")


def enregistrer(passe, cle, modele, d, u):
    dest = fichier(passe, cle)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps({"passe": passe, "cle": cle, "modele": modele, "usage": u, "donnees": d},
                               ensure_ascii=False, indent=1))
    with open(ETAT / "syntheses.jsonl", "a") as j:
        j.write(json.dumps({"t": time.strftime("%Y-%m-%d %H:%M:%S"), "passe": passe, "cle": cle,
                            "modele": modele, **u}) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("passe", choices=list(PASSES))
    ap.add_argument("--moteur", choices=["claude", "zai"], default="claude")
    ap.add_argument("--modele")
    ap.add_argument("--effort", default="high", choices=["low", "medium", "high"])
    ap.add_argument("--min-mentions", type=int, default=3)
    ap.add_argument("--cles", help="ne traiter que ces clés, séparées par des virgules")
    ap.add_argument("--test", type=int)
    ap.add_argument("--parallele", type=int, default=4)
    ap.add_argument("--lot", action="store_true")
    ap.add_argument("--relever", action="store_true")
    ap.add_argument("--attendre", action="store_true", help="avec --relever : patienter jusqu'à la fin des lots")
    ap.add_argument("--sortie", help="dossier de sortie à la place de syntheses/ (comparaisons)")
    ap.add_argument("--voir", action="store_true", help="afficher les tâches et leur taille, sans appel")
    args = ap.parse_args()
    args.modele = args.modele or moteurs.MODELE_DEFAUT[args.moteur]
    ETAT.mkdir(exist_ok=True)
    if args.sortie:
        global DOSSIER
        DOSSIER = Path(args.sortie).resolve()
    journal = ETAT / f"lots_{args.passe}.jsonl"
    table_ids = ETAT / f"lots_{args.passe}_ids.json"  # custom_id → clé

    if args.relever:
        cl = moteurs.client("claude")
        if args.attendre:
            moteurs.attendre(cl, journal)
        cles = json.load(open(table_ids)) if table_ids.exists() else {}
        for cid, modele, d, u, err in moteurs.relever(cl, journal):
            cle = cles.get(cid, cid)
            if err:
                print(f"  {cle} {err}")
            elif not fichier(args.passe, cle).exists():
                enregistrer(args.passe, cle, modele, d, u)
        return

    f = charger()
    taches = [(c, t) for c, t in PASSES[args.passe](f, args) if not fichier(args.passe, c).exists()]
    if args.cles:
        voulues = set(args.cles.split(","))
        taches = [(c, t) for c, t in taches if c in voulues]
    if args.test:
        taches = sorted(taches, key=lambda x: len(x[1]))[:args.test]  # les plus petites : un essai qui coûte peu
    systeme = CONSIGNES + "\n" + TACHE[args.passe].replace("{cle}", "la clé indiquée dans le message")
    total = sum(len(t) for _, t in taches)
    print(f"{args.passe} : {len(taches)} tâches, {total/1e6:.2f} M caractères ≈ {total/3.6/1e6:.2f} M tokens")
    if args.voir:
        for c, t in taches:
            print(f"  {c:40s} {len(t):8d} car.")
        return

    message = lambda c, t: f"{TACHE[args.passe].format(cle=c)}\n\nClé : {c}\n\nFiches :\n{t}"
    if args.lot:
        cles = json.load(open(table_ids)) if table_ids.exists() else {}
        inverse = {v: k for k, v in cles.items()}
        pris = set(cles)
        requetes = []
        for c, t in taches:
            cid = inverse.get(c) or id_lot(c, pris)
            cles[cid] = c
            requetes.append((cid, moteurs.params(args.modele, systeme, message(c, t), SCHEMAS[args.passe],
                                                 args.effort)))
        table_ids.write_text(json.dumps(cles, ensure_ascii=False, indent=1))
        moteurs.soumettre(moteurs.client("claude"), requetes, journal, args.modele)
        return

    cl = moteurs.client(args.moteur)
    echecs = 0
    with ThreadPoolExecutor(args.parallele) as ex:
        futurs = {ex.submit(moteurs.appeler, args.moteur, cl, args.modele, systeme, message(c, t),
                            SCHEMAS[args.passe], args.effort): c for c, t in taches}
        for fu in as_completed(futurs):
            c = futurs[fu]
            try:
                d, u = fu.result()
            except Exception as e:
                print(f"  {c} ÉCHEC {type(e).__name__}: {str(e)[:300]}", flush=True)
                echecs += 1
                continue
            enregistrer(args.passe, c, args.modele, d, u)
            print(f"  {c} ({u['entree']}→{u['sortie']} tokens)", flush=True)
    if echecs:
        raise SystemExit(f"{echecs} échec(s)")


if __name__ == "__main__":
    main()
