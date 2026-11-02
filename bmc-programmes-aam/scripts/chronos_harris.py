"""Chronos 2/5 : harris_events.json — faits tirés de 165 entretiens de Mary Emma Harris (Black Mountain College
Project, Appalachian State University), extraction automatique de décembre 2025.

Chaque fait porte la citation sur laquelle il repose. Vérification :
  - la citation est cherchée dans la transcription (DATA_BMC/Chronos/harris_transcripts/) : retrouvée telle quelle,
    en partie (au moins la moitié des segments de quatre mots), ou introuvable ;
  - à défaut, témoins de l'événement réunis dans un même passage (méthode de verifier_sources.py).
Recoupement avec l'AAM et Duberman :
  - fait daté au jour ou au mois : même date, personne commune → « confirmé (AAM | Duberman) » ;
  - fait daté plus largement : la personne a-t-elle une activité attestée dans la période ? → « présence attestée ».
Couche « Chronos » du semainier : les faits non confirmés, d'une durée de 13 mois au plus (souvenirs de témoins :
témoignage tardif +10). Les faits « uncertain_facts » de l'extraction et les cours cités restent dans le rapport.
Sorties : chronos/NNN_harris_recoupement.csv, _cours.csv, _couche.csv, _rapport.md.
"""
import csv, json, os, re, sys, collections, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chronos_commun as K
import verifier_sources as V

TYPE = {"academic": "cours", "arrival": "autre", "departure": "autre", "performance": "concert", "social": "social",
        "construction": "travail", "visit": "visite", "incident": "autre", "historical": "autre", "closure": "autre",
        "acquisition": "autre", "other": "autre"}


def lire(p):
    with open(p, encoding="utf-8") as f: return list(csv.DictReader(f))


def norm(s):
    s = V.plat(s).replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def citation(quote, texte_n):
    """(statut, position dans le texte normalisé)."""
    segs = [x.strip() for x in re.split(r"\.\.\.|…|\[.*?\]", quote or "") if x.strip()]
    grams, trouves, pos = 0, 0, None
    for sg in segs:
        mots = norm(re.sub(r"^[A-Z]{2,4}:\s*", "", sg)).split()
        for i in range(0, max(1, len(mots) - 3), 2):
            g = " ".join(mots[i:i + 4])
            if len(g) < 8: continue
            grams += 1
            k = texte_n.find(g)
            if k >= 0:
                trouves += 1
                if pos is None: pos = k
    if not grams: return "citation vide", None
    r = trouves / grams
    return ("citation retrouvée" if r >= 0.8 else "citation en partie" if r >= 0.4 else "citation introuvable"), pos


def localiser(quote, texte):
    """position (début, fin) de la citation dans le texte original, quels que soient ponctuation et sauts de ligne :
    on cherche la suite des premiers mots, séparés par n'importe quels non-mots."""
    tp = V.plat(texte)
    for sg in [x for x in re.split(r"\.\.\.|…|\[.*?\]", re.sub(r"^[A-Z]{2,4}:\s*", "", quote or "")) if x.strip()]:
        mots = re.findall(r"[a-z0-9]+", V.plat(sg))
        for n in (8, 6, 4):
            if len(mots) < min(n, 3): continue
            r = re.search(r"\W+".join(re.escape(w) for w in mots[:n]), tp)
            if r:
                fin = re.search(r"\W+".join(re.escape(w) for w in mots[-min(n, len(mots)):]), tp[r.start():r.start() + 2000])
                return r.start(), (r.start() + fin.end()) if fin else r.end()
    return -1, -1


def main():
    H = json.load(open(os.path.join(K.CHRONOS, "harris_events.json"), encoding="utf-8"))
    aam = lire(os.path.join(K.ROOT, "programme", "evenements.csv"))
    dub = lire(os.path.join(K.ROOT, "duberman", "evenements_duberman.csv"))
    cours_aam = lire(os.path.join(K.ROOT, "programme", "cours_par_periode.csv"))
    par_nom = collections.defaultdict(list)          # nom de famille -> [(date, base, activité)]
    for base, L in (("AAM", aam), ("Duberman", [e for e in dub if e["precision"] == "jour"])):
        for e in L:
            for n in K.noms_famille(e["qui"].split(";")): par_nom[n].append((e["date"], base, e["activite"]))
    textes = {}
    for t in H["transcripts"]:
        p = os.path.join(K.CHRONOS, "harris_transcripts", os.path.basename(t["source_file"]))
        textes[t["source_file"]] = open(p, encoding="utf-8", errors="replace").read() if os.path.exists(p) else ""
    V.rarete([V.plat(x) for x in textes.values()] + [V.plat(x) for x in V.textes_duberman().values()])

    lignes, cours, incertains = [], [], []
    for t in H["transcripts"]:
        iv, info = t.get("interviewee") or {}, t.get("interview_info") or {}
        texte = textes.get(t["source_file"], ""); tn = norm(texte)
        an_ent = re.search(r"(19|20)\d\d", info.get("date") or "")
        src = (f"Entretien de {iv.get('name', '?')} avec {info.get('interviewer') or 'Mary Emma Harris'}, {info.get('date') or 'date inconnue'}"
               f"{', ' + info['location'] if info.get('location') else ''} (Black Mountain College Project, Appalachian State University)")
        for u in t.get("uncertain_facts") or []:
            incertains.append({"temoin": iv.get("name", ""), "affirmation": u.get("claim", ""), "citation": u.get("quote", ""),
                               "raison": u.get("reason_uncertain", ""), "transcription": os.path.basename(t["source_file"])})
        for c in t.get("courses_mentioned") or []:
            ens = c.get("teacher") or ""; ys = [int(y) for y in re.findall(r"19\d\d", str(c.get("year") or ""))]
            m = [k for k in cours_aam if K.noms_famille([ens]) & K.noms_famille(k["enseignant"].split(";"))
                 and ys and any(abs(int(y) - ys[0]) <= 1 for y in re.findall(r"19\d\d", k["periode"]))]
            mt = [k for k in m if set(norm(c.get("name", "")).split()) & set(norm(k["cours"]).split())]
            cours.append({"temoin": iv.get("name", ""), "cours": c.get("name", ""), "enseignant": ens, "annee": c.get("year", ""),
                          "aam": "titre et enseignant dans l'AAM" if mt else "enseignant dans l'AAM cette année-là" if m else "absent de l'AAM",
                          "aam_cours": (mt or m or [{}])[0].get("cours", "")[:120], "transcription": os.path.basename(t["source_file"])})
        for k, ev in enumerate(t.get("factual_events") or []):
            d = K.lire_date(ev.get("date"))
            pers = [p for p in ev.get("people_involved") or [] if isinstance(p, str)]
            quoi = ev.get("event") or ""
            stc, pos = citation(ev.get("quote"), tn) if texte else ("transcription absente", None)
            if texte:
                noms, mots = V.temoins("; ".join(pers), quoi, True)
                occ = V.occurrences(V.plat(texte), {**{"n:" + a: b for a, b in noms.items()}, **{"m:" + a: b for a, b in mots.items()}})
                win = V.meilleur_passage(occ, {a: (3 if a.startswith("n:") else 1) for a in occ})
                g = lambda pr: {a[2:]: b for a, b in win.items() if a.startswith(pr)}
                stt = V.statut(noms, mots, g("n:"), g("m:"))
                # extrait : autour de la citation si elle est retrouvée, sinon autour des témoins
                if pos is not None:
                    k0, k1 = localiser(ev.get("quote"), texte)
                    ex = V.extrait(texte, {"q": (k0, k1)}) if k0 >= 0 else \
                         V.extrait(texte, {**{"n" + a: b for a, b in g("n:").items()}, **{"m" + a: b for a, b in g("m:").items()}})
                else:
                    ex = V.extrait(texte, {**{"n" + a: b for a, b in g("n:").items()}, **{"m" + a: b for a, b in g("m:").items()}})
            else:
                stt, ex = "texte introuvable", ""
            verif = "retrouvé" if stc == "citation retrouvée" or (stc == "citation en partie" and stt == "retrouvé") else \
                    "indice faible" if stc == "citation en partie" or stt in ("retrouvé", "indice faible") else "à relire"
            # recoupement
            statut, avec = "", ""
            if not d: statut = "date illisible"
            else:
                ns = K.noms_famille(pers)
                hits = [(x, b, a) for n in ns for (x, b, a) in par_nom.get(n, []) if d[0] <= x <= d[1]]
                if d[2] in ("jour", "plage", "mois") and hits:
                    statut = f"confirmé ({hits[0][1]})"; avec = f"{hits[0][0]} « {hits[0][2][:100]} »"
                elif hits:
                    statut = f"présence attestée ({', '.join(sorted({h[1] for h in hits}))})"
                    avec = f"{len(hits)} activité(s), du {min(h[0] for h in hits)} au {max(h[0] for h in hits)}"
                else: statut = "non confirmé"
            lignes.append({"id": f"{os.path.basename(t['source_file'])[:3]}-{k}", "temoin": iv.get("name", ""),
                           "role": iv.get("role_at_bmc", ""), "annees_bmc": iv.get("years_at_bmc", ""),
                           "entretien": info.get("date", ""), "date_harris": ev.get("date", ""),
                           "debut": d[0] if d else "", "fin": d[1] if d else "", "precision": d[2] if d else "",
                           "evenement": quoi[:300], "personnes": "; ".join(pers), "lieu": ev.get("location") or "",
                           "categorie": ev.get("category", ""), "confiance": ev.get("confidence", ""),
                           "citation": (ev.get("quote") or "")[:500], "verif_citation": stc, "verif": verif,
                           "statut": statut, "recoupement": avec, "_src": src, "_extrait": ex,
                           "_an_ent": int(an_ent.group(0)) if an_ent else None, "_fichier": os.path.basename(t["source_file"])})

    num = K.prochain_numero(K.SORTIE)
    base = os.path.join(K.SORTIE, f"{num}_harris")
    cols = [c for c in lignes[0] if not c.startswith("_")]
    for suff, rows, cs in (("_recoupement", lignes, cols), ("_cours", cours, list(cours[0])), ("_incertains", incertains, list(incertains[0]))):
        with open(base + suff + ".csv", "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cs, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    couche = []
    for l in lignes:
        if not l["debut"] or l["statut"].startswith("confirmé"): continue
        if (dt.date.fromisoformat(l["fin"]) - dt.date.fromisoformat(l["debut"])).days > 400: continue
        pct, mot = 10, ["extraction automatique (Chronos, décembre 2025), non relue (+10)"]
        ecart = (l["_an_ent"] - int(l["debut"][:4])) if l["_an_ent"] else None
        pct += 10; mot.append(f"témoignage oral{f', recueilli {ecart} ans après' if ecart else ''} (+10)")
        if l["confiance"] != "high": pct += 15; mot.append(f"confiance « {l['confiance']} » selon l'extraction (+15)")
        if l["precision"] not in ("jour", "plage"): pct += 25; mot.append(f"date « {l['precision']} » seulement (+25)")
        if l["verif"] != "retrouvé": pct += 15; mot.append(f"{l['verif_citation']} dans la transcription (+15)")
        couche.append({"id": f"ch{num}-{l['id']}", "source_chronos": "Harris (entretiens)", "date": l["debut"],
                       "date_fin": l["fin"] if l["fin"] != l["debut"] else "", "precision": l["precision"],
                       "type": TYPE.get(l["categorie"], "autre"), "activite": l["evenement"], "qui": l["personnes"], "lieu": l["lieu"],
                       "note": f"Souvenir de {l['temoin']} ({l['role']}, à BMC {l['annees_bmc']}) : « {l['citation']} »"
                               + (f" — {l['statut']} : {l['recoupement']}" if l["recoupement"] else ""),
                       "part_deduite_pct": min(pct, 90), "motifs_deduction": " ; ".join(mot),
                       "document_source": f"{l['_src']} — transcription {l['_fichier']}", "inventaire": "", "url_source": "",
                       "statut": l["statut"], "verif_statut": l["verif"], "verif_extrait": l["_extrait"], "date_source": l["date_harris"]})
    with open(base + "_couche.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(couche[0].keys())); w.writeheader(); w.writerows(couche)

    N = collections.Counter
    R = [f"# Chronos 2/5 : harris_events.json — entretiens de Mary Emma Harris ({num})", "",
         f"Source : `DATA_BMC/Chronos/harris_events.json` (extraction automatique du {H.get('extraction_date', '')[:10]}) : "
         f"{len(H['transcripts'])} transcriptions, {len(lignes)} faits, {len(incertains)} faits jugés incertains par l'extraction, "
         f"{len(cours)} cours cités. Les transcriptions sont dans `DATA_BMC/Chronos/harris_transcripts/`.", "",
         "## Vérification dans les transcriptions", "",
         "- Citation : " + ", ".join(f"{k} {v}" for k, v in N(l["verif_citation"] for l in lignes).most_common()) + ".",
         "- Statut retenu : " + ", ".join(f"{k} {v}" for k, v in N(l["verif"] for l in lignes).most_common()) + ".", "",
         "## Recoupement avec l'AAM et Duberman", "",
         "- " + ", ".join(f"{k} {v}" for k, v in N(l["statut"] for l in lignes).most_common()) + ".",
         "- « Présence attestée » : la personne a au moins une activité AAM ou Duberman dans la période du souvenir (le fait "
         "lui-même n'est pas confirmé, la présence l'est).",
         "- Précision des dates : " + ", ".join(f"{k} {v}" for k, v in N(l["precision"] or "illisible" for l in lignes).most_common()) + ".", "",
         f"## Couche du semainier : {len(couche)} faits (non confirmés, durée ≤ 13 mois)", "",
         "## Cours cités", "", "- " + ", ".join(f"{k} {v}" for k, v in N(c["aam"] for c in cours).most_common()) + f" (`{num}_harris_cours.csv`).",
         "", f"## Faits incertains selon l'extraction ({len(incertains)}) : `{num}_harris_incertains.csv`", ""]
    R += [f"- {u['temoin']} : {u['affirmation'][:120]} — {u['raison'][:100]}" for u in incertains[:25]]
    open(base + "_rapport.md", "w", encoding="utf-8").write("\n".join(R) + "\n")
    print("\n".join(R[:22]))


if __name__ == "__main__":
    main()
