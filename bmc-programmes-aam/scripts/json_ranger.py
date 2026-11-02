"""Rangement des JSON (2/11/2026) : un JSON compilé, complet, unique et autonome par source du semainier.

Les extractions automatiques du dossier Chronos (décembre 2025) existaient en plusieurs versions : fichier de base,
« _temp » (passage partiel), puis versions cumulées (« _complete », « _final », « _ultimate », « _wikipedia »…) qui
réunissent les quatre sources et ajoutent des enrichissements. Ce script :
  1. compile chaque source en UN fichier, DATA_BMC/json/semainier/<source>.json, qui garde la structure d'origine
     (mêmes clés : les scripts chronos_*.py le lisent sans changement) et ajoute :
       - « _meta » : description, champs, provenance (fichiers d'origine, sha1, taille), variantes vérifiées, contrôles,
         scripts qui le lisent — le fichier se comprend seul ;
       - un identifiant stable par enregistrement (« id ») ;
       - les enrichissements trouvés seulement dans les versions cumulées (Duberman : people_in_presence,
         people_wikipedia), sous la clé « enrichissements », marqués comme tels ;
       - Asheville : le numéro d'inventaire, le titre, la date et l'URL de la fiche du musée (metadata.json) ;
  2. vérifie que rien ne manque : chaque enregistrement de chaque variante doit se retrouver dans le fichier compilé
     (sinon il est ajouté, marqué « repris_de ») ;
  3. vérifie l'unicité : un doublon (même date, même texte, même document) est gardé mais marqué « doublon_de » ;
  4. écrit DATA_BMC/json/CATALOGUE.md et catalogue.csv : tous les JSON du dépôt, leur statut et leur place.
Lecture des originaux : DATA_BMC/Chronos/_versions/ (où ils ont été rangés par git mv), sinon DATA_BMC/Chronos/.
Les fichiers compilés ne sont jamais écrasés : s'ils existent et diffèrent, le script s'arrête (--forcer pour refaire).
"""
import collections, csv, datetime as dt, glob, hashlib, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEPOT = os.path.dirname(ROOT)
CHR = os.path.join(DEPOT, "DATA_BMC", "Chronos")
VERS = os.path.join(CHR, "_versions")
SORTIE = os.path.join(DEPOT, "DATA_BMC", "json")
SEM = os.path.join(SORTIE, "semainier")
AUJ = dt.date.today().isoformat()


def chemin(nom):
    for d in (VERS, CHR):
        p = os.path.join(d, nom)
        if os.path.exists(p): return p
    sys.exit(f"introuvable : {nom}")


def charger(nom):
    p = chemin(nom)
    return json.load(open(p, encoding="utf-8")), p


def rel(p): return os.path.relpath(p, DEPOT)


def empreinte(p):
    b = open(p, "rb").read()
    return {"fichier": rel(p), "sha1": hashlib.sha1(b).hexdigest(), "octets": len(b)}


def pl(s): return re.sub(r"[^a-z0-9]", "", str(s or "").lower())[:100]


def cle(e, texte="event"): return (str(e.get("date")), pl(e.get(texte)))


def marquer_doublons(L, f_cle, prefixe):
    vus, n = {}, 0
    for x in L:
        k = f_cle(x)
        if k in vus: x["doublon_de"] = vus[k]; n += 1
        else: vus[k] = x["id"]
    return n


def meta(titre, description, champs, origine, variantes, controles, lu_par):
    return {"titre": titre, "description": description, "statut": "source du semainier (couche Chronos), fichier compilé unique",
            "nature": "extraction automatique (Chronos, décembre 2025, modèle de langage) : à vérifier contre les documents ; "
                      "dans le semainier, chaque entrée est confrontée à l'AAM, à Duberman et au texte cité (scripts/chronos_*.py)",
            "champs": champs, "fichier_origine": origine, "variantes_verifiees": variantes, "controles": controles,
            "lu_par": lu_par, "compile_par": "bmc-programmes-aam/scripts/json_ranger.py", "compile_le": AUJ}


# ---------------------------------------------------------------- Duberman (bmc_chronology.json)
def duberman():
    B, pb = charger("bmc_chronology.json")
    E = B["events"]
    for i, e in enumerate(E, 1): e["id"] = f"dub-{i:04d}"
    par_cle = collections.defaultdict(list)
    for e in E: par_cle[cle(e)].append(e)
    variantes = []
    for nom in ["bmc_chronology_temp.json", "bmc_chronology_enriched.json", "bmc_chronology_with_presence.json",
                "bmc_chronology_final.json", "bmc_chronology_complete.json", "bmc_chronology_ultimate.json", "bmc_chronology_wikipedia.json"]:
        V, pv = charger(nom)
        # dans les versions cumulées, les événements de Duberman sont ceux qui ont des pages (source_pages) sans entretien
        VE = [x for x in V["events"] if not x.get("interview_source") and not str(x.get("source", "")).startswith("Asheville")
              and not ("farm" in str(x.get("source", "")).lower() or x.get("farm_info") or x.get("source_document"))]
        manque, ajout = 0, collections.Counter()
        for x in VE:
            cands = par_cle.get(cle(x))
            if not cands:
                manque += 1
                y = dict(x, id=f"dub-{len(E) + 1:04d}", repris_de=os.path.basename(pv)); E.append(y); par_cle[cle(y)].append(y)
                continue
            e = cands[0]
            for k in ("people_in_presence", "people_wikipedia"):
                if x.get(k) and k not in e.get("enrichissements", {}):
                    e.setdefault("enrichissements", {})[k] = x[k]; ajout[k] += 1
        variantes.append({**empreinte(pv), "evenements_duberman": len(VE), "absents_du_compile_ajoutes": manque,
                          "enrichissements_repris": dict(ajout),
                          "note": "passage partiel antérieur" if "temp" in nom else "version cumulée (Duberman + ferme + Harris + Asheville selon la version)"})
    nd = marquer_doublons(E, cle, "dub")
    out = {"_meta": meta("Duberman, Black Mountain: An Exploration in Community (1972) — chronologie extraite (« Chronos 2 »)",
                         "Événements datés tirés automatiquement du livre de Martin Duberman, avec page et citation.",
                         {"id": "identifiant stable (dub-NNNN)", "date": "date telle que lue", "date_precision": "exact, month, year…",
                          "event": "fait (anglais)", "people": "personnes", "location": "lieu", "source": "page citée",
                          "context": "chapitre", "category": "catégorie", "quote": "citation du livre", "source_pages": "pages",
                          "enrichissements": "repris des versions cumulées, calculés automatiquement : people_in_presence (personnes "
                                             "présentes d'après la base des personnes), people_wikipedia (fiches Wikipedia) — non vérifiés",
                          "doublon_de": "id du premier enregistrement identique", "repris_de": "enregistrement absent de la base, repris d'une variante"},
                         empreinte(pb), variantes,
                         {"evenements": len(E), "doublons_marques": nd, "sans_date": sum(1 for e in E if not e.get("date")),
                          "sans_citation": sum(1 for e in E if not e.get("quote"))},
                         ["scripts/chronos_duberman.py"]),
           "metadata": B.get("metadata", {}), "events": E}
    return "duberman_chronologie.json", out


# ---------------------------------------------------------------- Harris (harris_events.json)
def harris():
    H, ph = charger("harris_events.json")
    T = H["transcripts"]
    for i, t in enumerate(T, 1):
        t["id"] = f"har-{i:03d}"
        for k, e in enumerate(t.get("factual_events") or [], 1): e["id"] = f"har-{i:03d}-{k:02d}"
    tous = {(os.path.basename(t["source_file"]), cle(e)) for t in T for e in t.get("factual_events") or []}
    par_fichier = {os.path.basename(t["source_file"]): t for t in T}
    variantes = []
    HT, pt = charger("harris_temp.json")
    m_t = [t for t in HT if os.path.basename(t["source_file"]) not in par_fichier]
    m_e = [(t, e) for t in HT for e in t.get("factual_events") or [] if (os.path.basename(t["source_file"]), cle(e)) not in tous]
    for t in m_t: T.append(dict(t, id=f"har-{len(T) + 1:03d}", repris_de=os.path.basename(pt)))
    for t, e in m_e:
        if os.path.basename(t["source_file"]) in par_fichier:
            par_fichier[os.path.basename(t["source_file"])]["factual_events"].append(dict(e, repris_de=os.path.basename(pt)))
    variantes.append({**empreinte(pt), "entretiens": len(HT), "entretiens_absents_ajoutes": len(m_t), "faits_absents_ajoutes": len(m_e),
                      "note": "passage partiel antérieur"})
    U, pu = charger("bmc_chronology_ultimate.json")
    UE = [x for x in U["events"] if x.get("interview_source")]
    cles_txt = {cle(e) for t in T for e in t.get("factual_events") or []}
    variantes.append({**empreinte(pu), "faits_harris": len(UE), "absents_du_compile": sum(1 for x in UE if cle(x) not in cles_txt),
                      "note": "version cumulée : mêmes faits remis à plat (people_involved → people, interview_source)"})
    nd = 0
    for t in T: nd += marquer_doublons(t.get("factual_events") or [], cle, "har")
    nf = sum(len(t.get("factual_events") or []) for t in T)
    out = {"_meta": meta("Entretiens de Mary Emma Harris (Black Mountain College Project) — faits extraits",
                         "165 transcriptions d'entretiens (DATA_BMC/Chronos/harris_transcripts/) : pour chacune, faits datés avec "
                         "citation et confiance, personnes, cours, lieux cités, faits incertains.",
                         {"id": "har-NNN (entretien), har-NNN-KK (fait)", "interviewee": "personne interrogée", "interview_info": "date et lieu de l'entretien",
                          "factual_events": "faits : date, date_precision, event, people_involved, location, quote, confidence, category",
                          "people_mentioned": "personnes citées", "courses_mentioned": "cours cités", "locations_mentioned": "lieux cités",
                          "uncertain_facts": "faits que l'extraction juge incertains", "source_file": "transcription (harris_transcripts/)"},
                         empreinte(ph), variantes,
                         {"entretiens": len(T), "faits": nf, "doublons_marques": nd,
                          "transcriptions_presentes": sum(1 for t in T if os.path.exists(os.path.join(CHR, "harris_transcripts", os.path.basename(t["source_file"]))))},
                         ["scripts/chronos_harris.py"]),
           **{k: v for k, v in H.items() if k != "transcripts"}, "transcripts": T}
    return "harris_entretiens.json", out


# ---------------------------------------------------------------- Ferme (farm_events.json)
def ferme():
    F, pf = charger("farm_events.json")
    for i, e in enumerate(F["events"], 1): e["id"] = f"fer-e{i:03d}"
    for i, d in enumerate(F["documents"], 1): d["id"] = f"fer-d{i:03d}"
    ce = {cle(e) for e in F["events"]}
    cd = {(str(d.get("date")), pl(d.get("subject") or d.get("content_summary"))) for d in F["documents"]}
    FT, pt = charger("farm_temp.json")
    me = [e for e in FT["events"] if cle(e) not in ce]
    md = [d for d in FT["documents"] if (str(d.get("date")), pl(d.get("subject") or d.get("content_summary"))) not in cd]
    for e in me: F["events"].append(dict(e, id=f"fer-e{len(F['events']) + 1:03d}", repris_de=os.path.basename(pt)))
    for d in md: F["documents"].append(dict(d, id=f"fer-d{len(F['documents']) + 1:03d}", repris_de=os.path.basename(pt)))
    U, pu = charger("bmc_chronology_ultimate.json")
    UF = [x for x in U["events"] if not x.get("interview_source") and ("farm" in str(x.get("source", "")).lower() or x.get("farm_info") or x.get("source_document"))]
    # documents remis à plat : même pages du livre (« farm_low.pdf, pages 87-88 » ↔ source_pages « 87-88 »)
    pages_docs = {str(d.get("source_pages") or "").replace(" ", "") for d in F["documents"]}
    pg = lambda x: (re.search(r"pages?\s*([\d\-– ,]+)", str(x.get("source") or "")) or [None, ""])[1].strip(" ,").replace(" ", "")
    docs_u = [x for x in UF if x.get("document_type")]
    abs_ = [x for x in UF if not x.get("document_type") and cle(x) not in ce] + [x for x in docs_u if pg(x) not in pages_docs]
    variantes = [{**empreinte(pt), "evenements": len(FT["events"]), "documents": len(FT["documents"]),
                  "evenements_absents_ajoutes": len(me), "documents_absents_ajoutes": len(md), "note": "passage partiel antérieur"},
                 {**empreinte(pu), "entrees_ferme": len(UF), "dont_documents_remis_a_plat": len(docs_u),
                  "absents_du_compile": len(abs_), "note": "version cumulée : événements et documents datés remis à plat"}]
    nd = marquer_doublons(F["events"], cle, "fer") + marquer_doublons(F["documents"], lambda d: (str(d.get("date")), pl(d.get("subject")), pl(d.get("author")), str(d.get("source_pages"))), "fer")
    out = {"_meta": meta("David Silver, The Farm at Black Mountain College (2024) — événements et documents extraits",
                         "Extraction automatique du livre de Silver (OCR du scan, DATA_BMC/_correction_farm/pages.json) : événements datés "
                         "avec pages, et documents d'archives cités (lettres, rapports : auteur, destinataire, sujet, données de la ferme).",
                         {"id": "fer-eNNN (événement), fer-dNNN (document)", "events": "date, date_precision, event, people, category, source, source_pages",
                          "documents": "type, date, date_normalized, author, recipient, subject, content_summary, people_mentioned, financial_info, farm_info, source_pages",
                          "handwritten_notes": "notes manuscrites lues sur le scan"},
                         empreinte(pf), variantes,
                         {"evenements": len(F["events"]), "documents": len(F["documents"]), "doublons_marques": nd,
                          "evenements_sans_date": sum(1 for e in F["events"] if not e.get("date"))},
                         ["scripts/chronos_ferme.py"]),
           **{k: v for k, v in F.items() if k not in ("events", "documents")}, "events": F["events"], "documents": F["documents"]}
    return "ferme_silver.json", out


# ---------------------------------------------------------------- Asheville (asheville_events.json)
def asheville():
    A, pa = charger("asheville_events.json")
    fiches = {}
    for p in glob.glob(os.path.join(CHR, "asheville_bmc_collection", "*", "metadata.json")):
        m = json.load(open(p, encoding="utf-8")); fiches[os.path.basename(os.path.dirname(p))] = m
    D = A["documents"]
    for i, d in enumerate(D, 1):
        dos = d.get("source_folder") or os.path.basename(os.path.dirname(d.get("source_file", "")))
        m = fiches.get(dos, {})
        d["id"] = f"ash-{i:03d}"
        d["fiche_musee"] = {"inventaire": m.get("accession_number", ""), "titre": m.get("title", ""), "date": m.get("date", ""),
                            "url": m.get("url", ""), "dossier": rel(os.path.join(CHR, "asheville_bmc_collection", dos)) if dos else ""}
        for k, e in enumerate(d.get("events") or [], 1): e["id"] = f"ash-{i:03d}-{k:02d}"
    par_fichier = {d["source_file"]: d for d in D}
    AT, pt = charger("asheville_temp.json")
    m_d = [d for d in AT if d["source_file"] not in par_fichier]
    m_e = [(d, e) for d in AT if d["source_file"] in par_fichier for e in d.get("events") or []
           if cle(e) not in {cle(x) for x in par_fichier[d["source_file"]].get("events") or []}]
    for d in m_d: D.append(dict(d, id=f"ash-{len(D) + 1:03d}", repris_de=os.path.basename(pt)))
    for d, e in m_e: par_fichier[d["source_file"]]["events"].append(dict(e, repris_de=os.path.basename(pt)))
    U, pu = charger("bmc_chronology_ultimate.json")
    UA = [x for x in U["events"] if str(x.get("source", "")).startswith("Asheville")]
    ev = {cle(e) for d in D for e in d.get("events") or []}
    # entrées dérivées des rubriques calendar_dates, decisions, visitors_mentioned : le texte doit y figurer
    derive = {pl(x) for d in D for k in ("calendar_dates", "decisions", "visitors_mentioned") for it in d.get(k) or []
              for x in ([it.get("period"), it.get("name"), it.get("topic"), it.get("decision")] if isinstance(it, dict) else [it]) if x}
    hors = [x for x in UA if cle(x) not in ev]
    retrouve = sum(1 for x in hors if any(s and s[:25] in pl(x.get("event")) for s in derive if len(s) >= 6))
    variantes = [{**empreinte(pt), "documents": len(AT), "documents_absents_ajoutes": len(m_d), "faits_absents_ajoutes": len(m_e), "note": "passage partiel antérieur"},
                 {**empreinte(pu), "entrees_asheville": len(UA), "hors_rubrique_events": len(hors),
                  "dont_retrouvees_dans_calendar_dates_decisions_visitors": retrouve,
                  "note": "version cumulée : les rubriques calendar_dates, decisions et visitors_mentioned remises à plat en événements"}]
    nd = 0
    for d in D: nd += marquer_doublons(d.get("events") or [], cle, "ash")
    rub = ["events", "calendar_dates", "decisions", "visitors_mentioned", "faculty_listed", "students_listed", "courses_offered"]
    out = {"_meta": meta("Collection Black Mountain College de l'Asheville Art Museum — 377 fiches lues automatiquement",
                         "Pour chaque fiche du musée (DATA_BMC/Chronos/asheville_bmc_collection/<dossier>/ : metadata.json et data.txt) : "
                         "type, date, année scolaire, événements datés, calendrier, décisions, visiteurs, enseignants, étudiants et cours listés.",
                         {"id": "ash-NNN (document), ash-NNN-KK (événement)", "fiche_musee": "inventaire, titre, date, URL de la fiche (metadata.json)",
                          "document_type": "type", "document_date": "date du document", "academic_year": "année scolaire",
                          "events": "événements datés (date, date_precision, event, people, details…)",
                          "calendar_dates": "périodes (period, start, end)", "decisions": "décisions (topic, decision, date)",
                          "visitors_mentioned": "visiteurs (name, date, purpose)", "faculty_listed": "enseignants (name, title, department)",
                          "students_listed": "étudiants", "courses_offered": "cours (name, department, instructor)",
                          "source_folder": "dossier de la fiche", "source_file": "fichier lu"},
                         empreinte(pa), variantes,
                         {"documents": len(D), **{f"{k}": sum(len(d.get(k) or []) for d in D) for k in rub}, "doublons_marques": nd,
                          "documents_sans_fiche_musee": sum(1 for d in D if not d["fiche_musee"]["inventaire"])},
                         ["scripts/chronos_asheville.py"]),
           **{k: v for k, v in A.items() if k != "documents"}, "documents": D}
    return "asheville_documents.json", out


# ---------------------------------------------------------------- hors semainier : relations et enrichissements
HORS = os.path.join(SORTIE, "hors_semainier")
HV = os.path.join(HORS, "_versions")


def relations():
    ld = lambda n: (json.load(open(os.path.join(HV, n), encoding="utf-8")), os.path.join(HV, n))
    (R0, p0), (R1, p1), (R2, p2) = ld("bmc_relations.json"), ld("bmc_relations_enriched.json"), ld("bmc_relations_normalized.json")
    al = R2.get("alias_mapping", {}); nm = lambda n: al.get(n, n)
    k = lambda e, f=lambda x: x: (f(e["source"]), f(e["target"]), e["type"])
    e2 = {k(e) for e in R2["edges"]} | {(t, s_, ty) for s_, t, ty in (k(e) for e in R2["edges"])}
    manque = [e for R in (R0, R1) for e in R["edges"] if k(e, nm) not in e2]
    out = dict(R2)
    out["edges"] = R2["edges"] + [dict(e, repris_de="bmc_relations_enriched.json") for e in {json.dumps(x, sort_keys=True): x for x in manque}.values()]
    out["detailed_relations"] = R1.get("detailed_relations") or R0.get("detailed_relations")
    out = {"_meta": {"titre": "Relations entre personnes du Black Mountain College (graphe)", "statut": "hors semainier",
                     "nature": "graphe calculé automatiquement (cooccurrences dans les extractions Chronos, Duberman, Asheville) : non vérifié",
                     "fichier_origine": empreinte(p2), "variantes_verifiees": [
                         {**empreinte(p0), "aretes": len(R0["edges"]), "absentes_du_compile_meme_apres_normalisation_des_noms": sum(1 for e in R0["edges"] if k(e, nm) not in e2)},
                         {**empreinte(p1), "aretes": len(R1["edges"]), "absentes_du_compile_meme_apres_normalisation_des_noms": sum(1 for e in R1["edges"] if k(e, nm) not in e2),
                          "detailed_relations_reprises": len(out_dr := (R1.get("detailed_relations") or []))}],
                     "controles": {"noeuds": len(out["nodes"]), "aretes": len(out["edges"]), "relations_detaillees": len(out["detailed_relations"] or []),
                                   "relations_profondes": len(out.get("deep_relations") or {})},
                     "compile_par": "bmc-programmes-aam/scripts/json_ranger.py", "compile_le": AUJ}, **out}
    return os.path.join(HORS, "personnes_relations.json"), out


def enrichissements():
    pa, pb = os.path.join(HV, "people_enrichments.json"), os.path.join(HV, "enrichments_temp.json")
    a, b = json.load(open(pa, encoding="utf-8")), json.load(open(pb, encoding="utf-8"))
    out = {}
    for n, v in a.items():
        out[n] = dict(v)
        if n in b and b[n] != v: out[n]["autre_lecture"] = b[n]
    for n, v in b.items():
        if n not in out: out[n] = dict(v, repris_de="enrichments_temp.json")
    out = {"_meta": {"titre": "Enrichissements de personnes tirés de Duberman (extraction automatique)", "statut": "hors semainier",
                     "nature": "résumés produits par un modèle de langage (focus, rôle, faits, relations, citations, pages) : non vérifiés",
                     "fichier_origine": empreinte(pa),
                     "variantes_verifiees": [{**empreinte(pb), "personnes": len(b), "absentes_du_compile": sum(1 for n in b if n not in a),
                                              "lectures_differentes_gardees_en_autre_lecture": sum(1 for n in b if n in a and a[n] != b[n])}],
                     "controles": {"personnes": len(out)}, "compile_par": "bmc-programmes-aam/scripts/json_ranger.py", "compile_le": AUJ},
           "personnes": out}
    return os.path.join(HORS, "personnes_enrichissements.json"), out


# ---------------------------------------------------------------- catalogue
def catalogue():
    regles = [
        (r"^DATA_BMC/json/semainier/", "source du semainier (compilé)", "lu par les scripts chronos_*.py"),
        (r"^DATA_BMC/json/hors_semainier/_versions/", "hors semainier — version antérieure", "contenu repris dans le fichier canonique voisin"),
        (r"^DATA_BMC/json/hors_semainier/", "hors semainier", "personnes, relations, Wikipedia, fiction, météo : n'entre pas dans le semainier"),
        (r"^DATA_BMC/Chronos/_versions/", "version rangée (remplacée par DATA_BMC/json/semainier/)", "contenu vérifié dans le fichier compilé"),
        (r"^DATA_BMC/Chronos/asheville_bmc_collection/", "source : fiche du musée (métadonnées)", "lue par json_ranger.py et chronos_asheville.py"),
        (r"^DATA_BMC/bmcyearbook/", "source du semainier (base des personnes)", "lue par chronos_personnes.py"),
        (r"^DATA_BMC/_correction_farm/", "pièce de la correction du texte de Silver", "pages.json et pagemap.json lus par chronos_ferme.py"),
        (r"^bmc-scenario/sortie/", "source du semainier (scénario)", "lue par integrer_scenario.py"),
        (r"^bmc-scenario/syntheses/", "source du semainier (synthèses du scénario)", "lues par integrer_syntheses.py → bmc-programmes-aam/scenario/"),
        (r"^bmc-scenario/texte/", "texte des livres (OCR paginé)", "sert à la vérification (verifier_sources.py, Rumaker)"),
        (r"^bmc-scenario/(etat|comparaison)/", "interne à la chaîne bmc-scenario (hors semainier)", "état des traitements, essais de modèles"),
        (r"^bmc-programmes-aam/scenario/", "sortie numérotée (integrer_syntheses.py)", "lue par export_semainier.py (la plus récente)"),
        (r"^bmc-programmes-aam/duberman/_appui/", "pièce du dépouillement de Duberman", "lue par construire_duberman.py"),
        (r"^bmc-programmes-aam/programme/audit/lots/", "interne à l'audit", "lots de vérification"),
        (r"^bmc-programmes-aam/(fiches|fiches_sondees)\.json$", "source du semainier (fiches AAM)", "lues par les scripts du programme"),
        (r"^bmc-programmes-aam/rumaker/", "pièce du dépouillement de Rumaker", "lue par construire_rumaker.py"),
    ]
    L = []
    for r_, ds, fs in os.walk(DEPOT):
        if "/.git" in r_ or r_.endswith(".git"): continue
        for f in fs:
            if not re.search(r"\.(json|jsonl)(\.gz)?$", f): continue
            p = rel(os.path.join(r_, f))
            st, note = next(((s, n) for rx, s, n in regles if re.search(rx, p)), ("à classer", ""))
            L.append({"fichier": p, "octets": os.path.getsize(os.path.join(DEPOT, p)), "statut": st, "note": note})
    L.sort(key=lambda x: x["fichier"])
    with open(os.path.join(SORTIE, "catalogue.csv"), "w", encoding="utf-8", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=list(L[0].keys())); w.writeheader(); w.writerows(L)
    return L


def main():
    os.makedirs(SEM, exist_ok=True)
    forcer = "--forcer" in sys.argv
    resume = []
    for f in (duberman, harris, ferme, asheville):
        nom, out = f()
        p = os.path.join(SEM, nom)
        txt = json.dumps(out, ensure_ascii=False, indent=1)
        if os.path.exists(p) and not forcer:
            ancien = json.load(open(p, encoding="utf-8")); ancien["_meta"]["compile_le"] = out["_meta"]["compile_le"]
            if json.dumps(ancien, ensure_ascii=False, indent=1) != txt: sys.exit(f"{rel(p)} existe et diffère : relancer avec --forcer (git garde l'ancien)")
        open(p, "w", encoding="utf-8").write(txt + "\n")
        resume.append((nom, out["_meta"]))
        print(f"{rel(p)} : {json.dumps(out['_meta']['controles'], ensure_ascii=False)}")
        for v in out["_meta"]["variantes_verifiees"]:
            print("   ", os.path.basename(v["fichier"]), {k: x for k, x in v.items() if k not in ("fichier", "sha1", "octets", "note")})
    for f in (relations, enrichissements):
        p, out = f()
        open(p, "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
        print(f"{rel(p)} : {json.dumps(out['_meta']['controles'], ensure_ascii=False)}")
    L = catalogue()
    N = collections.Counter(x["statut"] for x in L)
    M = ["# Catalogue des JSON du dépôt (rangement du 2/11/2026)", "",
         f"{len(L)} fichiers JSON (dont {sum(1 for x in L if 'asheville_bmc_collection' in x['fichier'])} métadonnées de fiches du musée). "
         "Liste complète : `catalogue.csv`. Généré par `bmc-programmes-aam/scripts/json_ranger.py`.", "",
         "| statut | fichiers |", "|---|---|"] + [f"| {k} | {v} |" for k, v in N.most_common()] + ["",
         "## Sources du semainier compilées (`DATA_BMC/json/semainier/`)", "",
         "Un fichier par source, complet (toutes les variantes vérifiées, rien ne manque), unique (doublons marqués, pas de "
         "version concurrente en service) et autonome (`_meta` : description, champs, provenance avec sha1, contrôles, scripts "
         "qui le lisent). Les originaux et les variantes sont rangés dans `DATA_BMC/Chronos/_versions/` (git mv).", ""]
    for nom, m in resume:
        M += [f"### {nom}", "", m["titre"] + ".", "", f"- Origine : `{m['fichier_origine']['fichier']}` (sha1 {m['fichier_origine']['sha1'][:12]}).",
              "- Contrôles : " + ", ".join(f"{k} {v}" for k, v in m["controles"].items()) + "."]
        M += [f"- Variante `{os.path.basename(v['fichier'])}` : " + ", ".join(f"{k.replace('_', ' ')} {x}" for k, x in v.items() if k not in ("fichier", "sha1", "octets", "note")) + f" ({v['note']})." for v in m["variantes_verifiees"]]
        M.append("")
    M += ["## Hors semainier (`DATA_BMC/json/hors_semainier/`)", ""]
    M += [f"- `{x['fichier']}` — {x['statut']}" for x in L if x["fichier"].startswith("DATA_BMC/json/hors_semainier/")]
    M += ["", "## Autres JSON (en place)", ""]
    for st in N:
        if st.startswith(("source du semainier (compilé)", "hors semainier", "version rangée")): continue
        fs = [x["fichier"] for x in L if x["statut"] == st]
        M.append(f"- **{st}** ({len(fs)}) : " + ", ".join(f"`{f}`" for f in fs[:6]) + (" …" if len(fs) > 6 else ""))
    open(os.path.join(SORTIE, "CATALOGUE.md"), "w", encoding="utf-8").write("\n".join(M) + "\n")
    print(f"catalogue : {len(L)} JSON — " + ", ".join(f"{k} {v}" for k, v in N.most_common()))


if __name__ == "__main__":
    main()
