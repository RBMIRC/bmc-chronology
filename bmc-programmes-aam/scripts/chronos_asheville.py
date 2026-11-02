"""Chronos 1/5 : asheville_events.json (extraction automatique de 377 fiches du musée) contre l'AAM audité.

Pour chaque événement extrait par Chronos :
  1. il est confronté au texte du document (OCR du musée, metadata.json + data.txt) : témoins réunis dans un même
     passage, pondérés par leur rareté (méthode de verifier_sources.py) ;
  2. il est confronté aux activités AAM du même document (programme/evenements.csv, même inventaire) :
       confirmé ............... même document, même date (ou date AAM dans la période Chronos), noms ou mots communs
       date différente ........ même document, même fait probable (noms et mots communs), autre date
       absent de l'AAM ........ document de notre corpus, aucune activité correspondante
       document hors corpus ... inventaire absent de liste_pages.csv
Rien n'est ajouté au programme attesté : les « absents » retrouvés dans le texte sont des pistes à relire
(l'audit AAM a relu chaque phrase datée ; un « absent » peut être un oubli, une règle écartée ou une invention).
Sorties : chronos/NNN_asheville_recoupement.csv, NNN_asheville_rapport.md.
"""
import csv, glob, json, os, re, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chronos_commun as K
import verifier_sources as V


def lire(p):
    with open(p, encoding="utf-8") as f: return list(csv.DictReader(f))


def main():
    S = json.load(open(os.path.join(K.CHRONOS, "asheville_events.json"), encoding="utf-8"))
    # textes et inventaires des dossiers de la collection
    dossiers, urls = {}, {}
    for p in glob.glob(os.path.join(K.CHRONOS, "asheville_bmc_collection", "*", "metadata.json")):
        m = json.load(open(p, encoding="utf-8")); d = os.path.basename(os.path.dirname(p))
        txt = m.get("description") or ""
        dt_ = os.path.join(os.path.dirname(p), "data.txt")
        if os.path.exists(dt_): txt += "\n" + open(dt_, encoding="utf-8", errors="replace").read()
        dossiers[d] = (m.get("accession_number", ""), m.get("title", ""), txt)
        urls[m.get("accession_number", "")] = m.get("url", "")
    corpus = {p["accession"] for p in lire(os.path.join(K.ROOT, "liste_pages.csv"))}
    aam = lire(os.path.join(K.ROOT, "programme", "evenements.csv"))
    par_inv = collections.defaultdict(list)
    for i, e in enumerate(aam):
        for v in (e["inventaire"] or "").split(";"): par_inv[v.strip()].append((i, e))
    import datetime as dt
    par_jour = collections.defaultdict(list)
    for i, e in enumerate(aam): par_jour[e["date"]].append((i, e))
    cal = lire(os.path.join(K.ROOT, "programme", "calendrier_periodes.csv"))
    bornes_cal = collections.defaultdict(list)
    for c in cal:
        for x in (c["debut"], c["fin"]): bornes_cal[x].append(c)
    dub = [e for e in lire(os.path.join(K.ROOT, "duberman", "evenements_duberman.csv")) if e["precision"] == "jour"]
    dub_jour = collections.defaultdict(list)
    for e in dub: dub_jour[e["date"]].append(e)
    def voisins(d0, n=1):
        x = dt.date.fromisoformat(d0)
        return [(x + dt.timedelta(k)).isoformat() for k in range(-n, n + 1)]
    V.rarete([V.plat(t) for _, _, t in dossiers.values()] + [V.plat(t) for t in V.textes_duberman().values()])

    lignes = []
    for doc in S["documents"]:
        dossier = doc.get("source_folder") or os.path.basename(os.path.dirname(doc.get("source_file", "")))
        inv, titre, texte = dossiers.get(dossier, ("", "", ""))
        for ev in doc.get("events") or []:
            d = K.lire_date(ev.get("date"))
            pers = [p for p in ev.get("people") or [] if isinstance(p, str)]
            quoi = ev.get("event") or ""
            # 1. texte du document
            if texte:
                noms, mots = V.temoins("; ".join(pers), quoi + " " + (ev.get("details") or ""), True)
                gd = {}
                if d and d[2] == "jour":
                    y, mo, j = d[0].split("-"); gd = {"y": [y], "m": [V.MOIS_EN[int(mo) - 1]]}
                tp = V.plat(texte)
                occ = V.occurrences(tp, {**{"n:" + k: v for k, v in noms.items()}, **{"m:" + k: v for k, v in mots.items()},
                                         **{"d:" + k: v for k, v in gd.items()}})
                win = V.meilleur_passage(occ, {k: (3 if k.startswith("n:") else 1) for k in occ})
                g = lambda pr: {k[2:]: v for k, v in win.items() if k.startswith(pr)}
                verif = V.statut(noms, mots, g("n:"), g("m:"), g("d:") if gd else None)
                extrait = V.extrait(texte, {**{"n" + k: v for k, v in g("n:").items()}, **{"m" + k: v for k, v in g("m:").items()},
                                            **{"d" + k: v for k, v in g("d:").items()}})
            else:
                verif, extrait = "texte introuvable", ""
            # 2. activités AAM du même document
            statut, best = "", None
            if inv not in corpus: statut = "document hors corpus"
            elif not d: statut = "date illisible"
            else:
                nc = K.noms_famille(pers); mc = {w for w in re.findall(r"[a-z]{4,}", V.plat(quoi)) if w not in V.VIDES}
                cands = []
                for i, a in par_inv.get(inv, []):
                    na = K.noms_famille(a["qui"].split(";")) | set(re.findall(r"[a-z]{4,}", V.plat(a["activite"])))
                    ma = {w for w in re.findall(r"[a-z]{4,}", V.plat(a["activite"] + " " + a["note"])) if w not in V.VIDES}
                    score = 3 * len(nc & na) + len(mc & ma)
                    meme_date = d[0] <= a["date"] <= d[1]
                    cands.append((score, meme_date, i, a))
                cands.sort(key=lambda c: (-c[1], -c[0]))
                ok = [c for c in cands if c[1] and (c[0] >= 1 or not (nc or mc))]
                if ok: statut, best = "confirmé", ok[0]
                else:
                    autre = sorted([c for c in cands if not c[1] and c[0] >= 4], key=lambda c: -c[0])
                    if autre and d[2] in ("jour", "mois"): statut, best = "date différente", autre[0]
                    else:
                        statut = "absent de l'AAM"
                        if d[2] == "jour":
                            # calendrier attesté (débuts et fins de trimestre, vacances)
                            if ev.get("category") == "calendar" and any(bornes_cal.get(x) for x in voisins(d[0])):
                                c = next(c for x in voisins(d[0]) for c in bornes_cal.get(x, []))
                                statut, best = "confirmé (calendrier)", (0, True, "cal", {"date": c["debut"] + " → " + c["fin"], "activite": c["libelle"]})
                            else:
                                # toute activité AAM (autre document) ou Duberman du même jour, à un jour près
                                for x in voisins(d[0]):
                                    for i, a in par_jour.get(x, []):
                                        na = K.noms_famille(a["qui"].split(";")) | set(re.findall(r"[a-z]{4,}", V.plat(a["activite"])))
                                        ma = {w for w in re.findall(r"[a-z]{4,}", V.plat(a["activite"] + " " + a["note"])) if w not in V.VIDES}
                                        if (nc & na) or len(mc & ma) >= 2:
                                            statut, best = "confirmé par un autre document AAM", (0, True, i, a); break
                                    if best: break
                                if not best:
                                    for x in voisins(d[0]):
                                        for e2 in dub_jour.get(x, []):
                                            if nc & K.noms_famille(e2["qui"].split(";")):
                                                statut, best = "confirmé par Duberman", (0, True, "dub", e2); break
                                        if best: break
            lignes.append({"inventaire": inv, "document": titre[:120], "date_chronos": ev.get("date", ""),
                           "debut": d[0] if d else "", "fin": d[1] if d else "", "precision": d[2] if d else "",
                           "evenement": quoi[:300], "personnes": "; ".join(pers), "categorie": ev.get("category", ""),
                           "verif_texte": verif, "statut_aam": statut,
                           "aam_ligne": best[2] if best else "", "aam_date": best[3]["date"] if best else "",
                           "aam_activite": best[3]["activite"][:200] if best else "",
                           "_extrait": extrait, "_details": ev.get("details") or "", "_doc_date": doc.get("document_date", ""),
                           "_url": urls.get(inv, "")})

    num = K.prochain_numero(K.SORTIE)
    base = os.path.join(K.SORTIE, f"{num}_asheville")
    with open(base + "_recoupement.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[k for k in lignes[0] if not k.startswith("_")], extrasaction="ignore"); w.writeheader(); w.writerows(lignes)
    # couche « Chronos » du semainier : absents de l'AAM datés au jour, et documents hors corpus (datés au mois au plus)
    TYPE = {"performance": "concert", "visit": "visite", "academic": "cours", "calendar": "calendrier", "administrative": "reunion",
            "construction": "travail", "financial": "autre", "war": "autre", "death": "autre", "other": "autre", "publicity": "autre"}
    couche = []
    for k, l in enumerate(lignes):
        garder = (l["statut_aam"] == "absent de l'AAM" and l["precision"] == "jour") or \
                 (l["statut_aam"] == "document hors corpus" and l["precision"] in ("jour", "plage", "mois"))
        if not garder or l["verif_texte"] == "texte introuvable": continue
        pct, mot = 10, ["extraction automatique (Chronos, décembre 2025), non relue (+10)"]
        if l["statut_aam"] == "absent de l'AAM":
            pct += 15; mot.append("non retenu par l'audit manuel du même document : oubli, règle écartée ou date mal résolue — à relire (+15)")
        if l["precision"] != "jour": pct += 25; mot.append(f"date « {l['precision']} » seulement (+25)")
        if l["verif_texte"] != "retrouvé": pct += 15; mot.append(f"témoins non réunis dans le texte du document : {l['verif_texte']} (+15)")
        couche.append({"id": f"ca{num}-{k}", "source_chronos": "Asheville (fiches du musée)", "date": l["debut"],
                       "date_fin": l["fin"] if l["fin"] != l["debut"] else "", "precision": l["precision"],
                       "type": TYPE.get(l["categorie"], "autre"), "activite": l["evenement"], "qui": l["personnes"], "lieu": "",
                       "note": l["_details"] + (f" (document daté « {l['_doc_date']} »)" if l["_doc_date"] else ""),
                       "part_deduite_pct": min(pct, 90), "motifs_deduction": " ; ".join(mot),
                       "document_source": f"{l['document']} (inv. {l['inventaire']}), d'après Chronos asheville_events.json",
                       "inventaire": l["inventaire"], "url_source": l["_url"], "statut": l["statut_aam"],
                       "verif_statut": l["verif_texte"], "verif_extrait": l["_extrait"], "date_source": l["date_chronos"]})
    with open(base + "_couche.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(couche[0].keys())); w.writeheader(); w.writerows(couche)
    C = collections.Counter
    st = C(l["statut_aam"] for l in lignes); ve = C(l["verif_texte"] for l in lignes)
    croise = C((l["statut_aam"], l["verif_texte"]) for l in lignes)
    hors = sorted({(l["inventaire"], l["document"]) for l in lignes if l["statut_aam"] == "document hors corpus"})
    abs_ok = [l for l in lignes if l["statut_aam"] == "absent de l'AAM" and l["verif_texte"] == "retrouvé" and l["precision"] == "jour"]
    div = [l for l in lignes if l["statut_aam"] == "date différente"]
    R0 = f"Couche « Chronos » du semainier : {len(couche)} entrées (`{num}_asheville_couche.csv`)."
    R = [f"# Chronos 1/5 : asheville_events.json contre l'AAM audité ({num})", "",
         f"Source : `DATA_BMC/Chronos/asheville_events.json` (extraction automatique du {S.get('extraction_date', '')[:10]}, "
         f"{len(S['documents'])} documents, {len(lignes)} événements). Comparé à `programme/evenements.csv` "
         "(4 650 activités, extraction manuelle et audit phrase par phrase) et au texte OCR de chaque document.", "",
         "## Résultat", "",
         "| statut | événements | dont retrouvés dans le texte du document |", "|---|---|---|"]
    for k, v in st.most_common():
        R.append(f"| {k} | {v} | {croise[(k, 'retrouvé')]} ({100 * croise[(k, 'retrouvé')] / v:.0f} %) |")
    R += ["", "Vérification dans le texte : " + ", ".join(f"{k} {v}" for k, v in ve.most_common()) + ".", "",
          "## Lecture", "",
          "- **Confirmé** : l'extraction automatique retrouve une activité AAM du même document à la même date.",
          "- **Date différente** : même fait probable dans le même document, daté autrement. Ordre de confiance : la lecture "
          "manuelle (AAM) prime ; à relire seulement si Chronos est retrouvé dans le texte.",
          "- **Absent de l'AAM** : pistes. L'audit AAM a relu toutes les phrases datées : un absent est soit un oubli, soit une "
          "règle écartée volontairement (administratif, horaires), soit une invention du modèle (alors non retrouvé dans le texte).",
          "", f"## Absents de l'AAM, datés au jour et retrouvés dans le texte ({len(abs_ok)}) — à relire en priorité", ""]
    R += [f"- {l['debut']} · {l['inventaire']} · {l['evenement'][:140]}" for l in abs_ok[:80]]
    if len(abs_ok) > 80: R.append(f"- … {len(abs_ok) - 80} autres dans le CSV")
    R += ["", f"## Dates différentes ({len(div)})", ""]
    R += [f"- {l['inventaire']} : Chronos {l['date_chronos']} « {l['evenement'][:90]} » / AAM {l['aam_date']} « {l['aam_activite'][:90]} » ({l['verif_texte']})" for l in div[:60]]
    R += ["", f"## Documents hors du corpus AAM ({len(hors)})", ""] + [f"- {i} · {t}" for i, t in hors]
    R += ["", "## Couche du semainier", "", R0]
    open(base + "_rapport.md", "w", encoding="utf-8").write("\n".join(R) + "\n")
    print("\n".join(R[:20]))


if __name__ == "__main__":
    main()
