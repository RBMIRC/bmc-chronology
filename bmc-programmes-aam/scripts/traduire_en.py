"""Version anglaise du semainier : traductions des contenus rédigés en français.

Deux sources de traduction, par ordre de priorité :
  1. semainier/i18n/revu_en.tsv : traductions relues (« original<TAB>traduction »), faites à la main ; elles priment ;
  2. semainier/i18n/auto_en.json : traduction automatique hors ligne (Argos Translate, modèle fr→en), cache additif
     (une chaîne déjà traduite ne l'est pas deux fois ; rien n'est effacé).
Les chaînes en anglais (titres de cours, fiches du musée…) ne sont pas traduites.
Sortie : semainier/data_en.js → window.BMC_EN = {revu: {original: traduction}, auto: {original: traduction}}
(la page ne la charge qu'en anglais ; chaque texte traduit automatiquement y est signalé, l'original reste dans la fiche).
Usage : python3 scripts/traduire_en.py [--champs titres|notes|tout] [--max N]   (relançable : reprend où il s'est arrêté)
"""
import csv, json, os, re, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEM = os.path.join(ROOT, "semainier"); I18N = os.path.join(SEM, "i18n")
FR = re.compile(r"\b(le|la|les|des|du|de|et|une|un|pour|avec|dans|sur|est|au|aux|en|par|qui|que|ou|ses|son|sa|leur|chez|après|avant|selon)\b", re.I)
EN = re.compile(r"\b(the|and|of|with|for|to|in|on|at|is|by|from|his|her|their|after|before)\b", re.I)
ACCENTS = re.compile(r"[éèêàùâîôûçœ]")


def francais(t):
    f, e = len(FR.findall(t)), len(EN.findall(t))
    return f > e or (f == e and bool(ACCENTS.search(t)))


def charge(nom):
    s = open(os.path.join(SEM, nom), encoding="utf-8").read()
    return json.loads(s[s.index("{"): s.rstrip().rstrip(";").rindex("}") + 1])


def chaines(champs):
    """chaînes à traduire, par ordre d'importance (ce qui s'affiche dans les cases d'abord)."""
    D, C, S = charge("data.js"), charge("data_chronos.js"), charge("data_scenario.js")
    G = [g for Y in D.get("spec", {}).values() for g in Y["gabarits"]]
    titres = [e["title"] for e in D["events"]] + [e["title"] for e in D["duberman"] + D["duberman_panneau"]] + \
             [g["activite"] for g in G] + [p["libelle"] for p in D["periodes"]] + \
             [e["title"] for e in C["grille"] + C["panneau"]] + [e["title"] for e in S["grille"] + S["panneau"]]
    notes = [e["extendedProps"].get("note", "") for e in D["events"]] + [g["note"] for g in G] + \
            [e["extendedProps"].get("note", "") for e in C["grille"] + C["panneau"]] + \
            [e["extendedProps"].get("note", "") for e in D["duberman"] + D["duberman_panneau"]]
    out = titres if champs == "titres" else notes if champs == "notes" else titres + notes
    vus, L = set(), []
    for t in out:
        t = (t or "").strip()
        if t and t not in vus and francais(t): vus.add(t); L.append(t)
    return L


def main():
    champs = sys.argv[sys.argv.index("--champs") + 1] if "--champs" in sys.argv else "titres"
    maxi = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 10 ** 9
    os.makedirs(I18N, exist_ok=True)
    p_auto = os.path.join(I18N, "auto_en.json")
    auto = json.load(open(p_auto, encoding="utf-8")) if os.path.exists(p_auto) else {}
    revu = {}
    p_revu = os.path.join(I18N, "revu_en.tsv")
    if os.path.exists(p_revu):
        for l in open(p_revu, encoding="utf-8"):
            if "\t" in l and not l.startswith("#"):
                a, b = l.rstrip("\n").split("\t", 1); revu[a] = b
    L = [t for t in chaines(champs) if t not in revu and t not in auto][:maxi]
    print(f"{len(L)} chaînes à traduire automatiquement ({champs}) ; déjà : relues {len(revu)}, automatiques {len(auto)}", flush=True)
    # noms de famille des personnes (BMC Yearbook) : « X à Y » ne devient « X to Y » (lettre) que si Y est une personne
    try:
        P = charge("data_personnes.js")
        noms = {re.sub(r"[^A-Za-z]", "", k.split()[-1]) for k in P["fiches"] if k.split()}
    except Exception:
        noms = set()
    def lettre(m):
        return m.group(1) + (" to " if re.sub(r"[^A-Za-z]", "", m.group(2).split()[-1]) in noms else " à ") + m.group(2)
    if L:
        import argostranslate.translate as T
        t0, n = time.time(), 0
        for t in L:
            # « X à Y » entre deux noms propres (lettres) : « X to Y » ; le modèle lit « à » comme « in »
            src = re.sub(r"(\b[A-Z][\w.'’-]+) à ([A-Z][\w.'’-]+(?: [A-Z][\w.'’-]+)?)", lettre, t)
            try: auto[t] = T.translate(src, "fr", "en")
            except Exception as e: print("échec :", t[:60], e, flush=True); continue
            n += 1
            if n % 200 == 0:
                json.dump(auto, open(p_auto, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
                print(f"  {n}/{len(L)} ({time.time() - t0:.0f} s)", flush=True)
        json.dump(auto, open(p_auto, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    with open(os.path.join(SEM, "data_en.js"), "w", encoding="utf-8") as f:
        f.write("// généré par scripts/traduire_en.py — traductions relues (revu) et automatiques (auto, Argos Translate fr→en)\n")
        f.write("window.BMC_EN = " + json.dumps({"revu": revu, "auto": auto}, ensure_ascii=False, separators=(",", ":")) + ";\n")
    print(f"semainier/data_en.js : relues {len(revu)}, automatiques {len(auto)}")


if __name__ == "__main__":
    main()
