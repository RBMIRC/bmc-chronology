"""Scénario BMC (bmc-scenario/sortie/NNN_bmc_scenario_1933-1957.json.gz) → semainier, avec recoupements.

Le scénario est une extraction AUTOMATIQUE (modèle de langage, pipeline bmc-scenario 04-07) de 60 livres :
il n'a pas été relu. Ce script en garde les événements et les scènes datés entre le 1er septembre 1933 et le
31 décembre 1957, les met au format du semainier avec une part déduite (barème ci-dessous), puis les confronte :
  - au programme attesté AAM (programme/evenements.csv) ;
  - au dépouillement de Duberman (duberman/evenements_duberman.csv) ;
  - à la liste des cours AAM (programme/cours_par_periode.csv) pour les fiches « cours » du scénario.
Il ne modifie rien d'existant. Sorties (dans scenario/, numérotées, jamais écrasées : un nouveau numéro à chaque
version) :
  NNN_evenements_scenario.csv     une ligne par événement ou scène retenu
  NNN_recoupements_scenario.csv   même jour + personne commune (AAM, Duberman), avec décision automatique
  NNN_divergences_scenario.csv    même fait probable à des dates différentes (scénario contre Duberman)
  NNN_cours_scenario.csv          fiches « cours » du scénario rapprochées des cours AAM
  NNN_rapport_scenario.md         chiffres, barème, contrôles
Option --numero NNN : écrire sous ce numéro (sinon le suivant libre).

Barème (additif, plafond 90 %, comme scripts/deduction.py) :
  extraction automatique par modèle de langage, non relue ............................ +10
  certitude : atteste 0 · temoignage_direct +10 (souvenir publié) · interpretation_auteur +15 ·
              oui_dire +25 · conteste +25 · hypothese +25
  date : jour 0 · semaine +10 · mois, saison, session, année, période +25
  date tirée du cadre du passage et non du fait (ancrage.deduit) ......................... +25
"""
import csv, gzip, json, os, re, sys, glob, collections, unicodedata, datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))     # bmc-programmes-aam/
DEPOT = os.path.dirname(ROOT)
SORTIE = os.path.join(ROOT, "scenario")
DEBUT, FIN = "1933-09-01", "1957-12-31"

CERT = {"atteste": (0, ""), "temoignage_direct": (10, "témoignage direct (souvenir publié, souvent tardif)"),
        "interpretation_auteur": (15, "interprétation de l'auteur du livre"), "oui_dire": (25, "ouï-dire"),
        "conteste": (25, "fait contesté entre les sources"), "hypothese": (25, "hypothèse de l'auteur")}
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
MOMENT = {"soir": "soir", "nuit": "soir", "apres-midi": "après-midi", "matin": "matin"}
MOTS_VIDES = set("""dans pour avec sans sous chez vers entre après avant depuis pendant contre leur leurs elle elles
ils lui sont sont était être avoir fait faire font plus moins très tout tous toute toutes dont mais donc comme
aussi encore même cette ces celui celle ceux deux trois quatre premier première dernier dernière black mountain
college collège the and with from that this which their when were have been lettre letter réunion meeting""".split())


def norm(s):
    s = unicodedata.normalize("NFKD", (s or "").lower())
    return re.sub(r"[^a-z0-9]+", " ", "".join(c for c in s if not unicodedata.combining(c))).strip()


def mots(s):
    return {w for w in norm(s).split() if len(w) > 3 and w not in MOTS_VIDES and not w.isdigit()}


def noms(personnes):
    """noms de famille normalisés (dernier mot), sans les groupes."""
    out = set()
    for p in personnes or []:
        p = re.sub(r"\(.*?\)", "", p or "").strip()
        if not p or p[0].islower(): continue            # « communauté », « gardien de… »
        n = norm(p).split()
        if n and len(n[-1]) > 2: out.add(n[-1])
    return out


def precision_reelle(date, prec):
    """La précision déclarée n'est pas toujours celle de la date : on suit la date."""
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", date or ""): return prec if prec in ("jour", "soir", "nuit", "apres-midi", "matin") else "jour"
    if re.fullmatch(r"\d{4}-\d{2}", date or ""): return "mois" if prec in ("jour", "mois") else prec
    if re.fullmatch(r"\d{4}", date or ""): return "annee" if prec in ("jour", "mois", "annee") else prec
    return "inconnue"


def bornes(x):
    """(début, fin) ISO complets d'après l'ancrage (ou la date)."""
    a = x.get("ancrage") or {}
    d0, d1 = a.get("debut") or x.get("date") or "", a.get("fin") or x.get("date_fin") or x.get("date") or ""
    def comp(s, fin):
        s = (s or "").strip()
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s): return s
        if re.fullmatch(r"\d{4}-\d{2}", s):
            y, m = map(int, s.split("-"))
            if not 1 <= m <= 12: return ""
            if not fin: return f"{s}-01"
            nxt = dt.date(y + (m == 12), m % 12 + 1, 1) - dt.timedelta(1); return nxt.isoformat()
        if re.fullmatch(r"\d{4}", s): return f"{s}-12-31" if fin else f"{s}-01-01"
        return ""
    a0, a1 = comp(d0, False), comp(d1, True)
    if a0 and (not a1 or a1 < a0): a1 = a0 if len(d0) == 10 else comp(d0, True)
    return a0, a1


def certitude(c):
    """graphies fautives de l'extraction (« tmoignage_direct », « t?moignage_direct »)."""
    c = (c or "").strip()
    return "temoignage_direct" if re.fullmatch(r"t.?.?moignage_direct", c) else c


CORRESP = re.compile(r"\blettre|\bréponse|\bletter|^[A-ZÉ][\w.’' -]+ (à|aux?) [A-ZÉ]|\btélégramme|\bcorrespondance", re.I)
DUREE_MAX = 400   # jours : au-delà, l'entrée n'est pas reportée dans le semainier (reste dans le CSV)


def part(x, prec):
    pts, mot = 10, ["extraction automatique par modèle de langage, non relue (+10)"]
    p, m = CERT.get(certitude(x.get("certitude")), (25, f"certitude non reconnue « {x.get('certitude')} »"))
    if p: pts += p; mot.append(f"{m} (+{p})")
    if prec == "semaine": pts += 10; mot.append("date à la semaine (+10)")
    elif prec not in ("jour", "soir", "nuit", "apres-midi", "matin"): pts += 25; mot.append(f"date {prec} seulement (+25)")
    if (x.get("ancrage") or {}).get("deduit"): pts += 25; mot.append("date tirée du cadre du passage, pas du fait (+25)")
    return min(pts, 90), " ; ".join(mot)


def src_txt(x):
    out = []
    for s in x.get("sources") or []:
        pg = ", ".join(str(p).replace("p. ", "") for p in s.get("pages") or [])
        out.append(f"{s.get('titre') or s.get('source')}" + (f", p. {pg}" if pg else ""))
    return " ; ".join(out)


def detail(x):
    for k in x:
        if k.startswith("details_conc") and x[k]: return x[k]
    return ""


def lire(p):
    with open(p, encoding="utf-8") as f: return list(csv.DictReader(f))


def ecrire(p, cols, rows):
    with open(p, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(rows)


def main():
    fichiers = sorted(glob.glob(os.path.join(DEPOT, "bmc-scenario", "sortie", "[0-9][0-9][0-9]_bmc_scenario_*.json*")))
    if not fichiers: sys.exit("aucun scénario dans bmc-scenario/sortie/")
    src = fichiers[-1]
    op = gzip.open if src.endswith(".gz") else open
    S = json.load(op(src, "rt", encoding="utf-8"))
    F = S["fiches"]
    os.makedirs(SORTIE, exist_ok=True)
    if "--numero" in sys.argv: num = sys.argv[sys.argv.index("--numero") + 1]
    else:
        pris = [int(m.group(1)) for fn in os.listdir(SORTIE) if (m := re.match(r"(\d{3})_", fn))]
        num = f"{max(pris, default=0) + 1:03d}"
    if glob.glob(os.path.join(SORTIE, f"{num}_*")): sys.exit(f"le numéro {num} existe déjà : rien n'est écrasé")

    # ---------------------------------------------------------------- événements et scènes 1933-1957
    lignes = []
    for cat, liste in (("evenement", F["evenements"]), ("scene", F["scenes"])):
        for x in liste:
            d0, d1 = bornes(x)
            if not d0 or d1 < DEBUT or d0 > FIN: continue
            prec = precision_reelle(x.get("date") or (x.get("ancrage") or {}).get("debut"), x.get("precision") or "")
            if prec in ("jour", "soir", "nuit", "apres-midi", "matin") and len(d0) == 10 and d0 != d1 and (
                    dt.date.fromisoformat(d1) - dt.date.fromisoformat(d0)).days > 0:
                prec = "plage"
            pct, mot = part(x, "jour" if prec == "plage" else prec)
            if prec == "plage":
                n = (dt.date.fromisoformat(d1) - dt.date.fromisoformat(d0)).days
                if n > 6: pct = min(90, pct + 10); mot += f" ; plage de {n + 1} jours (+10)"
            pers = x.get("personnes") or x.get("personnages") or []
            if cat == "scene":
                desc = " ".join(t for t in (x.get("deroule"), ("Paroles : " + x["paroles_rapportees"]) if x.get("paroles_rapportees") else "",
                                            ("Atmosphère : " + x["atmosphere"]) if x.get("atmosphere") else "",
                                            ("Enjeu : " + x["enjeu_dramatique"]) if x.get("enjeu_dramatique") else "") if t)
            else:
                desc = " ".join(t for t in (x.get("description"), detail(x), ("Conséquences : " + x["consequences"]) if x.get("consequences") else "") if t)
            av = x.get("autres_versions")
            lignes.append({
                "id": x["id"], "categorie": cat, "date": d0, "date_fin": d1 if d1 != d0 else "",
                "jour": JOURS[dt.date.fromisoformat(d0).weekday()] if prec in ("jour", "soir", "nuit", "apres-midi", "matin") else "",
                "debut": MOMENT.get(prec, ""), "precision": prec, "type": "scene" if cat == "scene" else "autre",
                "activite": x.get("titre") or "", "qui": "; ".join(p for p in pers if p), "lieu": x.get("lieu") or "",
                "note": desc, "certitude": certitude(x.get("certitude")),
                "semainier": "oui" if (dt.date.fromisoformat(d1) - dt.date.fromisoformat(d0)).days <= DUREE_MAX else "non (plus de 13 mois)", "part_deduite_pct": pct, "motifs_deduction": mot,
                "document_source": src_txt(x), "sources_ids": " ".join(sorted({s.get("source", "") for s in x.get("sources") or []})),
                "autres_versions": json.dumps(av, ensure_ascii=False) if av else "",
                "date_scenario": (x.get("date") or "") + (f" → {x['date_fin']}" if x.get("date_fin") else ""),
                "recoupement": "", "renvoi_duberman": "", "fondu_dans": ""})
    lignes.sort(key=lambda e: (e["date"], e["id"]))

    # ---------------------------------------------------------------- recoupements le même jour
    aam = lire(os.path.join(ROOT, "programme", "evenements.csv"))
    dub = lire(os.path.join(ROOT, "duberman", "evenements_duberman.csv"))
    par_jour = collections.defaultdict(list)
    for i, a in enumerate(aam): par_jour[a["date"]].append(("AAM", i, a))
    for i, e in enumerate(dub):
        if e["precision"] == "jour": par_jour[e["date"]].append(("Duberman", i, e))
    rec = []
    for e in lignes:
        if e["precision"] not in ("jour", "soir", "nuit", "apres-midi", "matin"): continue
        ne = noms(e["qui"].split("; ")) | {w for w in norm(e["activite"]).split() if len(w) > 3}
        me = mots(e["activite"] + " " + e["lieu"])
        for base, i, a in par_jour.get(e["date"], []):
            na = noms(a["qui"].split(";")) | set(norm(a["activite"]).split())
            communs = sorted(noms(e["qui"].split("; ")) & na) or sorted(n for n in noms(a["qui"].split(";")) if n in ne)
            if not communs: continue
            ma = mots(a["activite"] + " " + a.get("lieu", ""))
            tous_noms = noms(e["qui"].split("; ")) | noms(a["qui"].split(";")) | set(communs)
            m_com = sorted((me & ma) - tous_noms)
            meme_livre = base == "Duberman" and "006" in e["sources_ids"].split()
            if meme_livre and m_com: decision = "même fait (Duberman, même livre)"
            elif m_com: decision = "même fait probable"
            else: decision = "même jour, même personne"
            rec.append({"date": e["date"], "scenario_id": e["id"], "scenario": e["activite"][:200], "base": base,
                        "ligne_base": i, "base_activite": a["activite"][:200], "noms_communs": " ; ".join(communs),
                        "mots_communs": " ; ".join(m_com[:8]), "decision": decision,
                        "base_source": (a["document_source"] or "")[:200]})
    # décision par élément du scénario : fondre dans Duberman si « même livre » ; renvoi sinon
    for e in lignes:
        r = [x for x in rec if x["scenario_id"] == e["id"]]
        mf = [x for x in r if x["decision"] == "même fait (Duberman, même livre)"]
        ma = [x for x in r if x["decision"] == "même fait probable" and x["base"] == "AAM"]
        md = [x for x in r if x["decision"] == "même fait probable" and x["base"] == "Duberman"]
        # fusion : l'entrée du scénario n'est pas dédoublée ; elle devient un renvoi dans la fiche AAM ou Duberman
        if ma: e["fondu_dans"] = f"AAM:{ma[0]['ligne_base']}"
        elif mf or md: e["fondu_dans"] = f"Duberman:{(mf or md)[0]['ligne_base']}"
        if mf:
            e["renvoi_duberman"] = f"{mf[0]['ligne_base']}"
        e["recoupement"] = " || ".join(f"{x['base']} : {x['decision']} — {x['base_activite'][:90]}" for x in r[:4])

    # ---------------------------------------------------------------- divergences de date (scénario / Duberman)
    div = []
    dub_mots = [(i, d, mots(d["activite"]), noms(d["qui"].split(";"))) for i, d in enumerate(dub) if d["date"]]
    for e in lignes:
        if e["precision"] not in ("jour", "mois"): continue
        me, ne = mots(e["activite"]), noms(e["qui"].split("; "))
        if len(me) < 3 or not ne or CORRESP.search(e["activite"]): continue
        for i, d, md, nd in dub_mots:
            if not (ne & nd) or CORRESP.search(d["activite"]): continue
            m2, d2 = me - ne - nd, md - ne - nd          # mots du titre, hors noms de personnes
            if len(m2 & d2) < 2: continue
            j = len(m2 & d2) / len(m2 | d2)
            if j < 0.4: continue
            # dates compatibles ? (le jour du scénario tombe dans la période Duberman, ou l'inverse)
            fin_d = d["date_fin"] or d["date"]
            if d["date"] <= e["date"] <= fin_d or (e["date"] <= d["date"] <= (e["date_fin"] or e["date"])): continue
            if e["precision"] == "mois" and e["date"][:7] == d["date"][:7]: continue
            ecart = (dt.date.fromisoformat(e["date"]) - dt.date.fromisoformat(d["date"])).days
            if abs(ecart) > 800: continue
            div.append({"scenario_id": e["id"], "scenario_date": e["date_scenario"], "scenario": e["activite"][:160],
                        "scenario_source": e["document_source"][:120], "duberman_date": d["date_livre"],
                        "duberman": d["activite"][:160], "duberman_source": f"ch. {d['chapitre']}, p. {d['page']} ({d['paragraphe']})",
                        "ecart_jours": ecart, "similarite": round(j, 2), "noms_communs": " ; ".join(sorted(ne & nd))})
    div.sort(key=lambda x: (-x["similarite"], x["scenario_date"]))

    # ---------------------------------------------------------------- cours : scénario contre cours AAM
    cours_aam = lire(os.path.join(ROOT, "programme", "cours_par_periode.csv"))
    par_ens = collections.defaultdict(list)
    for c in cours_aam:
        for n in noms(c["enseignant"].split(";")): par_ens[n].append(c)
    cr = []
    for c in F["cours"]:
        if c.get("atteste_a_bmc") == "non": continue
        ns = noms([c.get("enseignant") or ""])
        a = (c.get("ancrage") or {}).get("debut") or ""
        y = int(a[:4]) if a[:4].isdigit() else None
        cands = [k for n in ns for k in par_ens.get(n, [])]
        def proche(k):
            ys = [int(v) for v in re.findall(r"19\d\d", k["periode"])]
            return y is not None and ys and min(abs(v - y) for v in ys) <= 1
        meme_ens_annee = [k for k in cands if proche(k)]
        mc = mots(c.get("intitule") or "")
        titre = [k for k in meme_ens_annee if mc & mots(k["cours"])]
        statut = ("titre et enseignant dans l'AAM" if titre else "enseignant enseignant à BMC cette année-là (AAM), titre absent"
                  if meme_ens_annee else "enseignant connu de l'AAM, pas cette année-là" if cands else "absent de l'AAM")
        best = (titre or meme_ens_annee or cands or [{}])[0]
        cr.append({"id": c["id"], "enseignant": c.get("enseignant", ""), "intitule": c.get("intitule", ""), "periode": c.get("periode", ""),
                   "atteste_a_bmc": c.get("atteste_a_bmc", ""), "statut": statut, "aam_cours": best.get("cours", "")[:160],
                   "aam_periode": best.get("periode", ""), "aam_inventaire": best.get("inventaire", ""),
                   "objectifs": (c.get("objectifs") or "")[:400], "deroule": (c.get("deroule_seance") or "")[:400],
                   "source": src_txt(c)})

    # ---------------------------------------------------------------- écriture
    base = os.path.join(SORTIE, num)
    cols = ["id", "categorie", "date", "date_fin", "jour", "debut", "precision", "type", "activite", "qui", "lieu", "note",
            "certitude", "part_deduite_pct", "motifs_deduction", "document_source", "sources_ids", "autres_versions",
            "date_scenario", "recoupement", "renvoi_duberman", "fondu_dans", "semainier"]
    ecrire(f"{base}_evenements_scenario.csv", cols, lignes)
    ecrire(f"{base}_recoupements_scenario.csv", list(rec[0].keys()) if rec else ["date"], rec)
    ecrire(f"{base}_divergences_scenario.csv", list(div[0].keys()) if div else ["scenario_id"], div)
    ecrire(f"{base}_cours_scenario.csv", list(cr[0].keys()), cr)

    C = collections.Counter
    jour = [e for e in lignes if e["precision"] in ("jour", "soir", "nuit", "apres-midi", "matin")]
    R = [f"# Scénario BMC → semainier : rapport ({num})", "",
         f"Source : `{os.path.relpath(src, DEPOT)}` (assemblé le {S['meta'].get('assemble_le', '?')}). "
         "Extraction **automatique** de 60 livres par modèle de langage, non relue : chaque entrée garde son livre et ses pages, "
         "et sa part déduite commence à 10 %.", "",
         "## Barème", "", "| motif | points |", "|---|---|", "| extraction automatique, non relue | +10 |",
         "| témoignage direct | +10 |", "| interprétation de l'auteur | +15 |", "| ouï-dire, contesté, hypothèse | +25 |",
         "| date à la semaine | +10 |", "| date au mois, à la saison, à la session, à l'année | +25 |",
         "| date tirée du cadre du passage | +25 |", "| plage de plus d'une semaine | +10 |", "", "Plafond 90 %.", "",
         "## Retenu (1er septembre 1933 – 31 décembre 1957)", "",
         f"- {len(lignes)} entrées : {C(e['categorie'] for e in lignes)['evenement']} événements, {C(e['categorie'] for e in lignes)['scene']} scènes.",
         f"- Précision : " + ", ".join(f"{k} {v}" for k, v in C(e['precision'] for e in lignes).most_common()) + ".",
         f"- Certitude : " + ", ".join(f"{k} {v}" for k, v in C(e['certitude'] for e in lignes).most_common()) + ".",
         f"- Part déduite moyenne : {sum(e['part_deduite_pct'] for e in lignes) / max(1, len(lignes)):.1f} % ; datées au jour : {len(jour)}.",
         f"- Principales sources : " + ", ".join(f"{k} {v}" for k, v in C(s.strip().split(', p.')[0] for e in lignes for s in e['document_source'].split(' ; ') if s).most_common(12)) + ".",
         "", "## Recoupements le même jour", "",
         f"- {len(rec)} rapprochements (même jour + nom commun) : " + ", ".join(f"{k} {v}" for k, v in C((r['base'], r['decision']) for r in rec).most_common()) + ".",
         f"- Entrées du scénario datées au jour avec au moins un rapprochement : {sum(1 for e in jour if e['recoupement'])} sur {len(jour)} ; "
         f"fondues dans une fiche existante (pas de doublon dans le semainier) : AAM {sum(1 for e in lignes if e['fondu_dans'].startswith('AAM'))}, "
         f"Duberman {sum(1 for e in lignes if e['fondu_dans'].startswith('Duberman'))}.",
         f"- Reportées dans le semainier (durée ≤ 13 mois, non fondues) : {sum(1 for e in lignes if e['semainier'] == 'oui' and not e['fondu_dans'])} ; "
         f"écartées car trop longues : {sum(1 for e in lignes if e['semainier'] != 'oui')}.",
         "", "## Divergences de date avec Duberman", "",
         f"{len(div)} cas où un fait probablement identique (nom commun, titres proches) est daté autrement (écart ≤ 800 jours). "
         "À trancher à la main ; l'ordre de confiance du projet est : document daté attesté > Duberman corrigé > scénario.", ""]
    R += [f"- scénario {x['scenario_date']} « {x['scenario']} » ({x['scenario_source']}) / Duberman {x['duberman_date']} « {x['duberman']} » ({x['duberman_source']}) — écart {x['ecart_jours']} j" for x in div[:40]]
    if len(div) > 40: R.append(f"- … {len(div) - 40} autres dans `{num}_divergences_scenario.csv`.")
    R += ["", "## Cours du scénario contre cours AAM", "",
          f"{len(cr)} fiches « cours » à BMC (oui ou incertain) : " + ", ".join(f"{k} {v}" for k, v in C(x['statut'] for x in cr).most_common()) + ".",
          "Les fiches « absent de l'AAM » ou « titre absent » sont des pistes : cours connus par les témoignages ou les livres, que les fiches du musée ne donnent pas."]
    open(f"{base}_rapport_scenario.md", "w", encoding="utf-8").write("\n".join(R) + "\n")
    print("\n".join(R[:40]))


if __name__ == "__main__":
    main()
