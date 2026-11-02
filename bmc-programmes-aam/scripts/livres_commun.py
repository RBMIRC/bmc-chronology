"""Lecture des textes tirés des PDF (DATA_BMC/textes_pdf, scripts/pdf_vers_texte.py) : pages, colonnes, paragraphes.

pdftotext -layout garde la position des caractères : une page en deux colonnes donne des lignes où la colonne de gauche
et celle de droite se suivent (« …an enlightening series of 1938 he suffered a stroke… »). Pour chaque page, on cherche
la position de la gouttière : un rang de caractère où presque toutes les lignes longues ont une espace juste avant, et où
beaucoup de lignes commencent un mot (début de la colonne de droite) ; s'il y en a une, chaque ligne est coupée là et la
page se lit colonne de gauche puis colonne de droite. Les coupures de mots en fin de ligne (« re-\\nturned ») sont recollées.
"""
import re

MARQUE = re.compile(r"^--- Page (\d+)( \(OCR\))? ---\s*$", re.M)


def pages(texte):
    """[(numéro de page du PDF, ocr?, texte brut)]"""
    ms = list(MARQUE.finditer(texte))
    return [(int(m.group(1)), bool(m.group(2)), texte[m.end(): ms[i + 1].start() if i + 1 < len(ms) else len(texte)])
            for i, m in enumerate(ms)]


def gouttiere(lignes):
    """rang de début de la colonne de droite, ou None (page à une colonne) : bande verticale d'au moins deux caractères
    où 93 % des lignes qui la dépassent ont une espace (les retraits des notes ne gênent pas), la plus proche du milieu."""
    longues = [l.rstrip() for l in lignes if len(l.rstrip()) > 40]
    if len(longues) < 8: return None
    w = max(len(l) for l in longues)
    ok = []
    for q in range(int(0.2 * w), int(0.8 * w)):
        ls = [l for l in longues if len(l) > q + 3]
        if len(ls) < max(6, 0.3 * len(longues)): ok.append(False); continue
        ok.append(sum(1 for l in ls if l[q] == " ") / len(ls) >= 0.93)
    runs, i = [], 0
    while i < len(ok):
        if ok[i]:
            j = i
            while j + 1 < len(ok) and ok[j + 1]: j += 1
            if j - i + 1 >= 2: runs.append((int(0.2 * w) + i, int(0.2 * w) + j))
            i = j + 1
        else: i += 1
    if not runs: return None
    # une gouttière doit séparer du texte des deux côtés sur beaucoup de lignes
    def separe(a, b):
        n = sum(1 for l in longues if l[:a].strip() and len(l) > b + 1 and l[b + 1:].strip())
        return n >= 8 and n >= 0.25 * len(longues)
    runs = [r for r in runs if separe(*r)]
    if not runs: return None
    a, b = min(runs, key=lambda r: abs((r[0] + r[1]) / 2 - w / 2))
    return b + 1


def colonnes(ls, prof=0):
    """coupe récursivement aux gouttières : 2 colonnes, ou 3-4 (pages de notes) ; renvoie la liste des colonnes."""
    p = gouttiere(ls) if prof < 3 else None
    if p is None: return [ls]
    g, d = [], []
    for l in ls:
        if len(l) <= p: g.append(l); d.append(""); continue
        k = p
        if l[p - 1] != " ":            # mot à cheval : coupe à l'espace précédente
            k = l.rfind(" ", 0, p)
            if k < 0: g.append(l); d.append(""); continue
        g.append(l[:k]); d.append(l[k:])
    return colonnes(g, prof + 1) + colonnes(d, prof + 1)


def lignes_page(brut):
    ls = brut.split("\n")
    cs = colonnes(ls)
    if len(cs) == 1: return [l.strip() for l in ls], False
    out = []
    for c in cs: out += [l.strip() for l in c] + [""]
    return out, len(cs)


def paragraphes(lignes):
    """lignes → paragraphes (ligne vide = fin de paragraphe), coupures de mots recollées, espaces réduites."""
    out, cur = [], []
    for l in lignes + [""]:
        l = re.sub(r"\s{2,}", " ", l).strip()
        if not l:
            if cur: out.append(" ".join(cur)); cur = []
            continue
        if cur and re.search(r"[a-z]-$", cur[-1]) and re.match(r"[a-z]", l):
            cur[-1] = cur[-1][:-1] + l
        else: cur.append(l)
    return [re.sub(r"\s+", " ", p).strip() for p in out if p.strip()]


def phrases(par):
    """découpe simple en phrases (pas après une initiale, Mr., Dr., St., etc.)."""
    par = re.sub(r"\b(Mr|Mrs|Ms|Dr|St|Prof|Jr|Sr|Co|Inc|Vol|No|ca|cf|vs|ed|eds|pp|p)\.", lambda m: m.group(1) + "§", par)
    par = re.sub(r"\b([A-Z])\.", r"\1§", par)
    out = re.split(r"(?:(?<=[.!?])|(?<=[.!?][\"”’']))\s+(?=[\"“‘']?[A-Z0-9])", par)
    return [x.replace("§", ".").strip() for x in out if x.strip()]
