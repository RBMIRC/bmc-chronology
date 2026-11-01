"""Assemble extraction/*.txt en programme jour par jour.
Sorties dans programme/ : evenements.csv, cours_par_periode.csv, calendrier_periodes.csv,
programme_jour_par_jour.md. Option --verifier : contrôle seulement."""
import os, re, sys, csv, json, datetime as dt, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deduction import evaluer
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT = os.path.join(ROOT, "extraction"); OUT = os.path.join(ROOT, "programme")
JOURS = ["lun", "mar", "mer", "jeu", "ven", "sam", "dim"]
JOURS_FR = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
MOIS_FR = ["", "janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
           "septembre", "octobre", "novembre", "décembre"]
TYPES = set("cours atelier conference concert theatre danse reunion radio travail calendrier examen social expo visite sortie autre".split())

def meta():
    F = json.load(open(os.path.join(ROOT, "fiches.json")))
    p = os.path.join(ROOT, "fiches_sondees.json")
    if os.path.exists(p): F += json.load(open(p))
    return {f["accession"]: f for f in F}

def resoudre(tok, ref):
    tok = tok.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", tok): return [dt.date.fromisoformat(tok)]
    if re.fullmatch(r"\d{2}-\d{2}", tok):
        m, d = map(int, tok.split("-"))
        c = []
        for k in (-1, 0, 1):
            try: c.append(dt.date(ref.year + k, m, d))
            except ValueError: pass
        return [min(c, key=lambda x: abs((x - ref).days))]
    if tok == "0": return [ref]
    if re.fullmatch(r"[+-]\d+", tok): return [ref + dt.timedelta(days=int(tok))]
    m = re.fullmatch(r"([+-])(lun|mar|mer|jeu|ven|sam|dim)", tok)
    if m:
        w = JOURS.index(m.group(2)); s = 1 if m.group(1) == "+" else -1
        d = ref + dt.timedelta(days=s)
        while d.weekday() != w: d += dt.timedelta(days=s)
        return [d]
    m = re.fullmatch(r"R:([a-z,]+)@(\S+)\.\.(\S+)", tok)
    if m:
        ws = [JOURS.index(x) for x in m.group(1).split(",")]
        a, b = resoudre(m.group(2), ref)[0], resoudre(m.group(3), ref)[0]
        out = []; d = a
        while d <= b:
            if d.weekday() in ws: out.append(d)
            d += dt.timedelta(days=1)
        return out
    raise ValueError(f"date illisible : {tok!r}")

DEJA_ATTRIB = r"enseignant(e)?s? (probables?|déduite?s?|d.après)|attribution"

def lire():
    ev, cours, cal, err = [], [], [], []
    for fn in sorted(os.listdir(EXT)):
        if not fn.endswith(".txt") or fn.startswith("_"): continue
        acc = fn[:-4]; ref = None; sans_noms = False
        for n, line in enumerate(open(os.path.join(EXT, fn), encoding="utf-8"), 1):
            line = line.rstrip("\n")
            if not line.strip() or line.startswith("//"): continue
            if line.startswith("#ref"):
                ref = dt.date.fromisoformat(line.split()[1]); continue
            if line.startswith("#grille_sans_noms"):
                sans_noms = True; continue
            if line.startswith("#revu_evenements"): continue
            p = line.split("|")
            try:
                if p[0] == "E":
                    if len(p) != 9: raise ValueError(f"{len(p)} champs au lieu de 9")
                    _, d, h1, h2, ty, quoi, qui, lieu, note = p
                    if ty not in TYPES: raise ValueError(f"type inconnu {ty}")
                    dates = resoudre(d, ref)
                    if sans_noms and qui.strip() and re.search(r"grille", note, re.I) and not re.search(DEJA_ATTRIB, note, re.I):
                        note = (note + " ; " if note else "") + "enseignant déduit (la grille ne nomme personne)"
                    pct, mot = evaluer("E", d, note)
                    for x in dates:
                        ev.append(dict(date=x, debut=h1, fin=h2, type=ty, quoi=quoi, qui=qui, lieu=lieu,
                                       note=note, recurrent=d.startswith("R:"), source=acc, pct=pct, motifs=mot))
                elif p[0] == "C":
                    if len(p) != 6: raise ValueError(f"{len(p)} champs au lieu de 6")
                    pct, mot = evaluer("C", "", p[5], p[1] + " " + p[4])
                    cours.append(dict(periode=p[1], cours=p[2], enseignant=p[3], horaire=p[4], note=p[5], source=acc, pct=pct, motifs=mot))
                elif p[0] == "T":
                    if len(p) != 5: raise ValueError(f"{len(p)} champs au lieu de 5")
                    deb = resoudre(p[2], ref)[0] if p[2] else None
                    fin = resoudre(p[3], ref)[0] if p[3] else None
                    pct, mot = evaluer("T", "", p[4], p[1])
                    cal.append(dict(libelle=p[1], debut=deb, fin=fin, note=p[4], source=acc, pct=pct, motifs=mot))
                else: raise ValueError("préfixe inconnu")
            except Exception as e:
                err.append(f"{fn}:{n}: {e} :: {line[:90]}")
    return ev, cours, cal, err

def heure_cle(h):
    m = re.match(r"(\d{1,2}):(\d{2})", h or "")
    if m: return int(m.group(1)) * 60 + int(m.group(2))
    return {"matin": 9 * 60, "après-midi": 14 * 60, "soir": 19 * 60 + 59}.get(h, 24 * 60)

def dedoublonner(ev):
    """Même jour + même heure + même type + mêmes premiers mots : on garde une ligne, sources fusionnées.
    Une occurrence déduite d'un horaire récurrent cède la place à une mention explicite le même jour,
    à la même heure et du même type."""
    explicites = {(e["date"], e["debut"], e["type"]) for e in ev if not e["recurrent"] and e["debut"]}
    ev = [e for e in ev if not (e["recurrent"] and e["debut"] and (e["date"], e["debut"], e["type"]) in explicites)]
    vus = {}
    for e in ev:
        k = (e["date"], e["debut"], e["type"], re.sub(r"\W+", " ", e["quoi"].lower())[:40])
        if k in vus:
            if e["source"] not in vus[k]["source"]: vus[k]["source"] += " ; " + e["source"]
            if e["pct"] < vus[k]["pct"]: vus[k]["pct"], vus[k]["motifs"] = e["pct"], e["motifs"]
        else: vus[k] = dict(e)
    return list(vus.values())

MOTS_VIDES = set("the a an of and in for on with by to at de la le du des et from his her their".split())

def jetons(e):
    t = re.findall(r"[a-zà-ÿ']{4,}", (e["quoi"] + " " + e["qui"]).lower())
    return {w for w in t if w not in MOTS_VIDES}

def minutes(h):
    m = re.match(r"(\d{1,2}):(\d{2})", h or "")
    return int(m.group(1)) * 60 + int(m.group(2)) if m else None

def fusion_floue(ev):
    """Un même concert / spectacle / conférence vu dans deux sources (bulletin + programme imprimé) :
    même date, même type, heures compatibles, au moins deux mots significatifs en commun."""
    par_jour = collections.defaultdict(list)
    for e in ev: par_jour[(e["date"], e["type"])].append(e)
    out = []
    for (d, ty), L in par_jour.items():
        if ty not in ("concert", "theatre", "conference", "danse", "examen", "visite", "radio"):
            out += L; continue
        gard = []
        for e in sorted(L, key=lambda x: -len(x["quoi"])):
            for g in gard:
                a, b = minutes(e["debut"]), minutes(g["debut"])
                if a is not None and b is not None and abs(a - b) > 45: continue
                if e["recurrent"] != g["recurrent"]: continue
                if len(jetons(e) & jetons(g)) >= 2:
                    for src in e["source"].split(" ; "):
                        if src not in g["source"]: g["source"] += " ; " + src
                    if e["pct"] < g["pct"]:
                        g["pct"], g["motifs"] = e["pct"], e["motifs"] + " (meilleure des sources fusionnées)"
                    if not g["debut"] and e["debut"]: g["debut"] = e["debut"]
                    if not g["fin"] and e["fin"]: g["fin"] = e["fin"]
                    if not g["lieu"] and e["lieu"]: g["lieu"] = e["lieu"]
                    break
            else:
                gard.append(dict(e))
        out += gard
    return out

def hors_vacances(ev, cal):
    vac = [(c["debut"], c["fin"]) for c in cal if c["debut"] and c["fin"]
           and re.search(r"(?i)vacation|holiday|recess|free period", c["libelle"])]
    def en_vac(d): return any(a < d < b for a, b in vac)
    return [e for e in ev if not (e["recurrent"] and en_vac(e["date"]) and "vacation" not in e["note"].lower())]

if __name__ == "__main__":
    ev, cours, cal, err = lire()
    for e in err: print("ERREUR", e)
    if "--verifier" in sys.argv:
        print(len(ev), "événements,", len(cours), "cours,", len(cal), "périodes"); sys.exit(1 if err else 0)
    M = meta()
    n0 = len(ev)
    ev = hors_vacances(ev, cal)
    ev = dedoublonner(ev)
    ev = fusion_floue(ev)
    print(f"{n0} lignes brutes -> {len(ev)} après retrait des vacances et fusion des doublons")
    ev.sort(key=lambda e: (e["date"], heure_cle(e["debut"]), e["type"]))
    os.makedirs(OUT, exist_ok=True)
    url = lambda s: " ; ".join((M.get(a.strip(), {}).get("url") or "") for a in s.split(";"))
    def doc(s):
        out = []
        for a in s.split(";"):
            a = a.strip(); f = M.get(a, {})
            t = re.sub(r"\s+", " ", f.get("title", "")).strip().strip('"')
            out.append(f"{t} [{f.get('date','')}] (inv. {a})")
        return " ; ".join(out)
    def doc_court(s):
        out = []
        for a in s.split(";"):
            a = a.strip(); t = re.sub(r"\s+", " ", M.get(a, {}).get("title", "")).strip().strip('"')
            t = re.sub(r"^Black Mount[ia]+n College ", "BMC ", t)
            out.append(f"{t[:95]} (inv. {a})")
        return " ; ".join(out)
    with open(os.path.join(OUT, "evenements.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["date", "jour", "debut", "fin", "type", "activite", "qui", "lieu", "note", "recurrent_deduit",
                    "part_deduite_pct", "motifs_deduction", "document_source", "inventaire", "url_source"])
        for e in ev:
            w.writerow([e["date"].isoformat(), JOURS_FR[e["date"].weekday()], e["debut"], e["fin"], e["type"], e["quoi"],
                        e["qui"], e["lieu"], e["note"], "oui" if e["recurrent"] else "", e["pct"], e["motifs"],
                        doc(e["source"]), e["source"], url(e["source"])])
    with open(os.path.join(OUT, "cours_par_periode.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["periode", "cours", "enseignant", "horaire", "note", "part_deduite_pct", "motifs_deduction", "document_source", "inventaire", "url_source"])
        for c in sorted(cours, key=lambda c: (c["periode"], c["enseignant"], c["cours"])):
            w.writerow([c["periode"], c["cours"], c["enseignant"], c["horaire"], c["note"], c["pct"], c["motifs"], doc(c["source"]), c["source"], url(c["source"])])
    with open(os.path.join(OUT, "calendrier_periodes.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["debut", "fin", "libelle", "note", "part_deduite_pct", "motifs_deduction", "document_source", "inventaire", "url_source"])
        for c in sorted(cal, key=lambda c: (c["debut"] or c["fin"] or dt.date.min)):
            w.writerow([c["debut"] or "", c["fin"] or "", c["libelle"], c["note"], c["pct"], c["motifs"], doc(c["source"]), c["source"], url(c["source"])])
    # Markdown lisible jour par jour
    L = ["# Black Mountain College — programme jour par jour", "",
         "D'après les documents OCR de la collection de l'Asheville Art Museum (fonds Theodore Dreier Sr. et autres).",
         "Chaque entrée cite son document source (titre abrégé et n° d'inventaire ; titre complet, date et URL dans evenements.csv).",
         "« déduction » = part de l'entrée qui n'est pas écrite telle quelle dans la source (0 % = attesté ; règles dans LISEZMOI.md).",
         "« (récurrent) » = séance hebdomadaire projetée à partir d'un horaire régulier.", ""]
    an = mo = None
    for e in ev:
        d = e["date"]
        if d.year != an: an = d.year; mo = None; L += ["", f"## {an}", ""]
        if d.month != mo: mo = d.month; L += ["", f"### {MOIS_FR[mo]} {an}", ""]
        h = e["debut"] + (f"–{e['fin']}" if e["fin"] else "")
        qui = f" — {e['qui']}" if e["qui"] else ""
        lieu = f" ({e['lieu']})" if e["lieu"] else ""
        note = f" [{e['note']}]" if e["note"] else ""
        rec = " (récurrent)" if e["recurrent"] else ""
        L.append(f"- **{JOURS_FR[d.weekday()]} {d.day} {MOIS_FR[d.month]}** {h} · *{e['type']}* · {e['quoi']}{qui}{lieu}{note}{rec}"
                 f"  \n  ↳ source : {doc_court(e['source'])} · déduction {e['pct']} %")
    open(os.path.join(OUT, "programme_jour_par_jour.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    os.makedirs(os.path.join(OUT, "par_annee"), exist_ok=True)
    for bloc in re.split(r"\n(?=## \d{4}\n)", "\n".join(L))[1:]:
        an = bloc[3:7]
        open(os.path.join(OUT, "par_annee", f"{an}.md"), "w", encoding="utf-8").write(
            f"# Black Mountain College — {an}, jour par jour\n\n" + bloc.replace("## " + an + "\n", "", 1))
    print(len(ev), "événements ;", len(cours), "cours ;", len(cal), "périodes ;", len(err), "erreurs")
