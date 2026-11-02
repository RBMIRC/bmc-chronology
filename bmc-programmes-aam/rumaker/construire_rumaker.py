"""Dépouillement de Michael Rumaker, Black Mountain Days (2003) → CSV, recoupements, couche du semainier.

Entrée : rumaker/extraction/rumaker.txt (lignes E|…, format de duberman/_FORMAT.txt, lecture du texte corrigé
DATA_BMC/Rumaker/black_mountain_days_v6.txt) et rumaker/paragraphes_pages.json (¶ → pages du livre, par alignement
sur l'OCR paginé bmc-scenario/texte/007.jsonl.gz).
Part déduite : barème de duberman/construire_duberman.py (calc +5, rel +10, ded/prevu +15, corr +20, approx +25 ;
date plus grossière que le jour +25) et +10 pour un témoignage (mémoires écrits près de cinquante ans après).
Vérification : chaque fait est cherché dans son ¶ (témoins réunis, méthode de scripts/verifier_sources.py).
Recoupement : Duberman et AAM (même période, personne commune et mot commun), scénario (entrées tirées du même livre,
mêmes pages, personne commune).
Sorties (numéro suivant, jamais écrasées) : rumaker/NNN_evenements_rumaker.csv, NNN_rapport_rumaker.md,
et chronos/NNN_rumaker_couche.csv (couche « Chronos et Rumaker » du semainier).
"""
import csv, json, os, re, sys, collections, datetime as dt
ICI = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(ICI); DEPOT = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts")); sys.path.insert(0, os.path.join(ROOT, "duberman"))
import verifier_sources as V
import chronos_commun as K
from construire_duberman import borne, CODES, TYPES, CATEGORIES, GROSSIERE, JOURS

LIVRE = "Michael Rumaker, Black Mountain Days (Asheville, Black Mountain Press, 2003)"


def lire(p):
    with open(p, encoding="utf-8") as f: return list(csv.DictReader(f))


def main():
    paras = [l for l in open(os.path.join(DEPOT, "DATA_BMC", "Rumaker", "black_mountain_days_v6.txt"), encoding="utf-8").read().split("\n") if l.strip()]
    pp = json.load(open(os.path.join(ICI, "paragraphes_pages.json"), encoding="utf-8"))
    dub = lire(os.path.join(ROOT, "duberman", "evenements_duberman.csv"))
    aam = lire(os.path.join(ROOT, "programme", "evenements.csv"))
    scen = [e for e in lire(sorted(os.path.join(ROOT, "scenario", f) for f in os.listdir(os.path.join(ROOT, "scenario")) if f.endswith("_evenements_scenario.csv"))[-1])
            if "Rumaker 2003" in e["document_source"]]
    V.rarete([V.plat(p) for p in paras] + [V.plat(t) for t in V.textes_duberman().values()])
    erreurs, lignes = [], []
    for no, l in enumerate(open(os.path.join(ICI, "extraction", "rumaker.txt"), encoding="utf-8"), 1):
        if not l.startswith("E|"): continue
        f = [x.strip() for x in l.rstrip("\n").split("|")]
        if len(f) != 12: erreurs.append(f"ligne {no} : {len(f)} champs"); continue
        _, date, fin, heure, typ, cat, quoi, qui, lieu, para, codes, note = f
        if typ not in TYPES: erreurs.append(f"ligne {no} : type {typ}")
        if cat not in CATEGORIES: erreurs.append(f"ligne {no} : catégorie {cat}")
        d0, d1, prec = borne(date.lstrip("~"))
        if fin: d1 = borne(fin)[1]; prec = "plage" if prec == "jour" else prec
        cs = [c for c in re.split(r"[ ,;]+", codes) if c]
        pct, mot = 10, ["témoignage : mémoires écrits près de cinquante ans après (+10)"]
        for c in cs: pct += CODES[c][0]; mot.append(f"{CODES[c][1]} (+{CODES[c][0]})")
        if prec in GROSSIERE and "approx" not in cs: pct += 25; mot.append(f"date « {prec.replace('_', ' ')} » seulement (+25)")
        # ¶ et pages
        nums = []
        for a, b in re.findall(r"¶(\d+)(?:-(\d+))?", para):
            nums += list(range(int(a), int(b or a) + 1))
        pages = sorted({p for n in nums for p in pp[n - 1]["pages"] if p.isdigit()}, key=int)
        page = (pages[0] + (f"-{pages[-1]}" if pages[-1] != pages[0] else "")) if pages else ""
        texte = "\n".join(paras[n - 1] for n in nums if 0 < n <= len(paras))
        noms, mots = V.temoins(qui, quoi, False)
        occ = V.occurrences(V.plat(texte), {**{"n:" + a: b for a, b in noms.items()}, **{"m:" + a: b for a, b in mots.items()}})
        win = V.meilleur_passage(occ, {a: (3 if a.startswith("n:") else 1) for a in occ})
        g = lambda pr: {a[2:]: b for a, b in win.items() if a.startswith(pr)}
        verif = V.statut(noms, mots, g("n:"), g("m:"))
        ex = V.extrait(texte, {**{"n" + a: b for a, b in g("n:").items()}, **{"m" + a: b for a, b in g("m:").items()}})
        # recoupements
        ns = K.noms_famille(qui.split(";")) - {"rumaker"}
        mq = {w for w in re.findall(r"[a-z]{5,}", V.plat(quoi)) if w not in V.VIDES} - {w for p in qui.split(";") for w in re.findall(r"[a-z]+", V.plat(p))}
        def recoupe(base, L, champ_qui="qui", champ_txt="activite"):
            hits = []
            for x in L:
                xd = x["date"]; xf = x.get("date_fin") or xd
                if not xd or xd > d1.isoformat() or xf < d0.isoformat(): continue
                xn = K.noms_famille(x[champ_qui].split(";"))
                if ns and not (ns & xn): continue
                com = mq & set(re.findall(r"[a-z]{5,}", V.plat(x[champ_txt] + " " + x.get("note", ""))))
                if com or (ns & xn and prec == "jour"): hits.append((len(com), x))
            hits.sort(key=lambda h: -h[0])
            return f"{base} : {hits[0][1]['date']} « {hits[0][1][champ_txt][:90]} »" if hits else ""
        rd, ra = recoupe("Duberman", dub), recoupe("AAM", aam)
        sc = [e for e in scen if page and set(re.findall(r"\d+", e["document_source"])) & set(pages)
              and (not ns or ns & K.noms_famille(e["qui"].split("; ")))]
        lignes.append({"id": f"r{no}", "date": d0.isoformat(), "date_fin": d1.isoformat() if d1 != d0 else "",
                       "jour": JOURS[d0.weekday()] if prec == "jour" else "", "debut": heure, "precision": prec,
                       "type": typ, "categorie": cat, "activite": quoi, "qui": qui, "lieu": lieu, "note": note,
                       "part_deduite_pct": min(pct, 90), "motifs_deduction": " ; ".join(mot),
                       "document_source": f"{LIVRE}, p. {page} ({para})" if page else f"{LIVRE} ({para})",
                       "paragraphe": para, "page": page, "verif": verif, "recoupement_duberman": rd, "recoupement_aam": ra,
                       "scenario_memes_pages": " ; ".join(f"{e['id']} « {e['activite'][:60]} »" for e in sc[:3]),
                       "_extrait": ex, "date_livre": date + (f" → {fin}" if fin else "")})
    if erreurs: sys.exit("\n".join(erreurs))
    num = K.prochain_numero(ICI)
    cols = [c for c in lignes[0] if not c.startswith("_")]
    with open(os.path.join(ICI, f"{num}_evenements_rumaker.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(lignes)
    nc = K.prochain_numero(K.SORTIE)
    couche = [{"id": f"rm{num}-{l['id']}", "source_chronos": "Rumaker, Black Mountain Days (dépouillement)", "date": l["date"],
               "date_fin": l["date_fin"], "precision": l["precision"], "type": l["type"], "activite": l["activite"],
               "qui": l["qui"], "lieu": l["lieu"],
               "note": " ".join(x for x in (l["note"], ("Recoupement — " + " ; ".join(r for r in (l["recoupement_duberman"], l["recoupement_aam"]) if r)) if (l["recoupement_duberman"] or l["recoupement_aam"]) else "",
                                            ("Scénario, mêmes pages : " + l["scenario_memes_pages"]) if l["scenario_memes_pages"] else "") if x),
               "part_deduite_pct": l["part_deduite_pct"], "motifs_deduction": l["motifs_deduction"],
               "document_source": l["document_source"], "inventaire": "", "url_source": "",
               "statut": "confirmé (Duberman ou AAM)" if (l["recoupement_duberman"] or l["recoupement_aam"]) else "témoignage seul",
               "verif_statut": l["verif"], "verif_extrait": l["_extrait"], "date_source": l["date_livre"]}
              for l in lignes if l["date"] >= "1933-09-01" and l["date"] <= "1957-12-31"]
    with open(os.path.join(K.SORTIE, f"{nc}_rumaker_couche.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(couche[0].keys())); w.writeheader(); w.writerows(couche)
    N = collections.Counter
    R = [f"# Rumaker, Black Mountain Days : dépouillement ({num})", "",
         f"{len(lignes)} faits tirés des 151 phrases datées du texte corrigé (`rumaker/extraction/rumaker.txt`), avec ¶ et page du livre.", "",
         "- Précision : " + ", ".join(f"{k} {v}" for k, v in N(l["precision"] for l in lignes).most_common()) + ".",
         f"- Part déduite moyenne : {sum(l['part_deduite_pct'] for l in lignes) / len(lignes):.1f} %.",
         "- Vérification dans le ¶ cité : " + ", ".join(f"{k} {v}" for k, v in N(l["verif"] for l in lignes).most_common()) + ".",
         f"- Recoupés par Duberman : {sum(1 for l in lignes if l['recoupement_duberman'])} ; par l'AAM : {sum(1 for l in lignes if l['recoupement_aam'])} ; "
         f"déjà dans le scénario (mêmes pages, même personne) : {sum(1 for l in lignes if l['scenario_memes_pages'])}.",
         f"- Couche du semainier : {len(couche)} faits (`chronos/{nc}_rumaker_couche.csv`).", "",
         "## Recoupements et désaccords notés", ""]
    R += [f"- {l['date_livre']} « {l['activite'][:80]} » — {l['note']}" for l in lignes if re.search(r"Duberman|2017\.40|bulletin|catalogue", l["note"])]
    R += ["", "## Faits que ni Duberman, ni l'AAM, ni le scénario ne donnent", ""]
    R += [f"- {l['date_livre']} ({l['paragraphe']}, p. {l['page']}) {l['activite'][:110]}" for l in lignes
          if not (l["recoupement_duberman"] or l["recoupement_aam"] or l["scenario_memes_pages"])]
    open(os.path.join(ICI, f"{num}_rapport_rumaker.md"), "w", encoding="utf-8").write("\n".join(R) + "\n")
    print("\n".join(R[:10]))


if __name__ == "__main__":
    main()
