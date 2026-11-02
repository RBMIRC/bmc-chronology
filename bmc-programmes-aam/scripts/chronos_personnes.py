"""Chronos 5/5 : base des personnes du BMC Yearbook (https://bmcyearbook.org/biographies, Black Mountain College
Museum + Arts Center ; notices compilées des archives, Western Regional Archives surtout, beaucoup écrites par Mary Emma
Harris pour le Black Mountain College Project).
Source lue : la copie du site DATA_BMC/bmcyearbook/NNN_biographies.jsonl (scripts/yearbook_telecharger.py), la plus
récente ; à défaut, l'export texte DATA_BMC/Chronos/BlackMountainPeople.txt (1 299 notices, même base, sans les dates
au jour ni les renvois à l'AAM), qui sert alors de contrôle : personnes absentes de l'une ou l'autre, cours différents.
Le site donne en plus : dates d'arrivée et de départ au jour (pour moitié le premier ou le dernier jour d'une période de
cours attestée, 70 % à une semaine près : contrôle du 2/11/2026),
naissance et décès, lien vers la notice, et les documents de l'AAM qui nomment la personne (« Asheville Art Museum
Collection : 2017.40.024 September 1943 bulletin, "…" ») : chaque renvoi est cherché dans notre OCR de la fiche.

1. Présences : les années de la base sont confrontées aux activités attestées de la personne (AAM, Duberman au jour),
   reconnues par nom de famille ET prénom (ou surnom, ou initiale) pour éviter les homonymes :
     concordant ......... activités attestées toutes dans les années de la base (± 1 an)
     débordement ........ activités attestées hors de ces années : l'une des deux sources est à revoir
     non attesté ........ aucune activité nommée (cas de la plupart des étudiants)
     années incohérentes  fin avant début dans la base
2. Cours suivis (355 fiches) : ramenés à des trimestres (Fall 1936, Spring 1935-36 → printemps 1936, 1933 First Term),
   cours et enseignant, puis confrontés aux cours AAM (programme/cours_par_periode.csv) : titre et enseignant dans
   l'AAM / enseignant dans l'AAM cette année-là / absent de l'AAM.
3. Renvois à l'AAM (Yearbook) : la fiche citée est-elle dans liste_pages.csv, et le nom de famille dans son OCR ?
Sorties : chronos/NNN_personnes_presences.csv, _cours_suivis.csv, _renvois_aam.csv, _rapport.md ; semainier/data_personnes.js
(fiche de personne et cours suivis par trimestre, chargés par la page).
"""
import csv, datetime as dt, glob, json, os, re, sys, collections
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


ENTETE = re.compile(r"(?:(\d{4})\s+)?\b(Fall|Spring|Summer|Winter|First|Second)\s*(?:Term|Semester|Quarter|Session|Art Institute|Institute)?\s*,?\s*"
                    r"\(?(\d{4})?(?:\s*[-–]\s*(\d{2,4}))?\)?\s*(?:\[[^\]]*\])?\s*:", re.I)


def parse_cours(txt):
    """[(saison, année du trimestre, cours, enseignants)]"""
    txt = re.sub(r"\b([A-Z])\.(?=\s?[A-Z])", r"\1", txt)          # initiales : « M.C. Richards » → « MC Richards »
    txt = re.sub(r"\)o(?=(?:Fall|Spring|Summer|Winter|First|Second)\b)", "); ", txt)   # puce « o » collée : « (Larson)oSpring term »
    out, ms = [], list(ENTETE.finditer(txt))
    for i, m in enumerate(ms):
        seg = txt[m.end(): ms[i + 1].start() if i + 1 < len(ms) else len(txt)]
        s = m.group(2).lower(); y1 = m.group(1) or m.group(3)
        if not y1: continue
        y = int(y1)
        if m.group(4) and s in ("spring", "second", "winter", "summer"):       # « Spring 1935-36 » : printemps 1936
            y2 = int(m.group(4)); y = y2 if y2 > 100 else (y // 100) * 100 + y2
        for it in re.split(r"[,;]\s*(?![^()]*\))|\.\s+(?=[A-Z])", seg):
            it = re.sub(r"^(?:and|&)\s+", "", it.strip(" .;/"))
            abandon = bool(re.search(r"[—–-]{1,2}\s*dropped|\[dropped", it, re.I))
            it = re.sub(r"\s*[—–-]{1,2}\s*dropped.*$", "", it, flags=re.I).strip()
            if len(it) < 3: continue
            mm = re.match(r"(.+?)\s+with\s+(.+)$", it) or re.match(r"(.+?)\s*\(([^)]+)\)\s*$", it)
            cours, ens = (mm.group(1).strip(), mm.group(2).strip()) if mm else (it, "")
            note = "; ".join(x.strip() for x in re.findall(r"\[([^\]]*)\]", cours + " " + ens) if not re.match(r"dropped", x.strip(), re.I))
            cours = re.sub(r"\[[^\]]*\]", "", cours).strip()
            ens = re.sub(r"\[[^\]]*\]", "", ens).strip()
            out.append((SAISON[s], y, cours[:120], (ens + (" [abandonné]" if abandon else ""))[:80], note[:200]))
    return out


ROLES = {"student": "Student", "faculty": "Faculty", "guestFaculty": "Guest Faculty", "staff": "Staff", "guest": "Guest",
         "family": "Family", "admin": "Administrator"}
TITRES = {"relationships": "Relations", "relations": "Relations", "courses taken": "COURSE TAKEN",
          "asheville art museum collection": "AAM", "black mountain college project": "BMCP"}


def lire_yearbook(p, focus_txt):
    """notices du site → mêmes champs que BlackMountainPeople.txt, plus url, dates au jour, renvois à l'AAM."""
    out = []
    for l in open(p, encoding="utf-8"):
        d = json.loads(l); q = d["personne"]
        nom = " ".join(x for x in (q.get("firstName"), q.get("nickname"), q.get("lastName")) if x) or d["nom_liste"]
        sec, parts = "BIO", collections.defaultdict(list)
        for b in d["blocs"]:
            t = b["texte"].strip()
            k = TITRES.get(t.strip(": ").lower()) or ("COURSE TAKEN" if re.match(r"courses? (taken|taught)", t.lower()) and len(t) < 40 else None)
            if k and not b["puce"]: sec = k; continue
            if not b["puce"] and len(t) < 45 and not re.match(r"\d{4}\.", t) and sec == "BIO" and parts["BIO"]: sec = "BIO"   # intertitre (Early Life…)
            parts[sec].append(t)
        refs = []
        for t in parts["AAM"]:
            m = re.match(r"(\d{4}\.\d+\.\d+(?:\.\d+)?[a-z\-]*(?:\.\d+-\d+)?)\s*(.*)", t)
            if m: refs.append([m.group(1), m.group(2).strip(" ,"), ""])
            elif refs and not refs[-1][2]: refs[-1][2] = t.strip()[:400]
        a, z = q.get("collegeStart") or "", q.get("collegeStop") or ""
        out.append({"NAME": nom, "BIO": " ".join(parts["BIO"]), "Relations": "; ".join(parts["Relations"]),
                    "COURSE TAKEN": " ".join(x if re.search(r":\s*$|\.\s*$", x) else x + " ;" for x in parts["COURSE TAKEN"]),
                    "Focus": focus_txt.get(q.get("focus") or "", q.get("focus") or ""), "Role": "/ ".join(ROLES.get(r, r) for r in q.get("role") or []),
                    "Start Year": int(a[:4]) if a else None, "End Year": int(z[:4]) if z else None,
                    "url": d["url"], "debut": a, "fin": z, "naissance": q.get("dob") or "", "deces": q.get("dod") or "",
                    "lieux": " → ".join(x for x in (q.get("birthPlace"), q.get("deathPlace")) if x), "refs_aam": refs,
                    "bmcp": " ".join(parts["BMCP"])[:600],
                    "auteur": "Mary Emma Harris (Black Mountain College Project)" if re.search(r"written by Mary Emma Harris", " ".join(parts["BIO"])) else ""})
    return out


def annee_scolaire(saison, y):
    return f"{y}-{str(y + 1)[2:]}" if saison == "automne" else f"{y - 1}-{str(y)[2:]}"


def main():
    TXT = parse_base(open(os.path.join(K.CHRONOS, "BlackMountainPeople.txt"), encoding="utf-8").read())
    yb = sorted(glob.glob(os.path.join(K.DEPOT, "DATA_BMC", "bmcyearbook", "[0-9][0-9][0-9]_biographies.jsonl")))
    comparaison = []
    if yb:
        # libellés de domaine du .txt, appris sur les personnes communes (code du site → libellé)
        def cle(n):        # prénom + nom de famille, sans surnom ni ponctuation (« Mary "M.C." Richards » = « Mary "MC" Richards »)
            w = re.findall(r"[a-z]+", V.plat(re.sub(r'"[^"]*"|“[^”]*”|\(.*?\)', " ", n)))
            return f"{w[0]} {w[-1]}" if w else V.plat(n)
        par_nom = {cle(t["NAME"]): t for t in TXT}
        brut = [json.loads(l) for l in open(yb[-1], encoding="utf-8")]
        fx = collections.defaultdict(collections.Counter)
        for d in brut:
            q = d["personne"]; n = cle(" ".join(x for x in (q.get("firstName"), q.get("nickname"), q.get("lastName")) if x))
            if n in par_nom and q.get("focus"): fx[q["focus"]][par_nom[n]["Focus"]] += 1
        P = lire_yearbook(yb[-1], {k: v.most_common(1)[0][0] for k, v in fx.items()})
        SRC = f"BMC Yearbook (bmcyearbook.org/biographies), copie {os.path.basename(yb[-1])}"
        # rapprochement de secours (nom d'épouse, surnom) : même prénom et nom du .txt dans le nom complet du site,
        # ou même début de biographie
        complet = {d["url"]: V.plat(d["nom_liste"] or "") for d in brut}
        bio40 = {V.plat(p["BIO"])[:60]: p for p in P if len(p["BIO"]) > 60}
        for t in TXT:
            if cle(t["NAME"]) in {cle(p["NAME"]) for p in P}: continue
            w = re.findall(r"[a-z]+", V.plat(re.sub(r'"[^"]*"', " ", t["NAME"])))
            m = [p for p in P if w and complet.get(p["url"], "").split()[:1] == w[:1] and re.search(rf"\b{w[-1]}\b", complet.get(p["url"], ""))]
            m = m or [bio40[k] for k in [V.plat(t["BIO"])[:60]] if k in bio40]
            if len(m) == 1: par_nom[cle(m[0]["NAME"])] = t; m[0]["autre_nom"] = t["NAME"]
        noms_yb = {cle(p["NAME"]) for p in P} | {cle(p["autre_nom"]) for p in P if p.get("autre_nom")}
        for p in P:
            t = par_nom.get(cle(p["NAME"]))
            if not t: comparaison.append({"nom": p["NAME"], "url": p["url"], "ecart": "absent du .txt (ajouté au site depuis l'export ?)", "detail": ""}); continue
            if (t["Start Year"], t["End Year"]) != (p["Start Year"], p["End Year"]):
                comparaison.append({"nom": p["NAME"], "url": p["url"], "ecart": "années différentes", "detail": f".txt {t['Start Year']}-{t['End Year']} ; site {p['debut']} → {p['fin']}"})
            ct, cy = len(parse_cours(t["COURSE TAKEN"])) if t["COURSE TAKEN"] else 0, len(parse_cours(p["COURSE TAKEN"])) if p["COURSE TAKEN"] else 0
            if ct != cy: comparaison.append({"nom": p["NAME"], "url": p["url"], "ecart": "nombre de cours différent", "detail": f".txt {ct} ; site {cy}"})
        for t in TXT:
            if cle(t["NAME"]) not in noms_yb:
                comparaison.append({"nom": t["NAME"], "url": "", "ecart": "absent du site (nom changé, notice retirée ou en erreur) : repris du .txt", "detail": f"{t['Role']} {t['Start Year']}-{t['End Year']}"})
                P.append(dict(t, url="", auteur="", bmcp="", refs_aam=[], debut="", fin="", naissance="", deces="", lieux="",
                              BIO=t["BIO"] + " [notice reprise de l'export BlackMountainPeople.txt : absente de la copie du site]"))
    else:
        P, SRC = TXT, "DATA_BMC/Chronos/BlackMountainPeople.txt (export du BMC Yearbook)"
    # fiches AAM indexées aussi par numéro de base (« 2017.40.196a-e » → « 2017.40.196 ») : le site cite sans suffixe
    base_inv = lambda x: re.sub(r"(?<=\d)[a-z][a-z0-9\-,]*$", "", x.strip())
    TA = collections.defaultdict(str); docs_aam = {}
    for k, v in V.textes_aam().items(): TA[k] += v; TA[base_inv(k)] += v
    for r in lire(os.path.join(K.ROOT, "liste_pages.csv")): docs_aam.setdefault(r["accession"], r); docs_aam.setdefault(base_inv(r["accession"]), r)
    # personnes nommées dans l'AAM et Duberman (au jour) : (prénom, nom) → dates
    attest = collections.defaultdict(list)
    for base, L in (("AAM", lire(os.path.join(K.ROOT, "programme", "evenements.csv"))),
                    ("Duberman", [e for e in lire(os.path.join(K.ROOT, "duberman", "evenements_duberman.csv")) if e["precision"] == "jour"])):
        for e in L:
            for q in (e["qui"] or "").split(";"):
                w = re.findall(r"[a-z]+", V.plat(re.sub(r"\(.*?\)", "", q)))
                if len(w) >= 2: attest[w[-1]].append((w[0], e["date"], base))
    cours_aam = lire(os.path.join(K.ROOT, "programme", "cours_par_periode.csv"))

    pres, suivis, fiches, renvois = [], [], {}, []
    for p in P:
        nom = p["NAME"]; w = re.findall(r"[a-z]+", V.plat(re.sub(r"\(.*?\)", "", nom)))
        if not w: continue
        prenoms = {x for x in w[:-1]} | set(re.findall(r'"([a-z]+)"', V.plat(nom)))
        hits = [(d, b) for (pr, d, b) in attest.get(w[-1], []) if pr in prenoms or (len(pr) == 1 and pr in {x[0] for x in prenoms})]
        a, z = p["Start Year"], p["End Year"]
        # au jour (site) : activités attestées entre l'arrivée et le départ, à 45 jours près
        st_j = ""
        if p.get("debut") and p.get("fin") and hits:
            d0 = dt.date.fromisoformat(p["debut"]) - dt.timedelta(45); d1 = dt.date.fromisoformat(p["fin"]) + dt.timedelta(45)
            hors = [d for d, _ in hits if not (d0.isoformat() <= d <= d1.isoformat())]
            av = [d for d in hors if d < d0.isoformat()]; ap = [d for d in hors if d > d1.isoformat()]
            st_j = "dans les dates" if not hors else "; ".join(x for x in (f"{len(av)} avant l'arrivée (dès {av[0]})" if av else "",
                                                                           f"{len(ap)} après le départ (jusqu'au {ap[-1]})" if ap else "") if x)
        if a and z and z < a: st = "années incohérentes"
        elif not hits: st = "non attesté"
        else:
            ys = [int(d[:4]) for d, _ in hits]
            st = "concordant" if a and z and min(ys) >= a - 1 and max(ys) <= z + 1 else "débordement"
        pres.append({"nom": nom, "url": p.get("url", ""), "role": p["Role"], "domaine": p["Focus"], "debut_base": a or "", "fin_base": z or "",
                     "arrivee": p.get("debut", ""), "depart": p.get("fin", ""), "statut_au_jour": st_j, "statut": st,
                     "attestees": len(hits), "premiere": min((d for d, _ in hits), default=""), "derniere": max((d for d, _ in hits), default=""),
                     "bases": " + ".join(sorted({b for _, b in hits}))})
        cs = parse_cours(p["COURSE TAKEN"]) if p["COURSE TAKEN"] else []
        for s, y, c, e, nt in cs:
            ens_n = K.noms_famille([x.strip() for x in re.split(r",| and |/|&", e) if x.strip()]) or {V.plat(x) for x in re.findall(r"[A-Z][a-z\-]+", e)}
            ys = (y, y + 1) if s == "automne" else (y - 1, y)
            m = [k for k in cours_aam if ens_n & (K.noms_famille(k["enseignant"].split(";")) | {V.plat(x) for x in re.findall(r"[A-Z][a-z\-]+", k["enseignant"])})
                 and any(str(v) in k["periode"] for v in ys)]
            mt = [k for k in m if {x for x in re.findall(r"[a-z]{4,}", V.plat(c))} & {x for x in re.findall(r"[a-z]{4,}", V.plat(k["cours"]))}]
            suivis.append({"etudiant": nom, "url": p.get("url", ""), "trimestre": f"{s} {y}", "annee_scolaire": annee_scolaire(s, y), "cours": c, "enseignant": e, "note": nt,
                           "aam": "titre et enseignant dans l'AAM" if mt else "enseignant dans l'AAM cette année-là" if m else ("absent de l'AAM" if e else "enseignant non nommé"),
                           "aam_cours": (mt or m or [{}])[0].get("cours", "")[:100], "aam_inventaire": (mt or m or [{}])[0].get("inventaire", "")})
        # renvois à l'AAM : fiche connue ? nom dans son OCR ?
        nf = w[-1]
        for r in p.get("refs_aam", []):
            acc = r[0]; base_acc = base_inv(re.sub(r"\.\d+-\d+$", "", acc))
            doc = docs_aam.get(acc) or docs_aam.get(base_acc)
            txt = V.plat(TA.get(acc, "") or TA.get(base_acc, ""))
            r.append("fiche absente de notre corpus AAM (liste_pages.csv)" if not doc else "nom retrouvé dans l'OCR" if nf in txt else "fiche connue, nom non retrouvé dans l'OCR" if txt else "fiche connue, pas d'OCR")
            renvois.append({"nom": nom, "url": p.get("url", ""), "inventaire": acc, "libelle": r[1], "citation": r[2][:300], "statut": r[3],
                            "fiche_aam": doc["titre"] if doc else "", "date_aam": doc["date"] if doc else ""})
        fiches[nom] = {"bio": p["BIO"], "rel": p["Relations"], "role": p["Role"], "dom": p["Focus"], "a": a, "z": z,
                       "url": p.get("url", ""), "j": [p.get("debut", ""), p.get("fin", "")], "vie": [p.get("naissance", ""), p.get("deces", ""), p.get("lieux", "")],
                       "aam": [[r[0], r[1], r[3]] for r in p.get("refs_aam", [])], "auteur": p.get("auteur", ""),
                       "cours": [[s, y, c, e, nt] for s, y, c, e, nt in cs], "cours_brut": p["COURSE TAKEN"][:3000] if not cs else "",
                       "statut": st, "att": [len(hits), min((d for d, _ in hits), default=""), max((d for d, _ in hits), default="")]}
        if p.get("autre_nom"): fiches[p["autre_nom"]] = dict(fiches[nom], alias_de=nom)     # nom de l'export .txt (nom de jeune fille…)

    num = K.prochain_numero(K.SORTIE)
    base = os.path.join(K.SORTIE, f"{num}_personnes")
    for suff, rows in (("_presences", pres), ("_cours_suivis", suivis), ("_renvois_aam", renvois), ("_comparaison_txt", comparaison)):
        if not rows: continue
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
        f.write(f"// généré par scripts/chronos_personnes.py ({num}) depuis {SRC} — ne pas éditer à la main\n")
        f.write("window.BMC_PERS = " + json.dumps({"source": SRC, "fiches": fiches, "cours": cours_t}, ensure_ascii=False, separators=(",", ":")) + ";\n")
    N = collections.Counter
    R = [f"# Chronos 5/5 : base des personnes du BMC Yearbook ({num})", "",
         f"Source : {SRC}. {len(P)} personnes : " + ", ".join(f"{k} {v}" for k, v in N(p['Role'] for p in P).most_common(8)) + ".", ""]
    if comparaison:
        R += ["## Site contre l'export .txt (DATA_BMC/Chronos/BlackMountainPeople.txt)", "",
              "- " + ", ".join(f"{k} {v}" for k, v in N(c["ecart"] for c in comparaison).most_common()) + f" (détail : `{num}_personnes_comparaison_txt.csv`).", ""]
    if renvois:
        R += ["## Renvois du site aux fiches de l'AAM", "",
              f"- {len(renvois)} renvois ({len({r['nom'] for r in renvois})} personnes) : " + ", ".join(f"{k} {v}" for k, v in N(r["statut"] for r in renvois).most_common()) + ".", ""]
    R += [

         "## Présences contre l'AAM et Duberman (nom ET prénom)", "",
         "- " + ", ".join(f"{k} {v}" for k, v in N(x["statut"] for x in pres).most_common()) + ".",
         "- Au jour (arrivée et départ du site, ± 45 jours) : " + ", ".join(f"{k} {v}" for k, v in N(k for x in pres if x["statut_au_jour"] for k in (["dans les dates"] if x["statut_au_jour"] == "dans les dates" else
                                                       (["mentions avant l'arrivée"] if "avant" in x["statut_au_jour"] else []) + (["mentions après le départ (souvent des nouvelles d'anciens)"] if "après" in x["statut_au_jour"] else []))).most_common()) + ".",
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
