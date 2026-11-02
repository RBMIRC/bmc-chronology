"""Chronos 3/5 : farm_events.json — David Silver, The Farm at Black Mountain College (2024), extraction automatique
(GPT-4o Vision, décembre 2025) du scan farm_low.pdf, deux pages à la fois.

Les « source_pages » sont des pages du PDF (1 = première image). DATA_BMC/_correction_farm/ donne l'OCR de chaque page
(pages.json) et la page du livre correspondante (pagemap.json) : chaque entrée cite donc « Silver 2024, p. X-Y » et
est vérifiée dans le texte de ses deux pages (témoins réunis dans un même passage, méthode de verifier_sources.py).
Dates : écrites AAAA-MM-01 ou AAAA-01-01 même quand l'extraction déclare « month » ou « year » : la précision déclarée
est respectée (pas de faux jour) ; un « day » au 1er janvier est traité comme une année (date de remplissage probable).
Recoupement avec l'AAM et Duberman (même jour ou mois et personne commune ; sinon présence dans la période).
Couche « Chronos » : événements et documents datés du 1er septembre 1933 au 31 décembre 1957, non confirmés, ≤ 13 mois.
Sorties : chronos/NNN_ferme_recoupement.csv, _couche.csv, _rapport.md.
"""
import csv, json, os, re, sys, collections, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chronos_commun as K
import verifier_sources as V

TYPE = {"farm": "travail", "construction": "travail", "meeting": "reunion", "hiring": "autre", "financial": "autre",
        "education": "cours", "interview": "autre", "purchase": "autre", "resignation": "autre", "other": "autre"}
CORR = os.path.join(K.DEPOT, "DATA_BMC", "_correction_farm")


def lire(p):
    with open(p, encoding="utf-8") as f: return list(csv.DictReader(f))


def date_ferme(s, prec):
    """respecte la précision déclarée par l'extraction."""
    s = (s or "").strip()
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        y, mo, j = map(int, m.groups())
        if prec == "year" or (mo == 1 and j == 1 and prec != "month"):
            return f"{y}-01-01", f"{y}-12-31", "annee", prec == "day"
        if prec in ("month", "approximate") and j == 1:
            return f"{y}-{mo:02d}-01", K.fin_mois(y, mo).isoformat(), "mois", False
    d = K.lire_date(s)
    return (d[0], d[1], d[2], False) if d else None


def main():
    F = json.load(open(os.path.join(K.CHRONOS, "farm_events.json"), encoding="utf-8"))
    pages = {p["n"]: " ".join(e.get("text", "") for e in p.get("el") or []) for p in json.load(open(os.path.join(CORR, "pages.json"), encoding="utf-8"))}
    pagemap = json.load(open(os.path.join(CORR, "pagemap.json"), encoding="utf-8"))
    def texte_et_ref(sp):
        ns = [int(x) for x in re.findall(r"\d+", sp or "")]
        if not ns: return "", ""
        idx = [f"{n - 1:03d}" for n in range(ns[0], (ns[-1] if len(ns) > 1 else ns[0]) + 1)]
        livre = [pagemap.get(i) for i in idx if pagemap.get(i)]
        ref = (f"p. {livre[0]}" + (f"-{livre[-1]}" if livre[-1] != livre[0] else "")) if livre else f"pages {sp} du scan"
        return " ".join(pages.get(i, "") for i in idx), ref
    aam = lire(os.path.join(K.ROOT, "programme", "evenements.csv"))
    dub = lire(os.path.join(K.ROOT, "duberman", "evenements_duberman.csv"))
    par_nom = collections.defaultdict(list)
    for base, L in (("AAM", aam), ("Duberman", [e for e in dub if e["precision"] == "jour"])):
        for e in L:
            for n in K.noms_famille(e["qui"].split(";")): par_nom[n].append((e["date"], base, e["activite"]))
    V.rarete([V.plat(t) for t in pages.values()] + [V.plat(t) for t in V.textes_duberman().values()])

    entrees = []
    for k, e in enumerate(F["events"]):
        entrees.append(("événement", k, e.get("date"), e.get("date_precision"), e.get("event") or "", e.get("people") or [],
                        e.get("category", ""), e.get("source_pages", ""), ""))
    for k, d in enumerate(F["documents"]):
        if not d.get("date_normalized"): continue
        titre = f"Document ({d.get('type', '')}) : {d.get('subject') or ''}"
        if d.get("author") and d["author"] != "Not specified": titre += f" — {d['author']}" + (f" à {d['recipient']}" if d.get("recipient") and d["recipient"] != "Not specified" else "")
        entrees.append(("document", k, d.get("date_normalized"), "day" if re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(d.get("date") or "")) else "approximate",
                        titre, d.get("people_mentioned") or [], d.get("type", ""), d.get("source_pages", ""), d.get("content_summary") or ""))
    lignes = []
    for genre, k, date, prec, quoi, pers, cat, sp, resume in entrees:
        d = date_ferme(date, prec)
        texte, ref = texte_et_ref(sp)
        pers = [p for p in pers if isinstance(p, str)]
        if texte:
            noms, mots = V.temoins("; ".join(pers), quoi, True)
            occ = V.occurrences(V.plat(texte), {**{"n:" + a: b for a, b in noms.items()}, **{"m:" + a: b for a, b in mots.items()}})
            win = V.meilleur_passage(occ, {a: (3 if a.startswith("n:") else 1) for a in occ})
            g = lambda pr: {a[2:]: b for a, b in win.items() if a.startswith(pr)}
            verif = V.statut(noms, mots, g("n:"), g("m:"))
            ex = V.extrait(texte, {**{"n" + a: b for a, b in g("n:").items()}, **{"m" + a: b for a, b in g("m:").items()}})
        else: verif, ex = "texte introuvable", ""
        statut, avec = "", ""
        if not d: statut = "date illisible"
        else:
            hits = [(x, b, a) for n in K.noms_famille(pers) for (x, b, a) in par_nom.get(n, []) if d[0] <= x <= d[1]]
            mq = {w for w in re.findall(r"[a-z]{5,}", V.plat(quoi)) if w not in V.VIDES} - K.noms_famille(pers) - {w for p in pers for w in re.findall(r"[a-z]+", V.plat(p))} - {"board", "fellows", "college", "black", "mountain", "faculty"}
            commun = lambda h: len(mq & set(re.findall(r"[a-z]{4,}", V.plat(h[2]))))
            precis = sorted([h for h in hits if commun(h)], key=lambda h: -commun(h))
            if d[2] in ("jour", "plage", "mois") and precis:
                hits = precis; statut, avec = f"confirmé ({hits[0][1]})", f"{hits[0][0]} « {hits[0][2][:100]} »"
            elif hits: statut, avec = f"présence attestée ({', '.join(sorted({h[1] for h in hits}))})", f"{len(hits)} activité(s), du {min(h[0] for h in hits)} au {max(h[0] for h in hits)}"
            else: statut = "non confirmé"
        lignes.append({"id": f"{genre[0]}{k}", "genre": genre, "date_silver": date or "", "precision_declaree": prec or "",
                       "debut": d[0] if d else "", "fin": d[1] if d else "", "precision": d[2] if d else "",
                       "jour_douteux": "oui" if d and d[3] else "", "evenement": quoi[:300], "personnes": "; ".join(pers),
                       "categorie": cat, "pages_scan": sp, "pages_livre": ref, "verif": verif, "statut": statut,
                       "recoupement": avec, "_extrait": ex, "_resume": resume})

    num = K.prochain_numero(K.SORTIE)
    base = os.path.join(K.SORTIE, f"{num}_ferme")
    with open(base + "_recoupement.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[c for c in lignes[0] if not c.startswith("_")], extrasaction="ignore"); w.writeheader(); w.writerows(lignes)
    couche = []
    for l in lignes:
        if not l["debut"] or l["statut"].startswith("confirmé"): continue
        if l["fin"] < "1933-09-01" or l["debut"] > "1957-12-31": continue
        if (dt.date.fromisoformat(l["fin"]) - dt.date.fromisoformat(l["debut"])).days > 400: continue
        pct, mot = 10, ["extraction automatique (GPT-4o Vision sur le scan, décembre 2025), non relue (+10)"]
        if l["precision"] not in ("jour", "plage"): pct += 25; mot.append(f"date « {l['precision']} » seulement (+25)")
        if l["jour_douteux"]: mot.append("« day » au 1er janvier traité comme une année")
        if l["verif"] != "retrouvé": pct += 15; mot.append(f"témoins non réunis dans les pages citées : {l['verif']} (+15)")
        couche.append({"id": f"cf{num}-{l['id']}", "source_chronos": "Ferme (Silver 2024)", "date": l["debut"],
                       "date_fin": l["fin"] if l["fin"] != l["debut"] else "", "precision": l["precision"],
                       "type": "autre" if l["genre"] == "document" else TYPE.get(l["categorie"], "autre"),
                       "activite": l["evenement"], "qui": l["personnes"], "lieu": "",
                       "note": (l["_resume"] + " " if l["_resume"] else "") + (f"{l['statut']} : {l['recoupement']}" if l["recoupement"] else ""),
                       "part_deduite_pct": min(pct, 90), "motifs_deduction": " ; ".join(mot),
                       "document_source": f"David Silver, The Farm at Black Mountain College (Black Mountain College Museum + Arts Center / Atelier Editions, 2024), {l['pages_livre']} (scan farm_low.pdf, pages {l['pages_scan']})",
                       "inventaire": "", "url_source": "", "statut": l["statut"], "verif_statut": l["verif"],
                       "verif_extrait": l["_extrait"], "date_source": f"{l['date_silver']} ({l['precision_declaree']})"})
    with open(base + "_couche.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(couche[0].keys())); w.writeheader(); w.writerows(couche)
    N = collections.Counter
    R = [f"# Chronos 3/5 : farm_events.json — Silver, The Farm at Black Mountain College ({num})", "",
         f"Source : `DATA_BMC/Chronos/farm_events.json` ({F.get('analysis_method', '')}, {F.get('extraction_date', '')[:10]}) : "
         f"{len(F['events'])} événements, {len(F['documents'])} documents dont {sum(1 for l in lignes if l['genre'] == 'document')} datés. "
         "Texte de vérification : OCR des pages du scan (`DATA_BMC/_correction_farm/pages.json`), pages du livre d'après `pagemap.json`.", "",
         "- Vérification dans les pages citées : " + ", ".join(f"{k} {v}" for k, v in N(l["verif"] for l in lignes).most_common()) + ".",
         "- Précision (après correction) : " + ", ".join(f"{k} {v}" for k, v in N(l["precision"] or "illisible" for l in lignes).most_common()) + ".",
         f"- « day » au 1er janvier traités comme des années : {sum(1 for l in lignes if l['jour_douteux'])}.",
         "- Recoupement avec l'AAM et Duberman : " + ", ".join(f"{k} {v}" for k, v in N(l["statut"] for l in lignes).most_common()) + ".",
         f"- Couche Chronos : {len(couche)} entrées (1933-1957, non confirmées, durée ≤ 13 mois).", "",
         "## Confirmés (même date, personne commune, mot commun)", ""] + [f"- {l['date_silver']} « {l['evenement'][:110]} » — {l['recoupement']}" for l in lignes if l["statut"].startswith("confirmé")]
    R += ["", "## À relire (non retrouvés dans les pages citées)", ""] + [f"- {l['date_silver']} « {l['evenement'][:110]} » ({l['pages_livre']})" for l in lignes if l["verif"] == "à relire"]
    open(base + "_rapport.md", "w", encoding="utf-8").write("\n".join(R) + "\n")
    print("\n".join(R[:12]))


if __name__ == "__main__":
    main()
