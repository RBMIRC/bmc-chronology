"""Circuit de traduction anglaise relue (voir semainier/i18n/GUIDE_TRADUCTION.md).

  python3 scripts/traduction_en.py preparer [--taille 100]   lots de ce qui reste à traduire, par priorité :
        semainier/i18n/lots/lot_NNN.tsv  (id, source, contexte, texte français) — jamais écrasés
  (traduction : semainier/i18n/lots/lot_NNN.en.tsv  — une ligne « id<TAB>traduction » par chaîne)
  python3 scripts/traduction_en.py verifier NNN [NNN…] [--partiel] [--remplacer]
        contrôles ; si tout passe, intègre dans revu_en.tsv (--partiel : lot traduit en partie, le reste attend)
  python3 scripts/traduction_en.py etat                       avancement par source
Priorité : Duberman, documents du musée (AAM), reconstitution, compléments (Chronos), notes, livres et études,
puis champs des fiches (lieu, « qui », références, rattachements, renvois, autres versions) et résumés des livres.
revu_en.tsv est additif : une traduction déjà intégrée n'est remplacée qu'avec --remplacer.
"""
import csv, glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import traduire_en as T

ROOT = T.ROOT; I18N = T.I18N; LOTS = os.path.join(I18N, "lots"); REVU = os.path.join(I18N, "revu_en.tsv")
ORDRE = ["Duberman", "AAM", "reconstitution", "Chronos", "note", "livres", "fiches", "resumes"]
OUTILS_FR = re.compile(r"\b(le|la|les|des|du|une|pour|avec|dans|sur|qui|que|chez|selon|puis|aux|au|ses|leur|est|sont|été|à|où|très|après|avant|lors)\b", re.I)
# noms de lieux qui se traduisent (Caroline du Nord → North Carolina…) : pas des noms propres à garder tels quels
LIEUX_FR = {"Caroline", "Floride", "Géorgie", "Virginie", "Californie", "Louisiane", "Pennsylvanie", "Mexique", "Allemagne",
            "Angleterre", "Suisse", "Autriche", "Italie", "Espagne", "Grèce", "Japon", "Chine", "Inde", "Nouvelle", "Orléans", "Londres",
            "Vienne", "Prague", "Moscou", "Russie", "Hollande", "Belgique", "Canada", "Cuba", "Europe", "Amérique", "Pacifique", "Atlantique"}
# titres d'œuvres français gardés tels quels dans l'anglais (guide : « les titres d'œuvres gardent leur langue »)
# graphie corrigée dans la traduction quand le résumé français écorche un nom (« Frederic March » → Fredric March)
ORTHO_NOMS = {"Frederic": "Fredric", "Florace": "Horace", "Fiola": "Flola", "Edith": "Édith", "Victor": "Vicente", "Hild": "Field", "Hore": "Fiore", "Peek": "Peak"}
TITRES_FR = ["L'Honneur des poètes", "Le Déshonneur des poètes", "Le Piège de Méduse", "Le Malade imaginaire", "Le Médecin malgré lui", "Les Précieuses ridicules", "Pelléas et Mélisande", "Les Nuages", "Symphonie pour un homme seul", "Iceberg de poche",
             "Le Sacre du printemps", "Les Demoiselles d'Avignon", "La Cerisaie", "Les Mamelles de Tirésias",
             "Les Mariés de la tour Eiffel"]
GLOSSAIRE = [(r"réunion (du corps enseignant|de la faculté)", "faculty meeting"), (r"\brecteur\b", "rector"),
             (r"programme de travail", "work program"), (r"officiers étudiants", "student officers"),
             (r"salle à manger", "dining hall"), (r"\bBoard of Fellows\b", "Board of Fellows")]


def lire_revu():
    R = {}
    if os.path.exists(REVU):
        for l in open(REVU, encoding="utf-8"):
            if "\t" in l and not l.startswith("#"):
                a, b = l.rstrip("\n").split("\t", 1); R[a] = b
    return R


def sources():
    """texte → (source, contexte) pour toutes les chaînes affichées."""
    D, C, S = T.charge("data.js"), T.charge("data_chronos.js"), T.charge("data_scenario.js")
    ctx = {}
    def ajout(t, src, e=None, extra=""):
        t = (t or "").strip()
        if not t or t in ctx: return
        p = (e or {}).get("extendedProps", {}) if e else {}
        date = (e or {}).get("start", "")[:10] if e else ""
        ctx[t] = (src, "; ".join(x for x in (date, p.get("qui", ""), extra) if x)[:160])
    for e in D["duberman"] + D["duberman_panneau"]: ajout(e["title"], "Duberman", e)
    for e in D["events"]: ajout(e["title"], "AAM", e)
    for Y in D.get("spec", {}).values():
        for g in Y["gabarits"]: ajout(g["activite"], "reconstitution", None, g.get("libelle_terme", ""))
    for e in C["grille"] + C["panneau"]: ajout(e["title"], "Chronos", e, e["extendedProps"].get("source_chronos", ""))
    for e in D["events"] + D["duberman"] + D["duberman_panneau"] + C["grille"] + C["panneau"]: ajout(e["extendedProps"].get("note", ""), "note", e)
    for Y in D.get("spec", {}).values():
        for g in Y["gabarits"]: ajout(g.get("note", ""), "note", None, g.get("activite", ""))
    for e in S["grille"] + S["panneau"]: ajout(e["title"], "livres", e, e["extendedProps"].get("src", "")[:60])
    for p in D["periodes"]: ajout(p["libelle"], "AAM")
    # champs des fiches et résumés des livres (ajoutés en novembre 2026) : mêmes chaînes que traduire_en.chaines("fiches"/"resumes")
    for t in T.chaines("fiches"): ajout(t, "fiches")
    for e in S["grille"] + S["panneau"]: ajout(e["extendedProps"].get("note", ""), "resumes", e, e["extendedProps"].get("src", "")[:60])
    return ctx


def preparer(taille):
    os.makedirs(LOTS, exist_ok=True)
    R, ctx = lire_revu(), sources()
    deja = set(R)
    for f in glob.glob(os.path.join(LOTS, "lot_*.tsv")):
        if f.endswith(".en.tsv"): continue
        for r in csv.reader(open(f, encoding="utf-8"), delimiter="\t"):
            if len(r) == 4 and r[0] != "id": deja.add(r[3])
    a_faire = [(ctx[t][0], t, ctx[t][1]) for t in ctx if t not in deja and T.francais(t) and not T.noms_seuls(t)]
    a_faire.sort(key=lambda x: ORDRE.index(x[0]) if x[0] in ORDRE else 9)
    nums = [int(re.search(r"lot_(\d+)\.tsv$", f).group(1)) for f in glob.glob(os.path.join(LOTS, "lot_*.tsv")) if not f.endswith(".en.tsv")]
    n0 = max(nums, default=0)
    for k in range(0, len(a_faire), taille):
        n0 += 1; p = os.path.join(LOTS, f"lot_{n0:03d}.tsv")
        with open(p, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, delimiter="\t", lineterminator="\n"); w.writerow(["id", "source", "contexte", "fr"])
            for i, (src, t, c) in enumerate(a_faire[k:k + taille], 1): w.writerow([f"{n0:03d}-{i:03d}", src, c.replace("\t", " "), t.replace("\t", " ").replace("\n", " ")])
    print(f"{len(a_faire)} chaînes à traduire → lots {nums and max(nums) + 1 or 1} à {n0}")


def citations(t):   # guillemets imbriqués (« titre « citation » ») : on garde la citation la plus intérieure
    return [q.split("«")[-1].strip() for q in re.findall(r"«\s*([^»]+?)\s*»|“([^”]+)”|\"([^\"]+)\"", t) for q in q if q]


def verifier(num, remplacer=False, partiel=False):
    src = os.path.join(LOTS, f"lot_{num}.tsv"); tr = os.path.join(LOTS, f"lot_{num}.en.tsv")
    L = [r for r in csv.reader(open(src, encoding="utf-8"), delimiter="\t") if len(r) == 4 and r[0] != "id"]
    E = {}
    for l in open(tr, encoding="utf-8"):
        if "\t" in l: a, b = l.rstrip("\n").split("\t", 1); E[a.strip()] = b.strip()
    P = T.charge("data_personnes.js")
    noms = {w for k in P["fiches"] for w in re.findall(r"[A-Z][a-zà-ÿ'’\-]+", re.sub(r'"[^"]*"', " ", k))}
    erreurs, avert = [], []
    for i, _, _, fr in L:
        en = E.get(i)
        if not en:
            if not partiel: erreurs.append(f"{i} : traduction manquante")
            continue
        for q in citations(fr):          # citations des sources (en anglais) : à l'identique ; mots français entre guillemets : traduits
            q = re.sub(r"^(?:la|le|les|un|une|des|l')\s*(?=[a-z])", "", q) if re.match(r"^(?:la|le|les|un|une|des|l')\s*[a-z]+ [a-z]+ (?:of|the|and|to)\b", q) else q   # « la stupendous task of… » : article français collé à la citation
            norm = lambda x: re.sub(r"\s+([;:!?])", r"\1", x).replace("’", "'")
            if not T.francais(q) and re.search(r"[A-Za-z]{3}", q) and not re.search(r"[éèêàùç]", q) and norm(q) not in norm(en):
                # citation à mots outils anglais : bloquante ; mot isolé (anglais ou français ?) : à relire
                (erreurs if T.EN.search(q) and not re.search(r"\b(?:comme|une|les|des|avait|jamais|est|pas|va|se|ne|que|qui|avec|pour|dans|sur|tout|nous|vous|il|elle|n'|qu'|d'|l'|m'|\w+aient|\w{3,}ait)\b", q) else avert).append(f"{i} : citation altérée ou absente « {q[:50]} »")
        hors = re.sub(r"«[^»]*»|“[^”]*”|\"[^\"]*\"|\*[^*]*\*", " ", fr)
        for w in set(re.findall(r"\b[A-Z][a-zà-ÿ'’\-]{2,}\b", hors)):
            if w in noms and w not in en and w not in LIEUX_FR and not (w in ORTHO_NOMS and ORTHO_NOMS[w] in en):   # premier mot (« Avis au tableau ») : peut-être un mot commun
                (avert if re.match(rf"\W*{w}\b", fr) else erreurs).append(f"{i} : nom « {w} » absent")
        MOIS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        for j, m, a in re.findall(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b", hors):   # 25/09/1933 → September 25, 1933 (ou Sept. 25)
            if not (re.search(rf"\b{int(j)}\b", en) and a in en and re.search(MOIS[int(m) - 1][:3], en)): erreurs.append(f"{i} : date {j}/{m}/{a} mal rendue")
        hors = re.sub(r"\b\d{1,2}/\d{1,2}/\d{4}\b", " ", hors)
        for a, m, j in re.findall(r"\b(\d{4})-(\d{2})-(\d{2})\b", hors):   # 1953-11-24 → November 24, 1953
            if not (a in en and 1 <= int(m) <= 12 and re.search(rf"\b{int(j)}\b", en) and re.search(MOIS[int(m) - 1][:3], en)): erreurs.append(f"{i} : date {a}-{m}-{j} mal rendue")
        hors = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", " ", hors)
        for j, m in re.findall(r"\b(\d{1,2})/(\d{1,2})\b", hors):              # bulletin du 23/02 → February 23 bulletin
            if f"{j}/{m}" in en: continue                                      # fraction (chance 1/2), recopiée telle quelle
            if not (1 <= int(m) <= 12 and re.search(rf"\b{int(j)}\b", en) and re.search(MOIS[int(m) - 1][:3], en)): erreurs.append(f"{i} : date {j}/{m} mal rendue")
        hors = re.sub(r"\b\d{1,2}/\d{1,2}\b", " ", hors)
        for h, mn in re.findall(r"\b(\d{1,2})[:h]\s?(\d{2})\b", hors):          # 14:30, 16 h 30 → 2:30 p.m.
            h12 = (int(h) - 1) % 12 + 1
            duree = re.search(rf"\b{int(h)} hours? (?:and )?{int(mn)} minutes\b", en) or (int(h) == 1 and mn == "30" and "hour and a half" in en)   # durée « 1h30 »
            if not duree and not re.search(rf"\b({int(h)}|{h12}):{mn}\b", en): erreurs.append(f"{i} : heure {h}:{mn} mal rendue")
        hors = re.sub(r"\b\d{1,2}[:h]\s?\d{2}\b", " ", hors)
        if re.search(r"\b(?:inch|inches|foot|feet|gallons?|pounds?|miles?|yards?|ounces?)\b|-(?:inch|foot|gallon|pound|mile|yard)\b", en):   # mesures métriques rendues dans les unités américaines d'origine
            hors = re.sub(r"\b\d+(?:[,.]\d+)?(?:\s?[-–à]\s?\d+(?:[,.]\d+)?)?\s?(?:cm|mm|m|km|kg|g|l|litres?|mètres?|kilos?|kilomètres?|centimètres?)\b", " ", hors)
        for n in set(re.findall(r"\b\d+\b", hors)):
            if n not in en and n not in re.sub(r"(\d),(\d{3})\b", r"\1\2", en) and not (len(n) <= 2 and re.search(r"\bh\b|heure", hors)): erreurs.append(f"{i} : nombre {n} absent")
        sans = re.sub(r"“[^”]*”|\"[^\"]*\"|\*[^*]*\*|\([^)]*\)", " ", en)
        for x in TITRES_FR + ["Big Sur", "Des Moines", "La Luz", "Le Corbusier", "Le Nain", "avant-garde", "Comité de lutte contre la répression coloniale", "Comité d'action des intellectuels"]: sans = sans.replace(x, " ")
        # particules des noms propres (Francine du Plessix Gray) et articles des titres d’œuvres (Le Piège de Méduse), repris de l’original
        sans = re.sub(r"\b(?i:du|de|des|la|le|les|un|une)\s+([A-Z][\w'’\-]+)", lambda m: " " if re.sub(r"['’]s$", "", m.group(1)) in fr and m.group(1) not in LIEUX_FR else m.group(0), sans)
        reste = OUTILS_FR.findall(sans)
        if reste: erreurs.append(f"{i} : français restant ({', '.join(sorted(set(reste)))}) : {en[:70]}")
        if re.search(r"\s[:;!?](\s|$)", en): avert.append(f"{i} : espace avant ponctuation")
        for g, v in GLOSSAIRE:
            if re.search(g, fr, re.I) and v.lower() not in en.lower(): avert.append(f"{i} : glossaire « {v} »")
    print(f"lot {num} : {len(L)} chaînes, {len(E)} traduites — {len(erreurs)} erreur(s), {len(avert)} avertissement(s)")
    for x in erreurs[:40] + avert[:20]: print("  ", x)
    if erreurs: return False
    R = lire_revu(); n = 0
    with open(REVU, "a", encoding="utf-8") as f:
        if os.path.getsize(REVU) == 0 if os.path.exists(REVU) else True: f.write("# traductions relues (original\ttraduction) — scripts/traduction_en.py\n")
        for i, _, _, fr in L:
            if i not in E or (fr in R and not remplacer): continue
            f.write(f"{fr}\t{E[i]}\n"); n += 1
    print(f"   intégré : {n} traductions dans revu_en.tsv")
    return True


def etat():
    R, ctx = lire_revu(), sources()
    from collections import Counter
    tot, ok = Counter(), Counter()
    for t, (s, _) in ctx.items():
        if T.francais(t) and not T.noms_seuls(t): tot[s] += 1; ok[s] += t in R
    for s in ORDRE: print(f"{s:15s} {ok[s]:5d} / {tot[s]:5d} relues")
    print(f"{'total':15s} {sum(ok.values()):5d} / {sum(tot.values()):5d}")


if __name__ == "__main__":
    a = sys.argv[1:] or ["etat"]
    if a[0] == "preparer": preparer(int(a[a.index("--taille") + 1]) if "--taille" in a else 100)
    elif a[0] == "verifier": ok = all([verifier(n, "--remplacer" in a, "--partiel" in a) for n in a[1:] if not n.startswith("--")]); sys.exit(0 if ok else 1)
    else: etat()
