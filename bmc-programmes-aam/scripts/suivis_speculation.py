"""Cours suivis (fiches d'étudiants du BMC Yearbook, bmcyearbook.org) → tables de rattachement pour la couche spéculative.

Entrées : chronos/NNN_personnes_cours_suivis.csv (le plus récent, scripts/chronos_personnes.py) et le catalogue
spéculatif de l'année (speculation/catalogues/AAAA-AA.txt).
Sortie : speculation/suivis/AAAA-AA.csv (nouveau numéro si le fichier existe : jamais écrasé), une ligne par cours
suivi d'un trimestre de l'année, avec la décision lue par scripts/speculer.py (directive « #suivis ») :
  unité ............ le cours confirme une unité du catalogue (enseignant commun et mot du titre commun avec le titre
                     retenu ou un candidat) : ce trimestre-là, chance 1, et le titre est celui qu'a suivi l'étudiant
  nouveau .......... enseignant identifié, cours absent du catalogue de l'année : unité ajoutée pour ce trimestre ;
                     si le même titre est au catalogue sous un autre enseignant du corps enseignant, au même trimestre,
                     cette unité est « contredite » (colonne unite_contredite) : chance ramenée à 1/2 ce trimestre-là
  unité (discipline)  le cours ne partage avec le catalogue qu'un mot de discipline (« Music », « Dance ») et une seule
                     unité de l'enseignant y correspond : le trimestre est confirmé, pas le titre
  discipline (plusieurs unités)  idem, mais plusieurs unités de l'enseignant y correspondent : listé seulement
  non rattaché ..... enseignant non nommé ou non identifié : listé seulement
  unité hors trimestre  cours d'une unité du catalogue, mais suivi un trimestre où l'unité n'est pas programmée :
                     une unité est ajoutée pour ce trimestre (même titre)
Rattachement : titre du catalogue d'abord, puis ses équivalents des années voisines (catalogues par domaines,
1951-52 : « Mathematics » ← « Geometry; Calculus (Dehn, 1950-51) ») ; une unité sans enseignant (« — ») dont le titre
correspond reçoit l'enseignant de la fiche (enseignant_precise).
Contradiction retenue seulement si l'attribution du catalogue est elle-même une déduction : code R_ELIM, R_SEUL,
R_NOMME, R_COMPET ou R_DUBERMAN, ou source qui nomme les deux enseignants pour la discipline (« Philosophy: Levi;
Dehn ») ; sinon deux enseignants ont pu donner chacun un cours du même nom (French : Goldowski et Shepard).
Variantes de noms corrigées (évidentes) : table VARIANTES ci-dessous ; « Jennerjahn » seul est rattaché à Warren ou à
Elizabeth d'après le titre (danse → Elizabeth).
"""
import csv, glob, os, re, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verifier_sources as V

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TERME = {"automne": "fall", "printemps": "spring", "été": "summer", "hiver": "winter"}
VARIANTES = {"sheppard": "Shepard", "vilente": "Vicente", "wolfe": "Wolpe", "volfe": "Wolpe", "stefan volfe": "Wolpe",
             "hilda wolpe": "Morley", "madame goldowski": "Anna Goldowski", "creely": "Creeley", "jones": "Jones",
             "doyle jones": "Jones", "wes huss": "Huss", "hazel larsen": "Larsen", "esteban vicente": "Vicente",
             "merce cunningham": "Cunningham", "warren mackenzie": "MacKenzie", "mccaudles": "McCandless",
             "lesser": "Leser", "goldowsky": "Goldowski", "larson": "Larsen", "hazel": "Larsen", "billings": "Billing",
             "clement": "Greenberg", "greensberg": "Greenberg", "mcrichards": "Richards", "mc richards": "Richards",
             # prénoms seuls, rattachés par le même cours au même trimestre (à confirmer) : « Algebra with Truman » et
             # « Algebra with Truman MacHenry » (étudiant), printemps 1950 ; « Social Science with William » et
             # « Intro to Social Science with Levi » (Albert William Levi), printemps 1950
             "truman": "MacHenry", "william": "Levi", "jalowitz": "Jalowetz", "shephard": "Shepard", "volkos": "Voulkos"}
# champ « enseignant » ou « cours » qui a avalé la suite de la fiche (« Dehn Transcript reads… », « Litz  Obituary: … »)
DEBORDE = re.compile(r"transcript|obituary|graduated|dropped all|meetings|\bterm\b.*:|\(\d\d-\d\d\)|:", re.I)
HORS_COURS = re.compile(r"work program|work scholarship|transcript|maintenance|bookkeeping|book keeping|farm work|farm labou?r|to be arranged", re.I)
PAS_UN_NOM = {"unknown", "unlisted", "staff", "arranged", "various", "none"}
VIDES_TITRE = {"introduction", "introductory", "course", "class", "classes", "elementary", "advanced", "beginning",
               "beginners", "intermediate", "general", "lessons", "tutorial", "study", "with", "basic", "work"}


ABREGES = {"math": "mathematics", "maths": "mathematics", "intro": "introduction", "lit": "literature", "lit.": "literature",
           "phil": "philosophy", "anthro": "anthropology", "chem": "chemistry", "bio": "biology"}


def mots(s):
    return {ABREGES.get(w, w) for w in re.findall(r"[a-z]{3,}", V.plat(s)) if len(ABREGES.get(w, w)) >= 4} - VIDES_TITRE


# mots de discipline : ils disent le domaine, pas le cours (« Methods of Anthropology » n'est pas « Introduction to
# General Anthropology ») ; tirés des disciplines de tous les catalogues spéculatifs, plus quelques mots de domaine
GENERIQUES = {"history", "studies", "theory", "seminar", "workshop", "arts", "music", "musical"}
for _p in glob.glob(os.path.join(ROOT, "speculation", "catalogues", "*.txt")):
    for _l in open(_p, encoding="utf-8"):
        if _l.startswith("C|"): GENERIQUES |= mots(_l.split("|")[2])


def specifiques(s): return mots(s) - GENERIQUES


def proche(a, b, domaine=False):
    """titres proches : un mot significatif commun (hors mots de discipline), ou l'un contenu dans l'autre sans les
    espaces (« Book Binding ») ; domaine=True : mots de discipline seuls admis."""
    if specifiques(a) & specifiques(b): return 1 + len(specifiques(a) & specifiques(b))
    if mots(a) and mots(a) == mots(b): return 2          # même titre (« French », « Writing », « Advanced Physics »)
    if len(mots(a)) >= 2 and mots(a) <= mots(b): return 2   # « Social Philosophy » ⊂ « Social Philosophy Today »
    if domaine: return 1 if mots(a) & mots(b) else 0
    x, y = re.sub(r"[^a-z]", "", V.plat(a)), re.sub(r"[^a-z]", "", V.plat(b))
    return 1 if len(x) > 5 and len(y) > 5 and (x in y or y in x) and (domaine or x == y or (specifiques(a) and specifiques(b))) else 0


def nom_ens(brut, titre):
    b = re.sub(r"\[.*?\]|\(.*?\)|\?", "", brut or "").split("&")[0].split(" and ")[0].strip(" .,/")
    if not b or len(b.replace(".", "")) <= 2 or b == "?": return ""
    k = V.plat(b)
    if k in PAS_UN_NOM: return ""
    if k in VARIANTES: return VARIANTES[k]
    if "jennerjahn" in k: return "E. Jennerjahn" if re.search(r"danc", V.plat(titre)) else "W. Jennerjahn"
    w = re.findall(r"[A-Za-zÀ-ÿ\-']+", b)
    if w and V.plat(w[-1]) in PAS_UN_NOM: return ""
    return VARIANTES.get(V.plat(w[-1]), w[-1]) if w and len(w[-1]) >= 3 else ""


def lire_catalogue(p):
    C, U = {}, []
    for l in open(p, encoding="utf-8"):
        if l.startswith("C|"):
            f = l.rstrip("\n").split("|"); C[f[1]] = {"titre": f[3], "equiv": f"{f[4]} {f[5]}"}
        elif l.startswith("U|"):
            f = l.rstrip("\n").split("|")[1:]; f += [""] * (12 - len(f))
            U.append({"unite": f[0], "qui": f[1], "codes": f[3], "retenu": f[4].split("+"), "candidats": [x for x in f[6].split(";") if x],
                      "rattachement": f[8], "termes": f[11]})
    return C, U


def actif(u, t):
    """l'unité est-elle programmée au trimestre t ? (même règle que speculer.py : sans termes, toute l'année sauf l'été)"""
    if not u["termes"]: return t != "summer"
    return t in {x.split("@")[0].strip() for x in u["termes"].split(",")}


def noms_u(u): return {V.plat(x.strip().split()[-1]) for x in u["qui"].split(";") if x.strip() and x.strip() != "—"}


def equiv(cours, c):
    """rapprochement par les équivalents des années voisines (sans les noms d'enseignants entre parenthèses)."""
    return proche(cours, re.sub(r"\([^)]*\)", " ", c["equiv"]))


def main():
    src = sorted(glob.glob(os.path.join(ROOT, "chronos", "[0-9][0-9][0-9]_personnes_cours_suivis.csv")))[-1]
    rows = list(csv.DictReader(open(src, encoding="utf-8")))
    annees = sys.argv[1:] or ["1949-50", "1950-51", "1951-52", "1952-53", "1953-54", "1954-55"]
    os.makedirs(os.path.join(ROOT, "speculation", "suivis"), exist_ok=True)
    for an in annees:
        C, U = lire_catalogue(os.path.join(ROOT, "speculation", "catalogues", f"{an}.txt"))
        # cours suivis du même cours (même enseignant, même titre) réunis par trimestre
        groupes = collections.OrderedDict()
        for r in rows:
            if r["annee_scolaire"] != an: continue
            s, _ = r["trimestre"].split(" ", 1); t = TERME.get(s, s)
            e = nom_ens(r["enseignant"], r["cours"])
            k = (t, V.plat(e), V.plat(re.sub(r"\[.*?\]", "", r["cours"])).strip())
            g = groupes.setdefault(k, {"terme": t, "enseignant_brut": r["enseignant"], "enseignant": e, "cours": r["cours"], "etudiants": []})
            if r["etudiant"] not in g["etudiants"]: g["etudiants"].append(r["etudiant"])
        out = []
        corps = {n for u in U for n in noms_u(u)}
        for g in groupes.values():
            e, t = g["enseignant"], g["terme"]
            dec, unite, cid, titre, contredit, precise = "non rattaché", "", "", "", "", ""
            if HORS_COURS.search(g["cours"]): dec = "hors cours (travail)"
            elif DEBORDE.search(g["enseignant_brut"]) or DEBORDE.search(g["cours"]) or V.plat(e) in {"bmc", "agriculture"}:
                dec = "non rattaché (fiche mal découpée)"
            elif e:
                en = V.plat(e.split()[-1])
                cands = [u for u in U if en in noms_u(u)
                         and (not e[0:2].endswith(".") or V.plat(e[0]) in {V.plat(x.strip()[0]) for x in u["qui"].split(";") if x.strip()})]
                best = None
                # score : titre (×10) > équivalent ; unité programmée ce trimestre-là d'abord
                for u in cands + [u for u in U if not noms_u(u)]:
                    for c_id in u["retenu"] + u["candidats"]:
                        n = 10 * proche(g["cours"], C[c_id]["titre"]) or equiv(g["cours"], C[c_id])
                        if not n: continue
                        if not noms_u(u) and n < 10: continue          # unité sans enseignant : titre exigé
                        sc = (actif(u, t), bool(noms_u(u)), n)
                        if best is None or sc > best[0]: best = (sc, u, c_id)
                # sinon, par la discipline seule : l'unité est sûre si une seule unité de l'enseignant y correspond
                dom = {u["unite"]: (u, c_id) for u in cands for c_id in u["retenu"] + u["candidats"]
                       if proche(g["cours"], C[c_id]["titre"], True) or proche(g["cours"], re.sub(r"\([^)]*\)", " ", C[c_id]["equiv"]), True)}
                dom_actif = {k: v for k, v in dom.items() if actif(v[0], t)} or dom
                if best:
                    u = best[1]; unite, cid, titre = u["unite"], best[2], C[best[2]]["titre"]
                    dec = "unité" if actif(u, t) else "unité hors trimestre"
                    if not noms_u(u): precise = e
                elif len(dom_actif) == 1:
                    u, c_id = list(dom_actif.values())[0]; unite, cid = u["unite"], c_id
                    titre = " | ".join(C[x]["titre"] for x in u["retenu"] + u["candidats"])
                    dec = "unité (discipline)" if actif(u, t) else "unité hors trimestre"
                elif dom_actif:
                    dec = "discipline (plusieurs unités)"; titre = " ; ".join(f"{k} {C[v[1]]['titre']}" for k, v in dom_actif.items())
                else:
                    dec = "nouveau"
                    # même titre au catalogue sous un autre enseignant, même trimestre, attribution déduite : contredite
                    mc_ = mots(g["cours"])
                    autres = [(len(mc_), u, c_id) for u in U if u not in cands and noms_u(u) and en in corps and mc_ and actif(u, t)
                              and (re.search(r"R_(ELIM|SEUL|NOMME|COMPET|DUBERMAN)", u["codes"]) or en in V.plat(u["rattachement"]))
                              for c_id in u["retenu"] + u["candidats"] if mc_ <= mots(C[c_id]["titre"])]
                    if autres:
                        a = max(autres, key=lambda a: a[0]); contredit = a[1]["unite"]
                        titre = f"{C[a[2]]['titre']} (au catalogue sous {a[1]['qui']})"
            out.append({"terme": t, "enseignant_brut": g["enseignant_brut"], "enseignant": e, "cours": g["cours"],
                        "etudiants": "; ".join(g["etudiants"]), "n": len(g["etudiants"]), "decision": dec,
                        "unite": unite, "id_catalogue": cid, "titre_catalogue": titre, "unite_contredite": contredit,
                        "enseignant_precise": precise})
        p = os.path.join(ROOT, "speculation", "suivis", f"{an}.csv"); k = 2
        while os.path.exists(p): p = os.path.join(ROOT, "speculation", "suivis", f"{an}_{k}.csv"); k += 1
        with open(p, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
        N = collections.Counter(o["decision"] for o in out)
        print(f"{an} : {len(out)} cours suivis distincts ({sum(o['n'] for o in out)} inscriptions) — " + ", ".join(f"{a} {b}" for a, b in N.most_common()) + f" → {os.path.relpath(p, ROOT)}")


if __name__ == "__main__":
    main()
