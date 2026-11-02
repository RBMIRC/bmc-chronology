"""Produit semainier/data.js pour le semainier (semainier/index.html, Event Calendar MIT).
Sources : programme/evenements.csv, programme/calendrier_periodes.csv, programme/cours_par_periode.csv,
liste_pages.csv, extraction/*.txt (#ref = date établie du document), fiches*.json (images du musée),
semainier/documents_extra.csv (documents datés ajoutés à la main, facultatif),
duberman/evenements_duberman.csv (couche « Duberman »), duberman/documents_extra_duberman.csv (documents datés
cités dans les notes de Duberman) et duberman/001_doublons_aam.csv (rapprochements AAM/Duberman décidés à la main :
« doublon » = la ligne AAM est gardée et reçoit le renvoi Duberman ; « possible » = les deux restent, avec renvoi mutuel).
Chaque activité garde sa source (document, inventaire, lien) et sa part de déduction ;
le placement horaire indicatif d'une activité sans heure précise (« soir »…) est signalé à part."""
import csv, os, re, json, datetime as dt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROG = os.path.join(ROOT, "programme"); SEM = os.path.join(ROOT, "semainier"); DUB = os.path.join(ROOT, "duberman")
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

def placer(x, d, a, b, d_fin=""):
    """Place l'activité x dans la grille (start/end) d'après sa date et ses heures ; signale le placement indicatif."""
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
        x["end"] = (dt.date.fromisoformat(d_fin or d) + dt.timedelta(days=1)).isoformat()
        x["extendedProps"]["placement"] = ("aucune heure dans la source : affiché en journée entière" if not d_fin else
                                           f"plage de dates dans le livre : affiché du {d} au {d_fin}")

# Duberman : précisions affichées dans la grille ; les autres (mois, saison, année…) vont dans le panneau latéral
DUB_GRILLE = {"jour"}
DUB_PLAGE_MAX = 14  # une « plage » de jours n'est mise dans la grille que si elle dure au plus 14 jours
DUB_LIB = {"mois": "au mois", "saison": "à la saison", "annee": "à l'année", "annee_scolaire": "à l'année scolaire",
           "plage": "sur une plage de dates", "plage_annees": "sur plusieurs années", "sans_date": "sans date"}

def duberman(evs, res):
    """Couche Duberman : (événements de la grille, événements imprécis pour le panneau, stats).
    Les doublons décidés dans 001_doublons_aam.csv ne sont pas repris : leur renvoi va dans la fiche AAM."""
    p = os.path.join(DUB, "evenements_duberman.csv")
    if not os.path.exists(p): return [], [], {}
    lignes = lire(p)
    dec = lire(os.path.join(DUB, "001_doublons_aam.csv")) if os.path.exists(os.path.join(DUB, "001_doublons_aam.csv")) else []
    par_ref = {f"{e['fichier_extraction']}:{e['ligne_extraction']}": e for e in lignes}
    aam = {}
    for e in evs: aam.setdefault((e["start"][:10], e["title"]), e)
    caches, renvois_dub = set(), {}
    for r in dec:
        if r["decision"] not in ("doublon", "possible"): continue
        e = par_ref.get(r["duberman_ref"]); a = aam.get((r["date"], r["aam_activite"]))
        if not e or e["activite"] != r["duberman_activite"] or not a:
            print(f"  attention : rapprochement introuvable {r['duberman_ref']} / {r['aam_activite'][:60]}"); continue
        lien = {"decision": r["decision"], "motif": r["motif"], "activite": e["activite"], "qui": e["qui"],
                "note": e["note"], "src": e["document_source"], "pct": int(e["part_deduite_pct"] or 0),
                "notes": e["notes_texte"]}
        a["extendedProps"].setdefault("dub", []).append(lien)
        if r["decision"] == "doublon": caches.add(r["duberman_ref"])
        else: renvois_dub.setdefault(r["duberman_ref"], []).append(
            {"motif": r["motif"], "activite": a["title"], "src": a["extendedProps"]["src"], "inv": a["extendedProps"]["inv"]})
    grille, panneau, st = [], [], {"total": len(lignes), "doublons": len(caches), "possibles": len(renvois_dub)}
    for i, e in enumerate(lignes):
        ref = f"{e['fichier_extraction']}:{e['ligne_extraction']}"
        if ref in caches or not e["date"]: 
            if not e["date"]: st["sans_date"] = st.get("sans_date", 0) + 1
            continue
        prec, d, f = e["precision"], e["date"], e["date_fin"]
        en_grille = prec in DUB_GRILLE or (prec == "plage" and re.fullmatch(r"\d{4}-\d{2}-\d{2}", f or "") and
                    (dt.date.fromisoformat(f) - dt.date.fromisoformat(d)).days <= DUB_PLAGE_MAX)
        qui = personnes(e["qui"]) or ["(non nommé)"]
        x = {"id": f"d{i}", "title": e["activite"], "resourceIds": qui,
             "extendedProps": {"type": e["type"], "qui": e["qui"], "lieu": e["lieu"], "note": e["note"],
                               "pct": int(e["part_deduite_pct"] or 0), "motifs": e["motifs_deduction"], "rec": False,
                               "src": e["document_source"], "inv": "", "url": "", "heure": e["debut"], "fin": e["fin"],
                               "duberman": True, "precision": prec, "date_livre": e["date_livre"], "categorie": e["categorie"],
                               "chapitre": e["chapitre"], "page": e["page"], "paragraphe": e["paragraphe"],
                               "notes": e["notes_texte"], "aam": renvois_dub.get(ref, [])}}
        if en_grille:
            placer(x, d, e["debut"].strip(), e["fin"].strip(), f if prec == "plage" else "")
            for q in qui:
                res.setdefault(q, 0); res[q] += 1
            grille.append(x)
        else:
            x["start"], x["fin_periode"] = d, f or d
            x["extendedProps"]["placement"] = f"date {DUB_LIB.get(prec, prec)} dans le livre : listé dans le panneau, pas dans la grille"
            panneau.append(x)
    st.update(grille=len(grille), panneau=len(panneau))
    return grille, panneau, st

SCEN_GRILLE = {"jour", "soir", "nuit", "apres-midi", "matin"}
SCEN_MOMENT = {"soir": "soir", "nuit": "soir", "apres-midi": "après-midi", "matin": "matin"}

def scenario():
    """Couche « Scénario » (scenario/NNN_evenements_scenario.csv, le plus récent, produit par scripts/integrer_scenario.py),
    écrite à part dans semainier/data_scenario.js. Les entrées fondues dans une fiche AAM ou Duberman n'y sont pas en
    double : elles deviennent des renvois, appliqués par la page."""
    d = os.path.join(ROOT, "scenario")
    fs = sorted(f for f in os.listdir(d) if re.fullmatch(r"\d{3}_evenements_scenario\.csv", f)) if os.path.isdir(d) else []
    if not fs: return None
    lignes = lire(os.path.join(d, fs[-1]))
    grille, panneau, renvois, res = [], [], {}, {}
    for e in lignes:
        lien = {"id": e["id"], "activite": e["activite"], "src": e["document_source"], "pct": int(e["part_deduite_pct"]),
                "certitude": e["certitude"], "date": e["date_scenario"]}
        if e["fondu_dans"]:
            base, i = e["fondu_dans"].split(":")
            renvois.setdefault(("" if base == "AAM" else "d") + i, []).append(dict(lien, decision="même fait"))
            continue
        if e["semainier"] != "oui": continue
        qui = personnes(e["qui"]) or ["(non nommé)"]
        x = {"id": "s" + e["id"], "title": e["activite"], "resourceIds": qui,
             "extendedProps": {"type": e["type"] if e["type"] != "scene" else "social", "qui": e["qui"], "lieu": e["lieu"],
                               "note": e["note"], "pct": int(e["part_deduite_pct"]), "motifs": e["motifs_deduction"], "rec": False,
                               "src": e["document_source"], "inv": "", "url": "", "heure": SCEN_MOMENT.get(e["precision"], ""), "fin": "",
                               "scenario": True, "categorie": e["categorie"], "certitude": e["certitude"],
                               "precision": e["precision"], "date_scen": e["date_scenario"], "versions": e["autres_versions"],
                               "recoupement": e["recoupement"]}}
        dur = (dt.date.fromisoformat(e["date_fin"] or e["date"]) - dt.date.fromisoformat(e["date"])).days
        if e["precision"] in SCEN_GRILLE or (e["precision"] in ("plage", "semaine") and dur <= 14):
            placer(x, e["date"], SCEN_MOMENT.get(e["precision"], ""), "", e["date_fin"] if e["precision"] in ("plage", "semaine") else "")
            for q in qui: res[q] = res.get(q, 0) + 1
            grille.append(x)
        else:
            x["start"], x["fin_periode"] = e["date"], e["date_fin"] or e["date"]
            x["extendedProps"]["placement"] = f"date « {e['precision']} » dans le scénario : listé dans le panneau, pas dans la grille"
            panneau.append(x)
    # rapprochements « même jour, même personne » : renvoi possible des deux côtés
    rp = sorted(f for f in os.listdir(d) if re.fullmatch(r"\d{3}_recoupements_scenario\.csv", f))
    if rp:
        for r in lire(os.path.join(d, rp[-1])):
            if r["decision"] != "même jour, même personne": continue
            cle = ("" if r["base"] == "AAM" else "d") + r["ligne_base"]
            renvois.setdefault(cle, []).append({"id": r["scenario_id"], "activite": r["scenario"], "src": "", "pct": None,
                                                "certitude": "", "date": r["date"], "decision": "même jour, même personne"})
    return {"fichier": fs[-1], "grille": grille, "panneau": panneau, "renvois": renvois, "personnes": res}

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

    pdx = os.path.join(DUB, "documents_extra_duberman.csv"); ndx = 0
    if os.path.exists(pdx):
        for i, p in enumerate(lire(pdx)):
            if not p.get("date"): continue
            ndx += 1
            docs[f"dub-{i}"] = {"inv": p.get("inventaire") or "", "titre": p["titre"], "url": p.get("url", ""),
                                "categorie": p.get("type", "document"), "date": p["date"], "date_musee": "",
                                "datation": p.get("datation") or "", "img": p.get("image", ""),
                                "nimg": 1 if p.get("image") else 0, "kind": "extra", "origine": "duberman",
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
        placer(x, d, a, b)
        evs.append(x)

    dub, dub_panneau, dst = duberman(evs, res)

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
    data = {"genere": dt.date.today().isoformat(), "events": evs, "duberman": dub, "duberman_panneau": dub_panneau, "resources": resources, "spec": spec, "audit": audit,
            "documents": sorted(docs.values(), key=lambda d: d["date"] or "9999"),
            "periodes": periodes, "cours": cours}
    os.makedirs(SEM, exist_ok=True)
    sc = scenario()
    if sc:
        with open(os.path.join(SEM, "data_scenario.js"), "w", encoding="utf-8") as f:
            f.write("// généré par scripts/export_semainier.py depuis scenario/" + sc["fichier"] + " — ne pas éditer à la main\n")
            f.write("window.BMC_SCEN = " + json.dumps(sc, ensure_ascii=False, separators=(",", ":")) + ";\n")
        print(f"semainier/data_scenario.js : {len(sc['grille'])} entrées du scénario dans la grille, {len(sc['panneau'])} au panneau, "
              f"{sum(len(v) for v in sc['renvois'].values())} renvois vers {len(sc['renvois'])} fiches AAM ou Duberman")
    with open(os.path.join(SEM, "data.js"), "w", encoding="utf-8") as f:
        f.write("// généré par scripts/export_semainier.py — ne pas éditer à la main\n")
        f.write("window.BMC = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n")
    nd = sum(1 for d in docs.values() if d["date"])
    if dst:
        print(f"Duberman : {dst['total']} événements → {dst['grille']} dans la grille, {dst['panneau']} au panneau (date imprécise), "
              f"{dst['doublons']} doublons fondus dans la ligne AAM, {dst['possibles']} avec renvoi AAM, {dst.get('sans_date', 0)} sans date ; "
              f"{ndx} documents datés cités dans les notes")
    print(f"semainier/data.js : {len(evs)} activités attestées + couche spéculative ({len(spec)} années, environ {nspec} entrées développées), {len(res)} personnes/groupes, "
          f"{len(docs)} documents ({nd} datés au jour), {len(periodes)} périodes, {len(cours)} cours")

if __name__ == "__main__":
    main()
