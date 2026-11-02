"""Synthèses du scénario (chroniques mensuelles, dossiers de personnages) → semainier, avec recoupements.

Les synthèses de bmc-scenario (étape 06) sont RÉDIGÉES par un modèle de langage à partir des fiches ; elles ne sont
pas des sources. Ce script n'en garde que ce qui renvoie à des fiches (champ « refs ») : chaque élément affiché porte
ses références, et chaque référence son livre et ses pages (vérifiables par scripts/verifier_sources.py). Les champs
de portrait psychologique (noyau, blessures, désirs, peurs, manière d'aimer…) sont laissés au scénario.

Recoupements :
  - présents probables d'un mois (chronique) contre les personnes nommées ce mois-là dans l'AAM et dans Duberman ;
  - périodes de présence d'un dossier contre la première et la dernière activité AAM / Duberman de la personne.

Sorties (scenario/, numéro suivant, jamais écrasées) :
  NNN_chroniques_mois.json   NNN_dossiers.json   NNN_references.json (id de fiche → titre, livre, pages, certitude)
  NNN_recoupement_presences.csv   NNN_rapport_syntheses.md
et semainier/data_syntheses.js (chargé par la page à la demande).
"""
import csv, gzip, json, os, re, sys, glob, collections, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEPOT = os.path.dirname(ROOT)
SORTIE = os.path.join(ROOT, "scenario")
CHAMPS_DOSSIER = ["nom", "autres_noms", "dates_de_vie", "statut_bmc", "presence", "arc_bmc", "avant", "apres",
                  "relations_cles", "contradictions_entre_sources", "questions_ouvertes", "citations"]
CHAMPS_MOIS = ["session", "situation", "presents_probables", "evenements", "quotidien", "tensions", "lacunes"]


def plat(s):
    s = unicodedata.normalize("NFKD", (s or "").lower())
    return re.sub(r"[^a-z0-9 ]+", " ", "".join(c for c in s if not unicodedata.combining(c))).strip()


def nom_famille(n):
    n = re.sub(r"\(.*?\)", "", n or "").strip()
    ws = [w for w in plat(n).split() if len(w) > 1]
    return ws[-1] if ws else ""


def lire(p):
    with open(p, encoding="utf-8") as f: return list(csv.DictReader(f))


def src_txt(x):
    out = []
    for s in x.get("sources") or []:
        pg = ", ".join(str(p).replace("p. ", "") for p in s.get("pages") or [])
        out.append(f"{s.get('titre') or s.get('source')}" + (f", p. {pg}" if pg else ""))
    return " ; ".join(out)


def titre_fiche(x):
    for k in ("titre", "intitule", "idee", "theme", "nom", "texte_original", "moment_present"):
        if x.get(k): return str(x[k])[:160]
    if x.get("personne_a"): return f"{x['personne_a']} — {x.get('personne_b', '')} ({x.get('nature', '')})"
    return x.get("id", "")


def main():
    src = sorted(glob.glob(os.path.join(DEPOT, "bmc-scenario", "sortie", "[0-9][0-9][0-9]_bmc_scenario_*.json*")))[-1]
    S = json.load((gzip.open if src.endswith(".gz") else open)(src, "rt", encoding="utf-8"))
    fiches = {x["id"]: x for cat in S["fiches"].values() for x in cat if isinstance(x, dict) and x.get("id")}
    os.makedirs(SORTIE, exist_ok=True)
    pris = [int(m.group(1)) for fn in os.listdir(SORTIE) if (m := re.match(r"(\d{3})_", fn))]
    num = f"{max(pris, default=0) + 1:03d}"

    # ---------------------------------------------------------------- présences attestées (AAM, Duberman), par mois
    pres = collections.defaultdict(lambda: collections.defaultdict(set))   # nom de famille -> mois -> {bases}
    bornes = collections.defaultdict(lambda: {})                           # nom -> base -> [premier, dernier, n]
    for base, chemin, prec_ok in (("AAM", os.path.join(ROOT, "programme", "evenements.csv"), None),
                                  ("Duberman", os.path.join(ROOT, "duberman", "evenements_duberman.csv"), "jour")):
        for e in lire(chemin):
            if prec_ok and e.get("precision") != prec_ok: continue
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", e["date"]): continue
            for q in (e["qui"] or "").split(";"):
                n = nom_famille(q)
                if len(n) < 3: continue
                pres[n][e["date"][:7]].add(base)
                b = bornes[n].setdefault(base, [e["date"], e["date"], 0])
                b[0] = min(b[0], e["date"]); b[1] = max(b[1], e["date"]); b[2] += 1

    refs_utiles = set()
    def garder_refs(v):
        if isinstance(v, dict):
            for k, x in v.items():
                if k == "refs": refs_utiles.update(r for r in x if re.fullmatch(r"[A-Z]{2}-\d{5}", str(r)))
                else: garder_refs(x)
        elif isinstance(v, list):
            for x in v:
                if isinstance(x, str) and re.fullmatch(r"[A-Z]{2}-\d{5}", x): refs_utiles.add(x)
                else: garder_refs(x)

    # ---------------------------------------------------------------- chroniques mensuelles
    chron, rec = {}, []
    for m in S["chronologie"]["mois"]:
        mo, et = m["mois"], m.get("etat") or {}
        c = {k: et.get(k) for k in CHAMPS_MOIS if et.get(k)}
        for p in c.get("presents_probables") or []:
            n = nom_famille(p.get("nom"))
            bases = sorted(pres.get(n, {}).get(mo, set()))
            p["confirme"] = " + ".join(bases)
            rec.append({"type": "présent probable (chronique)", "mois": mo, "personne": p.get("nom", ""),
                        "certitude_scenario": p.get("certitude", ""), "confirme_ce_mois": " + ".join(bases) or "non",
                        "aam_premier": "", "aam_dernier": "", "aam_n": ""})
        garder_refs(c); chron[mo] = c

    # ---------------------------------------------------------------- dossiers
    doss = {}
    for p in S["personnages"]:
        d = p.get("dossier")
        if not d: continue
        x = {k: d.get(k) for k in CHAMPS_DOSSIER if d.get(k)}
        x["id"], x["mentions"], x["statut"] = p["id"], p.get("mentions"), p.get("statut_bmc")
        n = nom_famille(p["nom"]); b = bornes.get(n, {})
        x["atteste"] = {base: v for base, v in b.items()}
        for per in x.get("presence") or []:
            rec.append({"type": "séjour (dossier)", "mois": f"{per.get('debut') or '?'} → {per.get('fin') or '?'}",
                        "personne": p["nom"], "certitude_scenario": per.get("precision", ""),
                        "confirme_ce_mois": "", "aam_premier": (b.get("AAM") or ["", "", ""])[0],
                        "aam_dernier": (b.get("AAM") or ["", "", ""])[1], "aam_n": (b.get("AAM") or ["", "", ""])[2]})
        garder_refs(x); doss[p["nom"]] = x

    # ---------------------------------------------------------------- références
    refs = {}
    for r in sorted(refs_utiles):
        f = fiches.get(r)
        if not f: refs[r] = {"t": "(fiche introuvable dans le scénario)", "s": "", "c": "", "d": ""}; continue
        a = f.get("ancrage") or {}
        refs[r] = {"t": titre_fiche(f), "s": src_txt(f), "c": f.get("certitude", ""),
                   "d": f.get("date") or a.get("debut") or f.get("periode") or ""}

    # ---------------------------------------------------------------- écriture
    base = os.path.join(SORTIE, num)
    for suff, obj in (("chroniques_mois", chron), ("dossiers", doss), ("references", refs)):
        json.dump(obj, open(f"{base}_{suff}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(f"{base}_recoupement_presences.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rec[0].keys())); w.writeheader(); w.writerows(rec)
    with open(os.path.join(ROOT, "semainier", "data_syntheses.js"), "w", encoding="utf-8") as f:
        f.write(f"// généré par scripts/integrer_syntheses.py ({num}) — ne pas éditer à la main\n")
        f.write("window.BMC_SYNTH = " + json.dumps({"numero": num, "chroniques": chron, "dossiers": doss, "refs": refs},
                                                    ensure_ascii=False, separators=(",", ":")) + ";\n")
    C = collections.Counter
    pp = [r for r in rec if r["type"].startswith("présent")]
    introuv = sum(1 for v in refs.values() if v["t"].startswith("(fiche introuvable"))
    R = [f"# Synthèses du scénario → semainier ({num})", "",
         f"Source : `{os.path.relpath(src, DEPOT)}`. Synthèses rédigées par un modèle de langage à partir des fiches : "
         "seules les parties qui renvoient à des fiches sont reprises, avec leurs références.", "",
         f"- Chroniques mensuelles : {len(chron)} mois ({min(chron)} → {max(chron)}).",
         f"- Dossiers de personnages : {len(doss)} (champs factuels seulement : {', '.join(CHAMPS_DOSSIER)}).",
         f"- Références citées : {len(refs)} fiches ; introuvables dans le scénario : {introuv}.", "",
         "## Recoupement des présences", "",
         f"- « Présents probables » des chroniques : {len(pp)} mentions ; nommés le même mois dans l'AAM ou Duberman : "
         f"{sum(1 for r in pp if r['confirme_ce_mois'] != 'non')} ({100 * sum(1 for r in pp if r['confirme_ce_mois'] != 'non') / max(1, len(pp)):.0f} %) ; "
         f"certitude déclarée : " + ", ".join(f"{k} {v}" for k, v in C(r['certitude_scenario'] for r in pp).most_common()) + ".",
         "- Une absence de confirmation ne réfute rien : beaucoup de mois n'ont aucun document AAM, et une présence ne laisse "
         "pas forcément de trace écrite. Le détail est dans le CSV et dans la chronique du semainier (« attesté ce mois-ci »).",
         f"- Séjours des dossiers : {sum(1 for r in rec if r['type'].startswith('séjour'))} périodes ; la première et la dernière "
         "activité AAM de la personne sont données en regard."]
    open(f"{base}_rapport_syntheses.md", "w", encoding="utf-8").write("\n".join(R) + "\n")
    print("\n".join(R))


if __name__ == "__main__":
    main()
