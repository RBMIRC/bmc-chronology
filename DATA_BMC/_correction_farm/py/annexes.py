"""Index (PDF 188-194) et crédits photographiques (PDF 196-199), d'après l'OCR par colonne."""
import re, json
from notes import lignes_col
from assemble import fusion

TETE = re.compile(r"Farm at Bl|^\W*(Index|INDEX|Image Credits|IMAGE CREDITS)\W*\d*\W*$|^\W*\d{3}\W*$")


def colonnes(pages):
    for i in pages:
        for side in (0, 1):
            L = [l for l in lignes_col(f"{i:03d}", side) if not TETE.search(l['text']) and re.search(r"[A-Za-z0-9]", l['text'])]
            if L: yield i, L


def index():
    entrees = []
    for i, L in colonnes(range(188, 195)):
        base = min(l['x0'] for l in L)
        for l in L:
            t = l['text'].strip()
            d = l['x0'] - base
            if t in ("Note", "Page references in italics refer to Illustrations."):
                continue
            if re.fullmatch(r"[A-Z]", t):
                entrees.append({"t": "lettre", "x": t}); continue
            if d < 18 and not re.match(r"^[\d,–-]", t):
                entrees.append({"t": "e", "x": t}); continue
            if d > 100 and not re.match(r"^[\d,–-]", t):
                entrees.append({"t": "s", "x": t}); continue
            if entrees:
                a = entrees[-1]["x"]
                entrees[-1]["x"] = fusion(a, t) if a.endswith("-") and not re.search(r"\d-$", a) else a + " " + t
    return entrees


def credits():
    out = []
    for i, L in colonnes(range(196, 200)):
        base = min(l['x0'] for l in L)
        for l in L:
            t = l['text'].strip()
            d = l['x0'] - base
            if t in ("IMAGE CREDITS",): continue
            if d < 25 and re.match(r"^\d{1,3}(-\d{1,3})?\b", t):
                out.append({"t": "c", "x": t}); continue
            if d < 25:
                out.append({"t": "h", "x": t}); continue
            if out:
                a = out[-1]["x"]
                out[-1]["x"] = fusion(a, t) if a.endswith("-") else a + " " + t
    return out


if __name__ == "__main__":
    ix, cr = index(), credits()
    json.dump({"index": ix, "credits": cr}, open("/tmp/farm/out/annexes.json", "w"), ensure_ascii=False, indent=0)
    print(len(ix), "entrées d'index ;", len(cr), "lignes de crédits")
    for e in ix[:15]: print(e)
    for e in cr[:15]: print(e)
