"""Audit semaine par semaine du programme (sept. 1933 → 1957) et contrôles de cohérence.
Écrit programme/audit/semaines.csv, programme/audit/controles.csv et programme/audit/AUDIT.md.

Statut d'une semaine (lundi → dimanche), d'après programme/calendrier_periodes.csv :
  cours       : au moins 3 jours ouvrables dans une période d'enseignement (trimestre, semestre, session, institut),
                hors vacances / interlude ;
  vacances    : sinon, au moins 3 jours ouvrables en vacances, interlude ou entre deux périodes connues de la même année ;
  work camp   : seulement un Work Camp ;
  inconnu     : aucune période attestée ne couvre la semaine.
Une période « prévue / planned / announced » est ignorée quand une période effective de même clé (année + saison) existe.

Niveau de remplissage d'une semaine de cours (activités attestées seulement, couche spéculative à part) :
  complète  : des séances de cours sur au moins 5 jours ouvrables et au moins 15 séances ;
  partielle : au moins 10 activités ou des cours sur au moins 2 jours ;
  maigre    : 1 à 9 activités ;
  vide      : aucune activité."""
import csv, os, re, sys, datetime as dt, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calendrier
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROG = os.path.join(ROOT, "programme"); OUT = os.path.join(PROG, "audit")
D0, D1 = dt.date(1933, 9, 18), dt.date(1957, 9, 30)
ENS = re.compile(r"term|semester|quarter|session|institute|seminar|summer school", re.I)
VAC = re.compile(r"vacation|holiday|recess|interlude|week without classes|closes", re.I)
PREVU = re.compile(r"prévu|planned|announced|annonc|tentative|décidé|official", re.I)
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

def lire(p):
    with open(p, encoding="utf-8") as f: return list(csv.DictReader(f))

def cle(lib):
    a = re.search(r"(19\d\d-\d\d|19\d\d)", lib); s = re.search(r"fall|winter|spring|summer|first|second|christmas", lib, re.I)
    return (a.group(1) if a else "", s.group(0).lower() if s else "")

def d(s): return dt.date.fromisoformat(s)

def main():
    cal = calendrier.charger()
    ens, vac, camp = cal["ens"], cal["vac"], cal["camp"]

    evs = lire(os.path.join(PROG, "evenements.csv"))
    pspec_sem = collections.Counter()   # lundi -> nombre de jours reconstitués (couche spéculative)
    ds = os.path.join(PROG, "speculatif")
    for fn in sorted(os.listdir(ds)) if os.path.isdir(ds) else []:
        if re.fullmatch(r"annee_\d{4}-\d\d_semaines\.csv", fn):
            for x in lire(os.path.join(ds, fn)): pspec_sem[x["lundi"]] += len(x["jours"].split())
    par = collections.defaultdict(list)
    for e in evs: par[e["date"]].append(e)


    rows = []
    lun = D0 - dt.timedelta(D0.weekday())
    while lun <= D1:
        ouvr = [lun + dt.timedelta(i) for i in range(6)]
        n_ens = sum(1 for x in ouvr if x in ens and x not in vac)
        n_vac = sum(1 for x in ouvr if x in vac)
        n_camp = sum(1 for x in ouvr if x in camp)
        statut = "cours" if n_ens >= 3 else "vacances" if n_vac >= 3 else "work camp" if n_camp >= 3 else \
                 ("cours" if n_ens else "inconnu")
        semaine = [lun + dt.timedelta(i) for i in range(7)]
        es = [e for x in semaine for e in par.get(x.isoformat(), [])]
        cours = [e for e in es if e["type"] in ("cours", "atelier")]
        jc = {e["date"] for e in cours if d(e["date"]).weekday() < 6}
        srcs = {e["inventaire"] for e in es}
        rec = sum(1 for e in es if e["recurrent_deduit"] == "oui")
        moy = round(sum(int(e["part_deduite_pct"]) for e in es) / len(es)) if es else ""
        if not es: niveau = "vide"
        elif len(jc) >= 5 and len(cours) >= 15: niveau = "complète"
        elif len(es) >= 10 or len(jc) >= 2: niveau = "partielle"
        else: niveau = "maigre"
        nsp = pspec_sem.get(lun.isoformat(), 0)
        an = lun.year if lun.month >= 9 else lun.year - 1
        rows.append({"lundi": lun.isoformat(), "annee_scolaire": f"{an}-{str(an + 1)[2:]}", "statut": statut,
                     "jours_cours_calendrier": n_ens, "activites": len(es), "seances_cours": len(cours),
                     "jours_avec_cours": len(jc), "issues_de_recurrences": rec, "documents": len(srcs),
                     "deduction_moyenne": moy, "niveau": niveau, "speculatif": nsp,
                     "sources": " ; ".join(sorted(srcs))[:300]})
        lun += dt.timedelta(7)

    # ---- contrôles de cohérence
    C = []
    def ctl(gravite, quoi, e, detail=""):
        C.append({"gravite": gravite, "controle": quoi, "date": e.get("date", ""), "debut": e.get("debut", ""),
                  "activite": e.get("activite", e.get("libelle", ""))[:90], "inventaire": e.get("inventaire", ""), "detail": detail})
    vus = collections.Counter()
    for e in evs:
        x = d(e["date"])
        if JOURS[x.weekday()] != e["jour"]: ctl("erreur", "jour ≠ date", e, f"jour écrit {e['jour']}, date = {JOURS[x.weekday()]}")
        if not (D0 <= x <= D1): ctl("erreur", "date hors de l'existence du collège", e)
        if re.fullmatch(r"\d\d:\d\d", e["debut"]) and re.fullmatch(r"\d\d:\d\d", e["fin"]) and e["fin"] <= e["debut"]:
            ctl("erreur", "fin avant début", e, f"{e['debut']}–{e['fin']}")
        attendu = re.search(r"interlude|vacation|during|holiday|weekly class|visit", e["activite"] + " " + e["note"], re.I)
        if e["type"] in ("cours", "atelier") and x in vac and attendu:
            ctl("info", "cours pendant des vacances, signalé tel quel par la source", e)
        elif e["recurrent_deduit"] == "oui" and x in vac and e["type"] in ("cours", "atelier"):
            ctl("erreur", "cours récurrent projeté pendant des vacances", e)
        elif e["type"] in ("cours", "atelier") and x in vac:
            ctl("à vérifier", "cours daté pendant des vacances", e)
        if e["type"] in ("cours", "atelier") and x not in ens and x not in vac and x not in camp:
            ctl("à vérifier", "cours hors de toute période attestée", e)
        if e["type"] in ("cours", "atelier") and not e["qui"].strip():
            ctl("info", "cours sans enseignant nommé", e)
        k = (e["date"], e["debut"], e["activite"].lower()[:60])
        vus[k] += 1
        if vus[k] == 2: ctl("erreur", "doublon exact", e)
    # double réservation d'une même personne (activités attestées à heures précises)
    def mn(h): return int(h[:2]) * 60 + int(h[3:])
    occ = collections.defaultdict(list)
    for e in evs:
        if not (re.fullmatch(r"\d\d:\d\d", e["debut"]) and re.fullmatch(r"\d\d:\d\d", e["fin"])): continue
        for q in [re.sub(r"\(.*?\)", "", q).strip() for q in e["qui"].split(";")]:
            if not q or re.search(r"faculty|students|community|everyone|board|committee|chorus|group|class", q, re.I): continue
            for f in occ[(q, e["date"])]:
                if mn(e["debut"]) < mn(f["fin"]) and mn(f["debut"]) < mn(e["fin"]) and f["activite"] != e["activite"]:
                    ctl("à vérifier", "même personne à deux endroits", e, f"{q} : aussi « {f['activite'][:50]} » {f['debut']}–{f['fin']}")
            occ[(q, e["date"])].append(e)
    for p in lire(os.path.join(PROG, "calendrier_periodes.csv")):
        if p["debut"] and p["fin"] and p["fin"] < p["debut"]: ctl("erreur", "période : fin avant début", p)
    inv = {p["accession"] for p in lire(os.path.join(ROOT, "liste_pages.csv"))}
    for e in evs:
        for i in e["inventaire"].split(" ; "):
            if i not in inv: ctl("erreur", "inventaire inconnu de liste_pages.csv", e, i)

    os.makedirs(OUT, exist_ok=True)
    for nom, data in (("semaines", rows), ("controles", C)):
        with open(os.path.join(OUT, nom + ".csv"), "w", encoding="utf-8", newline="") as f:
            if data:
                w = csv.DictWriter(f, fieldnames=list(data[0].keys())); w.writeheader(); w.writerows(data)

    # ---- rapport
    L = ["# Audit du programme semaine par semaine", "", f"Généré par `scripts/audit_semaines.py` le {dt.date.today().isoformat()}.", ""]
    st = collections.Counter(r["statut"] for r in rows)
    cours = [r for r in rows if r["statut"] == "cours"]
    nv = collections.Counter(r["niveau"] for r in cours)
    L += [f"{len(rows)} semaines du {rows[0]['lundi']} au {rows[-1]['lundi']} : " + ", ".join(f"{k} {v}" for k, v in st.most_common()) + ".", "",
          f"Semaines de cours ({len(cours)}) : " + ", ".join(f"{k} {nv.get(k, 0)}" for k in ("complète", "partielle", "maigre", "vide")) +
          f" ; " + f"{sum(1 for r in cours if r['speculatif'])} semaines de cours ont une couche spéculative, {sum(1 for r in cours if r['niveau'] != 'complète' and not r['speculatif'])} restent sans programme complet ni reconstitution.", "",
          "## Par année scolaire", "", "| année | semaines de cours | complètes | partielles | maigres | vides | inconnues (calendrier) | activités |", "|---|---|---|---|---|---|---|---|"]
    for an in sorted({r["annee_scolaire"] for r in rows}):
        rs = [r for r in rows if r["annee_scolaire"] == an]; cs = [r for r in rs if r["statut"] == "cours"]
        n = collections.Counter(r["niveau"] for r in cs)
        L.append(f"| {an} | {len(cs)} | {n['complète']} | {n['partielle']} | {n['maigre']} | {n['vide']} | "
                 f"{sum(1 for r in rs if r['statut'] == 'inconnu')} | {sum(r['activites'] for r in rs)} |")
    cc = collections.Counter((c["gravite"], c["controle"]) for c in C)
    L += ["", "## Contrôles de cohérence", "", "| gravité | contrôle | nombre |", "|---|---|---|"]
    L += [f"| {g} | {q} | {n} |" for (g, q), n in sorted(cc.items())]
    L += ["", "Détail : `programme/audit/controles.csv`. Semaine par semaine : `programme/audit/semaines.csv`.", ""]
    open(os.path.join(OUT, "AUDIT.md"), "w", encoding="utf-8").write("\n".join(L))
    print("\n".join(L[4:8]))
    for (g, q), n in sorted(cc.items()): print(f"  {g:10} {q} : {n}")

if __name__ == "__main__":
    main()
