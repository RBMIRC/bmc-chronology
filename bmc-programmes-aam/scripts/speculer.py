"""Couche spéculative, année scolaire par année scolaire.
Entrée : speculation/annees/AAAA-AA.txt (format speculation/_FORMAT.txt) et, par la directive « #catalogue »,
la concordance des cours de l'année (speculation/catalogues/AAAA-AA.txt).
Pour chaque trimestre (ou semestre) attesté de l'année, le script construit UN gabarit de semaine : les activités
placées à la main (lignes S) et les cours (lignes U) répartis selon les règles ci-dessous ; puis il applique ce gabarit
à chaque semaine de cours du trimestre, jour de cours par jour de cours (calendrier.py), sauf aux semaines déjà
complètes en données attestées. Rien ne distingue une semaine d'une autre dans les sources : le gabarit se répète.

Sorties (programme/speculatif/) :
  annee_AAAA-AA.md             analyse, barème, gabarit de chaque trimestre, semaines couvertes
  annee_AAAA-AA_gabarits.csv   une ligne par entrée de gabarit (trimestre, jour, heures, sources, part déduite…)
  annee_AAAA-AA_semaines.csv   une ligne par semaine reconstituée (trimestre, lundi, jours de cours)
  catalogue_AAAA-AA_concordance.csv/.md   chaque cours du catalogue : où il est, ou pourquoi il n'y est pas

Part déduite d'une case de cours = case (somme des codes) combinée au titre (100 × (1 − chance)) :
  total = 100 × (1 − (1 − case) × (1 − titre)), plafonné à 90 %.
Répartition (modèle : grille attestée de l'automne 1944, 2017.40.176a-h ; reprise des cours à 16 h, catalogue 1936-38) :
  3 h = 2 × 90 min, 4 h = 2 × 120 min, 2 h = 1 × 120 min, 1 h = 1 × 60 min ; début 08:30 ou 10:30, ou 16:00 ;
  samedi : matin seulement ; laboratoires : 16:00 en semaine ; deux séances d'un cours sur des jours non consécutifs ;
  jamais deux séances à la fois pour un enseignant ; créneaux les moins chargés d'abord ; ordre déterministe."""
import csv, os, re, sys, datetime as dt, collections
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calendrier
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC, OUT = os.path.join(ROOT, "speculation"), os.path.join(ROOT, "programme", "speculatif")

CODES = {
    "MEME_ANNEE": (0, "cours ou activité attesté pour l'année même"),
    "DIT_1935": (0, "le catalogue 1936-38 le dit offert « last year » (1935-36)"),
    "SEMAINE": (10, "présence cette semaine-là déduite d'un rythme régulier (hebdomadaire, quotidien, cours de toute l'année)"),
    "VOISIN": (10, "structure (heures, semestres) ou usage pris dans une année voisine"),
    "LOIN": (25, "transposé d'une période éloignée ou d'un autre campus"),
    "R_ATTESTE": (0, "enseignant nommé pour ce cours dans le catalogue de l'année"),
    "R_SEUL": (5, "enseignant rattaché par sa discipline : seul enseignant de cette matière au catalogue"),
    "R_NOMME": (5, "enseignant rattaché par sa discipline et nommé pour ce cours (ou son équivalent) dans une année voisine"),
    "R_ELIM": (10, "enseignant rattaché par élimination entre collègues de la même discipline"),
    "R_COMPET": (20, "enseignant inconnu ou rattaché par simple compétence"),
    "EQUIV": (10, "équivalence de titre avec une année voisine probable mais non certaine"),
    "VOLUME": (10, "volume horaire supposé (non donné pour ce cours)"),
    "OCCASION": (25, "activité occasionnelle, mensuelle ou « à la demande » : rien ne dit qu'elle tombe cette semaine"),
    "JOUR": (20, "jour choisi par moi"),
    "HEURE_CADRE": (10, "heure choisie par moi dans un créneau attesté (matin, après-midi de cours, après le dîner, samedi soir)"),
    "HEURE": (20, "heure choisie par moi sans source"),
    "LISTE_VOISINE": (15, "liste de cours de l'année précédente : celle de l'année n'est pas lisible dans le corpus"),
    "TERME_DEDUIT": (15, "liste de cours donnée pour d'autres trimestres de l'année, reconduite pour celui-ci"),
    "PRESENCE": (15, "présence de l'enseignant pendant tout le trimestre non attestée"),
    # ajoutés le 1/11/2026 pour 1951-57 (sans effet sur les années précédentes, qui ne les emploient pas)
    "R_DUBERMAN": (10, "enseignant rattaché d'après Duberman (texte corrigé), pas d'après un document de l'année"),
    "ANNONCE": (15, "domaine annoncé à l'avance (« fields represented will be… ») : cours réel non attesté"),
    # ajouté le 2/11/2026 : directive « #suivis » (scripts/suivis_speculation.py)
    "SUIVI": (0, "cours suivi ce trimestre-là d'après les fiches d'étudiants (BMC Yearbook, bmcyearbook.org)"),
    # ajouté le 2/11/2026 : lignes Q (cours d'une période sans gabarit, ex. tissage de l'été 1943)
    "CONDITION": (25, "cours annoncé sous condition (« if enough students ») : tenue non attestée"),
}
JOURS = ["lun", "mar", "mer", "jeu", "ven", "sam", "dim"]
NOMS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
PAIRES = [("lun", "jeu"), ("mar", "ven"), ("mer", "sam"), ("lun", "mer"), ("mar", "jeu"), ("mer", "ven")]
MATIN, APREM = ["08:30", "10:30"], ["16:00"]
SAISONS_FR = {"fall": "automne", "winter": "hiver", "spring": "printemps", "summer": "été", "": "période"}

def somme(codes):
    pts, mot = 0, []
    for c in codes:
        p, m = CODES[c]; pts += p; mot.append(f"{m} (+{p})")
    return min(pts, 90), mot

def mn(h): return int(h[:2]) * 60 + int(h[3:])
def hm(m): return f"{m // 60:02d}:{m % 60:02d}"

def jours(tok):
    if tok == "semaine": return ["semaine"]
    if "-" in tok:
        a, b = tok.split("-"); return JOURS[JOURS.index(a):JOURS.index(b) + 1]
    return tok.split(",")

def lire_csv(p):
    with open(p, encoding="utf-8") as f: return list(csv.DictReader(f))

def docs():
    return {p["accession"]: (f"{p['titre']} [{p['date']}] (inv. {p['accession']})", p["url"])
            for p in lire_csv(os.path.join(ROOT, "liste_pages.csv"))}

TRIPLES = [("lun", "mer", "ven"), ("mar", "jeu", "sam")]
PERIODES = None     # « #periodes » : périodes de cours de l'année (ex. 1942-43 : 55 min à 8:15, 9:20, 10:25, 11:30)

def seances(vol):
    out = []
    for part in vol.split("+"):
        if "x" in part:   # « 2x90 » : nombre de séances et durée donnés par la source (ex. « two 1½-hour periods »)
            lab = part.endswith("L"); k, d = part.rstrip("L").split("x"); out.append((int(k), int(d), lab)); continue
        lab = part.endswith("L"); n = int(part.rstrip("L"))
        if PERIODES and not lab:   # une heure de cours = une période ; 4 h = deux doubles périodes
            n_s, dur = {1: (1, PERIODES), 2: (2, PERIODES), 3: (3, PERIODES), 4: (2, 2 * PERIODES + 10)}[n]
        else:
            n_s, dur = {1: (1, 60), 2: (1, 120), 3: (2, 90), 4: (2, 120)}[n]
        out.append((n_s, dur, lab))
    return out

CHAMPS_U = ["unite", "qui", "vol", "codes", "retenu", "precision", "candidats", "chance", "rattachement", "place", "note", "termes"]

def lire_catalogue(path):
    C, U, N, entete = {}, [], {}, []
    for l in open(path, encoding="utf-8"):
        l = l.rstrip("\n")
        if l.startswith("# Sources") or l.startswith("#   "): entete.append(l[1:].strip())
        if l.startswith("C|"):
            _, i, disc, titre, e_av, e_ap = l.split("|")
            if i in C: sys.exit(f"id en double : {i}")
            C[i] = dict(id=i, disc=disc, titre=titre, e_av=e_av, e_ap=e_ap)
        elif l.startswith("U|"):
            f = l.split("|")[1:]
            if len(f) not in (11, 12): sys.exit(f"ligne U mal formée ({len(f)} champs) : {l[:80]}")
            U.append(dict(zip(CHAMPS_U, f + [""] * (12 - len(f)))))
        elif l.startswith("N|"):
            _, i, r = l.split("|", 2); N[i] = r
    vus = set()
    for u in U:
        for i in u["retenu"].split("+") + [x for x in u["candidats"].split(";") if x]:
            if i not in C: sys.exit(f"id inconnu dans {u['unite']} : {i}")
            vus.add(i)
        Fraction(u["chance"] or "1")
    for i in N:
        if i not in C: sys.exit(f"id inconnu (N) : {i}")
    manque = [i for i in C if i not in vus and i not in N]
    if manque: sys.exit(f"cours du catalogue non rattachés : {manque}")
    return C, U, N, entete

# Directive « #suivis speculation/suivis/AAAA-AA.csv » (ajout du 2/11/2026) : les cours suivis des fiches d'étudiants
# (BMC Yearbook, bmcyearbook.org/biographies, « Courses Taken », via scripts/chronos_personnes.py puis
# scripts/suivis_speculation.py) disent le trimestre d'un cours. Règles :
#  - unité suivie ce trimestre-là : chance 1, titre = celui qu'a suivi l'étudiant (s'il est l'un des candidats) ;
#    codes de rattachement déduit, de trimestre reconduit ou de domaine annoncé retirés ; R_ATTESTE + SUIVI ;
#  - unité suivie un autre trimestre de l'année, mais d'aucune fiche ce trimestre-ci (alors que des fiches existent
#    pour ce trimestre) : chance ramenée à 1/2 au plus ; si de plus le titre est donné à un autre enseignant par une
#    fiche du même trimestre (attribution « contredite ») : 1/3 au plus ; contredite seulement : 1/2 au plus ;
#  - cours absent du catalogue, ou cours d'une unité qui n'est pas programmée ce trimestre-là : unité ajoutée pour ce
#    seul trimestre (id « suivi.N », unité « SN »), enseignant de la fiche, volume supposé (VOLUME) ;
#  - unité sans enseignant (« — ») dont une fiche donne le titre : l'enseignant de la fiche lui est donné.
RETIRES_SI_SUIVI = {"R_ELIM", "R_SEUL", "R_NOMME", "R_COMPET", "R_DUBERMAN", "TERME_DEDUIT", "LISTE_VOISINE", "ANNONCE", "PRESENCE", "EQUIV"}
ATELIER = re.compile(r"weav|ceram|potter|print|photo|wood|bookbind|sculpt|litho|graphic|carpent|silk", re.I)
TUTORAT = re.compile(r"tutori|lesson|private|individual|thesis|independent|\bproject", re.I)

def lire_suivis(chemin, C, U):
    rows = lire_csv(os.path.join(ROOT, chemin))
    par_u = {u["unite"]: u for u in U}
    complet = {}                               # nom de famille → nom complet, d'après le catalogue de l'année
    for u in U:
        for q in u["qui"].split(";"):
            q = q.strip()
            if q and q != "—": complet.setdefault((q.split()[-1].lower(), q[0].lower()), q); complet.setdefault((q.split()[-1].lower(), ""), q)
    def nom(e):
        if not e: return ""
        ini = e[0].lower() if e[1:2] == "." else ""
        if len(e.split()) > 1 and not ini:      # prénom donné (« Anna Goldowski ») : nom complet du catalogue s'il a ce prénom
            return next((q for q in complet.values() if q.lower().split()[0] == e.lower().split()[0] and q.lower().split()[-1] == e.lower().split()[-1]), e)
        return complet.get((e.split()[-1].lower(), ini)) or complet.get((e.split()[-1].lower(), "")) or e
    def cle_mots(x): return frozenset(w for w in re.findall(r"[a-z]{3,}", x.lower()) if w not in {"and", "the", "with", "tutorial"})
    def qui_suit(rs):
        et = []
        for r in rs:
            for x in r["etudiants"].split("; "):
                if x not in et: et.append(x)
        cours = "; ".join(dict.fromkeys(f"« {r['cours']} » avec {r['enseignant_brut']}" for r in rs))
        return f"suivi par {len(et)} étudiant(s) : {', '.join(et[:6])}{' …' if len(et) > 6 else ''} ({cours} ; BMC Yearbook)"
    preuve, contre, nouveaux = collections.defaultdict(list), collections.defaultdict(list), collections.OrderedDict()
    termes_suivis = collections.Counter()
    for r in rows:
        d, t = r["decision"], r["terme"]
        if d in ("unité", "unité (discipline)", "discipline (plusieurs unités)", "unité hors trimestre", "nouveau"): termes_suivis[t] += 1
        if d in ("unité", "unité (discipline)"):
            preuve[(r["unite"], t)].append(r)
            u = par_u[r["unite"]]
            if r["enseignant_precise"] and u["qui"].strip() in ("", "—"):
                u["qui"] = nom(r["enseignant_precise"]); u["rattachement"] += f" ; enseignant d'après une fiche d'étudiant : {r['enseignant_brut']}"
        elif d == "unité hors trimestre":
            nouveaux.setdefault((t, "u", r["unite"]), []).append(r)
        elif d == "nouveau":
            nouveaux.setdefault((t, nom(r["enseignant"]), cle_mots(re.sub(r"\[.*?\]", "", r["cours"]))), []).append(r)
            if r["unite_contredite"]: contre[(r["unite_contredite"], t)].append(r)
    def actif(u, t):
        return t != "summer" if not u["termes"] else t in {x.split("@")[0].strip() for x in u["termes"].split(",")}
    SV = {}
    for u in U:
        prouves = {t for (x, t) in preuve if x == u["unite"]}
        for t in ("fall", "winter", "spring", "summer"):
            if not actif(u, t): continue
            o = {}
            if (u["unite"], t) in preuve:
                rs = preuve[(u["unite"], t)]; titres = [r for r in rs if r["decision"] == "unité"]
                if titres:      # titre confirmé
                    cid = collections.Counter(r["id_catalogue"] for r in titres).most_common(1)[0][0]
                    o = {"chance": "1", "ids": [cid] if cid not in u["retenu"].split("+") else None, "suivi": qui_suit(rs)}
                else:           # discipline seule : le trimestre est sûr, le titre reste à choisir parmi les candidats
                    n_t = 1 + len([x for x in u["candidats"].split(";") if x])
                    o = {"chance": str(max(Fraction(u["chance"] or "1"), Fraction(1, n_t))), "ids": None,
                         "suivi": qui_suit(rs) + (f" ; titre non précisé : 1 chance sur {n_t}" if n_t > 1 else "")}
            else:
                lim, mot = None, []
                if prouves and termes_suivis[t]:
                    lim = Fraction(1, 2); mot.append(f"suivi d'après les fiches d'étudiants en {', '.join(SAISONS_FR[x] for x in sorted(prouves))}, d'aucune fiche ce trimestre-ci")
                if (u["unite"], t) in contre:
                    rs = contre[(u["unite"], t)]
                    lim = Fraction(1, 3) if lim else Fraction(1, 2)
                    mot.append("titre suivi ce trimestre-là avec un autre enseignant : " + "; ".join(f"« {r['cours']} » avec {r['enseignant_brut']} ({r['etudiants']})" for r in rs))
                if lim is not None:
                    o = {"chance": str(min(Fraction(u["chance"] or "1"), lim)), "ids": None, "baisse": " ; ".join(mot)}
            if o: SV[(u["unite"], t)] = o
    k = 0
    for (t, qui, x), rs in nouveaux.items():
        k += 1; i = f"suivi.{k}"; r0 = rs[0]
        if qui == "u":
            u0 = par_u[x]; cid = r0["id_catalogue"]
            C[i] = dict(C[cid], id=i); qui_n, vol, place = u0["qui"], u0["vol"], u0["place"]
            ratt = f"cours de l'unité {x} ({C[cid]['titre']}, {u0['qui']}), suivi un trimestre où elle n'est pas programmée"
        else:
            titre = re.sub(r"\s*\[.*?\]", "", r0["cours"]).strip()
            C[i] = dict(id=i, disc="Cours suivis (fiches d'étudiants)", titre=titre, e_av="—", e_ap="—")
            qui_n, place = qui, ""; vol = "1x120L" if ATELIER.search(titre) else "1" if TUTORAT.search(titre) else "3"
            ratt = f"enseignant nommé par la fiche d'étudiant ({r0['enseignant_brut']})"
            if r0["unite_contredite"]: ratt += f" ; même titre au catalogue sous un autre enseignant : {r0['titre_catalogue']}"
        U.append(dict(unite=f"S{k}", qui=qui_n, vol=vol, codes="MEME_ANNEE+R_ATTESTE+SUIVI+VOLUME", retenu=i, precision="",
                      candidats="", chance="1", rattachement=ratt, place=place, note=qui_suit(rs)[0].upper() + qui_suit(rs)[1:], termes=t))
    return SV, rows

def semaines_completes():
    """lundis des semaines déjà complètes en données attestées (même critère que l'audit)."""
    par = collections.defaultdict(list)
    for e in lire_csv(os.path.join(ROOT, "programme", "evenements.csv")):
        x = dt.date.fromisoformat(e["date"]); par[x - dt.timedelta(x.weekday())].append(e)
    out = set()
    for lun, es in par.items():
        cours = [e for e in es if e["type"] in ("cours", "atelier")]
        jc = {e["date"] for e in cours if dt.date.fromisoformat(e["date"]).weekday() < 6}
        if len(jc) >= 5 and len(cours) >= 15: out.add(lun)
    return out

def traiter(path):
    global MATIN, APREM, PERIODES
    MATIN, APREM, PERIODES = ["08:30", "10:30"], ["16:00"], None    # valeurs par défaut, remplacées par « #periodes »
    annee, analyse, S, Q, cat, deduits, suivis = None, [], [], [], None, {}, None
    for l in open(path, encoding="utf-8"):
        l = l.rstrip("\n")
        if l.startswith("#annee"): annee = l.split()[1]
        elif l.startswith("#catalogue"): cat = l.split(None, 2)[1:]
        elif l.startswith("#terme_deduit"): deduits[l.split()[1]] = True
        elif l.startswith("#suivis"): suivis = l.split()[1]
        elif l.startswith("#periodes"):   # #periodes 08:15,09:20,10:25,11:30 16:00 55
            _, m_, a_, d_ = l.split(); MATIN, APREM, PERIODES = m_.split(","), a_.split(","), int(d_)
        elif l.startswith(">"): analyse.append(l[2:] if len(l) > 1 else "")
        elif l.startswith("S|"):
            f = l.split("|")[1:]
            if len(f) not in (10, 11): sys.exit(f"ligne S mal formée ({len(f)} champs) : {l[:80]}")
            S.append(f + [""] * (11 - len(f)))
        elif l.startswith("Q|"):      # Q|… comme S|… + motif (regex, peut contenir « | ») des activités attestées qui la remplacent
            f = l.split("|", 12)[1:]
            if len(f) not in (10, 11, 12): sys.exit(f"ligne Q mal formée ({len(f)} champs) : {l[:80]}")
            Q.append(f + [""] * (12 - len(f)))
    a0 = int(annee[:4]); debut_an, fin_an = dt.date(a0, 9, 1), dt.date(a0 + 1, 8, 31)
    cal = calendrier.charger(spec=True); compl = semaines_completes(); D = docs()
    D["BMCYearbook"] = ("BMC Yearbook, biographies, rubrique « Courses Taken » (bmcyearbook.org/biographies, Black Mountain "
                        "College Museum + Arts Center ; copie DATA_BMC/bmcyearbook, dépouillée par scripts/chronos_personnes.py)",
                        "https://bmcyearbook.org/biographies")
    C, U, N, entete, src_cat = {}, [], {}, [], ""
    if cat:
        C, U, N, entete = lire_catalogue(os.path.join(ROOT, cat[0])); src_cat = cat[1] if len(cat) > 1 else ""
    SV, suivis_rows, n_cat = {}, [], len(U)
    if suivis: SV, suivis_rows = lire_suivis(suivis, C, U)

    # trimestres de l'année : jours de cours groupés par (saison, libellé)
    termes = collections.OrderedDict()
    x = debut_an
    while x <= fin_an:
        if calendrier.jour_de_cours(cal, x):
            s, lib = cal["terme"][x]
            termes.setdefault((s, lib), []).append(x)
        x += dt.timedelta(1)
    # un même trimestre peut apparaître sous plusieurs libellés (annonce, dates effectives) : fusion par saison
    fus = collections.OrderedDict()
    for (s, lib), js in termes.items():
        k = s or lib
        fus.setdefault(k, {"saison": s, "libelles": [], "jours": []})
        fus[k]["libelles"].append(lib); fus[k]["jours"] += js

    def bornes(champ, s):
        out = []
        for tok in [t.strip() for t in (champ or "").split(",") if "@" in t]:
            ss, b = tok.split("@"); a, z = b.split("..")
            if ss == s: out += [dt.date.fromisoformat(a), dt.date.fromisoformat(z) + dt.timedelta(1)]
        return out
    def pour(champ, s, deb, fin, defaut):
        if not champ: return defaut
        for tok in [t.strip() for t in champ.split(",")]:
            ss, _, b = tok.partition("@")
            if ss != s: continue
            if not b: return True
            a, z = b.split(".."); 
            if dt.date.fromisoformat(a) <= deb and fin <= dt.date.fromisoformat(z): return True
        return False
    sous = []
    for k, T in fus.items():
        s = T["saison"]; jours_t = sorted(set(T["jours"]))
        cuts = sorted({c for u in U for c in bornes(u["termes"], s)} | {c for x in S for c in bornes(x[10], s)})
        morceaux, cur = [], []
        for x in jours_t:
            if cur and any(cur[-1] < c <= x for c in cuts): morceaux.append(cur); cur = []
            cur.append(x)
        if cur: morceaux.append(cur)
        lundis_saison = sorted({x - dt.timedelta(x.weekday()) for x in jours_t})
        for i, m in enumerate(morceaux):
            cle_t = (s or k) + (f"#{i + 1}" if len(morceaux) > 1 else "")
            lib_t = f"{annee}, {SAISONS_FR.get(s, s)}" + (f" ({m[0].strftime('%d/%m/%Y')} – {m[-1].strftime('%d/%m/%Y')})" if len(morceaux) > 1 else "")
            sous.append((cle_t, s, lib_t, m, lundis_saison))

    def allouer(saison, morceaux, avant):
        """répartit une seule fois, pour toute la saison, les unités valables dans au moins un morceau.
        place « =UNITE » : mêmes créneaux que l'unité nommée (reprise d'un cours par un autre enseignant)."""
        occ = {j: {} for j in JOURS}; charge = {}
        def libre(qui, j, a, b): return all(not (a < y and x_ < b) for q in qui for x_, y in occ[j].get(q, []))
        def prendre(qui, j, a, b):
            for q in qui: occ[j].setdefault(q, []).append((a, b))
            charge[(j, hm(a))] = charge.get((j, hm(a)), 0) + 1
        for jt, a, b, typ, quoi, qui, lieu, note, codes, sources, tm in S:
            if a and any(pour(tm, saison, m[0], m[-1], True) for m in morceaux):
                for j in jours(jt):
                    if j != "semaine": prendre([q.strip() for q in qui.split(";") if q.strip()], j, mn(a), mn(b or a))
        us = [u for u in U if any(pour(u["termes"], saison, m[0], m[-1], saison != "summer") for m in morceaux)]
        poses_de = {}
        # ordre : placements fixes, puis unités avec laboratoire (les labos n'ont que les après-midi), puis les autres,
        # puis les reprises « =UNITE »
        ordre = sorted(us, key=lambda u: 0 if (u["place"] and not u["place"].startswith("=")) else 3 if u["place"].startswith("=")
                       else 0.5 if u["unite"] in avant else 1 if "L" in u["vol"] else 2)
        for u in ordre:
            ps = [q.strip() for q in u["qui"].split(";") if q.strip()]; poses = []
            if u["place"].startswith("="):
                ref = poses_de.get(u["place"][1:]) or avant.get(u["place"][1:], [])
                # reprise dans la même saison (sous-périodes successives) : l'unité visée n'a pas lieu en même temps,
                # ses créneaux sont donc repris même s'ils sont occupés par le même enseignant
                meme_saison = u["place"][1:] in poses_de
                if ref and (meme_saison or all(libre(ps, j, mn(a), mn(b)) for j, a, b, _ in ref)):
                    for j, a, b, lab in ref: prendre(ps, j, mn(a), mn(b)); poses.append((j, a, b, lab))
                    poses_de[u["unite"]] = poses; continue
            if u["place"] and not u["place"].startswith("="):
                # « jeu 20:00-21:30 », ou plusieurs créneaux : « mar,jeu 10:30-13:00;ven 10:30-12:00 »
                for grp in u["place"].split(";"):
                    js, h = grp.split(); a, b = h.split("-")
                    for j in js.split(","): prendre(ps, j, mn(a), mn(b)); poses.append((j, a, b, False))
            elif u["unite"] in avant and avant[u["unite"]] and all(libre(ps, j, mn(a), mn(b)) for j, a, b, _ in avant[u["unite"]]):
                # cours de toute l'année : mêmes créneaux qu'au trimestre précédent
                for j, a, b, lab in avant[u["unite"]]: prendre(ps, j, mn(a), mn(b)); poses.append((j, a, b, lab))
            else:
                pris = set()
                parts = seances(u["vol"])
                avec_lab = any(l for _, _, l in parts) or bool(set(ps) & profs_labo)   # garder les après-midi libres pour les labos
                for n_s, dur, lab in sorted(parts, key=lambda p: not p[2]):     # le laboratoire d'abord
                    best = None
                    heures = APREM if lab else (MATIN if avec_lab else MATIN + APREM)
                    grp = TRIPLES if n_s == 3 else PAIRES
                    cands = [(pr, h) for pr in grp for h in heures] if n_s >= 2 else [((j,), h) for j in JOURS[:6] for h in heures]
                    n_pref = len(cands)
                    if avec_lab and not lab:   # repli l'après-midi seulement si aucun matin libre
                        cands += [(pr, h) for pr in grp for h in APREM] if n_s >= 2 else [((j,), h) for j in JOURS[:6] for h in APREM]
                    for i, (pr, h) in enumerate(cands):
                        if any(j == "sam" and h >= "12:00" for j in pr) or (lab and "sam" in pr): continue
                        a = mn(h); b = a + dur
                        if a < 12 * 60 and b > 12 * 60 + 30: continue      # un cours du matin finit avant le déjeuner
                        if not all(libre(ps, j, a, b) for j in pr): continue
                        score = ((100 if i >= n_pref else 0) + sum(charge.get((j, h), 0) for j in pr) + 3 * len(pris & set(pr)), i)
                        if best is None or score < best[0]: best = (score, pr, h)
                    if not best:
                        print(f"  ! {annee} {saison} : pas de créneau pour {u['unite']} ({u['qui']})", file=sys.stderr); continue
                    _, pr, h = best
                    for j in pr:
                        a = mn(h); prendre(ps, j, a, a + dur); pris.add(j); poses.append((j, h, hm(a + dur), lab))
            poses_de[u["unite"]] = poses
        return poses_de

    profs_labo = {q.strip() for u in U if "L" in u["vol"] for q in u["qui"].split(";") if q.strip()}
    par_saison = collections.defaultdict(list)
    for k, s, lib_t, jours_t, _ in sous: par_saison[s].append(jours_t)
    positions, avant = {}, {}
    for s_, ms in par_saison.items():          # dans l'ordre de l'année : une reprise peut viser un trimestre précédent
        positions[s_] = allouer(s_, ms, avant); avant.update(positions[s_])

    gabarits, semaines, quotidien, place_de = [], [], [], collections.defaultdict(dict)
    attestes = collections.defaultdict(list)       # activités attestées (repas, courrier…) par jour, pour les exclusions des lignes Q
    for e in lire_csv(os.path.join(ROOT, "programme", "evenements.csv")):
        attestes[dt.date.fromisoformat(e["date"])].append(e)
    for k, s, lib_t, jours_t, lundis_saison in sous:
        deb_t, fin_t = jours_t[0], jours_t[-1]
        def ajouter(j, a, b, typ, quoi, qui, lieu, note, codes, sources, extra=None, terme=None, sauf=""):
            p_case, mot = somme(codes); xx = extra or {}
            chance = Fraction(xx.get("chance") or "1"); p_titre = round(100 * (1 - chance))
            p = min(90, round(100 * (1 - (1 - p_case / 100) * (1 - p_titre / 100))))
            if p_titre: mot.append(f"titre : chance {chance} que ce soit bien ce cours ce trimestre-là (part du titre {p_titre} %)")
            invs = [i for i in sources.split("+") if i]; inv_aam = [i for i in invs if re.match(r"\d{4}\.", i)]
            gabarits.append({"annee": annee, "terme": terme or k, "libelle_terme": lib_t, "jour": j, "debut": a, "fin": b,
                "type": typ, "activite": quoi, "qui": qui, "lieu": lieu, "note": note, "codes": "+".join(codes),
                "part_case_pct": p_case, "part_titre_pct": p_titre, "part_deduite_pct": p, "motifs_deduction": " ; ".join(mot),
                "unite": xx.get("unite", ""), "discipline": xx.get("disc", ""), "cours_catalogue": xx.get("cours", ""),
                "precision": xx.get("precision", ""), "candidats": xx.get("candidats", ""), "chance": str(chance),
                "rattachement": xx.get("rattachement", ""), "equivalent_avant": xx.get("e_av", ""), "equivalent_apres": xx.get("e_ap", ""),
                "document_source": " ; ".join(D.get(i, (i, ""))[0] for i in invs), "inventaire": " ; ".join(inv_aam),
                "url_source": " ".join(D.get(i, ("", ""))[1] for i in invs), "sauf": sauf})
        for jt, a, b, typ, quoi, qui, lieu, note, codes, sources, tm in S:
            if not pour(tm, s, deb_t, fin_t, True): continue
            cs = [c for c in codes.split("+") if c]
            for j in jours(jt):
                ajouter(j, a, b, typ, quoi.replace("{terme}", lib_t), qui, lieu, note, cs, sources)
        for u in [u for u in U if pour(u["termes"], s, deb_t, fin_t, s != "summer")]:
            ov = SV.get((u["unite"], s), {})
            ids = ov.get("ids") or u["retenu"].split("+"); cours = " + ".join(C[i]["titre"] for i in ids)
            titre = cours + (f" — {u['precision']}" if u["precision"] else "")
            cands = [i for i in u["candidats"].split(";") + u["retenu"].split("+") if i and i not in ids] if ov.get("ids") else [i for i in u["candidats"].split(";") if i]
            extra = dict(unite=u["unite"], disc=C[ids[0]]["disc"], cours=cours, precision=u["precision"],
                         candidats=" | ".join(C[i]["titre"] for i in cands), chance=ov.get("chance", u["chance"]),
                         rattachement=u["rattachement"], e_av=" + ".join(C[i]["e_av"] for i in ids), e_ap=" + ".join(C[i]["e_ap"] for i in ids))
            cs = [c for c in u["codes"].split("+") if c]
            cs += ["SEMAINE", "JOUR"] + ([] if "HEURE" in cs else ["HEURE_CADRE"]) + (["TERME_DEDUIT"] if s in deduits else [])
            note = u["note"]
            if "suivi" in ov:
                cs = list(dict.fromkeys([c for c in cs if c not in RETIRES_SI_SUIVI] + ["MEME_ANNEE", "R_ATTESTE", "SUIVI"]))
                note = (note + " ; " if note else "") + "Ce trimestre-là : cours " + ov["suivi"]
                extra["rattachement"] += " ; confirmé par les fiches d'étudiants"
            elif "baisse" in ov:
                note = (note + " ; " if note else "") + "Fiches d'étudiants : " + ov["baisse"]
            if u in U[n_cat:] and s == "summer" and len(par_saison[s]) > 1:
                # été en plusieurs périodes : la fiche dit « summer », pas laquelle
                extra["chance"] = str(min(Fraction(extra["chance"] or "1"), Fraction(1, 2)))
                extra["rattachement"] += " ; fiche « summer » sans la période de la session d'été"
            sources = src_cat + ("+" if src_cat and (ov or u in U[n_cat:]) else "") + ("BMCYearbook" if (ov or u in U[n_cat:]) else "")
            poses = positions[s].get(u["unite"], [])
            for j, a, b, lab in poses:
                ajouter(j, a, b, "cours", titre + (" — laboratoire" if lab else ""), u["qui"], "", note, cs, sources, extra)
            place_de[u["unite"]][k] = sorted(poses, key=lambda p: (JOURS.index(p[0]), p[1]))
        # lignes Q (routine quotidienne, et cours d'une période sans gabarit) : toutes les semaines du trimestre, même
        # complètes en données attestées. Exclusions (« sauf ») : repas, courrier… → le jour où un document donne déjà ce
        # moment (même motif, heure à 90 min près) ; cours ou atelier → la semaine où un document donne ce cours (même motif,
        # n'importe quelle heure), et les semaines où le gabarit ordinaire du trimestre le contient déjà ; bornes de dates
        # « saison@début..fin » → jours hors bornes
        kq = k + "~q"; n_q = 0
        gab_k = [g for g in gabarits if g["terme"] == k]
        for jt, a, b, typ, quoi, qui, lieu, note, codes, sources, tm, rx in Q:
            toks = [t.strip() for t in tm.split(",") if t.strip()]
            if toks and not any(t.partition("@")[0] == s for t in toks): continue
            bornes_q = [tuple(map(dt.date.fromisoformat, t.partition("@")[2].split(".."))) for t in toks if t.partition("@")[0] == s and "@" in t]
            dans = lambda x: not bornes_q or any(a_ <= x <= z_ for a_, z_ in bornes_q)
            if not any(dans(x) for x in jours_t): continue
            cours_q = typ in ("cours", "atelier")
            sem_exclues = set()
            if cours_q and rx:
                for x, es in attestes.items():
                    if any(re.search(rx, e["activite"], re.I) for e in es): sem_exclues.add(x - dt.timedelta(x.weekday()))
                if any(re.search(rx, g["activite"], re.I) for g in gab_k):
                    sem_exclues |= {x - dt.timedelta(x.weekday()) for x in jours_t if x - dt.timedelta(x.weekday()) not in compl}
            cs = [c for c in codes.split("+") if c]
            for j in jours(jt):
                wd = JOURS.index(j) if j in JOURS else -1
                def exclu(x):
                    if not dans(x): return True
                    if cours_q: return x - dt.timedelta(x.weekday()) in sem_exclues
                    return bool(rx) and any(re.search(rx, e["activite"], re.I) and (not a or not re.match(r"\d\d:\d\d", e["debut"]) or abs(mn(e["debut"][:5]) - mn(a)) <= 90)
                                            for e in attestes.get(x, []))
                sauf = sorted(x.isoformat() for x in jours_t if x.weekday() == wd and exclu(x))
                if wd >= 0 and len(sauf) == sum(1 for x in jours_t if x.weekday() == wd): continue
                ajouter(j, a, b, typ, quoi.replace("{terme}", lib_t), qui, lieu, note, cs, sources, terme=kq, sauf=" ".join(sauf)); n_q += 1
        if n_q:
            for lun in sorted({x - dt.timedelta(x.weekday()) for x in jours_t}):
                js = [x for x in jours_t if lun <= x < lun + dt.timedelta(7)]
                quotidien.append({"annee": annee, "terme": kq, "libelle_terme": lib_t, "numero": lundis_saison.index(lun) + 1,
                                  "lundi": lun.isoformat(), "jours": " ".join(x.isoformat() for x in js)})
        # semaines du trimestre
        lundis = sorted({x - dt.timedelta(x.weekday()) for x in jours_t})
        for lun in lundis:
            if lun in compl: continue
            n = lundis_saison.index(lun) + 1
            js = [x for x in jours_t if lun <= x < lun + dt.timedelta(7)]
            semaines.append({"annee": annee, "terme": k, "libelle_terme": lib_t, "numero": n, "lundi": lun.isoformat(),
                             "jours": " ".join(x.isoformat() for x in js)})

    os.makedirs(OUT, exist_ok=True)
    base = os.path.join(OUT, f"annee_{annee}")
    if not gabarits or not (semaines or quotidien):
        # année sans aucun jour de cours dans le calendrier attesté (ajout du 1/11/2026, 1955-57) : pas de gabarit,
        # seulement l'analyse ; le semainier ne lit que les _gabarits.csv
        L = [f"# {annee} — reconstitution spéculative de l'année", "",
             f"Généré par `scripts/speculer.py` depuis `{os.path.relpath(path, ROOT)}`. **Aucune semaine reconstituée** : "
             "le calendrier attesté (`programme/calendrier_periodes.csv`) n'a aucun jour de cours pour cette année.", ""] + analyse
        open(base + ".md", "w", encoding="utf-8").write("\n".join(L) + "\n")
        print(f"{os.path.relpath(base, ROOT)} : aucune semaine (pas de période attestée) ; analyse seule")
        return
    for suff, rows in (("_gabarits", gabarits), ("_semaines", semaines), ("_quotidien", quotidien)):
        if not rows and suff == "_quotidien": continue
        with open(base + suff + ".csv", "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["annee", "terme", "libelle_terme", "numero", "lundi", "jours"])
            w.writeheader(); w.writerows(rows)
    # rapport
    L = [f"# {annee} — reconstitution spéculative de l'année", "",
         f"Généré par `scripts/speculer.py` depuis `{os.path.relpath(path, ROOT)}`" + (f" et `{cat[0]}`" if cat else "") +
         f". {len(semaines)} semaines reconstituées ; gabarits : " +
         ", ".join(f"{SAISONS_FR.get(t, t)} {sum(1 for g in gabarits if g['terme'] == t)} entrées" for t in dict.fromkeys(g["terme"] for g in gabarits)) + ".", ""]
    L += analyse + ["", "## Barème appliqué", "", "| code | points | motif |", "|---|---|---|"]
    L += [f"| {c} | +{p} | {m} |" for c, (p, m) in CODES.items()]
    L += ["", "Case de cours : s'ajoute la part du titre, 100 × (1 − chance). Total = 100 × (1 − (1 − case) × (1 − titre)), plafonné à 90 %.", ""]
    for t in dict.fromkeys(g["terme"] for g in gabarits):
        gs = [g for g in gabarits if g["terme"] == t]; ss = [x for x in semaines + quotidien if x["terme"] == t]
        moy = sum(g["part_deduite_pct"] for g in gs) / len(gs)
        L += [f"## Gabarit — {gs[0]['libelle_terme']}" + (" — lignes Q : routine quotidienne et cours de toutes les semaines du trimestre (même complètes)" if t.endswith("~q") else ""), "",
              f"{len(ss)} semaines : " + ", ".join(x["lundi"] for x in ss) + f". Part déduite moyenne du gabarit : {moy:.0f} %.", ""]
        for j in ["semaine"] + JOURS:
            es = sorted([g for g in gs if g["jour"] == j], key=lambda g: (g["debut"] or "", g["activite"]))
            if not es: continue
            L += [f"### {'Toute la semaine' if j == 'semaine' else NOMS[JOURS.index(j)].capitalize()}", ""]
            for e in es:
                h = f"{e['debut']}–{e['fin']}" if e["debut"] else "—"
                ligne = f"- **{h}** {e['activite']}" + (f" · {e['qui']}" if e["qui"] else "") + f"  \n  ↳ déduction {e['part_deduite_pct']} %"
                if e["unite"]:
                    ligne += f" (case {e['part_case_pct']} %, titre {e['part_titre_pct']} %) · {e['discipline']} · rattachement : {e['rattachement']}"
                    if e["candidats"]: ligne += f"  \n  ↳ autres cours possibles : {e['candidats']}"
                    ligne += f"  \n  ↳ année précédente : {e['equivalent_avant']} · année suivante : {e['equivalent_apres']}"
                else: ligne += f" ({e['codes']})"
                ligne += f"  \n  ↳ sources : {e['inventaire']}" + (f" · {e['note']}" if e["note"] else "")
                if e["sauf"]: ligne += f"  \n  ↳ retiré {len(e['sauf'].split())} jour(s) où un document donne déjà ce moment : {e['sauf'][:120]}{' …' if len(e['sauf']) > 120 else ''}"
                L.append(ligne)
            L.append("")
    if suivis:
        dec = collections.Counter(r["decision"] for r in suivis_rows)
        L += ["", "## Cours suivis d'après les fiches d'étudiants (directive « #suivis »)", "",
              f"Table : `{suivis}` (scripts/suivis_speculation.py, depuis la rubrique « COURSE TAKEN » de "
              "BMC Yearbook, bmcyearbook.org/biographies). " + ", ".join(f"{k} {v}" for k, v in dec.most_common()) + ".", "",
              "Règles : unité suivie ce trimestre-là → chance 1 et code SUIVI (rattachement déduit, trimestre reconduit et domaine "
              "annoncé retirés) ; suivie seulement par la discipline (« Music », « Dance ») → trimestre sûr, titre au plus 1 chance "
              "sur le nombre de titres possibles ; suivie un autre trimestre seulement → chance 1/2 au plus ; titre suivi avec un autre "
              "enseignant (attribution déduite contredite) → 1/2, ou 1/3 si les deux ; cours absent du catalogue → unité ajoutée "
              "pour ce seul trimestre (volume supposé, VOLUME +10) ; été en plusieurs périodes → unité ajoutée à 1/2.", ""]
        for t in ("fall", "winter", "spring", "summer"):
            conf = [u for u in U[:n_cat] if "suivi" in SV.get((u["unite"], t), {})]
            bas = [u for u in U[:n_cat] if "baisse" in SV.get((u["unite"], t), {})]
            aj = [u for u in U[n_cat:] if u["termes"] == t]
            if not (conf or bas or aj): continue
            L += [f"### {SAISONS_FR[t].capitalize()}" + ("" if t in par_saison else " — trimestre absent du calendrier attesté : rien n'est placé"), ""]
            if conf: L.append("- Confirmées : " + ", ".join(f"{u['unite']} ({u['qui']})" for u in conf) + ".")
            for u in bas: L.append(f"- Abaissée : {u['unite']} ({u['qui']}, chance {SV[(u['unite'], t)]['chance']}) — {SV[(u['unite'], t)]['baisse']}.")
            for u in aj: L.append(f"- Ajoutée : {u['unite']} « {C[u['retenu']]['titre']} » ({u['qui']}, volume {u['vol']}) — {u['note']}")
            L.append("")
    open(base + ".md", "w", encoding="utf-8").write("\n".join(L))
    print(f"{os.path.relpath(base, ROOT)} : {len(semaines)} semaines, {len(gabarits)} entrées de gabarit")

    if cat:
        nom = os.path.splitext(os.path.basename(cat[0]))[0]
        rows = []
        def cr(u): return " / ".join(f"{t} : " + ", ".join(f"{NOMS[JOURS.index(j)][:3]} {a}-{b}" for j, a, b, _ in ps)
                                     for t, ps in place_de.get(u["unite"], {}).items())
        for i, c in C.items():
            ret = [u for u in U if i in u["retenu"].split("+")]; can = [u for u in U if i in u["candidats"].split(";")]
            if ret: statut = "programmé"; detail = " ; ".join(f"{u['unite']} ({u['qui'] or 'enseignant inconnu'} ; {cr(u)} ; chance {u['chance']})" for u in ret)
            elif can: statut = "candidat"; detail = " ; ".join(f"{u['unite']} ({u['qui']} ; à la place de « {' + '.join(C[k]['titre'] for k in u['retenu'].split('+'))} »)" for u in can)
            else: statut = "non programmé"; detail = N[i]
            rows.append({"discipline": c["disc"], "id": i, "cours": c["titre"], "equivalent_avant": c["e_av"], "equivalent_apres": c["e_ap"],
                         "enseignant": "; ".join(sorted({u["qui"] for u in ret + can if u["qui"]})) or "—", "statut": statut, "detail": detail})
        bc = os.path.join(OUT, f"catalogue_{nom}_concordance")
        with open(bc + ".csv", "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
        st = collections.Counter(r["statut"] for r in rows)
        M = [f"# Concordance des cours — {nom}", "", f"{len(rows)} cours : {st['programmé']} programmés, {st['candidat']} candidats, {st['non programmé']} non programmés.", ""]
        M += [f"- {x}" for x in entete] + [""]; disc = None
        for r in rows:
            if r["discipline"] != disc: disc = r["discipline"]; M += ["", f"## {disc}", ""]
            M.append(f"- **{r['cours']}** — {r['enseignant']} — *{r['statut']}* : {r['detail']}  \n  année précédente : {r['equivalent_avant']} · année suivante : {r['equivalent_apres']}")
        open(bc + ".md", "w", encoding="utf-8").write("\n".join(M) + "\n")
        print(f"{os.path.relpath(bc, ROOT)} : {len(rows)} cours — " + ", ".join(f"{k} {v}" for k, v in st.items()))

if __name__ == "__main__":
    d = os.path.join(SPEC, "annees")
    seule = sys.argv[1] if len(sys.argv) > 1 else None
    for fn in sorted(os.listdir(d)):
        if re.fullmatch(r"\d{4}-\d{2}\.txt", fn) and (not seule or fn.startswith(seule)): traiter(os.path.join(d, fn))
