"""Recalcule la page du livre de chaque note de Duberman (chap:n) à partir de l'OCR tesseract des pages
(/tmp/dub/tess/NNN.txt, NNN = index PDF à partir de 1 ; page du livre = NNN − 21).
Chaque chapitre des notes est borné par ses en-têtes « CHAPTER n: » ; dans ces bornes, la note n est
cherchée en début de ligne (« n. premier mot »), en avançant sans jamais reculer. Écrit _appui/pages_notes.json."""
import json, os, re, unicodedata, collections

ICI = os.path.dirname(os.path.abspath(__file__))


def norm(s):
    s = unicodedata.normalize("NFKD", s.lower())
    return re.sub(r"[^a-z0-9]+", " ", "".join(c for c in s if not unicodedata.combining(c))).strip()


notes = json.load(open(os.path.join(ICI, "_appui", "notes_by_id.json"), encoding="utf-8"))
pages = {}
for fn in os.listdir("/tmp/dub/tess"):
    if fn.endswith(".txt"):
        bp = int(fn[:3]) - 21
        if 460 <= bp <= 566:
            t = open(os.path.join("/tmp/dub/tess", fn), encoding="utf-8", errors="replace").read()
            pages[bp] = re.sub(r"-\s*\n\s*", "", t)
ordre = sorted(pages)

# bornes des chapitres : page de l'en-tête « CHAPTER c: »
entete = {}
for b in ordre:
    for m in re.finditer(r"CHAPTER\s+(\d+)\s*[:;.]", pages[b]):
        entete.setdefault(int(m.group(1)), b)
chapitres = sorted({int(k.split(":")[0]) for k in notes})
for c in chapitres:
    if c not in entete:  # en-tête mal lu : on prend la fin du chapitre précédent
        entete[c] = entete.get(c - 1, ordre[0])

def numeros(t):
    """Numéros de notes visibles en début de ligne (tesseract sépare souvent le numéro de son texte)."""
    return {int(m.group(1)) for m in re.finditer(r"(?m)^\s*(\d{1,3})\s*[.,;:%]", t)}


nums_page = {b: numeros(pages[b]) for b in ordre}
res, manque = {}, []
for c in chapitres:
    debut = entete[c]
    fin = min([entete[d] for d in chapitres if d > c and entete[d] > debut] or [ordre[-1]])
    plage = [p for p in ordre if debut <= p <= fin]
    nums = sorted(int(k.split(":")[1]) for k in notes if int(k.split(":")[0]) == c)
    # alignement monotone (programmation dynamique) : chaque note reçoit une page, jamais en arrière ;
    # +1 si le numéro est lu sur la page, −0,6 par page sautée au-delà de la suivante
    P = len(plage); NEG = -1e9
    score = [[NEG] * P for _ in nums]; arg = [[0] * P for _ in nums]
    for j in range(P):
        score[0][j] = (1 if nums[0] in nums_page[plage[j]] else 0) - 0.6 * j
    for i in range(1, len(nums)):
        best, bq = NEG, 0
        for j in range(P):
            # meilleur prédécesseur q ≤ j avec pénalité de saut
            for q in range(max(0, j - 3), j + 1):
                v = score[i - 1][q] - 0.6 * max(0, j - q - 1)
                if v > score[i][j] - (1 if nums[i] in nums_page[plage[j]] else 0):
                    score[i][j] = v + (1 if nums[i] in nums_page[plage[j]] else 0); arg[i][j] = q
    j = max(range(P), key=lambda x: score[-1][x])
    for i in range(len(nums) - 1, -1, -1):
        res[f"{c}:{nums[i]}"] = plage[j]
        if nums[i] not in nums_page[plage[j]]: manque.append(f"{c}:{nums[i]}")
        j = arg[i][j]

json.dump({k: str(v) for k, v in res.items()}, open(os.path.join(ICI, "_appui", "pages_notes.json"), "w"), indent=0)
print(len(res), "notes ;", len(manque), "non retrouvées (page de la précédente) :", manque)
par = collections.defaultdict(list)
for k, v in res.items(): par[int(k.split(":")[0])].append(v)
for c in sorted(par): print(c, "en-tête p.", entete[c], "notes p.", min(par[c]), "→", max(par[c]))
