"""Chronos 4/5 : bmc_chronology.json — ancienne extraction automatique de Duberman (« Chronos 2 », 559 événements)
contre notre dépouillement manuel du texte corrigé (duberman/evenements_duberman.csv, 935 événements).

Les pages de Chronos ne sont pas celles de notre édition ; on se sert de la citation que porte chaque événement
(476 sur 559) : elle est cherchée dans les paragraphes du texte corrigé (duberman/_appui/paged.json), ce qui donne
le ¶ et la page de notre édition. Puis :
  retrouvé ............... un de nos événements couvre ce ¶ (± 1) et sa date est compatible (même année au moins)
  date différente ........ un de nos événements du même ¶ nomme la même personne, à une autre date : à trancher (notre lecture du
                           texte corrigé prime, ordre de confiance du projet)
  absent du dépouillement  citation retrouvée, aucun de nos événements sur ce ¶ : piste (couche Chronos)
  citation introuvable ... la citation n'est pas dans le texte corrigé (paraphrase, autre édition, ou index)
Sans citation : rapprochement par date et nom (même jour ou mois, personne commune).
Sorties : chronos/NNN_duberman_recoupement.csv, _couche.csv, _rapport.md.
"""
import csv, json, os, re, sys, collections, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chronos_commun as K
import verifier_sources as V

TYPE = {"academic": "cours", "artistic": "concert", "personal": "autre", "financial": "autre", "arrival": "autre",
        "political": "autre", "departure": "autre", "event": "autre", "founding": "autre", "other": "autre"}


def lire(p):
    with open(p, encoding="utf-8") as f: return list(csv.DictReader(f))


def mots(s): return re.findall(r"[a-z0-9]+", V.plat(s))


def main():
    C = json.load(open(os.path.join(K.CHRONOS, "bmc_chronology.json"), encoding="utf-8"))
    paged = json.load(open(os.path.join(K.ROOT, "duberman", "_appui", "paged.json"), encoding="utf-8"))
    par = {int(x["i"]): x for x in paged}
    plat_par = {i: " ".join(mots(x["text"])) for i, x in par.items()}
    notes = json.load(open(os.path.join(K.ROOT, "duberman", "_appui", "notes_by_id.json"), encoding="utf-8"))
    plat_notes = {k: " ".join(mots(" ".join(v))) for k, v in notes.items()}
    dub = lire(os.path.join(K.ROOT, "duberman", "evenements_duberman.csv"))
    par_para = collections.defaultdict(list)
    for j, e in enumerate(dub):
        for a, b in re.findall(r"¶(\d+)(?:-(\d+))?", e["paragraphe"]):
            for k in range(int(a), int(b or a) + 1): par_para[k].append((j, e))

    def localiser(quote):
        """(¶ ou clé de note, part de la citation retrouvée)."""
        q = [w for w in mots(re.sub(r"^[A-Z]{2,}:\s*", "", quote or "")) if w]
        if len(q) < 4: return None, 0
        grams = [" ".join(q[i:i + 5]) for i in range(0, max(1, len(q) - 4), 3)]
        best, score = None, 0
        for src in (plat_par, plat_notes):
            for k, t in src.items():
                n = sum(1 for g in grams if g in t)
                if n > score: best, score = k, n
            if score / len(grams) >= 0.5: break
        return best, score / len(grams)

    lignes = []
    for k, e in enumerate(C["events"]):
        d = K.lire_date(e.get("date"))
        pers = [p for p in e.get("people") or [] if isinstance(p, str)]
        para, part = localiser(e.get("quote"))
        trouve = part >= 0.5
        statut, avec, ref, page = "", "", "", ""
        if para is not None and trouve:
            if isinstance(para, int):
                x = par[para]; ref = f"¶{para}"; page = (x["p0"] or "?") + (f"-{x['p1']}" if x["p1"] and x["p1"] != x["p0"] else "")
                cands = [c for q in (para - 1, para, para + 1) for c in par_para.get(q, [])]
            else:
                ref = f"note {para}"; page = "notes"; ch, n = para.split(":")
                cands = [(j, x) for j, x in enumerate(dub) if str(x["chapitre"]) == ch and re.search(rf"\bn{n}\b", x["notes_citees"])]
            if not cands: statut = "absent du dépouillement"
            elif not d: statut, avec = "retrouvé (date illisible chez Chronos)", cands[0][1]["activite"][:120]
            else:
                compat = [c for c in cands if c[1]["date"] and (c[1]["date"][:4] <= d[1][:4] and (c[1]["date_fin"] or c[1]["date"])[:4] >= d[0][:4])]
                if compat: statut, avec = "retrouvé", f"{compat[0][1]['date_livre']} « {compat[0][1]['activite'][:110]} »"
                else:
                    ns = K.noms_famille(pers)
                    meme = [c for c in cands if ns & K.noms_famille(c[1]["qui"].split(";"))]
                    if meme: statut, avec = "date différente", f"{meme[0][1]['date_livre']} « {meme[0][1]['activite'][:110]} »"
                    else: statut, avec = "absent du dépouillement", f"autre fait relevé dans ce paragraphe : {cands[0][1]['date_livre']} « {cands[0][1]['activite'][:90]} »"
        elif e.get("quote"):
            statut = "citation introuvable" + (" (index)" if "index" in (e.get("context") or "").lower() else "")
        else:
            statut = "sans citation"
            if d:
                ns = K.noms_famille(pers)
                hit = [x for x in dub if x["date"] and d[0] <= x["date"] <= d[1] and ns & K.noms_famille(x["qui"].split(";"))]
                if hit: statut, avec = "retrouvé (date et nom)", f"{hit[0]['date_livre']} « {hit[0]['activite'][:110]} »"
        lignes.append({"id": k, "date_chronos": e.get("date", ""), "precision_chronos": e.get("date_precision", ""),
                       "debut": d[0] if d else "", "fin": d[1] if d else "", "precision": d[2] if d else "",
                       "evenement": (e.get("event") or "")[:300], "personnes": "; ".join(pers), "chapitre_chronos": e.get("context", ""),
                       "citation": (e.get("quote") or "")[:400], "citation_retrouvee": f"{part:.0%}" if e.get("quote") else "",
                       "paragraphe": ref, "page_notre_edition": page, "statut": statut, "notre_depouillement": avec,
                       "categorie": e.get("category", "")})

    num = K.prochain_numero(K.SORTIE)
    base = os.path.join(K.SORTIE, f"{num}_duberman")
    with open(base + "_recoupement.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(lignes[0].keys())); w.writeheader(); w.writerows(lignes)
    couche = []
    for l in lignes:
        if l["statut"] != "absent du dépouillement" or not l["debut"]: continue
        if l["fin"] < "1933-09-01" or l["debut"] > "1957-12-31": continue
        if (dt.date.fromisoformat(l["fin"]) - dt.date.fromisoformat(l["debut"])).days > 400: continue
        pct, mot = 10, ["extraction automatique (Chronos 2), citation retrouvée dans le texte corrigé de Duberman (+10)"]
        if l["precision"] not in ("jour", "plage"): pct += 25; mot.append(f"date « {l['precision']} » seulement (+25)")
        texte = par[int(l["paragraphe"][1:])]["text"] if l["paragraphe"].startswith("¶") else " ".join(notes.get(l["paragraphe"][5:], []))
        k0 = V.plat(texte).find(V.plat(l["citation"])[:25])
        ex = V.extrait(texte, {"q": (k0, k0 + min(len(l["citation"]), 220))} if k0 >= 0 else {})
        couche.append({"id": f"cd{num}-{l['id']}", "source_chronos": "Duberman (ancienne extraction Chronos 2)",
                       "date": l["debut"], "date_fin": l["fin"] if l["fin"] != l["debut"] else "", "precision": l["precision"],
                       "type": TYPE.get(l["categorie"], "autre"), "activite": l["evenement"], "qui": l["personnes"], "lieu": "",
                       "note": f"« {l['citation']} »", "part_deduite_pct": min(pct, 90), "motifs_deduction": " ; ".join(mot),
                       "document_source": f"Duberman, Black Mountain: An Exploration in Community (1972, Anchor 1973), p. {l["page_notre_edition"]} ({l['paragraphe']}), d'après Chronos bmc_chronology.json",
                       "inventaire": "", "url_source": "", "statut": "absent de notre dépouillement de Duberman",
                       "verif_statut": "retrouvé", "verif_extrait": ex, "date_source": l["date_chronos"]})
    with open(base + "_couche.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(couche[0].keys())); w.writeheader(); w.writerows(couche)
    N = collections.Counter
    st = N(l["statut"] for l in lignes)
    R = [f"# Chronos 4/5 : bmc_chronology.json (Duberman, « Chronos 2 ») contre notre dépouillement ({num})", "",
         f"Source : `DATA_BMC/Chronos/bmc_chronology.json` ({len(lignes)} événements, extraction du {C['metadata'].get('extraction_date', '')[:10]}). "
         "Référence : `duberman/evenements_duberman.csv` (935 événements, lecture manuelle du texte corrigé).", "",
         "| statut | événements |", "|---|---|"] + [f"| {k} | {v} |" for k, v in st.most_common()]
    R += ["", "- Citations retrouvées dans le texte corrigé (≥ 50 % des segments de cinq mots) : "
          f"{sum(1 for l in lignes if l['paragraphe'])} sur {sum(1 for l in lignes if l['citation'])}.",
          f"- Couche Chronos : {len(couche)} événements absents de notre dépouillement, citation retrouvée, 1933-1957, ≤ 13 mois.", "",
          "## Dates différentes (à trancher ; notre lecture du texte corrigé prime)", ""]
    R += [f"- {l['paragraphe']} p. {l['page_notre_edition']} : Chronos {l['date_chronos']} « {l['evenement'][:90]} » / notre dépouillement {l['notre_depouillement'][:120]}" for l in lignes if l["statut"] == "date différente"]
    R += ["", "## Absents de notre dépouillement (citation retrouvée)", ""]
    R += [f"- {l['paragraphe']} p. {l['page_notre_edition']} · {l['date_chronos']} · {l['evenement'][:120]}" for l in lignes if l["statut"] == "absent du dépouillement"]
    open(base + "_rapport.md", "w", encoding="utf-8").write("\n".join(R) + "\n")
    print("\n".join(R[:16]))


if __name__ == "__main__":
    main()
