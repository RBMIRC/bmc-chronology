"""Ajoute des entrées E à une extraction et la marque « #revu_evenements ». Usage : marquer_revu.py fichier.json
fichier.json : {"inventaire": ["E|...", ...], ...} (liste vide = relu, rien à ajouter)."""
import json, os, sys, datetime as dt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for inv, lignes in json.load(open(sys.argv[1], encoding="utf-8")).items():
    p = os.path.join(ROOT, "extraction", inv + ".txt")
    s = open(p, encoding="utf-8").read().rstrip("\n")
    for l in lignes:
        n = {"E": 9, "C": 6, "T": 5}.get(l[:1])
        if not l.startswith("//") and len(l.split("|")) != n: sys.exit(f"{inv} : ligne mal formée : {l}")
    if lignes: s += "\n" + "\n".join(lignes)
    if "#revu_evenements" not in s:
        s += f"\n#revu_evenements {dt.date.today().isoformat()} (audit d'exhaustivité : phrases datées relues une à une)"
    open(p, "w", encoding="utf-8").write(s + "\n")
    print(inv, len(lignes), "ajoutées")
