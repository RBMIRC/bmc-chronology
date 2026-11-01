"""Audit d'exhaustivité des événements : chaque phrase datée de chaque document est-elle dans le calendrier ?
Pour chaque document de liste_pages.csv : découpe le texte transcrit (pages_txt/) en phrases, garde celles qui portent
un repère temporel (jour de la semaine, date, heure, « tonight », « next week »…), et cherche parmi les entrées E tirées
du MÊME document (extraction/<inventaire>.txt) celle qui la couvre (mots significatifs et noms propres en commun).
Sorties : programme/audit/evenements_candidats.csv (une ligne par phrase datée : couverte / à vérifier)
          programme/audit/EVENEMENTS.md (bilan par document).
Une phrase « à vérifier » n'est pas forcément un oubli : rappel d'un événement déjà noté ailleurs, date d'une autre
nature (naissance, publication), phrase coupée par l'OCR. Chaque cas est tranché à la main dans extraction/."""
import csv, os, re, glob, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "programme", "audit")
MOIS = r"(jan(uary)?|feb(ruary)?|mar(ch)?|apr(il)?|may|june?|july?|aug(ust)?|sept?(ember)?|oct(ober)?|nov(ember)?|dec(ember)?)\.?"
REPERES = [
    ("jour", r"\b(mon|tues|wednes|thurs|fri|satur|sun)day\b"),
    ("date", r"\b" + MOIS + r"\s+\d{1,2}\b|\b\d{1,2}(st|nd|rd|th)?\s+(of\s+)?" + MOIS + r"\b"),
    ("heure", r"(?<![$\d.,])\b\d{1,2}[:.]\d{2}\b(?![\d.,])|\b\d{1,2}\s*(o'?clock|o’clock|a\.?\s?m\.?|p\.?\s?m\.?)\b"),
    ("relatif", r"\b(tonight|tomorrow|this (morning|afternoon|evening|week|weekend)|next (week|month|term|semester|quarter)|last (week|night|month|term)|yesterday|today)\b"),
]
VIDE = set("""the a an and or of to in on at for by with from is are was were be been will would this that these those his her
their its our we he she they it as not but also has have had which who whom what when where there here into than then
so such all any each other more most some no only same very can may shall should could one two three four five six
seven eight nine ten first second third next last week weeks day days evening morning afternoon night college black
mountain community bulletin monday tuesday wednesday thursday friday saturday sunday january february march april june
july august september october november december o'clock p.m a.m mr mrs miss dr""".split())

def mots(s):
    return {m for m in re.findall(r"[a-zà-ÿ][a-zà-ÿ'’-]{2,}", s.lower()) if m not in VIDE}

def noms(s):
    return set(re.findall(r"\b[A-Z][a-z]{2,}\b", s)) - {"The", "This", "There", "Black", "Mountain", "College", "Monday",
        "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "January", "February", "March", "April", "May",
        "June", "July", "August", "September", "October", "November", "December", "Mrs", "Miss", "Bulletin", "Community"}

def phrases(texte):
    t = re.sub(r"\s+", " ", texte)
    t = re.sub(r"\b(Mr|Mrs|Dr|Miss|St|No|Vol|p\.m|a\.m|Jr|Sr|ca|vs|etc)\.", lambda m: m.group(0).replace(".", "§"), t)
    out = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9“\"(])", t)
    return [p.replace("§", ".").strip() for p in out if len(p.strip()) > 15]

def main():
    pages = {}
    for f in glob.glob(os.path.join(ROOT, "pages_txt", "*", "*.txt")):
        pages[os.path.basename(f).split("_")[0]] = f
    with open(os.path.join(ROOT, "liste_pages.csv"), encoding="utf-8") as f:
        docs = list(csv.DictReader(f))
    MOISN = {m: i + 1 for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}
    JOURS_EN = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    JOURS_FR = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    par_inv = collections.defaultdict(list)
    with open(os.path.join(ROOT, "programme", "evenements.csv"), encoding="utf-8") as f:
        for e in csv.DictReader(f):
            for i in e["inventaire"].split(" ; "): par_inv[i].append(e)
    per_inv = collections.defaultdict(list)
    with open(os.path.join(ROOT, "programme", "calendrier_periodes.csv"), encoding="utf-8") as f:
        for p_ in csv.DictReader(f):
            for i in p_["inventaire"].split(" ; "):
                for dd in (p_["debut"], p_["fin"]):
                    if dd: per_inv[i].append({"date": dd, "debut": "", "activite": p_["libelle"], "qui": "", "lieu": "",
                                              "note": p_["note"], "jour": JOURS_FR[__import__("datetime").date.fromisoformat(dd).weekday()]})
    par_date = collections.defaultdict(list)          # tous les événements, toutes sources, par date
    with open(os.path.join(ROOT, "programme", "evenements.csv"), encoding="utf-8") as f:
        for e in csv.DictReader(f): par_date[e["date"]].append(e)
    rows, bilan = [], []
    for d in docs:
        inv = d["accession"]; f = pages.get(inv)
        if not f: continue
        texte = open(f, encoding="utf-8").read()
        texte = texte.split("=" * 20, 1)[-1]                    # sans l'en-tête de la fiche
        ext = os.path.join(ROOT, "extraction", inv + ".txt")
        lignes = [l.rstrip("\n").split("|") for l in open(ext, encoding="utf-8")] if os.path.exists(ext) else []
        E = [l for l in lignes if l and l[0] == "E" and len(l) == 9]
        ignore = any(l and l[0].startswith("//") for l in lignes) and not E
        revu = any(l and l[0].startswith("#revu_evenements") for l in lignes)
        jumeaux = set()
        for l in lignes:
            if l and l[0].startswith("//"):
                jumeaux |= set(re.findall(r"\d{4}\.\d{2}\.[0-9a-z.\-]+", "|".join(l)))
        evs = list(par_inv.get(inv, [])) + list(per_inv.get(inv, []))
        for j in jumeaux - {inv}:
            for k in par_inv:
                if k == j or k.startswith(j.rstrip(".")): evs += par_inv[k]
        ref_doc = next((l[0].split()[1] for l in lignes if l and l[0].startswith("#ref")), d["date"])
        indexE = [(mots(" ".join([e["activite"], e["qui"], e["lieu"], e["note"]])),
                   noms(" ".join([e["activite"], e["qui"], e["lieu"], e["note"]])), e) for e in evs]
        n_dates = n_couv = 0
        for p in phrases(texte):
            rep = [k for k, rx in REPERES if re.search(rx, p, re.I)]
            if not rep: continue
            n_dates += 1
            mp, np_ = mots(p), noms(p)
            # contraintes de date : mois-jour explicites, jour de la semaine
            md = set()
            for m in re.finditer(r"\b" + MOIS + r"\s+(\d{1,2})\b", p, re.I):
                md.add((MOISN[m.group(1)[:3].lower()], int(m.group(m.lastindex))))
            for m in re.finditer(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(?:of\s+)?" + MOIS + r"\b", p, re.I):
                md.add((MOISN[m.group(2)[:3].lower()], int(m.group(1))))
            js = {JOURS_FR[i] for i, j in enumerate(JOURS_EN) if re.search(r"\b" + j + r"\b", p, re.I)}
            best, sc = None, 0
            cands = list(indexE)
            if md:   # date explicite : aussi les événements de ces dates, toutes sources (année du document ± 1)
                try: an = int(re.search(r"\d{4}", ref_doc).group(0))
                except Exception: an = None
                for (mo_, d_) in md:
                    for y_ in ([an - 1, an, an + 1] if an else []):
                        for e in par_date.get(f"{y_}-{mo_:02d}-{d_:02d}", []):
                            t = " ".join([e["activite"], e["qui"], e["lieu"], e["note"]])
                            cands.append((mots(t), noms(t), e))
            for mE, nE, e in cands:
                y, mo, d_ = map(int, e["date"].split("-"))
                if md and (mo, d_) not in md: continue
                if not md and js and e["jour"] not in js: continue
                s = len(mp & mE) + 2 * len(np_ & nE)
                if s > sc: best, sc = e, s
            couvert = sc >= (2 if md else 3)
            n_couv += couvert
            rows.append({"inventaire": inv, "categorie": d["categorie"][:1], "date_doc": d["date"], "reperes": "+".join(rep),
                         "statut": "couverte" if couvert else ("relue, non retenue" if revu else "à vérifier"),
                         "score": sc, "phrase": p[:500],
                         "entree_proche": (f"{best['date']} {best['debut']} {best['activite']} · {best['qui']}" if best else "")[:300]})
        bilan.append((inv, d["categorie"][:1], d["titre"][:70], n_dates, n_couv, len(E), ignore))
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "evenements_candidats.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    st = collections.Counter(r["statut"] for r in rows)
    L = ["# Audit d'exhaustivité des événements", "",
         f"{len(bilan)} documents, {len(rows)} phrases datées : " + ", ".join(f"{k} {v}" for k, v in st.most_common()) + ".", "",
         "| inventaire | cat. | titre | phrases datées | couvertes | entrées E | à vérifier |", "|---|---|---|---|---|---|---|"]
    for inv, c, t, n, k, e, ig in sorted(bilan, key=lambda b: -(b[3] - b[4])):
        if n: L.append(f"| {inv} | {c} | {t} | {n} | {k} | {e} | {'écarté' if ig else n - k} |")
    open(os.path.join(OUT, "EVENEMENTS.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(L[2])

if __name__ == "__main__":
    main()
