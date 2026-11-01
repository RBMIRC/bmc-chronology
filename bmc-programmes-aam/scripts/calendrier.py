"""Calendrier attesté (programme/calendrier_periodes.csv) → jours de cours, de vacances, de Work Camp, et trimestre
de chaque jour de cours. Partagé par audit_semaines.py et speculer.py.
Règles :
- une période « prévue / planned / announced » est ignorée quand une période effective de même clé (année + saison) existe ;
- « … quarter ends (winter holidays from 12:30) » reste une période d'enseignement ; interlude = sans cours ;
- un trou de 6 semaines au plus entre deux périodes d'enseignement = vacances implicites ;
- le jour où une période d'enseignement commence est un jour de cours, même s'il clôt des vacances."""
import csv, os, re, datetime as dt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENS = re.compile(r"term|semester|quarter|session|institute|seminar|summer school", re.I)
VAC = re.compile(r"vacation|holiday|recess|interlude|week without classes|closes", re.I)
PREVU = re.compile(r"prévu|planned|announced|annonc|tentative|décidé|official", re.I)
PRINCIPAL = re.compile(r"term|semester|quarter", re.I)

def cle(lib):
    a = re.search(r"(19\d\d-\d\d|19\d\d)", lib); s = re.search(r"fall|winter|spring|summer|first|second|christmas", lib, re.I)
    return (a.group(1) if a else "", s.group(0).lower() if s else "")

def saison(lib):
    l = lib.lower()
    for s, motifs in (("fall", ("fall", "first semester")), ("winter", ("winter",)), ("spring", ("spring", "second semester")),
                      ("summer", ("summer", "institute", "work camp", "seminar on america", "american seminar"))):
        if any(m in l for m in motifs): return s
    return ""

def annee_scolaire(x):
    a = x.year if x.month >= 9 else x.year - 1
    return f"{a}-{str(a + 1)[2:]}"

SPEC = os.path.join(ROOT, "speculation", "calendrier_speculatif.csv")

def periodes_speculatives():
    if not os.path.exists(SPEC): return []
    with open(SPEC, encoding="utf-8") as f: return list(csv.DictReader(f))

def charger(path=None, spec=False):
    """spec=True : ajoute speculation/calendrier_speculatif.csv, seulement pour les années scolaires
    sans aucune période d'enseignement attestée."""
    path = path or os.path.join(ROOT, "programme", "calendrier_periodes.csv")
    with open(path, encoding="utf-8") as f:
        per = [p for p in csv.DictReader(f) if p["debut"] and p["fin"]]
    jours_spec = set()
    if spec:
        attestees = {annee_scolaire(dt.date.fromisoformat(p["debut"])) for p in per if ENS.search(p["libelle"]) and not VAC.search(p["libelle"])}
        for p in periodes_speculatives():
            if annee_scolaire(dt.date.fromisoformat(p["debut"])) in attestees: continue
            per.append(p)
            a, b = dt.date.fromisoformat(p["debut"]), dt.date.fromisoformat(p["fin"])
            jours_spec |= {a + dt.timedelta(i) for i in range((b - a).days + 1)}
    eff = {cle(p["libelle"]) for p in per if not PREVU.search(p["libelle"] + " " + p["note"])}
    garde = [p for p in per if not (PREVU.search(p["libelle"] + " " + p["note"]) and cle(p["libelle"]) in eff and cle(p["libelle"])[1])]
    ens, vac, camp, terme = set(), set(), set(), {}
    for p in garde:
        a, b = dt.date.fromisoformat(p["debut"]), dt.date.fromisoformat(p["fin"])
        jours = {a + dt.timedelta(i) for i in range((b - a).days + 1)}
        lib = p["libelle"]
        est_vac = (VAC.search(lib) and not re.search(r"quarter|semester|\bterm\b|session", lib, re.I)) or \
                  re.search(r"interlude|week without classes", lib, re.I)
        if est_vac: vac |= jours
        elif re.search(r"work camp", lib, re.I): camp |= jours
        elif ENS.search(lib):
            ens |= jours
            prio = 0 if PRINCIPAL.search(lib) else 1
            for x in jours:
                if x not in terme or prio < terme[x][0]:
                    terme[x] = (prio, saison(lib), lib)
    tri = sorted(ens); implicite = set()
    for x, y in zip(tri, tri[1:]):
        if 1 < (y - x).days <= 42:
            implicite |= {x + dt.timedelta(i) for i in range(1, (y - x).days)}
    vac |= implicite - ens
    vac -= {dt.date.fromisoformat(p["debut"]) for p in garde if ENS.search(p["libelle"]) and not re.search(r"interlude", p["libelle"], re.I)}
    return {"ens": ens, "vac": vac, "camp": camp, "terme": {x: (s, lib) for x, (_, s, lib) in terme.items()}, "spec": jours_spec}

def jour_de_cours(cal, x):
    return x in cal["ens"] and x not in cal["vac"]
