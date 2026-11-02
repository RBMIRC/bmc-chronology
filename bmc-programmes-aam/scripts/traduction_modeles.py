"""Brouillon anglais des notes formulaires d'un lot (présence attestée, souvenirs du BMC Yearbook, document daté, cours suivis).
  python3 scripts/traduction_modeles.py semainier/i18n/lots/lot_NNN.tsv > brouillon.tsv   (le reste est listé sur stderr : RESTE …)
Le brouillon passe ensuite par « traduction_en.py verifier », comme une traduction faite à la main."""
import csv, re, sys
def presence(t):
    return re.sub(r"présence attestée \(([^)]*)\) : (\d+) activité\(s\), du (\S+) au (\S+)",
                  lambda m: f"attested presence ({m[1]}): {m[2]} {'activity' if m[2] == '1' else 'activities'}, " + (f"on {m[3]}" if m[3] == m[4] else f"from {m[3]} to {m[4]}"), t)
def souvenir(t):
    def f(m):
        nom, role, ans, q = m[1].replace('""', '"'), m[2], m[3], m[4]
        ans = "dates uncertain" if ans == "uncertain" else ans
        return f"Recollection of {nom} ({role}, at BMC {ans}): “{q}”" if ans != "dates uncertain" else f"Recollection of {nom} ({role}, at BMC, dates uncertain): “{q}”"
    return re.sub(r"Souvenir de (.+?) \(([^,()]+), à BMC ([^)]+)\) : « (.+?) »", f, t)
def suivis(t):
    n = lambda k: f"{k} student" + ("" if k == "1" else "s")
    t = re.sub(r"Ce trimestre-là : cours suivi par (\d+) étudiant\(s\) : ", lambda m: f"That term: course taken by {n(m[1])}: ", t)
    t = re.sub(r"(?<![\w-])Suivi par (\d+) étudiant\(s\) : ", lambda m: f"Taken by {n(m[1])}: ", t)
    t = re.sub(r"Fiches d'étudiants : suivi d'après les fiches d'étudiants en (automne|hiver|printemps|été), d'aucune fiche ce trimestre-ci",
               lambda m: f"Student records: taken in the {dict(automne='fall', hiver='winter', printemps='spring', été='summer')[m[1]]} according to the student records; no record for this quarter", t)
    t = re.sub(r"Fiches d'étudiants : ", "Student records: ", t)
    t = re.sub(r"titre suivi ce trimestre-là avec un autre enseignant : ", "title taken that term with another teacher: ", t)
    t = re.sub(r"« ([^»]*?) » avec ", r"“\1” with ", t)
    t = t.replace(" [abandonné]", " [dropped]").replace(" ; BMC Yearbook)", "; BMC Yearbook)").replace("; « ", "; “")
    t = t.replace("plage indicative ; ", "indicative time slot; ").replace("volume et horaire supposés ; ", "hours and schedule assumed; ")
    t = t.replace(" ; title taken", "; title taken").replace(" ; Student records", "; Student records").replace(" ; That quarter", "; That quarter").replace(" ; Taken by", "; Taken by")
    return t


def doc(t): return re.sub(r"\(document daté « ([^»]+) »\)", r"(document dated “\1”)", t)
for r in csv.reader(open(sys.argv[1], encoding="utf-8"), delimiter="\t"):
    if len(r) != 4 or r[0] == "id": continue
    t = r[3]
    if t.startswith('"') and t.endswith('"'): t = t[1:-1].replace('""', '"')
    e = suivis(doc(souvenir(presence(t)))).replace(" — attested", " — attested")
    if re.search(r"présence|Souvenir|document daté|activité|étudiant|suivi|Fiches|trimestre|« |\bdu\b|\bau\b|\bavec\b| ; ", e): print("RESTE", r[0], e, file=sys.stderr); continue
    if e == t: print("RESTE", r[0], t, file=sys.stderr); continue
    print(f"{r[0]}\t{e}")
