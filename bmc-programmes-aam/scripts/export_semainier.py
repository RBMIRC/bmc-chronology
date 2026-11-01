"""Produit semainier/data.js pour le semainier (semainier/index.html, Event Calendar MIT).
Sources : programme/evenements.csv, programme/calendrier_periodes.csv, programme/cours_par_periode.csv,
liste_pages.csv, extraction/*.txt (#ref = date établie du document), fiches*.json (images du musée),
et semainier/documents_extra.csv (documents datés ajoutés à la main, facultatif).
Chaque activité garde sa source (document, inventaire, lien) et sa part de déduction ;
le placement horaire indicatif d'une activité sans heure précise (« soir »…) est signalé à part."""
import csv, os, re, json, datetime as dt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROG = os.path.join(ROOT, "programme"); SEM = os.path.join(ROOT, "semainier")
MUSEE = "https://collection.ashevilleart.org"

# Même personne écrite de deux façons dans les sources (normalisation d'affichage seulement ;
# le champ « qui » d'origine reste dans la fiche de chaque activité).
ALIAS = {
    "Bob Babcock": "Robert Babcock", "Erik Haugaard": "Eric Haugaard", "Frederick H. Koch": "Frederic H. Koch",
    "Ken Kurtz": "Kenneth Kurtz", "Dick Lockwood": "Richard Lockwood", "Mackie Quave": "Mackey Quave",
    "William McLaughlin": "Bill McLaughlin", "Sylvesta Martin": "Vesta Martin", "McGuire Wood": "Mac Wood",
    "Robert Wunsch": "Bob Wunsch", "Mrs Fritz Hansgirg": "Maria Hansgirg", "Mr Nowak": "Lionel Nowak",
    "Internal Finances Committee": "Internal Finance Committee", "Ilse Hoffman": "Ilse Hoffmann",
    "A Cappella group": "A Cappella Group", "Madrigal group": "Madrigal Group", "Dramatic Department": "Drama Department",
}
GROUPE = re.compile(r"\b(faculty|board|committee|department|group|class|students?|chorus|choir|quartet|trio|"
                    r"seminar|campers|committees|workshop|officers|council|union|club|orchestra|ensemble|tutors|community|college|school|"
                    r"society|institute|workers|members|guests|staff|everyone|all|cast|players|singers|league|"
                    r"association|conference|meeting|y\.?m\.?c\.?a|church|university|team|crew|band)\b", re.I)
# Placement indicatif dans la grille pour les moments sans heure : (début, fin)
MOMENTS = {"matin": ("09:00", "12:00"), "après-midi": ("14:00", "17:00"), "soir": ("20:00", "22:00")}

def lire(p):
    with open(p, encoding="utf-8") as f:
        return list(csv.DictReader(f))

def personnes(qui):
    out = []
    for q in (qui or "").split(";"):
        q = re.sub(r"\s+", " ", re.sub(r"\(.*?\)", "", q)).strip(" .,")
        if q and q not in ("—", "-"):
            q = ALIAS.get(q, q)
            if q not in out: out.append(q)
    return out

def plus1h(h):
    t = dt.datetime.strptime(h, "%H:%M") + dt.timedelta(hours=1)
    return "23:59" if t.day > 1 else t.strftime("%H:%M")

def refs():
    """inventaire -> date établie (#ref) depuis extraction/."""
    d = {}
    for fn in os.listdir(os.path.join(ROOT, "extraction")):
        if not fn.endswith(".txt") or fn.startswith("_"): continue
        with open(os.path.join(ROOT, "extraction", fn), encoding="utf-8") as f:
            for l in f:
                m = re.match(r"#ref\s+(\d{4}-\d{2}-\d{2})", l)
                if m: d[fn[:-4]] = m.group(1); break
    return d

def images():
    d = {}
    for fn in ("fiches.json", "fiches_sondees.json"):
        p = os.path.join(ROOT, fn)
        if os.path.exists(p):
            for f in json.load(open(p, encoding="utf-8")):
                if f.get("images") and f["accession"] not in d:
                    d[f["accession"]] = [MUSEE + i for i in f["images"]]
    return d

def main():
    ref, img = refs(), images()
    docs = {}
    for p in lire(os.path.join(ROOT, "liste_pages.csv")):
        inv = p["accession"]; date = ref.get(inv)
        docs[inv] = {"inv": inv, "titre": p["titre"], "url": p["url"], "categorie": p["categorie"],
                     "date": date or "", "date_musee": p["date"],
                     "datation": "date établie à la lecture (#ref de l'extraction)" if date else "date du musée seulement",
                     "img": (img.get(inv) or [""])[0], "nimg": len(img.get(inv) or []), "kind": "musee"}
    extra = os.path.join(SEM, "documents_extra.csv")
    if os.path.exists(extra):
        for i, p in enumerate(lire(extra)):
            if not p.get("date"): continue
            docs[f"extra-{i}"] = {"inv": p.get("inventaire") or "", "titre": p["titre"], "url": p.get("url", ""),
                                  "categorie": p.get("type", "document ajouté"), "date": p["date"], "date_musee": "",
                                  "datation": p.get("datation") or "ajouté à la main", "img": p.get("image", ""),
                                  "nimg": 1 if p.get("image") else 0, "kind": "extra",
                                  "source": p.get("source", ""), "pct": int(p.get("part_deduite_pct") or 0)}

    evs, res = [], {}
    for i, e in enumerate(lire(os.path.join(PROG, "evenements.csv"))):
        qui = personnes(e["qui"]) or ["(non nommé)"]
        for q in qui:
            res.setdefault(q, 0); res[q] += 1
        d, a, b = e["date"], e["debut"].strip(), e["fin"].strip()
        x = {"id": str(i), "title": e["activite"], "resourceIds": qui,
             "extendedProps": {"type": e["type"], "qui": e["qui"], "lieu": e["lieu"], "note": e["note"],
                               "pct": int(e["part_deduite_pct"] or 0), "motifs": e["motifs_deduction"],
                               "rec": e["recurrent_deduit"] == "oui", "src": e["document_source"],
                               "inv": e["inventaire"], "url": e["url_source"], "heure": a, "fin": b}}
        if re.fullmatch(r"\d{1,2}:\d{2}", a):
            a = a.zfill(5)
            b = b.zfill(5) if re.fullmatch(r"\d{1,2}:\d{2}", b) and b.zfill(5) > a else ""
            x["start"] = f"{d}T{a}"; x["end"] = f"{d}T{b or plus1h(a)}"
            x["extendedProps"]["placement"] = "" if b else "fin non attestée : durée d'1 h affichée par défaut"
        elif a in MOMENTS:
            s, t = MOMENTS[a]
            x["start"] = f"{d}T{s}"; x["end"] = f"{d}T{t}"
            x["extendedProps"]["placement"] = f"« {a} » dans la source : placé {s}–{t} à titre indicatif"
        else:
            x["start"] = d; x["allDay"] = True
            x["end"] = (dt.date.fromisoformat(d) + dt.timedelta(days=1)).isoformat()
            x["extendedProps"]["placement"] = "aucune heure dans la source : affiché en journée entière"
        evs.append(x)

    # couche spéculative (scripts/speculer.py) : gabarits par trimestre + semaines, développés dans la page
    dspec = os.path.join(PROG, "speculatif"); spec = {}; nspec = 0
    for fn in sorted(os.listdir(dspec)) if os.path.isdir(dspec) else []:
        m = re.fullmatch(r"annee_(\d{4}-\d{2})_gabarits\.csv", fn)
        if not m: continue
        an = m.group(1)
        gab = lire(os.path.join(dspec, fn))
        sem = lire(os.path.join(dspec, f"annee_{an}_semaines.csv"))
        for g in gab:
            g["resourceIds"] = personnes(g["qui"]) or ["(non nommé)"]
            for q in g["resourceIds"]:
                res.setdefault(q, 0); res[q] += 1
            for k in ("part_case_pct", "part_titre_pct", "part_deduite_pct"): g[k] = int(g[k])
        for x in sem: x["jours"] = x["jours"].split()
        spec[an] = {"gabarits": gab, "semaines": sem,
                    "analyse": open(os.path.join(dspec, f"annee_{an}.md"), encoding="utf-8").read()}
        nspec += sum(1 for x in sem for g in gab if g["terme"] == x["terme"] and (g["jour"] == "semaine" or True))

    resources = [{"id": "G:personnes", "title": "Personnes", "children": []},
                 {"id": "G:groupes", "title": "Groupes et instances", "children": []}]
    for q in sorted(res, key=lambda s: (s.split()[-1].lower() if not GROUPE.search(s) else s.lower())):
        resources[1 if (GROUPE.search(q) or q == "(non nommé)") else 0]["children"].append(
            {"id": q, "title": q, "extendedProps": {"n": res[q]}})

    periodes = [{"debut": p["debut"], "fin": p["fin"], "libelle": p["libelle"], "note": p["note"],
                 "pct": int(p["part_deduite_pct"] or 0), "motifs": p["motifs_deduction"],
                 "src": p["document_source"], "url": p["url_source"]}
                for p in lire(os.path.join(PROG, "calendrier_periodes.csv"))]
    ps = os.path.join(ROOT, "speculation", "calendrier_speculatif.csv")
    if os.path.exists(ps):
        periodes += [{"debut": p["debut"], "fin": p["fin"], "libelle": p["libelle"], "note": p["note"], "spec": True,
                      "pct": int(p["part_deduite_pct"] or 0), "motifs": p["motifs_deduction"],
                      "src": p["document_source"], "url": p["url_source"].split()[0]} for p in lire(ps)]
    cours = [{"periode": c["periode"], "cours": c["cours"], "qui": c["enseignant"], "horaire": c["horaire"],
              "note": c["note"], "pct": int(c["part_deduite_pct"] or 0), "motifs": c["motifs_deduction"],
              "src": c["document_source"], "url": c["url_source"]}
             for c in lire(os.path.join(PROG, "cours_par_periode.csv"))]

    audit = {}
    pa = os.path.join(PROG, "audit", "semaines.csv")
    if os.path.exists(pa):
        for r in lire(pa):
            audit[r["lundi"]] = {k: r[k] for k in ("statut", "niveau", "activites", "seances_cours", "jours_avec_cours", "documents", "issues_de_recurrences", "speculatif")}
    data = {"genere": dt.date.today().isoformat(), "events": evs, "resources": resources, "spec": spec, "audit": audit,
            "documents": sorted(docs.values(), key=lambda d: d["date"] or "9999"),
            "periodes": periodes, "cours": cours}
    os.makedirs(SEM, exist_ok=True)
    with open(os.path.join(SEM, "data.js"), "w", encoding="utf-8") as f:
        f.write("// généré par scripts/export_semainier.py — ne pas éditer à la main\n")
        f.write("window.BMC = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n")
    nd = sum(1 for d in docs.values() if d["date"])
    print(f"semainier/data.js : {len(evs)} activités attestées + couche spéculative ({len(spec)} années, environ {nspec} entrées développées), {len(res)} personnes/groupes, "
          f"{len(docs)} documents ({nd} datés au jour), {len(periodes)} périodes, {len(cours)} cours")

if __name__ == "__main__":
    main()
