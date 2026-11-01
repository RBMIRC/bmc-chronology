"""05 — Fusion des extractions : noms canoniques, ancrage dans le temps, doublons.

Sans appel au modèle. Pour chaque catégorie, une liste d'entrées numérotées,
chacune avec :
  sources   [{source, titre, pages, morceau}]  — toujours citable
  ancrage   {debut, fin, precision, deduit}     — situe l'entrée dans les 24 ans
  personnes noms canoniques
Les faits rapportés par plusieurs sources sont réunis, chaque version gardée.
Sorties : fusion/<categorie>.json, fusion/_noms.csv (à relire), fusion/_bilan.txt
"""
import csv
import json
import re
import shutil
import time
from collections import Counter, defaultdict

from rapidfuzz import fuzz
from unidecode import unidecode

from config import EXTRACTIONS, FICTION, FUSION, REFERENTIEL
from schema import CATEGORIES

PREFIXE = {"evenements": "EV", "personnes": "PE", "relations": "RE", "cours": "CO", "idees": "ID",
           "lieux": "LI", "quotidien": "QU", "scenes": "SC", "citations": "CI", "oeuvres": "OE",
           "conflits": "CF", "echos": "EC"}
# champs qui portent des noms de personnes
CHAMPS_NOMS = {"evenements": ["personnes"], "scenes": ["personnages"], "relations": ["personne_a", "personne_b"],
               "cours": ["enseignant"], "idees": ["auteur"], "citations": ["locuteur"], "oeuvres": ["auteur"],
               "personnes": ["nom"]}
TITRES = re.compile(r"^(mr|mrs|miss|ms|dr|prof|professor|herr|frau)\.?\s+")
DATE_ISO = re.compile(r"^(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?")
ANNEE = re.compile(r"\b(18[5-9]\d|19\d\d|20[0-2]\d)\b")


# ---------------------------------------------------------------- noms

def norm(n):
    n = unidecode(n or "").lower().strip()
    n = re.sub(r"\(.*?\)", "", n)
    n = TITRES.sub("", n)
    n = re.sub(r"[^a-z\s\-]", " ", n)
    return re.sub(r"\s+", " ", n).strip()


COLLECTIF = re.compile(r"etudiant|communaute|groupe|temoin|anonyme|famille|professeurs|faculte|"
                       r"inconnu|plusieurs|habitants|enfants|tous|public|foule|membres|visiteurs")
SUFFIXES = {"jr", "sr", "ii", "iii"}
PARTICULES = {"de", "van", "von", "du", "der", "da", "di", "la", "le", "del", "den", "ter", "dite", "dit"}
PARENTE = {"mere", "pere", "fils", "fille", "femme", "mari", "frere", "soeur", "oncle", "tante", "epouse", "veuve",
           "ami", "amie", "cousin", "cousine", "enfant", "bebe", "mother", "father", "wife", "husband", "son",
           "daughter", "brother", "sister", "grand-mere", "grand-pere", "madame", "monsieur", "mme", "mlle"}
LISTE = re.compile(r"\s(et|ou|and|avec|dont|with)\s|/|,|;|\?|&|\+")


def a_un_titre(n):
    return bool(TITRES.match(unidecode(n or "").lower().strip()))


def propre(n):
    """Un vrai nom de personne : majuscule initiale, 2 à 5 mots, ni liste ni description."""
    n = re.sub(r"\(.*?\)", "", n or "").strip()
    if not n or not n[0].isupper() or LISTE.search(n) or a_un_titre(n):
        return False
    mots = n.split()
    if any(unidecode(m).lower() in PARENTE for m in mots):
        return False
    return 2 <= len(mots) <= 5 and all(
        m[0].isupper() or m.lower() in PARTICULES or m.lower().strip(".") in SUFFIXES for m in mots)


def sans_suffixe(k):
    return [m for m in k.split() if m not in SUFFIXES]


def charger_distincts():
    """Paires à ne jamais fusionner (referentiel/distincts.csv : nom_a,nom_b)."""
    chemin = REFERENTIEL / "distincts.csv"
    if not chemin.exists():
        return set()
    with open(chemin, newline="") as f:
        return {frozenset((norm(r["nom_a"]), norm(r["nom_b"]))) for r in csv.DictReader(f)}


DISTINCTS = charger_distincts()


def voisins(a, b):
    """Même personne mal orthographiée ? Prénom identique et nom de famille proche, ou nom
    identique et prénom à une lettre près (jamais Johann / Johanna, jamais une initiale)."""
    if frozenset((a, b)) in DISTINCTS:
        return False
    if {m for m in a.split() if m in SUFFIXES} != {m for m in b.split() if m in SUFFIXES}:
        return False  # le père (Sr.) n'est pas le fils (Jr.)
    ma, mb = sans_suffixe(a), sans_suffixe(b)
    if len(ma) < 2 or len(mb) < 2 or len(ma[0]) < 3 or len(mb[0]) < 3:
        return False
    if ma[0] == mb[0] and len(ma[-1]) >= 5 and fuzz.ratio(ma[-1], mb[-1]) >= 88:
        return True
    return ma[-1] == mb[-1] and len(ma[0]) == len(mb[0]) and sum(x != y for x, y in zip(ma[0], mb[0])) <= 1


def forme(n):
    return re.sub(r"\s+", " ", unidecode(n or "").lower()).strip()


class Noms:
    def __init__(self):
        self.vers = {}            # forme normalisée → nom canonique
        self.local = {}           # (source, forme) → nom canonique, propre à un livre
        self.formes = {}          # forme normalisée non résolue → graphie la plus fréquente
        self.fusions = []         # (forme, canonique, raison) à relire
        self.reels = set()        # noms du référentiel (personnes réelles connues)
        with open(REFERENTIEL / "alias.csv", newline="") as f:
            for r in csv.DictReader(f):
                self.vers[norm(r["canonique"])] = r["canonique"]
                self.reels.add(norm(r["canonique"]))
                for a in filter(None, r["alias"].split("|")):
                    self.vers[norm(a)] = r["canonique"]
                    self.reels.add(norm(a))

    def apprendre(self, vus, vus_par_source, alias_source):
        """vus : Counter des noms bruts ; vus_par_source : {source: set(noms)} ;
        alias_source : {(source, forme): nom} tiré des « autres_noms » des fiches personnes."""
        # graphies d'un nom non résolu : on ne réunit que celles qui diffèrent par les accents ou la casse
        for n in sorted(vus, key=lambda n: -vus[n]):
            self.formes.setdefault(forme(n), n.strip())
        complets = sorted({n for n in vus if propre(n) and not COLLECTIF.search(norm(n))}, key=lambda n: -vus[n])
        for n in complets:
            k = norm(n)
            if k in self.vers:
                continue
            proche = next((c for c in set(self.vers.values()) if propre(c) and voisins(k, norm(c))), None)
            if proche:
                self.vers[k] = proche
                self.fusions.append((n, proche, "graphie voisine"))
            else:
                self.vers[k] = n
        canons = {c for c in set(self.vers.values()) if propre(c)}
        par_nom, prenoms_connus = defaultdict(set), set()
        for c in canons:
            mots = sans_suffixe(norm(c))
            par_nom[mots[-1]].add(c)
            prenoms_connus.add(mots[0])
        for source, presents in vus_par_source.items():
            ici = {self.vers.get(norm(n)) for n in presents} & canons
            prenoms_ici, noms_ici = defaultdict(set), defaultdict(set)
            for c in ici:
                mots = sans_suffixe(norm(c))
                prenoms_ici[mots[0]].add(c)
                noms_ici[mots[-1]].add(c)
            for n in presents:
                k = norm(n)
                if k in self.vers or len(k.split()) != 1 or COLLECTIF.search(k) or not n.strip()[:1].isupper():
                    continue
                cible, raison = None, ""
                precise = "(" in n  # « David (étudiant de l'Ohio) » : la parenthèse désigne quelqu'un d'autre
                if (source, k) in alias_source and not precise:
                    cible, raison = alias_source[(source, k)], f"autre nom donné dans la source {source}"
                elif precise or a_un_titre(n):
                    pass
                elif len(prenoms_ici.get(k, ())) == 1:
                    cible, raison = next(iter(prenoms_ici[k])), f"prénom unique dans la source {source}"
                elif len(noms_ici.get(k, ())) == 1:
                    cible, raison = next(iter(noms_ici[k])), f"nom de famille unique dans la source {source}"
                elif k not in prenoms_connus and len(par_nom.get(k, ())) == 1:
                    cible, raison = next(iter(par_nom[k])), "nom de famille d'une seule personne"
                if cible:
                    self.local[(source, k)] = cible
                    self.fusions.append((n, cible, raison))

    def __call__(self, n, source=None):
        k = norm(n)
        return self.vers.get(k) or self.local.get((source, k)) or self.formes.get(forme(n)) or (n or "").strip()


# ---------------------------------------------------------------- temps

def parse_date(d):
    m = DATE_ISO.match(d or "")
    if not m:
        return None
    a, mo, j = m.groups()
    return "-".join(x for x in (a, mo, j) if x)


def ancrage(e, cadre):
    """Situe une entrée : sa propre date, sinon les années de son texte, sinon le cadre du passage."""
    debut, fin = parse_date(e.get("date")), parse_date(e.get("date_fin"))
    if debut:
        return {"debut": debut, "fin": fin or debut, "precision": e.get("precision") or "inconnue", "deduit": False}
    texte = " ".join(str(e.get(k) or "") for k in ("periode", "presence_bmc", "titre"))
    annees = sorted({int(a) for a in ANNEE.findall(texte)})
    if annees:
        return {"debut": str(annees[0]), "fin": str(annees[-1]), "precision": "annee", "deduit": False}
    cd, cf = parse_date((cadre or {}).get("debut")), parse_date((cadre or {}).get("fin"))
    if cd:
        return {"debut": cd, "fin": cf or cd, "precision": "periode", "deduit": True}
    return {"debut": None, "fin": None, "precision": "inconnue", "deduit": True}


# ---------------------------------------------------------------- fusion

def cle_texte(e):
    return " ".join(str(e.get(k) or "") for k in ("titre", "description", "deroule", "idee", "texte_original"))[:400]


def meme_fait(a, b, cat):
    """Deux entrées de sources différentes racontent-elles la même chose ?"""
    if cat == "citations":
        return fuzz.ratio(norm(a["texte_original"]), norm(b["texte_original"])) >= 85
    if cat not in ("evenements", "scenes", "conflits", "oeuvres"):
        return False
    pa, pb = set(a["personnes"]), set(b["personnes"])
    if pa and pb and not pa & pb:
        return False
    ya, yb = (a["ancrage"]["debut"] or "")[:4], (b["ancrage"]["debut"] or "")[:4]
    if ya and yb and ya != yb:
        return False
    return fuzz.token_set_ratio(norm(a.get("titre", "")), norm(b.get("titre", ""))) >= 82 or \
        fuzz.token_set_ratio(norm(cle_texte(a)), norm(cle_texte(b))) >= 78


def main():
    FUSION.mkdir(exist_ok=True)
    fichiers = sorted(EXTRACTIONS.glob("*.json"))
    extraits = [json.load(open(f)) for f in fichiers]

    vus = Counter()
    vus_par_source = defaultdict(set)
    cibles_alias = defaultdict(set)
    vus_fiction = Counter()
    for x in extraits:
        d = x["donnees"]
        if x["source"] in FICTION:
            for cat, champs in CHAMPS_NOMS.items():
                for e in d[cat]:
                    for c in champs:
                        v = e.get(c)
                        vus_fiction.update(n.strip() for n in (v if isinstance(v, list) else [v]) if n)
            continue
        for p in d["personnes"]:
            vus[p["nom"]] += 3
            vus_par_source[x["source"]].add(p["nom"])
            if propre(p["nom"]):
                for a in p.get("autres_noms") or []:
                    if len(norm(a).split()) == 1:
                        cibles_alias[(x["source"], norm(a))].add(p["nom"])
        for cat, champs in CHAMPS_NOMS.items():
            for e in d[cat]:
                for c in champs:
                    v = e.get(c)
                    for n in (v if isinstance(v, list) else [v]):
                        if n:
                            vus[n] += 1
                            vus_par_source[x["source"]].add(n)
    noms = Noms()
    alias_source = {k: noms(next(iter(v))) for k, v in cibles_alias.items() if len(v) == 1}
    noms.apprendre(vus, vus_par_source, alias_source)

    graphie_fiction = {}
    for n, _ in vus_fiction.most_common():
        graphie_fiction.setdefault(forme(n), n)

    def nommer(n, x):
        """Nom canonique ; dans un roman, les personnages restent à part."""
        if not n:
            return n
        if x["source"] in FICTION and norm(n) not in noms.reels:
            return f"{graphie_fiction.get(forme(n), n.strip())} (personnage, {x['source_court']})"
        return noms(n, x["source"])

    brut = defaultdict(list)
    motifs = Counter()
    resumes = []
    for x in extraits:
        d = x["donnees"]
        cadre = d.get("cadre_temporel")
        src = {"source": x["source"], "titre": x["source_court"], "morceau": x["morceau"]}
        resumes.append({"morceau": x["morceau"], "source": x["source"], "titre": x["source_court"],
                        "pertinence": d["pertinence"], "cadre_temporel": cadre, "resume": d["resume"]})
        motifs.update(m.strip().lower() for m in d.get("motifs", []))
        for cat in CATEGORIES:
            for e in d[cat]:
                e = dict(e)
                e["sources"] = [{**src, "pages": e.pop("pages", [])}]
                e["ancrage"] = ancrage(e, cadre)
                for c in CHAMPS_NOMS.get(cat, []):
                    v = e.get(c)
                    e[c] = [nommer(n, x) for n in v] if isinstance(v, list) else nommer(v, x)
                if cat in ("evenements", "scenes"):
                    e["personnes"] = sorted(set(e.get("personnes") or e.get("personnages") or []))
                else:
                    e["personnes"] = sorted({e[c] for c in CHAMPS_NOMS.get(cat, []) if isinstance(e.get(c), str)})
                brut[cat].append(e)

    # la fusion précédente est gardée à part : ses identifiants sont repris tant que possible
    if (FUSION / "evenements.json").exists():
        copie = FUSION / f"_precedente_{time.strftime('%Y%m%d-%H%M')}"
        copie.mkdir()
        for f in FUSION.glob("*.json"):
            shutil.copy2(f, copie / f.name)
    redirections = {}  # toujours recalculées depuis fusion/_reference
    bilan = []
    for cat in CATEGORIES:
        entrees = sorted(brut[cat], key=lambda e: (e["ancrage"]["debut"] or "9999", e["sources"][0]["morceau"]))
        if cat == "personnes":
            fusion = regrouper_personnes(entrees)
        else:
            fusion = []
            for e in entrees:
                cible = next((f for f in fusion[-300:]
                              if f["sources"][0]["source"] != e["sources"][0]["source"] and meme_fait(f, e, cat)), None)
                if cible:
                    cible.setdefault("autres_versions", []).append(
                        {k: v for k, v in e.items() if k not in ("ancrage", "personnes")})
                    cible["sources"] += e["sources"]
                    cible["personnes"] = sorted(set(cible["personnes"]) | set(e["personnes"]))
                else:
                    fusion.append(e)
        redirections.update(stabiliser(cat, fusion, noms))
        json.dump(fusion, open(FUSION / f"{cat}.json", "w"), ensure_ascii=False, indent=1)
        bilan.append(f"{cat:11s} {len(brut[cat]):6d} extraites → {len(fusion):6d} après fusion")

    # chaînes de redirection résolues jusqu'au bout (A → B → C devient A → C)
    for k in list(redirections):
        v, vus_ = redirections[k], {k}
        while v in redirections and v not in vus_:
            vus_.add(v)
            v = redirections[v]
        redirections[k] = v
    json.dump(redirections, open(FUSION / "_redirections.json", "w"), ensure_ascii=False, indent=1)
    json.dump(resumes, open(FUSION / "passages.json", "w"), ensure_ascii=False, indent=1)
    json.dump(motifs.most_common(), open(FUSION / "motifs.json", "w"), ensure_ascii=False, indent=1)
    with open(FUSION / "_noms.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["forme_vue", "rattachee_a", "raison", "occurrences"])
        for vue, c, raison in noms.fusions:
            w.writerow([vue, c, raison, vus[vue]])
        resolus = {f for f, _, _ in noms.fusions}
        seuls = [n for n in vus if len(norm(n).split()) == 1 and norm(n) not in noms.vers and n not in resolus]
        for n in sorted(seuls, key=lambda n: -vus[n]):
            w.writerow([n, "", "nom seul non résolu", vus[n]])
    txt = "\n".join([f"{len(extraits)} morceaux fusionnés"] + bilan +
                    [f"noms rattachés automatiquement : {len(noms.fusions)} (voir _noms.csv)"])
    (FUSION / "_bilan.txt").write_text(txt + "\n")
    print(txt)


HORS_EMPREINTE = {"sources", "ancrage", "personnes", "id", "autres_versions"}


def empreinte(v, cat):
    """Texte propre d'une fiche, sans les champs de noms (qui changent quand on corrige les noms)."""
    exclus = HORS_EMPREINTE | set(CHAMPS_NOMS.get(cat, []))
    morceaux = [str(v[k]) for k in sorted(v) if k not in exclus and isinstance(v[k], (str, int, float))]
    return norm(" ".join(morceaux))[:240]


def cles(e, cat):
    """Empreintes d'une fiche fusionnée (elle-même et ses autres versions), pour la retrouver
    d'une fusion à l'autre."""
    if cat == "personnes":
        return [("nom", e["nom"])]
    return [(v["sources"][0]["morceau"], empreinte(v, cat)) for v in [e] + e.get("autres_versions", [])]


def stabiliser(cat, fusion, noms):
    """Numérote les fiches en reprenant les identifiants de la fusion précédente :
    les synthèses déjà rédigées y renvoient. Renvoie {ancien_id: nouvel_id} pour les fiches absorbées."""
    # référence = la fusion sur laquelle les synthèses ont été rédigées
    chemin = FUSION / "_reference" / f"{cat}.json"
    if not chemin.exists():
        chemin = FUSION / f"{cat}.json"
    anciens = json.load(open(chemin)) if chemin.exists() else []
    vers_ancien = defaultdict(list)
    for a in anciens:
        for k in cles(a, cat):
            vers_ancien[k].append(a["id"])
    pris, suivant = set(), 1 + max((int(a["id"][3:]) for a in anciens), default=0)
    a_numeroter = []
    for e in fusion:
        id_ = next((i for k in cles(e, cat) for i in vers_ancien.get(k, []) if i not in pris), None)
        if id_:
            e["id"] = id_
            pris.add(id_)
        else:
            a_numeroter.append(e)
    for e in a_numeroter:
        e["id"] = f"{PREFIXE[cat]}-{suivant:05d}"
        suivant += 1
    # anciennes fiches absorbées : vers la fiche qui contient leur empreinte (ou leur nouveau nom)
    par_cle = {k: e["id"] for e in fusion for k in cles(e, cat)}
    redir = {}
    for a in anciens:
        if a["id"] in pris:
            continue
        if cat == "personnes":
            src = a["sources"][0]["source"] if a.get("sources") else None
            cible = par_cle.get(("nom", noms(a["nom"], src)))
        else:
            cible = next((par_cle[k] for k in cles(a, cat) if k in par_cle), None)
        if cible:
            redir[a["id"]] = cible
    return redir


def regrouper_personnes(fiches):
    """Une fiche par personne ; chaque trait garde sa source."""
    par_nom = {}
    for f in fiches:
        p = par_nom.setdefault(f["nom"], {"nom": f["nom"], "autres_noms": set(), "statut_bmc": Counter(),
                                          "traits": defaultdict(list), "sources": [], "personnes": [f["nom"]]})
        p["autres_noms"] |= set(f.get("autres_noms") or [])
        p["statut_bmc"][f.get("statut_bmc")] += 1
        p["sources"] += f["sources"]
        for k in ("presence_bmc", "apparence", "temperament", "psychologie", "manieres_et_voix", "habitudes",
                  "convictions", "contradictions", "avant_bmc", "apres_bmc"):
            if f.get(k):
                p["traits"][k].append({"texte": f[k], "certitude": f.get("certitude"), **f["sources"][0]})
    sortie = []
    for p in sorted(par_nom.values(), key=lambda p: -len(p["sources"])):
        p["autres_noms"] = sorted(p["autres_noms"] - {p["nom"]})
        p["statut_bmc"] = p["statut_bmc"].most_common(1)[0][0]
        p["traits"] = dict(p["traits"])
        p["mentions"] = len(p["sources"])
        p["ancrage"] = {"debut": None, "fin": None, "precision": "inconnue", "deduit": True}
        sortie.append(p)
    return sortie


if __name__ == "__main__":
    main()
