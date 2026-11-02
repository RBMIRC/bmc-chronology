"""Outils communs aux sources du dossier DATA_BMC/Chronos (extractions automatiques de décembre 2025).

Les fichiers Chronos sont produits par un modèle de langage (GPT-4o pour la ferme) : dates en anglais libre
(« July 6, 1949 », « Summer 1945 », « March 1949 », « 1949-50 »), précision déclarée peu fiable. Ce module les ramène
au format du projet : (début ISO, fin ISO, précision) — précision recalculée d'après la date elle-même.
"""
import calendar, datetime as dt, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))          # bmc-programmes-aam/
DEPOT = os.path.dirname(ROOT)
CHRONOS = os.path.join(DEPOT, "DATA_BMC", "Chronos")
SORTIE = os.path.join(ROOT, "chronos")
MOIS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august", "september",
                                    "october", "november", "december"], 1)}
MOIS.update({m[:3]: i for m, i in list(MOIS.items())}); MOIS["sept"] = 9
SAISONS = {"spring": (3, 1, 5, 31), "summer": (6, 1, 8, 31), "fall": (9, 1, 11, 30), "autumn": (9, 1, 11, 30),
           "winter": (12, 1, 2, 28)}
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


def fin_mois(y, m): return dt.date(y, m, calendar.monthrange(y, m)[1])


def lire_date(s):
    """« July 6, 1949 » → ('1949-07-06', '1949-07-06', 'jour') ; None si illisible."""
    s0 = (s or "").strip()
    s = re.sub(r"(\d)(st|nd|rd|th)\b", r"\1", s0.lower()).replace(",", " ").replace(".", " ")
    s = re.sub(r"\b(circa|ca|c|about|around|approximately|early|late|mid|probably|possibly)\b", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    approx = bool(re.search(r"\b(circa|ca\.?|c\.|about|around|approximately|early|late|mid|probably|possibly|\?)", s0.lower()))
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        try: d = dt.date(*map(int, m.groups())); return d.isoformat(), d.isoformat(), "jour", approx
        except ValueError: return None
    m = re.fullmatch(r"(\d{4})-(\d{2})", s)
    if m and 1 <= int(m.group(2)) <= 12:
        y, mo = int(m.group(1)), int(m.group(2)); return f"{y}-{mo:02d}-01", fin_mois(y, mo).isoformat(), "mois", approx
    m = re.fullmatch(r"([a-z]+) (\d{1,2}) (\d{4})", s) or re.fullmatch(r"(\d{1,2}) ([a-z]+) (\d{4})", s)
    if m:
        a, b, y = m.groups()
        mo, j = (MOIS.get(a), b) if a.isalpha() else (MOIS.get(b), a)
        if mo:
            try: d = dt.date(int(y), mo, int(j)); return d.isoformat(), d.isoformat(), "jour", approx
            except ValueError: return None
    m = re.fullmatch(r"([a-z]+) (\d{1,2})[-–](\d{1,2}) (\d{4})", s)
    if m and MOIS.get(m.group(1)):
        mo, y = MOIS[m.group(1)], int(m.group(4))
        try: return dt.date(y, mo, int(m.group(2))).isoformat(), dt.date(y, mo, int(m.group(3))).isoformat(), "plage", approx
        except ValueError: return None
    m = re.fullmatch(r"([a-z]+) (\d{4})", s)
    if m and MOIS.get(m.group(1)):
        y, mo = int(m.group(2)), MOIS[m.group(1)]; return f"{y}-{mo:02d}-01", fin_mois(y, mo).isoformat(), "mois", approx
    if m and m.group(1) in SAISONS:
        y = int(m.group(2)); m1, d1, m2, d2 = SAISONS[m.group(1)]
        if m.group(1) == "winter": return f"{y - 1}-12-01", fin_mois(y, 2).isoformat(), "saison", approx
        return f"{y}-{m1:02d}-{d1:02d}", f"{y}-{m2:02d}-{d2:02d}", "saison", approx
    m = re.fullmatch(r"(\d{4}) ?[-–/] ?(\d{2}|\d{4})", s)
    if m:
        y1 = int(m.group(1)); y2 = int(m.group(2)) if len(m.group(2)) == 4 else (y1 // 100) * 100 + int(m.group(2))
        if y2 == y1 + 1: return f"{y1}-09-01", f"{y2}-06-30", "annee_scolaire", approx
        if y2 > y1: return f"{y1}-01-01", f"{y2}-12-31", "plage_annees", approx
    m = re.fullmatch(r"(\d{4})s?", s)
    if m:
        y = int(m.group(1))
        if s.endswith("s"): return f"{y}-01-01", f"{y + 9}-12-31", "decennie", approx
        return f"{y}-01-01", f"{y}-12-31", "annee", approx
    return None


def plat(s):
    import unicodedata
    return "".join((unicodedata.normalize("NFKD", c)[:1] or c).lower() for c in (s or ""))


def noms_famille(personnes):
    out = set()
    for p in personnes or []:
        p = re.sub(r"\(.*?\)", "", str(p)).strip()
        if not p or not p[:1].isupper(): continue
        w = re.split(r"\s+", p)[-1].strip(".’'")
        if len(w) > 2: out.add(plat(w))
    return out


def prochain_numero(dossier, motif=r"(\d{3})_"):
    os.makedirs(dossier, exist_ok=True)
    pris = [int(m.group(1)) for fn in os.listdir(dossier) if (m := re.match(motif, fn))]
    return f"{max(pris, default=0) + 1:03d}"
