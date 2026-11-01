"""Tableau de bord : où en est chaque étape, ce qu'a coûté l'extraction."""
import json

import moteurs
from config import ETAT, EXTRACTIONS, FUSION, MORCEAUX, SORTIE, SYNTHESES, TEXTE

morceaux = [json.loads(l) for l in open(MORCEAUX / "morceaux.jsonl")] if (MORCEAUX / "morceaux.jsonl").exists() else []
faits = {p.stem for p in EXTRACTIONS.glob("*.json")} if EXTRACTIONS.exists() else set()
print(f"02 texte         {len(list(TEXTE.glob('*.jsonl.gz')))} sources")
print(f"03 morceaux      {len(morceaux)}")
print(f"04 extraction    {len(faits)}/{len(morceaux)} morceaux")
if (FUSION / "_bilan.txt").exists():
    print("05 fusion        " + (FUSION / "_bilan.txt").read_text().splitlines()[0])
for passe in ("personnes", "annees", "enseignements", "mois"):
    d = SYNTHESES / passe
    print(f"06 {passe:13s} {len(list(d.glob('*.json'))) if d.exists() else 0}")
print(f"07 sorties       {sorted(p.name for p in SORTIE.glob('*.json'))[-1:] if SORTIE.exists() else '—'}")

for journal in ("extraction.jsonl", "syntheses.jsonl"):
    j = ETAT / journal
    if not j.exists():
        continue
    cout, toks = 0.0, [0, 0]
    for l in open(j):
        r = json.loads(l)
        toks[0] += r["entree"] + r["cache_lu"] + r["cache_ecrit"]
        toks[1] += r["sortie"]
        pe, ps = moteurs.PRIX.get(r["modele"], (0, 0))
        cout += (r["entree"] * pe + r["cache_ecrit"] * pe * 1.25 + r["cache_lu"] * pe * 0.1 + r["sortie"] * ps) / 1e6
    print(f"{journal:18s} {toks[0]/1e6:.2f} M tokens entrée, {toks[1]/1e6:.2f} M sortie, "
          f"≈ {cout:.2f} $ au tarif direct (lots : moitié ; z.ai : forfait)")
