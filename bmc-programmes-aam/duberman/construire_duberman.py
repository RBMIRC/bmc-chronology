"""Dépouillement chronologique de Duberman, Black Mountain: An Exploration in Community (1972).

Entrées : duberman/extraction/*.txt (lignes E|…, voir _FORMAT.txt), écrites à la lecture du texte corrigé
          DATA_BMC/Duberman_Black_Mountain_corrige.txt (racine du dépôt) ;
          /tmp/dub/paged.json et /tmp/dub/notes_by_id.json (paragraphes et notes → pages du livre),
          ou leurs copies dans duberman/_appui/ si /tmp a été vidé.
Sorties (dans duberman/, jamais par-dessus programme/ ni semainier/) :
  evenements_duberman.csv        mêmes colonnes que programme/evenements.csv + colonnes Duberman
  documents_duberman.csv         documents datés cités dans les notes (lettres, procès-verbaux, entretiens…)
  documents_extra_duberman.csv   les mêmes, avant 1958, au format de semainier/documents_extra.csv
  recoupements_duberman.csv      confrontation avec programme/evenements.csv (AAM) et Chronos 2
  rapport_duberman.txt           contrôles et chiffres
"""
import csv, json, os, re, shutil, sys, calendar, collections, datetime as dt, unicodedata

ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(ICI)
EXTR = os.path.join(ICI, "extraction")
APPUI = os.path.join(ICI, "_appui")
# racine du dépôt = dossier parent de bmc-programmes-aam/ ; Chronos 2 n'est pas recopié dans le dépôt
# (recoupement Chronos sauté s'il manque : ne pas relancer le script pour écraser recoupements_duberman.csv)
DEPOT = os.path.dirname(ROOT)
CHRONOS = os.path.join(DEPOT, "DATA_BMC", "Chronos 2", "bmc_chronology.json")
AAM = os.path.join(ROOT, "programme", "evenements.csv")

LIVRE = "Duberman, Black Mountain: An Exploration in Community (1972 ; Anchor 1973)"
CHAPITRES = {1: "The Rollins Fracas", 2: "A Beginning", 3: "Anni and Josef Albers", 4: "The Thirties",
             5: "Schism", 6: "A New Home", 7: "The Split", 8: "Aftermaths and Continuities",
             9: "New Definitions of Community", 10: "Entries and Exits", 11: "Transition",
             12: "A New Black Mountain", 13: "Olson", 14: "Expelled and Imploding"}
FICHIERS = {"liminaire": "Introduction et préface", "acknowledgments": "Remerciements"}
TYPES = {"cours", "atelier", "conference", "concert", "theatre", "danse", "reunion", "radio", "travail",
         "calendrier", "examen", "social", "expo", "visite", "sortie", "autre"}
CATEGORIES = set("""arrivee depart recrutement renvoi demission deces naissance mariage conflit decision gouvernance
finances immobilier construction ferme publication lettre admission integration proces sante voyage vie_privee
enseignement spectacle fete institut_ete contexte historiographie calendrier social visite travail concert examen
autre""".split())
CODES = {"calc": (5, "jour calculé d'après une autre date du livre"),
         "rel": (10, "date relative résolue sur une date du livre moins précise"),
         "ded": (15, "élément supposé (date, durée ou participant)"),
         "prevu": (15, "annoncé ou prévu, réalisation non attestée"),
         "corr": (20, "date corrigée (incohérence du livre)"),
         "approx": (25, "date approximative ou incomplète dans le livre")}
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
SAISONS = {"hiver": (1, 1, 2, 28), "printemps": (3, 1, 5, 31), "ete": (6, 1, 8, 31), "automne": (9, 1, 12, 31)}
MOMENTS = {"matin", "après-midi", "soir", "nuit", "midi"}
COLONNES_AAM = ["date", "jour", "debut", "fin", "type", "activite", "qui", "lieu", "note", "recurrent_deduit",
                "part_deduite_pct", "motifs_deduction", "document_source", "inventaire", "url_source"]
COLONNES = COLONNES_AAM + ["date_fin", "precision", "date_livre", "categorie", "chapitre", "page", "paragraphe",
                           "notes_citees", "notes_texte", "recoupement_aam", "fichier_extraction", "ligne_extraction"]


def appui(nom):
    """Fichier d'appui : /tmp/dub/<nom>, recopié dans duberman/_appui/ pour survivre au nettoyage de /tmp."""
    os.makedirs(APPUI, exist_ok=True)
    src, dst = os.path.join("/tmp/dub", nom), os.path.join(APPUI, nom)
    if os.path.exists(src) and not os.path.exists(dst):
        shutil.copy2(src, dst)
    p = dst if os.path.exists(dst) else src
    return json.load(open(p, encoding="utf-8"))


def norm(s):
    s = unicodedata.normalize("NFKD", s.lower())
    return re.sub(r"[^a-z0-9]+", " ", "".join(c for c in s if not unicodedata.combining(c))).strip()


# ---------------------------------------------------------------- dates
def borne(s):
    """'1944-07-14', '1944-07', '1944', '1944-ete', '1944-45', '1951-56' → (début, fin, précision)."""
    s = s.strip()
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        d = dt.date(*map(int, m.groups()))
        return d, d, "jour"
    m = re.fullmatch(r"(\d{4})-(\d{2})", s)
    if m:
        y, mo = map(int, m.groups())
        if mo <= 12:
            return dt.date(y, mo, 1), dt.date(y, mo, calendar.monthrange(y, mo)[1]), "mois"
        # AAAA-AA : année scolaire si AA = AAAA+1, sinon plage d'années
        y2 = (y // 100) * 100 + mo
        if y2 < y: y2 += 100
        if y2 == y + 1:
            return dt.date(y, 9, 1), dt.date(y2, 6, 30), "annee_scolaire"
        return dt.date(y, 1, 1), dt.date(y2, 12, 31), "plage_annees"
    m = re.fullmatch(r"(\d{4})-(hiver|printemps|ete|automne)", s)
    if m:
        y, sa = int(m.group(1)), m.group(2)
        m1, d1, m2, d2 = SAISONS[sa]
        if sa == "hiver":  # hiver rattaché à janvier : déc. de l'année précédente → février
            return dt.date(y - 1, 12, 1), dt.date(y, 2, calendar.monthrange(y, 2)[1]), "saison"
        return dt.date(y, m1, d1), dt.date(y, m2, d2), "saison"
    m = re.fullmatch(r"(\d{4})", s)
    if m:
        y = int(s)
        return dt.date(y, 1, 1), dt.date(y, 12, 31), "annee"
    raise ValueError(f"date illisible : {s!r}")


GROSSIERE = {"mois", "saison", "annee", "annee_scolaire", "plage_annees"}


# ---------------------------------------------------------------- pages
class Pages:
    def __init__(self):
        self.par = {}
        for x in appui("paged.json"):
            self.par[x["i"]] = (x["chap"], x["p0"], x["p1"], x["text"])
        self.notes = appui("notes_by_id.json")
        # page de chaque note : calculée sur l'OCR des pages de notes par pages_notes.py
        pn = os.path.join(APPUI, "pages_notes.json")
        self.page_note = json.load(open(pn, encoding="utf-8")) if os.path.exists(pn) else {}

    def pages(self, refs):
        """'¶864-865; ¶868' → '186-187'."""
        ps = []
        for a, b in re.findall(r"¶(\d+)(?:-(\d+))?", refs or ""):
            for i in range(int(a), int(b or a) + 1):
                if i in self.par:
                    for p in self.par[i][1:3]:
                        if p and p not in ps: ps.append(p)
        def cle(p):
            return (0, int(p)) if p.isdigit() else (-1, p)
        ps.sort(key=cle)
        if not ps: return ""
        return ps[0] if len(ps) == 1 else f"{ps[0]}-{ps[-1]}"

    def texte_notes(self, chap, nums):
        out = []
        for n in nums:
            k = f"{chap}:{n}"
            if k in self.notes:
                out.append(f"n{n} : " + " ".join(self.notes[k]))
        return " || ".join(out)


# ---------------------------------------------------------------- lecture des extractions
def chapitre_de(fn):
    m = re.fullmatch(r"ch(\d+)\.txt", fn)
    return int(m.group(1)) if m else None


def lire_extractions(pg, erreurs):
    lignes = []
    for fn in sorted(os.listdir(EXTR)):
        if not fn.endswith(".txt"): continue
        chap = chapitre_de(fn)
        for no, l in enumerate(open(os.path.join(EXTR, fn), encoding="utf-8"), 1):
            l = l.rstrip("\n")
            if not l.startswith("E|"): continue
            f = l.split("|")
            if len(f) != 12:
                erreurs.append(f"{fn}:{no} : {len(f)} champs au lieu de 12"); continue
            _, date, fin, heure, typ, cat, quoi, qui, lieu, para, codes, note = [x.strip() for x in f]
            lignes.append(dict(fn=fn, no=no, chap=chap, date=date, fin=fin, heure=heure, type=typ, cat=cat,
                               quoi=quoi, qui=qui, lieu=lieu, para=para, codes=codes, note=note))
    return lignes


def convertir(e, pg, erreurs):
    ou = f"{e['fn']}:{e['no']}"
    if e["type"] not in TYPES: erreurs.append(f"{ou} : type inconnu {e['type']!r}")
    if e["cat"] not in CATEGORIES: erreurs.append(f"{ou} : catégorie inconnue {e['cat']!r}")
    codes = [c for c in re.split(r"[ ,;]+", e["codes"]) if c]
    for c in codes:
        if c not in CODES: erreurs.append(f"{ou} : code inconnu {c!r}")
    codes = [c for c in codes if c in CODES]
    if not e["date"]:
        d0 = d1 = None; prec = "sans_date"
    else:
        tilde = e["date"].startswith("~")
        try:
            d0, d1, prec = borne(e["date"].lstrip("~"))
        except ValueError as x:
            erreurs.append(f"{ou} : {x}"); return None
        if tilde and not set(codes) & {"calc", "rel", "ded", "approx", "corr"}:
            codes.append("approx")
    if e["fin"]:
        try:
            f0, f1, fprec = borne(e["fin"].lstrip("~"))
            d1 = f1
            if fprec in GROSSIERE and prec == "jour": prec = "plage"
            elif prec == "jour": prec = "plage"
        except ValueError as x:
            erreurs.append(f"{ou} : fin {x}")
    pct, motifs = 0, []
    for c in dict.fromkeys(codes):
        pct += CODES[c][0]; motifs.append(f"{CODES[c][1]} (+{CODES[c][0]})")
    if prec in GROSSIERE and "approx" not in codes:
        pct += 25; motifs.append(f"date au {prec.replace('_', ' ')} seulement (+25)")
    if prec == "sans_date":
        pct += 25; motifs.append("événement sans date dans le livre (+25)")
    if e["date"].startswith("~") and "approx" in codes and "date approximative" not in " ".join(motifs):
        pass
    pct = min(pct, 90)
    if not motifs: motifs = ["date donnée telle quelle par Duberman"]
    debut = fin_h = ""
    h = e["heure"]
    if re.fullmatch(r"\d{1,2}:\d{2}", h): debut = h.zfill(5)
    elif h in MOMENTS: debut = h
    elif h: erreurs.append(f"{ou} : heure illisible {h!r}")
    chap = e["chap"]
    nums = [int(n) for n in re.findall(r"\bn(\d+)\b", e["para"] + " " + e["note"])]
    nums = list(dict.fromkeys(nums))
    page = pg.pages(e["para"])
    if not page and nums and chap:
        ps = [pg.page_note.get(f"{chap}:{n}") for n in nums]
        ps = [p for p in ps if p]
        if ps: page = f"{ps[0]} (notes)" if len(set(ps)) == 1 else f"{ps[0]}-{ps[-1]} (notes)"
    if not page and e["fn"] == "liminaire.txt": page = "pages liminaires"
    if chap:
        lieu_livre = f"ch. {chap} « {CHAPITRES[chap]} »"
    else:
        lieu_livre = FICHIERS.get(e["fn"][:-4], e["fn"][:-4])
    src = f"{LIVRE}, {lieu_livre}" + (f", p. {page}" if page else "") + (f" ({e['para']})" if e["para"] else "")
    return {
        "date": d0.isoformat() if d0 else "", "jour": JOURS[d0.weekday()] if d0 and (prec == "jour" or (prec == "plage" and re.fullmatch(r"~?\d{4}-\d{2}-\d{2}", e["date"]))) else "",
        "debut": debut, "fin": fin_h, "type": e["type"], "activite": e["quoi"], "qui": e["qui"], "lieu": e["lieu"],
        "note": e["note"], "recurrent_deduit": "", "part_deduite_pct": pct, "motifs_deduction": " ; ".join(motifs),
        "document_source": src, "inventaire": "", "url_source": "",
        "date_fin": d1.isoformat() if d1 and d1 != d0 else "", "precision": prec, "date_livre": e["date"] + (f" → {e['fin']}" if e["fin"] else ""),
        "categorie": e["cat"], "chapitre": chap or e["fn"][:-4], "page": page, "paragraphe": e["para"],
        "notes_citees": " ".join(f"n{n}" for n in nums), "notes_texte": pg.texte_notes(chap, nums) if chap else "",
        "fichier_extraction": e["fn"], "ligne_extraction": e["no"],
    }


# ---------------------------------------------------------------- documents datés des notes
MOIS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                    "september", "october", "november", "december"], 1)}
RX_MOIS = "(January|February|March|April|May|June|July|August|September|October|November|December)"
# « April 10, 20, September 1, 1944 » : suite de (mois jours…) close par l'année
RX_SUITE = re.compile(rf"((?:{RX_MOIS}\s+\d{{1,2}}(?:\s*\[\?\])?(?:\s*(?:,|and|&)\s*\d{{1,2}}(?!\d))*\s*,?\s*(?:and\s+)?)+)(\d{{4}})")
RX_MOIS_AN = re.compile(rf"(?<![\w]){RX_MOIS}\s*,?\s+(\d{{4}})")


def dates_de(seg):
    out = []
    for m in RX_SUITE.finditer(seg):
        an = int(m.group(3)); mois = None
        for t in re.finditer(rf"{RX_MOIS}|\d{{1,2}}", m.group(1)):
            if t.group(0).isalpha(): mois = MOIS[t.group(0).lower()]
            elif mois:
                try: out.append((dt.date(an, mois, int(t.group(0))).isoformat(), "jour"))
                except ValueError: pass
    if not out:
        for m in RX_MOIS_AN.finditer(seg):
            out.append((f"{int(m.group(2)):04d}-{MOIS[m.group(1).lower()]:02d}", "mois"))
    return out


def type_doc(seg):
    s = seg.lower()
    if re.search(r"\binterviews?\b|telephone conversation|\btape\b|taped reminiscences", s): return "entretien"
    if re.search(r"\bminutes\b|notes (?:on|of) (?:the )?(?:special |regular |annual )?(?:\w+ )?meeting|meetings? of the", s): return "proces_verbal"
    if re.search(r"bulletin|catalog|newsletter|review\b|magazine|\bform, no|partisan|times|journal|\bsun\b|citizen|herald|tribune|newspaper|\bpost\b|\bnation\b|\bwin\b", s): return "publication"
    if re.search(r"\btelegram|night letter|cable", s): return "telegramme"
    if re.search(r"\bdiary\b|journal entry", s): return "journal"
    if re.search(r"[A-Z][a-z.’']+\s+to\s+(?:me|the|[A-Z])", seg) or re.search(r"\b(?:wrote|letters?|note)\b", s): return "lettre"
    if re.search(r"statement|report|memo|manuscript|typewritten|petition|announcement|program", s): return "document"
    return "autre"


def fonds(apres):
    """Fonds cité juste après la date (avant le document suivant)."""
    a = re.split(r";|\.\s+[A-Z]", apres, 1)[0][:120]
    if re.search(r"Raleigh|State Archives", a): return "Raleigh Archives"
    m = re.search(r"courtesy (?:of )?([A-Z][\w.’' -]+?)(?:[,;.)]|$)", a)
    if m: return "courtesy " + m.group(1).strip()
    if "Rollins" in a: return "Rollins Archives"
    m = re.search(r"all (?:in|from) (?:the )?(Raleigh|Rollins|State Archives)|—\s*(?:all )?courtesy (?:of )?([A-Z][\w.’' -]+?)(?:[,;.)]|$)", apres[:900])
    if m: return ("Raleigh Archives" if m.group(1) == "State Archives" else m.group(1) + " Archives") if m.group(1) else "courtesy " + m.group(2).strip()
    return ""


def documents(pg):
    out = []
    for k, paras in pg.notes.items():
        chap, n = k.split(":")
        texte = " ".join(paras)
        texte = re.sub(r"^\s*\d+\.\s*", "", texte)
        # segmentation aux « ; » et « — » hors guillemets approximative
        segs = re.split(r";\s+|\s+—\s*(?=[A-Z])|(?<=\))\.\s+|(?<=[a-z]{3})\.\s+(?=[A-Z])", texte)
        off = 0
        for seg in segs:
            o = texte.find(seg, off); o = off if o < 0 else o; off = o + len(seg)
            # chaque date prend pour contexte le texte depuis la date précédente du même segment ;
            # sans mot-clé propre, le contexte hérite du type précédent (« interviews with A (…), B (…) »)
            t_prec, debut = None, 0
            pos = [m.end() for m in RX_SUITE.finditer(seg)] or [m.end() for m in RX_MOIS_AN.finditer(seg)]
            for fin in pos:
                ctx = seg[debut:fin]
                ds = dates_de(ctx[max(0, len(ctx) - 120):]) or dates_de(ctx)
                t = type_doc(ctx)
                if t == "autre" and t_prec: t = t_prec
                t_prec, debut = t, fin
                for d, p in ds:
                    out.append({"date": d, "precision": p, "type_doc": t, "description": seg.strip()[:500],
                                "contexte": ctx.strip(" ,;.")[:300],
                                "chapitre": chap, "note": f"n{n}", "page": pg.page_note.get(k, ""),
                                "fonds": fonds(texte[o + fin:])})
    vus, uniq = set(), []
    for d in out:
        c = (d["date"], norm(d["contexte"])[:120], d["chapitre"], d["note"])
        if c not in vus:
            vus.add(c); uniq.append(d)
    uniq.sort(key=lambda d: (d["date"], int(d["chapitre"]) if d["chapitre"].isdigit() else 0, d["note"]))
    return uniq


# ---------------------------------------------------------------- recoupements
def mots(s):
    return {w for w in norm(s).split() if len(w) > 3}


def recouper(evs):
    aam = list(csv.DictReader(open(AAM, encoding="utf-8"))) if os.path.exists(AAM) else []
    par_date = collections.defaultdict(list)
    for a in aam: par_date[a["date"]].append(a)
    lignes = []
    for e in evs:
        e["recoupement_aam"] = ""
        if e["precision"] != "jour": continue
        noms = {norm(q.split()[-1]) for q in e["qui"].split(";") if q.strip()}
        noms = {n for n in noms if len(n) > 3}
        forts = []
        for a in par_date.get(e["date"], []):
            texte_a = " " + norm(a["qui"] + " " + a["activite"]) + " "
            commun = sorted(n for n in noms if f" {n} " in texte_a)
            meme_type = e["type"] == a["type"] and e["type"] in ("reunion", "concert", "theatre", "conference", "danse", "expo", "visite")
            if commun or meme_type:
                force = "fort" if commun and (e["type"] == a["type"] or len(commun) > 1) else "moyen" if commun or meme_type else ""
                lignes.append({"source": "AAM programme/evenements.csv", "date": e["date"], "force": force,
                               "duberman": e["activite"][:200], "autre": a["activite"][:200],
                               "noms_communs": " ; ".join(commun), "meme_type": "oui" if e["type"] == a["type"] else "",
                               "duberman_ref": f"{e['fichier_extraction']}:{e['ligne_extraction']}",
                               "autre_ref": a["document_source"][:160]})
                if force == "fort" or meme_type: forts.append(a["activite"][:80] + f" [{a['inventaire']}]")
        e["recoupement_aam"] = " || ".join(forts[:3])
    # Chronos 2 : quelles dates de l'ancienne extraction n'ont pas d'équivalent ici ?
    chron = json.load(open(CHRONOS, encoding="utf-8"))["events"] if os.path.exists(CHRONOS) else []
    dates_d = collections.defaultdict(list)
    for e in evs:
        if e["date"]:
            for cle in {e["date"], e["date"][:7], e["date"][:4]}:
                dates_d[cle].append(e)
    absents = []
    def date_chronos(d):
        d = (d or "").strip()
        if re.fullmatch(r"\d{4}(-\d{2}(-\d{2})?)?", d): return d
        m = re.search(rf"{RX_MOIS}\s+(\d{{1,2}}),?\s+(\d{{4}})", d)
        if m: return f"{m.group(3)}-{MOIS[m.group(1).lower()]:02d}-{int(m.group(2)):02d}"
        m = re.search(rf"{RX_MOIS},?\s+(\d{{4}})", d)
        if m: return f"{m.group(2)}-{MOIS[m.group(1).lower()]:02d}"
        m = re.search(r"(christmas)\D*(\d{4})", d, re.I)
        if m: return f"{m.group(2)}-12"
        m = re.search(r"(\d{4})", d)
        return m.group(1) if m else ""
    for c in chron:
        d = date_chronos(c.get("date", ""))
        cands = (dates_d.get(d, []) + dates_d.get(d[:7], [])) if len(d) >= 7 else dates_d.get(d[:4], [])
        # tolérance : l'année voisine (dates de Chronos parfois décalées d'un an scolaire)
        if not cands or len(d) == 4:
            for y in (int(d[:4]) - 1, int(d[:4]) + 1) if d[:4].isdigit() else ():
                cands = cands + dates_d.get(str(y), [])
        noms = mots(" ".join(c.get("people") or []))
        trouve = any(noms & mots(x["activite"] + " " + x["qui"]) for x in cands) if noms else bool(cands)
        lignes.append({"source": "Chronos 2 bmc_chronology.json", "date": d, "force": "", "duberman": "" if not trouve else "trouvé",
                       "autre": c.get("event", "")[:200], "noms_communs": "", "meme_type": "",
                       "duberman_ref": "", "autre_ref": c.get("source", "")})
        if not trouve: absents.append(c)
    return lignes, absents, len(aam), len(chron)


def ecrire(p, cols, rows):
    with open(p, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)


def main():
    erreurs = []
    pg = Pages()
    evs = [x for x in (convertir(e, pg, erreurs) for e in lire_extractions(pg, erreurs)) if x]
    evs.sort(key=lambda e: (e["date"] or "9999", e["debut"] or "", e["chapitre"] if isinstance(e["chapitre"], int) else 0))
    docs = documents(pg)
    ecrire(os.path.join(ICI, "documents_duberman.csv"),
           ["date", "precision", "type_doc", "contexte", "description", "chapitre", "note", "page", "fonds"], docs)
    extra = [{"date": d["date"] if d["precision"] == "jour" else d["date"] + "-01",
              "titre": d["contexte"][:300], "url": "", "image": "", "type": d["type_doc"],
              "datation": "date du document citée dans les notes de Duberman" + ("" if d["precision"] == "jour" else " (mois seulement)"),
              "source": f"{LIVRE}, notes du ch. {d['chapitre']}, {d['note']}" + (f", p. {d['page']}" if d["page"] else ""),
              "part_deduite_pct": 0 if d["precision"] == "jour" else 25, "inventaire": ""}
             for d in docs if d["date"][:4] < "1958" and d["type_doc"] != "entretien"]
    ecrire(os.path.join(ICI, "documents_extra_duberman.csv"),
           ["date", "titre", "url", "image", "type", "datation", "source", "part_deduite_pct", "inventaire"], extra)
    rec, absents, n_aam, n_chron = recouper(evs)
    ecrire(os.path.join(ICI, "evenements_duberman.csv"), COLONNES, evs)
    ecrire(os.path.join(ICI, "recoupements_duberman.csv"),
           ["source", "date", "force", "duberman", "autre", "noms_communs", "meme_type", "duberman_ref", "autre_ref"], rec)

    c = collections.Counter
    with open(os.path.join(ICI, "rapport_duberman.txt"), "w", encoding="utf-8") as f:
        pr = lambda *a: print(*a, file=f)
        pr(f"Événements : {len(evs)}")
        pr("Par précision :", dict(c(e["precision"] for e in evs).most_common()))
        pr("Par type :", dict(c(e["type"] for e in evs).most_common()))
        pr("Par catégorie :", dict(c(e["categorie"] for e in evs).most_common()))
        pr("Par décennie :", dict(sorted(c((e["date"] or "????")[:3] + "0" for e in evs).items())))
        pr("Part déduite moyenne : %.1f %%" % (sum(e["part_deduite_pct"] for e in evs) / max(1, len(evs))))
        pr("Sans page :", sum(1 for e in evs if not e["page"]))
        pr(f"\nDocuments datés extraits des notes : {len(docs)} ({dict(c(d['type_doc'] for d in docs).most_common())})")
        pr(f"  dont au format documents_extra (avant 1958, hors entretiens) : {len(extra)}")
        pr(f"\nRecoupements AAM le même jour : {sum(1 for r in rec if r['force'] == 'fort')} forts (nom + type), "
           f"{sum(1 for r in rec if r['force'] == 'moyen')} moyens ; {sum(1 for e in evs if e['recoupement_aam'])} événements Duberman recoupés "
           f"(base AAM : {n_aam} événements)")
        jours = [e for e in evs if e["precision"] == "jour" and e["date"][:4] <= "1957" and e["categorie"] not in ("historiographie", "contexte")]
        pr(f"Événements Duberman datés au jour pendant la vie du college : {len(jours)}, dont sans équivalent AAM le même jour : {sum(1 for e in jours if not e['recoupement_aam'])}")
        pr(f"Chronos 2 : {n_chron - len(absents)}/{n_chron} retrouvés ; non retrouvés : {len(absents)}")
        for a in absents:
            pr(f"   {a.get('date',''):10} {a.get('event','')[:110]}  [{a.get('source','')}]")
        pr(f"\nErreurs de format : {len(erreurs)}")
        for x in erreurs: pr("  " + x)
    print(open(os.path.join(ICI, "rapport_duberman.txt"), encoding="utf-8").read()[:3000])
    if erreurs: sys.exit(1)


if __name__ == "__main__":
    main()
