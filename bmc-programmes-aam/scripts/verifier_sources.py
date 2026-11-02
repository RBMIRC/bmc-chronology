"""Vérification des sources de tout ce que montre le semainier.

Pour chaque entrée affichée — activités attestées AAM, couche Duberman, couche Scénario, couche spéculative —
le script ouvre le texte de la source citée et y cherche des « témoins » de l'entrée :
  - les noms de famille des personnes (champ « qui » et noms propres du titre) ;
  - les mots du titre (même langue que la source : anglais pour l'AAM) ;
  - l'année et le mois de la date.
Textes ouverts :
  AAM ........ pages_txt/*/<inventaire>_*.txt (OCR des fiches du musée)
  Duberman ... duberman/_appui/paged.json (texte corrigé, un paragraphe par ¶) + notes de Duberman
  Scénario ... ../bmc-scenario/texte/NNN.jsonl.gz (texte des livres, page par page), d'après les pages citées
  Spéculatif . les documents cités par le gabarit (inventaires), ou le paragraphe de Duberman cité
Statuts :
  retrouvé ................ les témoins sont réunis dans un même passage (600 caractères) du texte cité, et ils pèsent
                            au moins la moitié du poids total (poids = rareté du mot dans le corpus AAM + Duberman)
  indice faible ........... un nom ou quelques mots seulement : ne prouve rien à lui seul (le contrôle négatif
                            le donne aussi souvent avec un texte pris au hasard) ; à relire
  à relire ................ le texte cité est là, mais aucun témoin n'y est retrouvé automatiquement
                            (traduction, paraphrase, OCR fautif, ou erreur de référence)
  référence introuvable ... l'inventaire, le ¶ ou la page cités n'existent pas dans les textes du dépôt
  sans source ............. aucune source indiquée (ne doit pas arriver)
Contrôle négatif : pour 500 entrées par couche, on refait le test avec le texte d'une autre entrée tirée au hasard ;
le taux de « retrouvé » obtenu mesure les faux positifs de la méthode (donné dans le rapport).
Sorties (jamais écrasées, numéro suivant) :
  programme/audit/NNN_verification_sources.csv   une ligne par entrée
  programme/audit/NNN_verification_sources.md    chiffres par couche et par statut, listes à relire
  semainier/verification.js                      statut + extrait de la source (chargé par la page à la demande)
"""
import csv, gzip, json, os, re, sys, glob, collections, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEPOT = os.path.dirname(ROOT)
AUDIT = os.path.join(ROOT, "programme", "audit")
LARGEUR = 520          # longueur de l'extrait affiché
MOIS_EN = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october",
           "november", "december"]
VIDES = set("""dans pour avec sans sous chez vers entre apres avant depuis pendant contre leur leurs elle elles sont etait
etre avoir fait faire plus moins tres tout tous toute toutes dont mais donc comme aussi encore meme cette celui celle ceux
black mountain college the and with from that this which their when were have been will into about after before over
under also they them there then than what your said each other some such only very much more most just like week day
reunion meeting possible semaine for but not all are was his her its one two new old off out who how can has had per our any
de la le les des du un une et en au aux sur par est""".split())
CAPS_VIDES = set("""Réunion Conférence Lettre Concert Cours Arrivée Départ Mort Visite Séance Fête Pièce Exposition Première
Dernière Retour Fin Début Discussion Entretien Rapport Note Notes Faculty Board Community Meeting Student Students The
Summer Fall Spring Winter Session Institute Semaine Petit Déjeuner Dîner Programme Thé Café Concert Chorus Dining Hall
Studies Building Lake Eden Black Mountain College Lee Hall Blue Ridge Asheville Robert Charles John""".split())


def plat(s):
    """minuscules sans accents, même longueur que l'original (pour retrouver les positions)."""
    return "".join((unicodedata.normalize("NFKD", c)[:1] or c).lower() for c in s)


# titres en français (Duberman, scénario, couche spéculative) contre sources en anglais : équivalents cherchés
LEXIQUE = {"reunion": ["meeting", "met"], "enseignant": ["faculty", "teacher"], "enseignants": ["faculty", "teacher"],
           "etudiant": ["student"], "etudiants": ["student"], "conference": ["lecture", "talk", "spoke"],
           "lettre": ["letter", "wrote"], "mort": ["died", "death"], "deces": ["died", "death"], "incendie": ["fire", "burn"],
           "ferme": ["farm"], "concert": ["concert"], "demission": ["resign"], "arrivee": ["arrived", "came"],
           "depart": ["left", "leave"], "vente": ["sold", "sale"], "danse": ["dance", "danc"], "theatre": ["theater", "theatre", "play"],
           "peinture": ["paint"], "musique": ["music"], "tissage": ["weav"], "ceramique": ["ceramic", "pott"],
           "imprimerie": ["print"], "ecriture": ["writ"], "poesie": ["poe"], "chimie": ["chemi"], "physique": ["physic"],
           "mathematiques": ["mathem"], "philosophie": ["philosoph"], "histoire": ["histor"], "dessin": ["drawing"],
           "couleur": ["color"], "choeur": ["chorus", "choir"], "the": ["tea"], "cafe": ["coffee"],
           "dejeuner": ["lunch", "breakfast"], "diner": ["dinner", "supper"], "repas": ["meal", "dining"], "travail": ["work"],
           "construction": ["build", "construct"], "batiment": ["building"], "exposition": ["exhibit"], "election": ["elect"],
           "integration": ["negro", "integrat"], "noirs": ["negro"], "accreditation": ["accredit"],
           "vacances": ["vacation", "holiday"], "fete": ["party"], "mariage": ["marri"], "naissance": ["born", "birth"],
           "visite": ["visit"], "cours": ["course", "class"], "seminaire": ["seminar"], "atelier": ["workshop", "shop"],
           "examen": ["exam"], "programme": ["program"], "dimanche": ["sunday"], "samedi": ["saturday"],
           "mercredi": ["wednesday"], "lundi": ["monday"], "mardi": ["tuesday"], "jeudi": ["thursday"],
           "vendredi": ["friday"], "soir": ["evening", "night"],
           "ouverture": ["open"], "fondation": ["found"], "premier": ["first"], "premiere": ["first"],
           "dernier": ["last"], "derniere": ["last"], "nouveau": ["new"], "nouvelle": ["new"], "retour": ["return", "back"],
           "spectacle": ["perform", "show"], "piece": ["play"], "recital": ["recital"], "lecture": ["reading", "read"],
           "poeme": ["poem"], "poemes": ["poem"], "livre": ["book"], "revue": ["review", "magazine"],
           "achat": ["bought", "purchas"], "argent": ["money", "dollar"], "dollars": ["dollar"], "dette": ["debt"],
           "hypotheque": ["mortgage"], "proces": ["suit", "court"], "guerre": ["war"], "armee": ["army"],
           "lac": ["lake"], "grange": ["barn"], "salle": ["hall", "room"], "manger": ["dining"], "bibliotheque": ["library"],
           "communaute": ["community"], "recteur": ["rector"], "sculpture": ["sculpt"], "architecture": ["architect"],
           "photographie": ["photograph"], "composition": ["compos"], "piano": ["piano"], "chant": ["sing", "voice"],
           "anniversaire": ["birthday", "anniversary"], "noel": ["christmas"], "malade": ["ill", "sick"],
           "hopital": ["hospital"], "suicide": ["suicide"], "divorce": ["divorce"], "enfant": ["child", "baby"],
           "bebe": ["baby"], "epouse": ["wife", "married"], "femme": ["wife", "woman"], "mari": ["husband"]}
RACINES = {v for vs in LEXIQUE.values() for v in vs}

FENETRE = 600   # les témoins doivent être réunis dans un même passage de cette longueur


def occurrences(texte_plat, groupes, maxi=300):
    """{clé: [(début, fin), …]} : toutes les occurrences (plafonnées) de chaque témoin."""
    out = {}
    for k, vs in groupes.items():
        occ = []
        for v in vs:
            pat = r"\b" + re.escape(v) + (r"\w*" if v in RACINES else r"s?\b")
            occ += [(r.start(), r.end()) for r in re.finditer(pat, texte_plat)][:maxi]
        if occ: out[k] = sorted(occ)
    return out


def meilleur_passage(occ, poids):
    """fenêtre de FENETRE caractères qui réunit le plus de témoins distincts (pondérés) ;
    renvoie {clé: (début, fin)} des témoins qui y sont."""
    evs = sorted((a, b, k) for k, l in occ.items() for a, b in l)
    best, best_set, j = -1, {}, 0
    compte = collections.Counter()
    for i in range(len(evs)):
        compte[evs[i][2]] += 1
        while evs[i][0] - evs[j][0] > FENETRE:
            compte[evs[j][2]] -= 1
            if not compte[evs[j][2]]: del compte[evs[j][2]]
            j += 1
        score = sum(poids.get(k, 1) for k in compte)
        if score > best:
            best = score
            best_set = {}
            for a, b, k in evs[j:i + 1]: best_set.setdefault(k, (a, b))
    return best_set
CACHE_PLAT = {}
TEMOINS_TEST = collections.defaultdict(list)


def temoins(qui, titre, langue_titre):
    """témoins de l'entrée : {clé: [variantes]}. Une personne = nom de famille ou prénom ; un mot du titre = le mot
    (source dans la même langue) ou ses équivalents anglais (titre français, source anglaise)."""
    noms, mots = {}, {}
    for q in re.split(r";|,| et | and ", qui or ""):
        q = re.sub(r"\(.*?\)", "", q).strip()
        if q and q[:1].isupper():
            ws = [w.strip(".’'") for w in q.split()]
            if ws and len(ws[-1]) > 2 and plat(ws[-1]) not in VIDES:
                noms[plat(ws[-1])] = [plat(ws[-1])] + ([plat(ws[0])] if len(ws) > 1 and len(ws[0]) > 3 else [])
    for w in re.findall(r"\b[A-ZÉ][a-zà-ÿ’'-]{3,}\b", titre or ""):
        w2 = plat(w.strip("’'"))
        if w not in CAPS_VIDES and w2 not in VIDES and w2 not in LEXIQUE: noms.setdefault(w2, [w2])
    for w in re.split(r"[^a-z]+", plat(titre or "")):
        if not w or w in noms or w in VIDES: continue
        if w in LEXIQUE: mots[w] = LEXIQUE[w] + [w]
        elif langue_titre and len(w) >= 3: mots[w] = [w]
    return noms, mots


def chercher(texte_plat, groupes):
    """{clé: position} des témoins retrouvés ; une variante suffit. Les racines du lexique (« weav », « pott ») valent
    préfixe ; les autres mots admettent un pluriel."""
    out = {}
    for k, vs in groupes.items():
        for v in vs:
            pat = r"\b" + re.escape(v) + (r"\w*" if v in RACINES else r"s?\b")
            r = re.search(pat, texte_plat)
            if r: out[k] = (r.start(), r.end()); break
    return out


def extrait(texte, positions):
    """fenêtre de LARGEUR caractères qui contient le plus de témoins ; témoins entre \x01…\x02."""
    if not texte: return ""
    pos = sorted(positions.values())
    d = 0
    if pos:
        best_n, a = 0, 0
        for i in range(len(pos)):
            while pos[i][0] - pos[a][0] > LARGEUR - 160: a += 1
            if i - a + 1 > best_n: best_n, d = i - a + 1, max(0, pos[a][0] - 80)
    seg = texte[d:d + LARGEUR]
    out, k = [], 0
    for a, b in pos:
        if a < d or b > d + LARGEUR or a - d < k: continue
        out += [seg[k:a - d], "\x01" + seg[a - d:b - d] + "\x02"]; k = b - d
    out.append(seg[k:])
    s = re.sub(r"\s+", " ", "".join(out)).strip()
    return ("… " if d else "") + s + (" …" if d + LARGEUR < len(texte) else "")


IDF = {}          # rareté des mots (log N/df) sur les documents AAM et les paragraphes de Duberman ; rempli par rarete()
IDF_DEFAUT = 5.0  # mot absent du corpus de référence : rare


def rarete(unites):
    """unites : liste de textes (déjà « plat »). Remplit IDF."""
    import math
    df = collections.Counter()
    for u in unites: df.update(set(re.findall(r"[a-z]{3,}", u)))
    n = len(unites)
    IDF.update({w: math.log(n / c) for w, c in df.items()})
    vocab = list(df)
    for r in RACINES:                       # racines : df = unités qui ont un mot commençant ainsi
        c = sum(1 for u in unites if re.search(r"\b" + r, u))
        IDF[r] = math.log(n / max(c, 1))


def poids_groupe(variantes):
    return max(IDF.get(v, IDF_DEFAUT) for v in variantes)


def statut(noms, mots, tn, tm, dates=None):
    """« retrouvé » = au moins la moitié du poids des témoins (rareté des mots) est dans le passage, et ce poids
    dépasse 2,5 (deux mots banals ne suffisent pas) ; « en partie » = un nom, ou un poids d'au moins 1,5."""
    tous = {**noms, **mots}
    total = sum(poids_groupe(v) for v in tous.values()) or 1
    trouve = sum(poids_groupe(tous[k]) for k in list(tn) + list(tm) if k in tous)
    if dates and len(dates) == 2: trouve += 1.0; total += 1.0       # année et mois dans le même passage
    if trouve / total >= 0.5 and trouve >= 2.5: return "retrouvé"
    if tn or trouve >= 1.5: return "indice faible"
    return "à relire"


# ---------------------------------------------------------------- textes
def textes_aam():
    t = {}
    for p in glob.glob(os.path.join(ROOT, "pages_txt", "*", "*.txt")):
        inv = os.path.basename(p).split("_")[0]
        s = open(p, encoding="utf-8").read()
        s = s.split("=" * 20, 1)[-1] if "=" * 20 in s else s       # sans l'en-tête technique
        s = re.sub(r"^=+\s*", "", s.lstrip())
        t[inv] = t.get(inv, "") + "\n" + s
    return t


def textes_duberman():
    par = {int(x["i"]): x["text"] for x in json.load(open(os.path.join(ROOT, "duberman", "_appui", "paged.json"), encoding="utf-8"))}
    return par


def paragraphes(ref, par, maxi=12):
    ids = []
    for a, b in re.findall(r"¶(\d+)(?:-(\d+))?", ref or ""):
        for i in range(int(a), min(int(b or a), int(a) + maxi) + 1): ids.append(i)
    return [i for i in ids if i in par], ids


class Livres:
    def __init__(self):
        self.cache = {}
    def pages(self, sid):
        if sid not in self.cache:
            p = os.path.join(DEPOT, "bmc-scenario", "texte", f"{sid}.jsonl.gz")
            d = collections.defaultdict(str)
            if os.path.exists(p):
                for l in gzip.open(p, "rt", encoding="utf-8"):
                    x = json.loads(l); d[str(x.get("page", "")).strip()] += "\n" + (x.get("texte") or "")
            self.cache[sid] = d
        return self.cache[sid]


def lire(p):
    with open(p, encoding="utf-8") as f: return list(csv.DictReader(f))


# ---------------------------------------------------------------- vérification
def main():
    os.makedirs(AUDIT, exist_ok=True)
    pris = [int(m.group(1)) for fn in os.listdir(AUDIT) if (m := re.match(r"(\d{3})_verification", fn))]
    num = f"{max(pris, default=0) + 1:03d}"
    T, P, L = textes_aam(), textes_duberman(), Livres()
    rarete([plat(t) for t in T.values()] + [plat(t) for t in P.values()])
    lignes, js = [], {}

    def evaluer(qui, titre, langue, date, texte_src):
        noms, mots = temoins(qui, titre, langue)
        an = (date or "")[:4]
        mo = MOIS_EN[int(date[5:7]) - 1] if re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])(-\d{2})?", date or "") else ""
        if not re.fullmatch(r"\d{4}", an): an = ""
        tp = CACHE_PLAT.get(texte_src)
        if tp is None:
            tp = plat(texte_src)
            if len(texte_src) > 5000: CACHE_PLAT[texte_src] = tp
        gd = {x: [x] for x in (an, mo) if x}
        occ = occurrences(tp, {**{"n:" + k: v for k, v in noms.items()}, **{"m:" + k: v for k, v in mots.items()},
                               **{"d:" + k: v for k, v in gd.items()}})
        win = meilleur_passage(occ, {k: (3 if k.startswith("n:") else 1) for k in occ})
        g = lambda pr: {k[2:]: v for k, v in win.items() if k.startswith(pr)}
        tn, tm, dates = g("n:"), g("m:"), g("d:")
        return noms, mots, tn, tm, dates, statut(noms, mots, tn, tm, dates if mo else None)

    def noter(couche, cle, date, titre, qui, ref, texte_src, langue, introuvable=""):
        noms, mots = temoins(qui, titre, langue)
        if not ref.strip(): st, tn, tm, ex = "sans source", {}, {}, ""
        elif not texte_src: st, tn, tm, ex = "référence introuvable", {}, {}, ""
        else:
            noms, mots, tn, tm, dates, st = evaluer(qui, titre, langue, date, texte_src)
            ex = extrait(texte_src, {**{"n" + k: v for k, v in tn.items()}, **{"m" + k: v for k, v in tm.items()},
                                     **{"d" + k: v for k, v in dates.items()}})
            tm = {**tm, **dates}
        if texte_src: TEMOINS_TEST[couche].append((qui, titre, langue, date, texte_src))
        lignes.append({"couche": couche, "cle": cle, "date": date, "activite": titre[:200], "statut": st,
                       "noms_retrouves": " ; ".join(sorted(tn)), "noms_absents": " ; ".join(sorted(set(noms) - set(tn))),
                       "mots_retrouves": " ; ".join(sorted(tm)), "reference": ref[:300], "note": introuvable})
        js[cle] = [st, ex, introuvable]

    # AAM
    for i, e in enumerate(lire(os.path.join(ROOT, "programme", "evenements.csv"))):
        invs = [x.strip() for x in (e["inventaire"] or "").split(";") if x.strip()]
        txt = "\n".join(T.get(v, "") for v in invs)
        manq = [v for v in invs if v not in T]
        noter("AAM", str(i), e["date"], e["activite"], e["qui"], e["document_source"] + " " + e["inventaire"], txt, True,
              ("inventaire sans texte : " + ", ".join(manq)) if manq else "")
    # Duberman
    dub = lire(os.path.join(ROOT, "duberman", "evenements_duberman.csv"))
    for i, e in enumerate(dub):
        ids, demandes = paragraphes(e["paragraphe"], P)
        txt = "\n".join(P[k] for k in ids) + "\n" + (e["notes_texte"] or "")
        noter("Duberman", f"d{i}", e["date"], e["activite"], e["qui"], e["document_source"], txt.strip(), False,
              ("¶ absents : " + ", ".join(map(str, sorted(set(demandes) - set(ids))))) if set(demandes) - set(ids) else "")
    # Scénario
    sc = sorted(glob.glob(os.path.join(ROOT, "scenario", "[0-9][0-9][0-9]_evenements_scenario.csv")))
    if sc:
        S = json.load(gzip.open(sorted(glob.glob(os.path.join(DEPOT, "bmc-scenario", "sortie", "[0-9][0-9][0-9]_*.json.gz")))[-1], "rt", encoding="utf-8"))
        par_id = {x["id"]: x for cat in ("evenements", "scenes") for x in S["fiches"][cat]}
        for e in lire(sc[-1]):
            if e["semainier"] != "oui": continue
            x = par_id.get(e["id"], {})
            morceaux, manq = [], []
            for s in x.get("sources") or []:
                pg = L.pages(s.get("source", ""))
                for p in s.get("pages") or []:
                    p = str(p).replace("p. ", "").replace("p.", "").strip()
                    for q in (re.findall(r"\d+", p)[:1] if "-" in p else [p]):
                        if pg.get(q): morceaux.append(pg[q])
                        else: manq.append(f"{s.get('source')} p. {q}")
                    m = re.fullmatch(r"(\d+)-(\d+)", p)
                    if m:
                        for k in range(int(m.group(1)) + 1, min(int(m.group(2)), int(m.group(1)) + 4) + 1):
                            if pg.get(str(k)): morceaux.append(pg[str(k)])
            cle = ("" if not e["fondu_dans"] else "") + "s" + e["id"]
            noter("Scénario", cle, e["date"], e["activite"], e["qui"], e["document_source"], "\n".join(morceaux), False,
                  ("pages introuvables : " + ", ".join(manq[:5])) if manq else "")
    # Spéculatif : chaque entrée de gabarit (clé = année, terme, rang dans le terme, comme dans la page)
    for fn in sorted(glob.glob(os.path.join(ROOT, "programme", "speculatif", "annee_*_gabarits.csv"))):
        an = re.search(r"annee_(\d{4}-\d{2})_", fn).group(1)
        rang = collections.Counter()
        for g in lire(fn):
            k = rang[g["terme"]]; rang[g["terme"]] += 1
            invs = [x.strip() for x in g["inventaire"].split(";") if x.strip()]
            txt, manq = [], []
            for v in invs:
                if v in T: txt.append(T[v])
                elif v.startswith("Duberman"):
                    ids, _ = paragraphes(v, P, maxi=40); txt += [P[j] for j in ids]
                    if not ids: manq.append(v)
                else: manq.append(v)
            titre = g.get("cours_catalogue") or g["activite"]
            noter("Spéculatif", f"g:{an}:{g['terme']}:{k}", g["libelle_terme"], titre, g["qui"], g["document_source"] or g["inventaire"],
                  "\n".join(txt), True, ("source sans texte : " + ", ".join(manq)) if manq else "")

    # ---------------------------------------------------------------- écriture
    cols = ["couche", "cle", "date", "activite", "statut", "noms_retrouves", "noms_absents", "mots_retrouves", "reference", "note"]
    with open(os.path.join(AUDIT, f"{num}_verification_sources.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(lignes)
    with open(os.path.join(ROOT, "semainier", "verification.js"), "w", encoding="utf-8") as f:
        f.write(f"// généré par scripts/verifier_sources.py ({num}) — ne pas éditer à la main\n")
        f.write("window.BMC_VERIF = " + json.dumps(js, ensure_ascii=False, separators=(",", ":")) + ";\n")
    C = collections.Counter
    ordre = ["retrouvé", "indice faible", "à relire", "référence introuvable", "sans source"]
    M = [f"# Vérification des sources du semainier ({num})", "",
         "Pour chaque entrée affichée, le texte de la source citée est ouvert et on y cherche les noms des personnes, "
         "les mots du titre (anglais pour l'AAM) et l'année ou le mois. Méthode et statuts : en-tête de "
         "`scripts/verifier_sources.py`. « À relire » ne veut pas dire faux : le passage est souvent traduit ou paraphrasé "
         "(Duberman et le scénario sont en français, leurs sources en anglais), ou l'entrée est générique (repas, thé).", "",
         "| couche | entrées | " + " | ".join(ordre) + " |", "|---|---|" + "---|" * len(ordre)]
    for c in ("AAM", "Duberman", "Scénario", "Spéculatif"):
        x = [l for l in lignes if l["couche"] == c]; n = C(l["statut"] for l in x)
        M.append(f"| {c} | {len(x)} | " + " | ".join(f"{n[o]} ({100 * n[o] / max(1, len(x)):.0f} %)" for o in ordre) + " |")
    # autres informations du semainier : présence d'une source et d'un lien
    per = lire(os.path.join(ROOT, "programme", "calendrier_periodes.csv"))
    ps = os.path.join(ROOT, "speculation", "calendrier_speculatif.csv")
    per += lire(ps) if os.path.exists(ps) else []
    cou = lire(os.path.join(ROOT, "programme", "cours_par_periode.csv"))
    dx = os.path.join(ROOT, "duberman", "documents_extra_duberman.csv")
    docs = lire(dx) if os.path.exists(dx) else []
    M += ["", "## Autres informations affichées", "",
          f"- Périodes (trimestres, vacances) : {len(per)} ; sans source : {sum(1 for x in per if not x['document_source'])} ; "
          f"sans lien : {sum(1 for x in per if not x['url_source'])}.",
          f"- Cours offerts (panneau) : {len(cou)} ; sans source : {sum(1 for x in cou if not x['document_source'])} ; "
          f"sans lien : {sum(1 for x in cou if not x['url_source'])}.",
          f"- Documents datés : {len(T)} fiches du musée (lien vers la fiche) ; {len(docs)} documents cités dans les notes de "
          f"Duberman, sans référence de note : {sum(1 for x in docs if not x['source'])}."]
    import random
    random.seed(7)
    M += ["", "## Contrôle négatif (fiabilité de la méthode)", "",
          "Taux de « retrouvé » sur 500 entrées par couche, avec leur vraie source puis avec la source d'une autre entrée tirée au hasard. "
          "L'écart mesure ce que vaut « retrouvé » ; le taux avec une source au hasard est le taux de faux positifs.", "",
          "| couche | vraie source | source au hasard |", "|---|---|---|"]
    for c in ("AAM", "Duberman", "Scénario", "Spéculatif"):
        X = TEMOINS_TEST[c]
        if len(X) < 50: continue
        ech = random.sample(X, min(500, len(X))); aut = random.sample(X, len(ech))
        v = sum(evaluer(q, t, l, d, src)[-1] == "retrouvé" for q, t, l, d, src in ech) / len(ech)
        h = sum(evaluer(q, t, l, d, a[4])[-1] == "retrouvé" for (q, t, l, d, _), a in zip(ech, aut)) / len(ech)
        M.append(f"| {c} | {100 * v:.0f} % | {100 * h:.0f} % |")
    for c in ("AAM", "Duberman", "Scénario", "Spéculatif"):
        intr = [l for l in lignes if l["couche"] == c and l["statut"] in ("référence introuvable", "sans source")]
        if intr:
            M += ["", f"## {c} : références introuvables ou absentes ({len(intr)})", ""]
            M += [f"- {l['date']} « {l['activite'][:90]} » — {l['note'] or l['reference'][:120]}" for l in intr[:60]]
            if len(intr) > 60: M.append(f"- … {len(intr) - 60} autres dans le CSV")
    open(os.path.join(AUDIT, f"{num}_verification_sources.md"), "w", encoding="utf-8").write("\n".join(M) + "\n")
    print("\n".join(M[:12]))


if __name__ == "__main__":
    main()
