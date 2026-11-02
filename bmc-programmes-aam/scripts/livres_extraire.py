"""Livres et articles (textes des PDF de DATA_BMC/textes_pdf) : inventaire, extraction des dates et des faits, recoupements,
couche du semainier.

Entrée : DATA_BMC/textes_pdf/*.txt (scripts/pdf_vers_texte.py, sur l'ordinateur qui a les PDF), lus par livres_commun.py
(pages, colonnes recollées, paragraphes, phrases).
1. Inventaire : référence (tirée de la page de titre, table META), genre, doublons (même texte), pages du livre
   (numéro imprimé repéré en tête ou en pied de page : décalage le plus fréquent avec la page du PDF).
2. Extraction : chaque phrase qui porte une date de 1933 à 1957 (« March 5, 1945 », « 5 March 1945 », « March 1945 »,
   « the summer of 1944 » ; « on March 5 » si l'année est donnée plus haut dans le même paragraphe) et qui parle du
   collège (personne de la base du BMC Yearbook, ou lieu ou mot du collège dans la phrase ou la précédente).
   Personnes : noms complets de la base, ou nom de famille seul quand il est propre à une seule personne du corps
   enseignant ; type d'après les mots de la phrase. L'activité affichée est le début de la phrase : rien n'est réécrit.
3. Vérification (règle du 2/11/2026, demande de Sylvain : « ne mets pas de dates à moitié vérifiées ») : rien de ces
   textes n'entre seul dans le semainier. Un fait n'y paraît que vérifié AU JOUR par une source qui fait foi (document
   daté de l'AAM, Duberman daté au jour, Rumaker daté au jour, fiche du musée datée au jour) : même jour exact (pas une
   plage, pas un mois), personne commune avec le même prénom, mot commun ; pour une lettre ou un procès-verbal cité,
   toutes ses personnes dans la fiche de base. Il devient un renvoi sur la fiche existante, après relecture manuelle
   (livres/revue_renvois.txt). Le reste est « à vérifier » (livres/NNN_a_verifier.md), avec ce qu'en disent l'AAM ou
   Duberman au mois, le scénario et les autres livres (indices, pas preuves). Traduction automatique : jamais posée.
Part déduite : genre (étude +10 ; témoignage écrit après coup +10 ; traduction automatique +20 ; document de l'époque 0)
+ extraction automatique non relue +10 + date au mois ou à la saison +25 ou année reprise du contexte +15 ; plafond 90.
Sorties (numéro suivant, jamais écrasées) : livres/NNN_inventaire.csv, NNN_evenements_livres.csv, NNN_renvois_semainier.csv,
NNN_a_verifier.md, NNN_rapport_livres.md ; chronos/NNN_livres_couche.csv vide (aucune entrée propre au semainier).
"""
import collections, csv, datetime as dt, glob, hashlib, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chronos_commun as K
import livres_commun as L
import verifier_sources as V

ROOT = K.ROOT; ICI = os.path.join(ROOT, "livres"); SRC = os.path.join(K.DEPOT, "DATA_BMC", "textes_pdf")

# référence et genre, d'après la page de titre de chaque texte (rien d'ajouté qui n'y soit) ; clé = début du nom de fichier
META = [
    ("The arts at Black Mountain College", "harris1987", "Mary Emma Harris, The Arts at Black Mountain College (Cambridge, Mass., MIT Press, 1987, 2e tirage)", "étude"),
    ("Black Mountain College_ sprouted seeds", "lane1990", "Mervin Lane (éd.), Black Mountain College: Sprouted Seeds. An Anthology of Personal Accounts (Knoxville, University of Tennessee Press, 1990)", "témoignage"),
    ("Red Brick, Black Mountain, White Clay", "benfey", "Christopher Benfey, Red Brick, Black Mountain, White Clay: Reflections on Art, Family, and Survival", "témoignage"),
    ("The Experimenters Chance and Design", "diaz", "Eva Díaz, The Experimenters: Chance and Design at Black Mountain College", "étude"),
    ("The Experimente", "diaz_b", "Eva Díaz, The Experimenters (autre copie)", "étude"),
    ("Art_of_Making_Art_Schools_Reader", "dking", "Dorothée King, Making Art Schools: A Reader", "étude"),
    ("tesis_ana_gilsanz_diaz_compressed (1_2", "gilsanz1", "Ana C. Gilsanz Díaz, thèse sur l'architecture au Black Mountain College (1933-57), 1re partie (traduction automatique Google de l'espagnol)", "traduction automatique"),
    ("tesis_ana_gilsanz_diaz_compressed 2_2", "gilsanz2", "Ana C. Gilsanz Díaz, thèse sur l'architecture au Black Mountain College (1933-57), 2e partie (traduction automatique Google de l'espagnol)", "traduction automatique"),
    ("This Other Way", "canter2024", "Kyle Canter, « This Other Way »: Photography at Black Mountain College (mémoire, Hunter College, CUNY, 2024)", "étude"),
    ("Revisiting Black Mountain", "oncurating2019", "Revisiting Black Mountain: Cross-Disciplinary Experiments and Their Potential for Democratization (OnCurating, n° 43, 2019)", "étude"),
    ("Revisiting_Black_MountainCross", "oncurating2019_b", "Revisiting Black Mountain (OnCurating, n° 43, 2019, autre copie)", "étude"),
    ("Black_Mountain_Research", "lehmann", "Annette Jael Lehmann (avec Verena Kittel et Anna-Lena Werner), Black Mountain Research", "étude"),
    ("A_new_art_of_living_The_three_ecologies (1)", "ecologies_b", "A New Art of Living: The Three Ecologies of Black Mountain College (mémoire de master, Georgetown University, autre copie)", "étude"),
    ("A_new_art_of_living_The_three_ecologies", "ecologies", "A New Art of Living: The Three Ecologies of Black Mountain College (mémoire de master, Georgetown University)", "étude"),
    ("The life and work of the college", "fisher_memoire", "Jonathan Fisher, The life and work of the college: Towards a history of Black Mountain College as an institution of progressive higher education, 1933-1949 (mémoire de Master of Education)", "étude"),
    ("The Life and Work of an Institution", "fisher_jbmcs", "Jonathan Fisher, « The Life and Work of an Institution of Progressive Higher Education: Towards a History of Black Mountain College, 1933-1949 », Journal of Black Mountain College Studies, vol. 6", "étude"),
    ("mc richards history", "taylor2019", "Mabel Capability Taylor, « \"It wouldn't have been like a history\": M.C. Richards's Black Mountain », Journal of Black Mountain College Studies, vol. 9 (printemps 2019)", "étude"),
    ("GOLDOWSKI-BlackMountainCollege", "bmcreview1951", "Black Mountain College Review (1951 ; contributions de Natasha Goldowski, Nick Cernovich, Russell Edson, Joel Oppenheimer, Alex Kemeny, Pat Edson, F. Dawson ; JSTOR, Reveal Digital)", "document d'époque"),
    ("The Sciences at Black Mountain College", "peifer", "David Peifer, « The Sciences at Black Mountain College », Journal of Black Mountain College Studies, vol. 12", "étude"),
    ("king-martha-black-mountain", "mking2010", "Martha King, « Three Months in 1955: A Memoir of Black Mountain College », Jacket 40 (fin 2010)", "témoignage"),
    ("Women at Black Mountain College", "unca_femmes", "Socioeconomic Subordination and Misogyny in the Progressive Left: Women at Black Mountain College, 1933-1957 (mémoire de licence en histoire, UNC Asheville)", "étude"),
    ("A Quaker History of Black Mountain College", "ates2022", "Alex Ates, « A Quaker History of Black Mountain College », Journal of Black Mountain College Studies, vol. 13 (avril 2022)", "étude"),
    ("Diaz-Arnolfini-BMC", "arnolfini", "Starting at Zero: Black Mountain College 1933-57 (catalogue ; essais de Mary Emma Harris, Christopher Benfey, Eva Díaz, Edmund de Waal)", "étude"),
    ("Why John Andrew Rice", "ritter2011", "Jennifer M. Ritter, « Beyond Progressive Education: Why John Andrew Rice Really Opened Black Mountain College », Rollins Undergraduate Research Journal, vol. 5, n° 2 (2011)", "étude"),
    ("Progressive Ideals and Experimental", "reynolds1997", "Katherine C. Reynolds, « Progressive Ideals and Experimental Higher Education: The Example of John Dewey and Black Mountain College », Education and Culture, vol. 14, n° 1 (1997)", "étude"),
    ("Pedagogy_of_Presence", "muir", "Angela Muir, « Pedagogy of Presence: The Black Mountain College Method of Instruction »", "étude"),
    ("TheMA_BlackMountainCollege_2017", "nikolic2017", "Sanela Nikolić, « The Educational Turn and Black Mountain College » (2017)", "étude"),
    ("Lindsay-ProgressiveEducationBlack-1977", "lindsay1977", "Beverly Lindsay et J. John Harris III, « Progressive Education and the Black College », Journal of Black Studies, vol. 7, n° 3 (mars 1977)", "étude"),
    ("Black_Mountain_College_Case_Transformati", "migasova2019", "Jana Migašová, « Black Mountain College Case: Transformation Trends in Art Education in the First Half of the 20th Century » (2019)", "étude"),
    ("Trueman MacHenry at Black Mountain College", "silver2015", "David Silver, « Trueman MacHenry at Black Mountain College », Journal of Black Mountain College Studies, vol. 7 (mars 2015)", "étude"),
    ("A Plan for Black Mountain College", "aydelotte", "« A Plan for Black Mountain College » (dossier « Alternative Institutions »)", "étude"),
    ("African American Students at BMC", "south2020", "African American Students at BMC (liste de Heather South, Western Regional Archives, mise à jour du 7 février 2020)", "document d'archives"),
]
PREFERE = {"diaz_b": "diaz", "oncurating2019_b": "oncurating2019", "ecologies_b": "ecologies"}   # doublon → copie gardée
GENRE = {"étude": (10, "étude publiée après coup (source secondaire)"), "témoignage": (10, "témoignage écrit après coup (mémoires, souvenirs)"),
         "traduction automatique": (20, "étude lue en traduction automatique (Google) : mots et noms peut-être altérés"),
         "document d'époque": (0, "document de l'époque"), "document d'archives": (0, "liste d'archives")}

MOIS = {m: i + 1 for i, m in enumerate("january february march april may june july august september october november december".split())}
MOIS.update({"jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12})
RM = r"(January|February|March|April|May|June|July|August|September|October|November|December|Jan\.|Feb\.|Mar\.|Apr\.|Jun\.|Jul\.|Aug\.|Sept?\.|Oct\.|Nov\.|Dec\.)"
RJ = r"(\d{1,2})(?:st|nd|rd|th)?"
RY = r"(19[3-5]\d)"
SAISONS = {"spring": (3, 21, 6, 20), "summer": (6, 21, 9, 22), "fall": (9, 23, 12, 20), "autumn": (9, 23, 12, 20), "winter": (12, 21, 3, 20)}
MOTIFS = [
    ("plage", re.compile(rf"\b{RM}\s+{RJ}\s*(?:and|-|–|to|through)\s*{RJ},?\s+{RY}\b")),       # November 23 and 24, 1944
    ("jour", re.compile(rf"\b{RM}\s+{RJ},?\s+{RY}\b")),                                   # March 5, 1945
    ("jour", re.compile(rf"\b{RJ}\s+(?:of\s+)?{RM},?\s+{RY}\b")),                          # 5 March 1945
    ("mois", re.compile(rf"\b{RM}\s+(?:of\s+)?{RY}\b")),                                  # March 1945, March of 1945
    ("saison", re.compile(rf"\b(?:the\s+)?(?:(early|late|mid-?)\s*)?(spring|summer|fall|autumn|winter)\s+(?:term|semester|quarter|session|institute\s+)?(?:of\s+)?{RY}\b", re.I)),
    ("saison", re.compile(rf"\b{RY}\s+(spring|summer|fall|autumn|winter)\b", re.I)),     # the 1944 summer session
    ("jour_contexte", re.compile(rf"\b(?:on|by|until|from|of)\s+{RM}\s+{RJ}\b(?!,?\s*\d)")),   # on March 5 (année plus haut)
]
LIEUX = [("Lake Eden", r"lake eden"), ("Blue Ridge Assembly (Robert E. Lee Hall)", r"lee hall|blue ridge assembly"),
         ("Studies Building", r"studies building"), ("Dining hall", r"dining hall"), ("Ferme du collège", r"\bthe farm\b"),
         ("Asheville", r"asheville"), ("Black Mountain (ville)", r"town of black mountain")]
COLLEGE = re.compile(r"black mountain|\bbmc\b|\bthe college\b|lake eden|blue ridge|lee hall|studies building|summer (session|institute)|"
                     r"\bfaculty\b|\bstudents?\b|work program|community", re.I)
TYPE_MOTS = [("concert", r"\bconcert|recital|sonata|quartet|orchestra|performed .*music"), ("theatre", r"\bplay\b|theat|drama|stage|ruse of medusa|masque"),
             ("danse", r"\bdanc"), ("conference", r"\blecture|\btalk\b|spoke|seminar|address"), ("expo", r"exhibit|exhibition|show of"),
             ("reunion", r"meeting|board|vote|voted|elected|rector"), ("travail", r"work program|farm|construction|built|building of"),
             ("visite", r"visit|arrived|came to|guest"), ("cours", r"\btaught|\bcourse|\bclass(es)?\b|seminar"),
             ("social", r"party|wedding|married|dinner|picnic|birthday|died|death|funeral")]
VIDES = V.VIDES | {"black", "mountain", "college", "which", "their", "there", "would", "after", "before", "during", "where", "these", "those",
                   "about", "other", "first", "years", "year", "summer", "spring", "winter", "students", "student", "faculty", "january",
                   "february", "march", "april", "june", "july", "august", "september", "october", "november", "december"}
COMMUNS = {"black", "white", "king", "hall", "brown", "wood", "young", "page", "french", "english", "lake", "rose", "bell", "hill", "long", "day",
           "law", "love", "price", "grant", "case", "major", "may", "west", "north", "rice", "mountain", "early", "small", "little", "street",
           "house", "lane", "bird", "moss", "fox", "gray", "green", "park", "ford", "rich", "early", "baker", "cook", "miller", "smith", "jones",
           "johnson", "williams", "taylor", "allen", "lee", "evans", "harris", "silver", "south", "nelson", "walker", "lewis", "moore", "martin"}


def lire(p):
    with open(p, encoding="utf-8") as f: return list(csv.DictReader(f))


def mots_sig(s): return {w for w in re.findall(r"[a-z]{5,}", V.plat(s)) if w not in VIDES}


def borne_saison(s, y):
    a = SAISONS[s.lower()]
    if s.lower() == "winter": return dt.date(y, 1, 1), dt.date(y, 3, 20)
    return dt.date(y, a[0], a[1]), dt.date(y, a[2], a[3])


def index_personnes():
    """noms de la base du BMC Yearbook : formes complètes → nom ; noms de famille propres à un seul enseignant."""
    pres = lire(sorted(glob.glob(os.path.join(ROOT, "chronos", "[0-9][0-9][0-9]_personnes_presences.csv")))[-1])
    complets, fam = {}, collections.defaultdict(set)
    for p in pres:
        n = p["nom"]; base = re.sub(r'"[^"]*"|“[^”]*”', " ", n); w = base.split()
        if len(w) < 2: continue
        complets[V.plat(f"{w[0]} {w[-1]}")] = n
        for nick in re.findall(r'"([^"/]+)', n):
            for x in nick.split("/"): complets[V.plat(f"{x.strip()} {w[-1]}")] = n
        if re.search(r"faculty|staff|admin", p["role"], re.I): fam[V.plat(w[-1])].add(n)
    seuls = {k: list(v)[0] for k, v in fam.items() if len(v) == 1 and k not in COMMUNS and len(k) > 3}
    ambigus = {k: sorted(v) for k, v in fam.items() if len(v) > 1}
    return complets, seuls, ambigus


def personnes_de(phrase, complets, seuls, ambigus):
    pl = V.plat(phrase); trouves, amb = [], []
    for m in re.finditer(r"\b([A-Z][a-zà-ÿ'’\-]+(?:\s+[A-Z]\.)?)\s+([A-Z][a-zà-ÿ'’\-]+)\b", phrase):
        k = V.plat(f"{m.group(1).split()[0]} {m.group(2)}")
        if k in complets and complets[k] not in trouves: trouves.append(complets[k])
    noms_f = {V.plat(n.split()[-1]) for n in trouves}
    for w in set(re.findall(r"\b[A-Z][a-zà-ÿ\-]{3,}\b", phrase)):
        k = V.plat(w)
        if k in noms_f: continue
        if k in seuls and seuls[k] not in trouves: trouves.append(seuls[k])
        elif k in ambigus and k not in COMMUNS: amb.append(f"{w} ({' ou '.join(ambigus[k][:3])})")
    return trouves, amb


def pages_imprimees(P):
    """décalage page du PDF → page imprimée (numéro seul en tête ou en pied de page), le plus fréquent."""
    dec = collections.Counter()
    for n, _, b in P:
        ls = [l.strip() for l in b.split("\n") if l.strip()]
        for l in ls[:2] + ls[-2:]:
            m = re.match(r"^(\d{1,3})\b(?!\.\d)|\b(\d{1,3})$", l)
            if m:
                v = int(m.group(1) or m.group(2))
                if 0 < v <= n: dec[n - v] += 1
    if not dec: return None
    d, c = dec.most_common(1)[0]
    return d if c >= max(5, 0.2 * len(P)) else None


def main():
    complets, seuls, ambigus = index_personnes()
    fichiers = sorted(glob.glob(os.path.join(SRC, "*.txt")))
    inv, textes, faits = [], {}, []
    empreintes = {}
    for f in fichiers:
        nom = os.path.basename(f)
        meta = next((m for m in META if nom.startswith(m[0])), None) or (None, re.sub(r"\W+", "_", nom[:20]).lower(), nom[:-4], "étude")
        _, code, ref, genre = meta
        t = open(f, encoding="utf-8").read(); P = L.pages(t)
        corps = re.sub(r"\s+", " ", "".join(b for _, _, b in P))
        emp = hashlib.sha1(re.sub(r"[^a-z]", "", corps.lower())[:200000].encode()).hexdigest()
        doublon = PREFERE.get(code, "") if code in PREFERE else "" if code in PREFERE.values() else empreintes.get(emp, "")
        if not doublon: empreintes.setdefault(emp, code)
        decal = pages_imprimees(P)
        n2 = 0; pars = []
        for n, ocr, b in P:
            ls, deux = L.lignes_page(b); n2 += deux
            for par in L.paragraphes(ls): pars.append((n, par))
        # paragraphe coupé par un saut de page ou de colonne : recollé au suivant s'il ne finit pas une phrase
        fus = []
        for n, par in pars:
            if fus and not re.search(r"[.!?:\"”’)]\s*$", fus[-1][1]) and re.match(r"[a-z(]", par):
                fus[-1] = (fus[-1][0], fus[-1][1] + " " + par)
            else: fus.append((n, par))
        textes[code] = fus
        inv.append({"code": code, "fichier": nom, "reference": ref, "genre": genre, "pages_pdf": len(P),
                    "pages_ocr": sum(1 for _, o, _ in P if o), "pages_deux_colonnes": n2, "decalage_page_imprimee": "" if decal is None else decal,
                    "mots": len(corps.split()), "doublon_de": doublon})
        if doublon: continue
        pen_g, mot_g = GENRE[genre]
        for n, par in fus:
            ph = L.phrases(par)
            annee_ctx = None
            for i, s in enumerate(ph):
                ys = re.findall(r"\b(19[3-5]\d)\b", s)
                trouve = []
                pris = []
                for prec, rx in MOTIFS:
                    for m in rx.finditer(s):
                        if any(m.start() < b and a < m.end() for a, b in pris): continue
                        try:
                            if prec == "plage":
                                mo, j, j2, y = m.groups(); mo = MOIS[mo.lower().rstrip(".")]
                                d0, d1 = dt.date(int(y), mo, int(j)), dt.date(int(y), mo, int(j2))
                                if d1 <= d0 or (d1 - d0).days > 14: continue
                            elif prec == "jour":
                                g = m.groups(); mo, j, y = (g[0], g[1], g[2]) if not g[0].isdigit() else (g[1], g[0], g[2])
                                d0 = d1 = dt.date(int(y), MOIS[mo.lower().rstrip(".")], int(j))
                            elif prec == "mois":
                                mo, y = m.groups(); d0 = dt.date(int(y), MOIS[mo.lower().rstrip(".")], 1)
                                d1 = (d0.replace(day=28) + dt.timedelta(4)).replace(day=1) - dt.timedelta(1)
                            elif prec == "saison":
                                g = [x for x in m.groups() if x]; y = next(x for x in g if x.isdigit()); sa = next(x for x in g if x.lower() in SAISONS)
                                d0, d1 = borne_saison(sa, int(y))
                            else:
                                apres = re.search(r"^[^.;]{0,25}?\b(19[3-5]\d)\b", s[m.end():])     # « on May 3 and in 1945 » : année qui suit
                                y_ = int(apres.group(1)) if apres else annee_ctx
                                if y_ is None: continue
                                mo, j = m.groups(); d0 = d1 = dt.date(y_, MOIS[mo.lower().rstrip(".")], int(j))
                        except (ValueError, KeyError, StopIteration): continue
                        if not (dt.date(1933, 1, 1) <= d0 <= dt.date(1957, 12, 31)): continue
                        pris.append((m.start(), m.end())); trouve.append((prec, d0, d1, m.group(0), m.start()))
                if ys: annee_ctx = int(ys[-1])
                if not trouve: continue
                if len(re.findall(r",\s*\d{1,3}(?:n\d+)?(?=[,;\s]|$)", s)) >= 4: continue     # entrée d'index (« Summer Art Institute, 54, 170n2 »)
                avant = ph[i - 1] if i else ""
                qui, amb = personnes_de(s, complets, seuls, ambigus)
                if not (qui or COLLEGE.search(s) or COLLEGE.search(avant)): continue
                lieu = next((l for l, rx in LIEUX if re.search(rx, s, re.I)), "")
                # note ou référence (« Letter, Albers to Rice, March 5, 1934 », « Asheville Citizen, 5 January 1940, p. 3 ») :
                # la date est celle du document cité, pas d'un événement raconté
                cite = (bool(re.search(r"\bpp?\.\s*\d|\b(Letter|letter|Carta|carta|Memo|memo|Memorandum|Telegram|Western Union|Correspondence|"
                                       r"correspondence)\b[^.]{0,80}\b(to|from)\b|\b(Folder|Papers|Box \d|Collection|Archives|Interview|interview|"
                                       r"Minutes|minutes|Bulletin|BMCP|BMCProj|WRA|Reference Letter)\b", s))
                        and (bool(re.match(r"^\d{1,3}[.:]?\s", s)) or bool(re.search(r"\bpp?\.\s*\d|Folder|Papers|Box \d|BMCP|WRA", s)) or len(s) < 200)) \
                       or bool(re.match(r"^\d{1,3}[.:]?\s+[A-Z][^.]{0,120}\b(to|interview|Letter|letter|Correspondence|Memorandum|minutes)\b", s))
                typ = "autre" if cite else next((t for t, rx in TYPE_MOTS if re.search(rx, s, re.I)), "autre")
                for prec, d0, d1, brut, pos in trouve:
                    # note qui cite plusieurs documents : le segment de la date seulement (entre deux « ; »)
                    seg = s
                    if cite and ";" in s:
                        a_ = s.rfind(";", 0, pos) + 1; b_ = s.find(";", pos); seg = s[a_: b_ if b_ >= 0 else len(s)].strip()
                    qui_s, amb_s = personnes_de(seg, complets, seuls, ambigus) if seg != s else (qui, amb)
                    pct, mot = pen_g, [f"{mot_g} (+{pen_g})"]
                    pct += 10; mot.append("fait tiré automatiquement de la phrase, non relu (+10)")
                    if prec in ("mois", "saison"): pct += 25; mot.append(f"date « {prec} » seulement (+25)")
                    if prec == "jour_contexte": pct += 15; mot.append("année reprise plus haut dans le paragraphe (+15)")
                    pg = f"p. {n - decal} (PDF p. {n})" if decal is not None and n - decal > 0 else f"PDF p. {n}"
                    if cite: s_ = re.sub(r"^\d{1,3}[.:]?\s+", "", seg)
                    else:       # proposition qui contient la date (le découpage en phrases bute sur les appels de note)
                        bornes = [0] + [m_.end() for m_ in re.finditer(r"[.;!?][\"”’'°\d]*\s+(?=[\"“‘']?[A-Z])", s)] + [len(s)]
                        a_ = max(x for x in bornes if x <= pos); b_ = min(x for x in bornes if x > pos)
                        s_ = s[a_:b_].strip() if b_ - a_ > 40 else s
                    act = ("Document cité : " if cite else "") + (s_ if len(s_) <= 160 else s_[:157].rsplit(" ", 1)[0] + " …")
                    faits.append({"id": f"{code}-{len(faits) + 1}", "code": code, "date": d0.isoformat(), "date_fin": d1.isoformat() if d1 != d0 else "",
                                  "precision": "jour" if prec.startswith("jour") else prec, "date_source": brut, "type": typ,
                                  "nature": "document cité (note, référence)" if cite else "fait raconté",
                                  "activite": act, "qui": "; ".join(qui_s),
                                  "noms_ambigus": "; ".join(amb_s), "lieu": lieu, "phrase": s[:900], "page": pg, "genre": genre,
                                  "document_source": f"{ref}, {pg}", "part_deduite_pct": min(pct, 90), "motifs_deduction": " ; ".join(mot)})
    # ---------------------------------------------------------------- vérification (règle du 2/11/2026)
    # Rien de ces textes n'entre seul dans le semainier. Un fait n'y paraît que s'il est VÉRIFIÉ AU JOUR par une source
    # qui fait foi : document daté de l'AAM, Duberman corrigé daté au jour, Rumaker daté au jour (dépouillement manuel),
    # fiche du musée datée au jour (Chronos Asheville) — même jour, personne commune et mot commun (trois mots sans
    # personne). Il devient alors un renvoi (« aussi dans… ») sur la fiche existante, pas un nouvel événement.
    # Hors semainier : dates au mois ou à la saison, accords au mois seulement, traduction automatique, et tout le reste
    # (« à vérifier », avec ce qu'en disent le scénario et les autres livres, qui ne valent pas preuve).
    aam = lire(os.path.join(ROOT, "programme", "evenements.csv"))
    dub = lire(os.path.join(ROOT, "duberman", "evenements_duberman.csv"))
    f_rum = sorted(glob.glob(os.path.join(ROOT, "rumaker", "[0-9][0-9][0-9]_evenements_rumaker.csv")))[-1]
    rum = lire(f_rum); n_rum = os.path.basename(f_rum)[:3]
    ash = lire(sorted(glob.glob(os.path.join(ROOT, "chronos", "[0-9][0-9][0-9]_asheville_couche.csv")))[-1])
    scen = lire(sorted(glob.glob(os.path.join(ROOT, "scenario", "[0-9][0-9][0-9]_evenements_scenario.csv")))[-1])
    for i, x in enumerate(aam): x["_cle"] = str(i); x["precision"] = "jour"
    for i, x in enumerate(dub): x["_cle"] = f"d{i}"
    for x in rum: x["_cle"] = f"rm{n_rum}-{x['id']}"
    for x in ash: x["_cle"] = x["id"]
    def idx(L_):
        I = collections.defaultdict(list)
        for x in L_:
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", x.get("date") or ""): I[x["date"][:7]].append(x)
        return I
    I_aam, I_dub, I_rum, I_ash, I_sce, I_liv = idx(aam), idx(dub), idx(rum), idx(ash), idx(scen), idx(faits)
    FOI = ((I_aam, "AAM"), (I_dub, "Duberman"), (I_rum, "Rumaker"), (I_ash, "fiche du musée (Asheville)"))
    def prenom_autre(qui_f, qui_x, nom_f):
        """vrai si les deux côtés donnent un prénom différent pour ce nom de famille."""
        pf = {V.plat(q.split()[0]) for q in qui_f.split("; ") if len(q.split()) > 1 and V.plat(q.split()[-1]) == nom_f}
        px = {V.plat(q.split()[0]) for q in qui_x if len(q.split()) > 1 and V.plat(q.split()[-1]) == nom_f}
        return bool(pf and px and not ({a[:1] for a in pf} & {b[:1] for b in px}))
    def recoupe(f, I, au_jour=True, meme_source=None, decalage=0):
        """au_jour : même jour exact des deux côtés (dates au jour), personne commune et un mot commun (trois sans
        personne) ; sinon accord dans la période (mois, saison) : personne commune et deux mots communs."""
        d0 = dt.date.fromisoformat(f["date"]) + dt.timedelta(decalage)
        d1 = (dt.date.fromisoformat(f["date_fin"]) if f["date_fin"] else dt.date.fromisoformat(f["date"])) + dt.timedelta(decalage)
        ns = K.noms_famille(f["qui"].split("; ")); mq = mots_sig(f["phrase"])
        best = None
        mois = {(d0 + dt.timedelta(k)).isoformat()[:7] for k in range(0, (d1 - d0).days + 1, 10)} | {d1.isoformat()[:7]}
        for x in (y for m_ in mois for y in I.get(m_, [])):
            if meme_source and x.get("code") == meme_source: continue
            # au jour : la fiche de base doit être datée au jour même (pas une plage, pas un mois)
            if au_jour and (x.get("precision") or "jour") not in ("jour", "soir", "matin", "apres-midi", "nuit"): continue
            xq = [q.strip() for q in (x.get("qui") or "").replace("; ", ";").split(";") if q.strip()]
            xn = K.noms_famille(xq)
            if ns and not (ns & xn): continue
            # même nom de famille mais autre prénom des deux côtés (Anne / Frederick Mangold) : pas la même personne
            if au_jour and ns and all(prenom_autre(f["qui"], xq, n_) for n_ in ns & xn): continue
            # document cité (lettre, procès-verbal) : toutes ses personnes nommées doivent être dans la fiche de base
            if au_jour and f["nature"].startswith("document") and ns - xn: continue
            com = mq & mots_sig((x.get("activite") or "") + " " + (x.get("note") or "") + " " + (x.get("phrase") or ""))
            xd0 = dt.date.fromisoformat(x["date"]); xd1 = dt.date.fromisoformat(x.get("date_fin") or x["date"])
            if au_jour and (xd1 - xd0).days > 14: continue
            if not (xd0 <= d1 and d0 <= xd1): continue
            besoin = (1 if ns else 3) if au_jour else (2 if ns else 99)
            if len(com) >= besoin and (best is None or len(com) > best[0]): best = (len(com), x)
        return best[1] if best else None
    jour = lambda f: f["precision"] in ("jour", "plage")
    # relecture manuelle des renvois (livres/revue_renvois.txt : « id_fait|clé de la fiche|ok ou faux|motif ») :
    # un renvoi jugé faux n'est pas posé
    revue = {}
    p_rev = os.path.join(ICI, "revue_renvois.txt")
    if os.path.exists(p_rev):
        for l in open(p_rev, encoding="utf-8"):
            if l.strip() and not l.startswith("#"):
                i_, c_, d_, m_ = (l.rstrip("\n").split("|") + ["", "", "", ""])[:4]; revue[(i_.strip(), c_.strip())] = (d_.strip(), m_.strip())
    # témoin négatif : mêmes faits décalés de 400 jours
    temoin = sum(1 for f in faits if jour(f) and any(recoupe(f, I, True, None, 400) for I, _ in FOI))
    renvois = []
    for f in faits:
        verif = [(n_, x) for I, n_ in FOI if jour(f) and (x := recoupe(f, I, True))]
        rejet = [(n_, x) for n_, x in verif if revue.get((f["id"], x["_cle"]), ("", ""))[0] == "faux"]
        verif = [v for v in verif if v not in rejet]
        f["renvoi_rejete"] = " ; ".join(f"{n_} {x['date']} « {(x.get('activite') or '')[:60]} » : {revue[(f['id'], x['_cle'])][1]}" for n_, x in rejet)
        mois_ = [(n_, x) for I, n_ in FOI if not verif and (x := recoupe(f, I, False))]
        sc = recoupe(f, I_sce, jour(f)); lv = recoupe(f, I_liv, jour(f), f["code"])
        f["verifie_par"] = " ; ".join(f"{n_} {x['date']} « {(x.get('activite') or '')[:80]} »" for n_, x in verif)
        f["accord_au_mois"] = " ; ".join(f"{n_} {x['date']} « {(x.get('activite') or '')[:70]} »" for n_, x in mois_)
        f["scenario"] = f"{sc['id']} {sc['date']} « {sc['activite'][:70]} » ({sc['document_source'][:60]})" if sc else ""
        f["autre_livre"] = f"{lv['code']} {lv['page']} « {lv['activite'][:70]} »" if lv else ""
        if verif and f["genre"] == "traduction automatique":
            f["statut"] = "vérifié au jour, mais texte en traduction automatique : hors semainier"
        elif verif:
            f["statut"] = "vérifié au jour (" + ", ".join(n_ for n_, _ in verif) + ") : renvoi sur la fiche existante"
            for n_, x in verif:
                renvois.append({"revue": revue.get((f["id"], x["_cle"]), ("non relu", ""))[0], "cle": x["_cle"], "base": n_, "date_fiche": x["date"], "fiche": (x.get("activite") or "")[:120],
                                "code": f["code"], "reference": f["document_source"], "date_livre": f["date_source"], "nature": f["nature"],
                                "phrase": f["phrase"], "id_fait": f["id"]})
        elif mois_:
            f["statut"] = "accord au mois seulement (jour non vérifié) : hors semainier"
        else:
            f["statut"] = "à vérifier : hors semainier"
    # ---------------------------------------------------------------- sorties
    num = K.prochain_numero(ICI)
    for suff, rows in (("_inventaire", inv), ("_evenements_livres", faits), ("_renvois_semainier", renvois)):
        if not rows: continue
        with open(os.path.join(ICI, f"{num}{suff}.csv"), "w", encoding="utf-8", newline="") as fo:
            w = csv.DictWriter(fo, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    # la couche « livres » du semainier ne garde aucune entrée propre (remplace chronos/010_livres_couche.csv)
    nc = K.prochain_numero(K.SORTIE)
    with open(os.path.join(K.SORTIE, f"{nc}_livres_couche.csv"), "w", encoding="utf-8", newline="") as fo:
        fo.write("id,source_chronos,date,date_fin,precision,type,activite,qui,lieu,note,part_deduite_pct,motifs_deduction,document_source,"
                 "inventaire,url_source,statut,verif_statut,verif_extrait,date_source\n")
    # liste à vérifier : faits au jour, hors semainier, qui nomment une personne (les plus utiles à relire)
    av = sorted((f for f in faits if f["statut"].startswith(("à vérifier", "accord au mois")) and jour(f) and f["qui"]
                 and f["genre"] != "traduction automatique"), key=lambda f: f["date"])
    A = [f"# Livres et articles : faits datés au jour à vérifier ({num})", "",
         "Hors semainier. Chaque ligne : date lue, texte et page, personnes, phrase ; puis ce qu'en disent l'AAM ou Duberman au "
         "mois, le scénario et les autres livres (indices, pas preuves : le scénario vient en partie des mêmes livres).", ""]
    for f in av:
        A.append(f"- **{f['date']}** ({f['date_source']}) · {f['code']} {f['page']} · {f['qui']} · {f['nature']}  \n  « {f['phrase'][:400]} »"
                 + "".join(f"  \n  ↳ {k} : {f[c]}" for k, c in (("au mois", "accord_au_mois"), ("scénario", "scenario"), ("autre livre", "autre_livre")) if f[c]))
    open(os.path.join(ICI, f"{num}_a_verifier.md"), "w", encoding="utf-8").write("\n".join(A) + "\n")
    N = collections.Counter
    R = [f"# Livres et articles (textes des PDF) : dépouillement automatique ({num})", "",
         f"{len(inv)} textes dans `DATA_BMC/textes_pdf` ; {sum(1 for x in inv if x['doublon_de'])} doublons écartés "
         f"({', '.join(x['code'] + ' = ' + x['doublon_de'] for x in inv if x['doublon_de'])}).", "",
         "| texte | genre | pages | 2 col. | page imprimée | mots | faits datés |", "|---|---|---|---|---|---|---|"]
    nf = N(f["code"] for f in faits)
    R += [f"| {x['code']} | {x['genre']} | {x['pages_pdf']} | {x['pages_deux_colonnes']} | {'décalage ' + str(x['decalage_page_imprimee']) if x['decalage_page_imprimee'] != '' else 'PDF'} | {x['mots']} | {nf.get(x['code'], 0) if not x['doublon_de'] else 'doublon'} |" for x in inv]
    R += ["", f"## {len(faits)} faits datés de 1933 à 1957", "",
          "- Précision : " + ", ".join(f"{k} {v}" for k, v in N(f["precision"] for f in faits).most_common()) + ".",
          "- Statut : " + "; ".join(f"{k} {v}" for k, v in N(f["statut"] for f in faits).most_common()) + ".",
          f"- Renvois posés sur des fiches existantes du semainier : {len(renvois)} (`livres/{num}_renvois_semainier.csv`) ; "
          f"aucune entrée nouvelle (`chronos/{nc}_livres_couche.csv` est vide). À vérifier : `livres/{num}_a_verifier.md` ({len(av)} faits au jour nommant une personne).",
          "- Nature : " + ", ".join(f"{k} {v}" for k, v in N(f["nature"] for f in faits).most_common()) + ".",
          f"- Témoin négatif (faits au jour décalés de 400 jours) : {temoin} vérifications fausses sur {sum(1 for f in faits if jour(f))} faits au jour, "
          f"contre {sum(1 for f in faits if f['verifie_par'])} à la bonne date.",
          f"- Avec au moins une personne de la base : {sum(1 for f in faits if f['qui'])} .",
          f"- Part déduite moyenne : {sum(f['part_deduite_pct'] for f in faits) / max(1, len(faits)):.1f} %.",
          ""] + ["## Faits vérifiés au jour (renvois)", ""] + [f"- {f['date']} {f['code']} {f['page']} « {f['activite'][:100]} » — {f['verifie_par'][:160]}" for f in faits if f["verifie_par"]] + ["", 
          ]
    open(os.path.join(ICI, f"{num}_rapport_livres.md"), "w", encoding="utf-8").write("\n".join(R) + "\n")
    print("\n".join(R[:48]))


if __name__ == "__main__":
    main()
