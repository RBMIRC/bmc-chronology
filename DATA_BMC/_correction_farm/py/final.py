"""Assemble le texte complet : pages liminaires, corps, notes, crédits, index, colophon, 4e de couverture."""
import json, re, os, collections
from assemble import fusion

SUP = "⁰¹²³⁴⁵⁶⁷⁸⁹"
fl = json.load(open('/tmp/farm/out/corps_appels.json'))
NT = json.load(open('/tmp/farm/out/notes.json'))
AX = json.load(open('/tmp/farm/out/annexes.json'))
POST = json.load(open('/tmp/farm/post.json')) if os.path.exists('/tmp/farm/post.json') else []
TITRES = {1: "Before Black Mountain", 2: "The Founding of the Farm", 3: "Pigs and Place", 4: "Moving to Lake Eden",
          5: "Barn Raising", 6: "Molly Gregory Raises the Roof", 7: "The Quakers",
          8: "“No more of this community horseshit!”", 9: "Collapse"}


def nettoie(x):
    # résidus d'OCR des appels : « 4° », « 2! », « '3 », « *' », « § », « ® », « %? » autour d'un exposant
    S = "[" + SUP + "]"
    NS = "[^\\sA-Za-z" + SUP + "]"
    x = re.sub(r"\s*[§®©¢]\s*(?=" + S + ")", "", x)
    x = re.sub(r"(" + S + r"+)\s+[\"'‘’!|*°§®©¢$%&]*\d{0,3}[°!'*’|®©]+(?=\s|$)", r"\1", x)
    x = re.sub(r"(" + S + r"+)\s+(?:\d{1,3}°|[!'’|]\d{1,3}|°)(?=\s|$)", r"\1", x)
    x = re.sub(r"\s+(?=" + NS + r"{0,2}[%?$!°'’*§|\"“®©¢&])" + NS + r"{1,3}(?=" + S + ")", "", x)
    x = re.sub(r"(?<=[.,;:!?”’)])[®©§%$!?*|°'’]+(?=" + S + ")", "", x)
    x = re.sub(r"(?<=[.,;:!?”’)])[\d!°'’|*§®©%$?]{1,4}(?=" + S + ")", "", x)
    x = re.sub(r" {2,}", " ", x)
    return x.strip()


def rendu(it):
    x = nettoie(it['x']) if it['t'] != 'document' else it['x']
    t = it['t']
    if t == 'citation':
        L = it.get('lignes') or []
        if len(L) >= 3 and max(len(l) for l in L) < 40:
            return "\n".join("    " + nettoie(l) for l in L)
        return "    " + x
    if t == 'legende':
        if len(re.sub(r"[^A-Za-z]", "", x)) < 15 or re.fullmatch(r"\d*\s*The Farm at Black Mountain College", x):
            return None
        x = re.sub(r"^(?:[^A-Za-z“\"]*\b(?:[a-z]{1,4}|[A-Z]{1,2})\b[^A-Za-z“\"]*)+(?=[A-Z“])", "", x) if not re.match(r"^[A-Z“]", x) else x
        return "[Légende] " + x
    if t == 'titre': return x.upper()
    if t == 'lacune': return "[" + x + "]"
    if t == 'document':
        l = x.split("\n"); return l[0] + "\n" + "\n".join("    " + y for y in l[1:])
    return x


out = []
out.append("THE FARM AT BLACK MOUNTAIN COLLEGE\n\nDavid Silver\n\n[Éd. : Black Mountain College Museum + Arts Center / Atelier Editions, 2024 ; texte établi d'après le scan « farm_low.pdf » (202 pages), voir la note de transcription à la fin]")
out.append("[Photographie de couverture] Two students walking to the fields, summer 1944. Photograph by Josef Breitenbach.")
out.append("This book is dedicated to Sarah and Siena.")
out.append("CONTENTS\n\n09  FOREWORD\n13  INTRODUCTION\n19  CHAPTER 1 — Before Black Mountain\n37  CHAPTER 2 — The Founding of the Farm\n55  CHAPTER 3 — Pigs and Place\n75  CHAPTER 4 — Moving to Lake Eden\n89  CHAPTER 5 — Barn Raising\n109 CHAPTER 6 — Molly Gregory Raises the Roof\n137 CHAPTER 7 — The Quakers\n163 CHAPTER 8 — “No more of this community horseshit!”\n185 CHAPTER 9 — Collapse\n205 APPENDIX — Endnotes, Image Credits")
out.append("[Légende] A wheelbarrow rests comfortably against the small barn, with the big barn in the background.")
out.append("FOREWORD")
for it in fl:
    r = rendu(it)
    if r is not None: out.append(r)
# notes
out.append("APPENDIX\n\nENDNOTES")
chap = None
for n in NT['notes']:
    if n['chap'] != chap:
        chap = n['chap']; out.append(f"CHAPTER {chap}: {TITRES[chap].upper()}")
    out.append(f"{n['n']}. {nettoie(n['x'])}")
out.append("IMAGE CREDITS\n\nKEY\nBMCC — Black Mountain College Collection\nBMCMAC — Black Mountain College Museum + Arts Center\nBMCPP — Black Mountain College Project Papers\nBMCRP — Black Mountain College Research Project\nWRA — Western Regional Archives")
for c in AX['credits']:
    out.append(c['x'])
out.append("INDEX\n\nNote : Page references in italics refer to Illustrations.")
for e in AX['index']:
    out.append(("    " if e['t'] == 's' else "") + e['x'])
texte = "\n\n".join(out)
# chiffres elzéviriens lus comme des lettres : « I May 1935 », « I5 »
MOIS = "January|February|March|April|May|June|July|August|September|October|November|December"
texte = re.sub(r"\bI (?=(?:" + MOIS + r")\b)", "1 ", texte)
texte = re.sub(r"\bI(?=\d)", "1", texte)
texte = re.sub(r"(?<=\d)I\b", "1", texte)
# traits d'union de fin de ligne restés : « pig-pen » alors que « pigpen » est la forme du livre
mots = collections.Counter(re.findall(r"[a-z]+", texte))
def soude(m):
    a, b = m.group(1), m.group(2)
    return a + b if mots[a + b] >= 2 else m.group(0)
texte = re.sub(r"\b([a-z]{2,})-([a-z]{2,})\b", soude, texte)
# « GropiusBreuer » : nom composé dont le trait d'union de fin de ligne a été retiré
for a_, b_ in set(re.findall(r"\b([A-Z][a-z]+)-([A-Z][a-z]+)\b", texte)):
    texte = texte.replace(a_ + b_, a_ + "-" + b_)
# intervalles numériques : tiret demi-cadratin, comme dans le livre (1934–35, 96–98)
texte = re.sub(r"(?<=\d)-(?=\d)", "–", texte)
texte = re.sub(r"(\w) —(\w)", r"\1—\2", texte)
texte = re.sub(r"(\w)— (\w)", r"\1—\2", texte)
# typographie : apostrophes et guillemets courbes, comme dans le livre
texte = re.sub(r"(?<=[A-Za-z])'(?=[A-Za-z])", "’", texte)
texte = re.sub(r"(?<=[A-Za-z.,!?])'(?=\s|$)", "’", texte)
texte = re.sub(r'(^|[\s(\[—])"(?=\S)', r"\1“", texte, flags=re.M)
texte = re.sub(r'(?<=\S)"', "”", texte)
# mots soudés ou mal lus, récurrents
for a, b in [(r"\bBMG\b", "BMC"), (r"\bofa\b", "of a"), (r"\bona\b", "on a"), (r"\basa\b", "as a"),
             (r"\bfora\b", "for a"), (r"\bhada\b", "had a"), (r"\bajob\b", "a job"), (r"\bofall\b", "of all"),
             (r"\bina\b", "in a"), (r"\bIo years\b", "10 years"), (r"\bFrangais\b", "Français")]:
    texte = re.sub(a, b, texte)
for a, b in POST:
    if a not in texte: print("POST introuvable :", a[:60])
    texte = texte.replace(a, b)
open('/tmp/farm/out/draft.txt', 'w').write(texte + "\n")
print(len(texte), "caractères")
