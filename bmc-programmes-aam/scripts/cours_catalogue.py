"""Repère dans un catalogue les blocs « titre de cours … ligne d'horaire avec enseignant » et
propose des lignes C| à relire. cours_catalogue.py ACC PERIODE"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voir
acc, per = sys.argv[1], sys.argv[2]
L = [l.strip() for l in voir.D[acc]["description"].splitlines() if l.strip() and not l.startswith("*Black")]
PROF = re.compile(r"\b(Mr|Mrs|Miss|Dr|Messrs)\.?\s+([A-Z][\w'’-]+(?:[- ][A-Z][\w'’-]+)?(?:,? (?:and|&) (?:Mr|Mrs|Miss|Dr)\.? [A-Z][\w'’-]+)*)")
HRS = re.compile(r"(?i)(semester|quarter|hours?|week|term|year|by arrangement|on demand)")
section = ""
for i, l in enumerate(L):
    if re.fullmatch(r"[A-Z][A-Z &,.-]{3,}", l): section = l.title()
    m = PROF.search(l)
    if m and HRS.search(l) and len(l) < 260:
        # titre : remonter jusqu'à une ligne courte non horaire
        j = i - 1; titre = ""
        while j >= 0 and i - j <= 6:
            c = L[j]
            if len(c) < 90 and not HRS.search(c) and not PROF.search(c):
                titre = c; break
            j -= 1
        hrs = PROF.sub("", l).strip(" .;,")
        profs = "; ".join(f"{a} {b}" for a, b in PROF.findall(l))
        print(f"C|{per}|{titre} [{section}]|{profs}|{hrs}|")
