"""Version publique du semainier (https://rbmirc.github.io/week, dépôt RBMIRC/week), tirée de la version complète.

La version complète (bmc-programmes-aam/semainier/) reste l'outil de travail local : rien n'y est changé.
La version publique garde toutes les entrées, leurs références exactes (livre et page, inventaire de l'AAM avec lien vers
la fiche du musée, lien vers la notice du BMC Yearbook) et leur part déduite, mais pas les extraits longs des textes
cités, qui appartiennent à leurs auteurs et éditeurs :
  - verification.js : statut seulement (« retrouvé », « à relire »…), sans l'extrait du texte cité ;
  - data.js : notes de Duberman recopiées (notes_texte) retirées ; couche spéculative découpée par année
    (spec/AAAA-AA.js, chargé quand une semaine de l'année est affichée) ;
  - data_chronos.js : extraits de vérification et phrases des livres retirés (statut gardé) ;
  - data_personnes.js : biographies du BMC Yearbook retirées (lien vers la notice gardé) ;
  - data_scenario.js, data_syntheses.js : repris tels quels (résumés et synthèses rédigés, avec leurs références).
Usage : python3 scripts/publier_semainier.py <dossier de sortie>   (ex. /home/user/week)
Le dossier de sortie est réécrit (c'est un dépôt git à part : l'historique garde chaque publication).
"""
import json, os, re, shutil, sys, datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEM = os.path.join(ROOT, "semainier")


def lire_js(nom):
    s = open(os.path.join(SEM, nom), encoding="utf-8").read()
    i = s.index("{"); j = s.rstrip().rstrip(";").rindex("}") + 1
    m = re.search(r"(window\.\w+\s*=\s*)\{", s)
    return s[:s.index(m.group(0))], m.group(1), json.loads(s[i:j])


def ecrire_js(dossier, nom, entete, affect, d):
    p = os.path.join(dossier, nom); os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(entete.rstrip() + "\n// version publique (scripts/publier_semainier.py) : références gardées, extraits longs retirés\n")
        f.write(affect + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";\n")
    return os.path.getsize(p)


def main():
    if len(sys.argv) < 2: sys.exit(__doc__)
    out = os.path.abspath(sys.argv[1])
    if not os.path.isdir(os.path.join(out, ".git")): sys.exit(f"{out} n'est pas un dépôt git (cloner RBMIRC/week d'abord)")
    for x in os.listdir(out):          # le dépôt public est entièrement régénéré (git garde l'historique)
        if x == ".git": continue
        p = os.path.join(out, x); shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    tailles, retraits = {}, {}
    # page et bibliothèque
    h = open(os.path.join(SEM, "index.html"), encoding="utf-8").read()
    h = h.replace('<script src="lib/event-calendar.min.js"></script>',
                  '<script>window.BMC_PUBLIC = true;</script>\n<script src="lib/event-calendar.min.js"></script>', 1)
    h = h.replace("<title>Semainier · Black Mountain College</title>", "<title>Semainier · Black Mountain College</title>\n"
                  '<meta name="description" content="Le Black Mountain College (1933-1957) semaine par semaine : faits attestés, sources et part déduite.">', 1)
    open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(h)
    shutil.copytree(os.path.join(SEM, "lib"), os.path.join(out, "lib"))
    # data.js : spéculatif par année, notes de Duberman retirées
    ent, aff, D = lire_js("data.js")
    n = 0
    for e in D.get("duberman", []) + D.get("duberman_panneau", []):
        if e["extendedProps"].get("notes"): e["extendedProps"]["notes"] = ""; n += 1
    retraits["notes de Duberman (data.js)"] = n
    for an, Y in (D.get("spec") or {}).items():
        tailles[f"spec/{an}.js"] = ecrire_js(out, f"spec/{an}.js", "// couche spéculative, année " + an, f'(window.BMC_SPEC_AN ||= {{}})["{an}"] = ',
                                             {"gabarits": Y.pop("gabarits"), "analyse": Y.pop("analyse", "")})
    tailles["data.js"] = ecrire_js(out, "data.js", ent, aff, D)
    # data_chronos.js : extraits retirés
    ent, aff, C = lire_js("data_chronos.js")
    n = 0
    for e in C.get("grille", []) + C.get("panneau", []):
        v = e["extendedProps"].get("verif")
        if v and (v[1] or (len(v) > 2 and v[2])): e["extendedProps"]["verif"] = [v[0], "", ""]; n += 1
    for L in (C.get("livres") or {}).values():
        for r in L: r["phrase"] = ""
    retraits["extraits Chronos et Rumaker (data_chronos.js)"] = n
    retraits["phrases des livres (renvois)"] = sum(len(L) for L in (C.get("livres") or {}).values())
    tailles["data_chronos.js"] = ecrire_js(out, "data_chronos.js", ent, aff, C)
    # data_personnes.js : biographies retirées
    ent, aff, P = lire_js("data_personnes.js")
    n = 0
    for f in P.get("fiches", {}).values():
        if f.get("bio"): f["bio"] = ""; n += 1
        f["cours_brut"] = ""
    retraits["biographies du BMC Yearbook"] = n
    tailles["data_personnes.js"] = ecrire_js(out, "data_personnes.js", ent, aff, P)
    # verification.js : statut seulement
    ent, aff, V = lire_js("verification.js")
    V = {k: [v[0], "", v[2] if len(v) > 2 else ""] for k, v in V.items()}
    retraits["extraits de vérification (verification.js)"] = len(V)
    tailles["verification.js"] = ecrire_js(out, "verification.js", ent, aff, V)
    # scénario et synthèses : tels quels
    for nom in ("data_scenario.js", "data_syntheses.js"):
        shutil.copy(os.path.join(SEM, nom), os.path.join(out, nom)); tailles[nom] = os.path.getsize(os.path.join(out, nom))
    open(os.path.join(out, ".nojekyll"), "w").close()
    total = sum(tailles.values())
    L = ["# Semainier · Black Mountain College (1933-1957)", "",
         "Le Black Mountain College semaine par semaine : https://rbmirc.github.io/week", "",
         "Chaque entrée porte sa source (document de l'Asheville Art Museum avec lien vers la fiche du musée, livre et page, "
         "notice du BMC Yearbook) et sa **part déduite** : 0 % pour un fait daté par un document, davantage pour ce qui est "
         "tiré d'un livre, d'une extraction automatique ou reconstitué (emploi du temps du trimestre). La vue « Journal » "
         "sépare ce qui est attesté de ce qui est reconstitué.", "",
         "## Version publique", "",
         "Cette version garde toutes les entrées et leurs références exactes, mais pas les extraits longs des textes cités "
         "(citations de livres, biographies, passages d'entretiens), qui appartiennent à leurs auteurs et éditeurs : ils "
         "restent consultables à la source. Retraits de cette publication :", ""]
    L += [f"- {k} : {v}" for k, v in retraits.items()]
    L += ["", "## Fichiers", "", f"Publié le {dt.date.today().isoformat()} depuis le dépôt de travail RBMIRC/bmc-chronology "
          "(`bmc-programmes-aam/scripts/publier_semainier.py`). Ne pas modifier ici : les fichiers sont régénérés à chaque publication.", "",
          "| fichier | taille |", "|---|---|"]
    L += [f"| `{k}` | {v / 1e6:.1f} Mo |" for k, v in sorted(tailles.items()) if not k.startswith("spec/")]
    L += [f"| `spec/*.js` ({sum(1 for k in tailles if k.startswith('spec/'))} années, chargées à la demande) | {sum(v for k, v in tailles.items() if k.startswith('spec/')) / 1e6:.1f} Mo |",
          "", f"Total : {total / 1e6:.1f} Mo (servis compressés par GitHub Pages).", "",
          "Bibliothèque d'affichage : Event Calendar (licence MIT), dans `lib/`."]
    open(os.path.join(out, "README.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L[9:]))


if __name__ == "__main__":
    main()
