"""Chronos 5/5 : BlackMountainPeople.txt — base de 1 299 personnes (nom, biographie, relations, cours suivis, domaine,
rôle, années). Provenance non indiquée dans le dossier Chronos (le style des notices est celui d'une base de personnes
de BMC ; à confirmer).

1. Présences : les années de la base sont confrontées aux activités attestées de la personne (AAM, Duberman au jour),
   reconnues par nom de famille ET prénom (ou surnom, ou initiale) pour éviter les homonymes :
     concordant ......... activités attestées toutes dans les années de la base (± 1 an)
     débordement ........ activités attestées hors de ces années : l'une des deux sources est à revoir
     non attesté ........ aucune activité nommée (cas de la plupart des étudiants)
     années incohérentes  fin avant début dans la base
2. Cours suivis (355 fiches) : ramenés à des trimestres (Fall 1936, Spring 1935-36 → printemps 1936, 1933 First Term),
   cours et enseignant, puis confrontés aux cours AAM (programme/cours_par_periode.csv) : titre et enseignant dans
   l'AAM / enseignant dans l'AAM cette année-là / absent de l'AAM.
Sorties : chronos/NNN_personnes_presences.csv, _cours_suivis.csv, _rapport.md ; semainier/data_personnes.js
(fiche de personne et cours suivis par trimestre, chargés par la page).
"""
import csv, json, os, re, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chronos_commun as K
import verifier_sources as V

SAISON = {"fall": "automne", "spring": "printemps", "summer": "été", "winter": "hiver", "first": "automne", "second": "printemps"}


def lire(p):
    with open(p, encoding="utf-8") as f: return list(csv.DictReader(f))


def parse_base(t):
    out = []
    for b in [b for b in re.split(r"\n\s*\n(?=NAME:)", t) if b.strip()]:
        d = {}
        for k, nxt in (("NAME", "BIO"), ("BIO", r"(?:Relations|COURSE TAKEN)"), ("Relations", "COURSE TAKEN"),
                       ("COURSE TAKEN", "Focus"), ("Focus", "Role"), ("Role", "Start Year"), ("Start Year", "End Year"), ("End Year", r"\Z")):
            m = re.search(rf"^{k}:[ \t]*(.*?)\n?(?=^{nxt}:|\Z)" if nxt != r"\Z" else rf"^{k}:[ \t]*(.*)", b, re.M | re.S)
            d[k] = m.group(1).strip() if m else ""
        for k in ("Start Year", "End Year"):
            m = re.match(r"(\d{4})", d[k]); d[k] = int(m.group(1)) if m else None
        out.append(d)
    return out


ENTETE = re.compile(r"(?:(\d{4})\s+)?\b(Fall|Spring|Summer|Winter|First|Second)\s*(?:Term|Semester|Quarter|Session|Art Institute|Institute)?\s*"
                    r"(\d{4})?(?:\s*[-–]\s*(\d{2,4}))?\s*(?:\[[^\]]*\])?\s*:", re.I)


def parse_cours(txt):
    """[(saison, année du trimestre, cours, enseignants)]"""
    out, ms = [], list(ENTETE.finditer(txt))
    for i, m in enumerate(ms):
        seg = txt[m.end(): ms[i + 1].start() if i + 1 < len(ms) else len(txt)]
        s = m.group(2).lower(); y1 = m.group(1) or m.group(3)
        if not y1: continue
        y = int(y1)
        if m.group(4) and s in ("spring", "second", "winter", "summer"):       # « Spring 1935-36 » : printemps 1936
            y2 = int(m.group(4)); y = y2 if y2 > 100 else (y // 100) * 100 + y2
        for it in re.split(r"[,;]\s*(?![^()]*\))|\.\s+(?=[A-Z])", seg):
            it = it.strip(" .;/")
            if len(it) < 3: continue
            mm = re.match(r"(.+?)\s+with\s+(.+)$", it) or re.match(r"(.+?)\s*\(([^)]+)\)\s*$", it)
            cours, ens = (mm.group(1).strip(), mm.group(2).strip()) if mm else (it, "")
            cours = re.sub(r"\[[^\]]*\]", "", cours).strip()
            out.append((SAISON[s], y, cours[:120], ens[:80]))
    return out


def annee_scolaire(saison, y):
    return f"{y}-{str(y + 1)[2:]}" if saison == "automne" else f"{y - 1}-{str(y)[2:]}"


def main():
    P = parse_base(open(os.path.join(K.CHRONOS, "BlackMountainPeople.txt"), encoding="utf-8").read())
    # personnes nommées dans l'AAM et Duberman (au jour) : (prénom, nom) → dates
    attest = collections.defaultdict(list)
    for base, L in (("AAM", lire(os.path.join(K.ROOT, "programme", "evenements.csv"))),
                    ("Duberman", [e for e in lire(os.path.join(K.ROOT, "duberman", "evenements_duberman.csv")) if e["precision"] == "jour"])):
        for e in L:
            for q in (e["qui"] or "").split(";"):
                w = re.findall(r"[a-z]+", V.plat(re.sub(r"\(.*?\)", "", q)))
                if len(w) >= 2: attest[w[-1]].append((w[0], e["date"], base))
    cours_aam = lire(os.path.join(K.ROOT, "programme", "cours_par_periode.csv"))

    pres, suivis, fiches = [], [], {}
    for p in P:
        nom = p["NAME"]; w = re.findall(r"[a-z]+", V.plat(re.sub(r"\(.*?\)", "", nom)))
        if not w: continue
        prenoms = {x for x in w[:-1]} | set(re.findall(r'"([a-z]+)"', V.plat(nom)))
        hits = [(d, b) for (pr, d, b) in attest.get(w[-1], []) if pr in prenoms or (len(pr) == 1 and pr in {x[0] for x in prenoms})]
        a, z = p["Start Year"], p["End Year"]
        if a and z and z < a: st = "années incohérentes"
        elif not hits: st = "non attesté"
        else:
            ys = [int(d[:4]) for d, _ in hits]
            st = "concordant" if a and z and min(ys) >= a - 1 and max(ys) <= z + 1 else "débordement"
        pres.append({"nom": nom, "role": p["Role"], "domaine": p["Focus"], "debut_base": a or "", "fin_base": z or "", "statut": st,
                     "attestees": len(hits), "premiere": min((d for d, _ in hits), default=""), "derniere": max((d for d, _ in hits), default=""),
                     "bases": " + ".join(sorted({b for _, b in hits}))})
        cs = parse_cours(p["COURSE TAKEN"]) if p["COURSE TAKEN"] else []
        for s, y, c, e in cs:
            ens_n = K.noms_famille([x.strip() for x in re.split(r",| and |/|&", e) if x.strip()]) or {V.plat(x) for x in re.findall(r"[A-Z][a-z\-]+", e)}
            ys = (y, y + 1) if s == "automne" else (y - 1, y)
            m = [k for k in cours_aam if ens_n & (K.noms_famille(k["enseignant"].split(";")) | {V.plat(x) for x in re.findall(r"[A-Z][a-z\-]+", k["enseignant"])})
                 and any(str(v) in k["periode"] for v in ys)]
            mt = [k for k in m if {x for x in re.findall(r"[a-z]{4,}", V.plat(c))} & {x for x in re.findall(r"[a-z]{4,}", V.plat(k["cours"]))}]
            suivis.append({"etudiant": nom, "trimestre": f"{s} {y}", "annee_scolaire": annee_scolaire(s, y), "cours": c, "enseignant": e,
                           "aam": "titre et enseignant dans l'AAM" if mt else "enseignant dans l'AAM cette année-là" if m else ("absent de l'AAM" if e else "enseignant non nommé"),
                           "aam_cours": (mt or m or [{}])[0].get("cours", "")[:100], "aam_inventaire": (mt or m or [{}])[0].get("inventaire", "")})
        fiches[nom] = {"bio": p["BIO"], "rel": p["Relations"], "role": p["Role"], "dom": p["Focus"], "a": a, "z": z,
                       "cours": [[s, y, c, e] for s, y, c, e in cs], "cours_brut": p["COURSE TAKEN"][:3000] if not cs else "",
                       "statut": st, "att": [len(hits), min((d for d, _ in hits), default=""), max((d for d, _ in hits), default="")]}

    num = K.prochain_numero(K.SORTIE)
    base = os.path.join(K.SORTIE, f"{num}_personnes")
    for suff, rows in (("_presences", pres), ("_cours_suivis", suivis)):
        with open(base + suff + ".csv", "w", encoding="utf-8", newline="") as f:
            w_ = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w_.writeheader(); w_.writerows(rows)
    # cours suivis par trimestre, pour le panneau du semainier
    par_t = collections.defaultdict(lambda: collections.defaultdict(lambda: {"ens": "", "etu": [], "aam": ""}))
    for s in suivis:
        k = (V.plat(s["cours"]).strip(), V.plat(s["enseignant"]).strip())
        x = par_t[s["trimestre"]][k]; x["c"] = s["cours"]; x["ens"] = s["enseignant"]; x["etu"].append(s["etudiant"]); x["aam"] = s["aam"]
    cours_t = {t: sorted(({"c": v["c"], "ens": v["ens"], "etu": v["etu"], "aam": v["aam"]} for v in d.values()), key=lambda v: (-len(v["etu"]), v["c"]))
               for t, d in par_t.items()}
    with open(os.path.join(K.ROOT, "semainier", "data_personnes.js"), "w", encoding="utf-8") as f:
        f.write(f"// généré par scripts/chronos_personnes.py ({num}) depuis DATA_BMC/Chronos/BlackMountainPeople.txt — ne pas éditer à la main\n")
        f.write("window.BMC_PERS = " + json.dumps({"fiches": fiches, "cours": cours_t}, ensure_ascii=False, separators=(",", ":")) + ";\n")
    N = collections.Counter
    R = [f"# Chronos 5/5 : BlackMountainPeople.txt — base des personnes ({num})", "",
         f"{len(P)} personnes : " + ", ".join(f"{k} {v}" for k, v in N(p['Role'] for p in P).most_common(8)) + ". Provenance non indiquée dans le dossier.", "",
         "## Présences contre l'AAM et Duberman (nom ET prénom)", "",
         "- " + ", ".join(f"{k} {v}" for k, v in N(x["statut"] for x in pres).most_common()) + ".",
         "- Par rôle (attestés / total) : " + ", ".join(f"{r} {sum(1 for x in pres if x['role'] == r and x['attestees'])}/{sum(1 for x in pres if x['role'] == r)}"
                                                          for r, _ in N(x["role"] for x in pres).most_common(5)) + ".", "",
         "## Débordements (activités attestées hors des années de la base)", ""]
    R += [f"- {x['nom']} ({x['role']}) : base {x['debut_base']}-{x['fin_base']} ; attesté du {x['premiere']} au {x['derniere']} ({x['bases']}, {x['attestees']} activités)"
          for x in pres if x["statut"] == "débordement"][:80]
    R += ["", "## Années incohérentes dans la base", ""] + [f"- {x['nom']} : {x['debut_base']} → {x['fin_base']}" for x in pres if x["statut"] == "années incohérentes"]
    R += ["", f"## Cours suivis ({len(suivis)} inscriptions, {len({s['etudiant'] for s in suivis})} étudiants, {len(cours_t)} trimestres)", "",
          "- " + ", ".join(f"{k} {v}" for k, v in N(s["aam"] for s in suivis).most_common()) + ".",
          "- Par année scolaire : " + ", ".join(f"{k} {v}" for k, v in sorted(N(s["annee_scolaire"] for s in suivis).items())) + "."]
    open(base + "_rapport.md", "w", encoding="utf-8").write("\n".join(R) + "\n")
    print("\n".join(R[:12])); print(R[-2]); print(R[-1])


if __name__ == "__main__":
    main()
