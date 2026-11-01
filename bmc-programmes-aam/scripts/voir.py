"""Affiche le texte OCR compact d'une ou plusieurs fiches : voir.py ACC [ACC...]"""
import sys, json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = json.load(open(os.path.join(ROOT, "fiches.json")))
p = os.path.join(ROOT, "fiches_sondees.json")
if os.path.exists(p): F += json.load(open(p))
D = {}
for f in F: D.setdefault(f["accession"], f)
if __name__ == "__main__":
  for acc in sys.argv[1:]:
      f = D[acc]
      t = re.sub(r"[ \t]+", " ", f["description"]); t = re.sub(r"\n\s*\n+", "\n", t)
      print(f"##### {acc} | {f['title']} | {f['date']}\n{t}\n")
