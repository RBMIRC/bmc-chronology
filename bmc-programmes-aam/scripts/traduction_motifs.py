"""Brouillon anglais des motifs de part déduite (« phrase (+N) ; phrase (+N) ; … ») et des champs voisins de la reconstitution.
Chaque phrase type est traduite une fois (PHRASES) ; mêmes formulations que REGLES_EN (semainier/i18n.js).
  python3 scripts/traduction_motifs.py semainier/i18n/lots/lot_NNN.tsv > brouillon.tsv   (le reste : RESTE sur stderr)"""
import csv, re, sys
PHRASES = [
    (r"présence cette semaine-là déduite d'un rythme régulier \(hebdomadaire, quotidien, cours de toute l'année\)", "presence that week deduced from a regular rhythm (weekly, daily, year-long course)"),
    (r"jour choisi par moi", "day chosen by me"),
    (r"heure choisie par moi dans un créneau attesté \(matin, après-midi de cours, après le dîner, samedi soir\)", "time chosen by me within an attested time slot (morning, afternoon classes, after dinner, Saturday evening)"),
    (r"heure choisie par moi sans source", "time chosen by me without a source"),
    (r"cours ou activité attesté pour l'année même", "course or activity attested for the same year"),
    (r"volume horaire supposé \(non donné pour ce cours\)", "number of hours assumed (not given for this course)"),
    (r"titre : chance (\d+/\d+) que ce soit bien ce cours ce trimestre-là \(part du titre (\d+) %\)", r"title: a \1 chance that this is the course given that term (title share \2%)"),
    (r"enseignant nommé pour ce cours dans le catalogue de l'année", "teacher named for this course in the year's catalog"),
    (r"structure \(heures, semestres\) ou usage pris dans une année voisine", "structure (hours, semesters) or practice taken from a neighboring year"),
    (r"enseignant rattaché par sa discipline et nommé pour ce cours \(ou son équivalent\) dans une année voisine", "teacher attributed by subject and named for this course (or its equivalent) in a neighboring year"),
    (r"activité occasionnelle, mensuelle ou « à la demande » : rien ne dit qu'elle tombe cette semaine", "occasional, monthly, or “on request” activity: nothing says it falls this week"),
    (r"liste de cours de l'année précédente : celle de l'année n'est pas lisible dans le corpus", "course list of the previous year: the year's own list is not legible in the corpus"),
    (r"enseignant rattaché par sa discipline : seul enseignant de cette matière au catalogue", "teacher attributed by subject: the only teacher of the subject in the catalog"),
    (r"liste de cours donnée pour d'autres trimestres de l'année, reconduite pour celui-ci", "course list given for other terms of the year, carried over to this one"),
    (r"présence de l'enseignant pendant tout le trimestre non attestée", "the teacher's presence throughout the term not attested"),
    (r"enseignant rattaché par élimination entre collègues de la même discipline", "teacher attributed by elimination among colleagues in the same subject"),
    (r"enseignant inconnu ou rattaché par simple compétence", "teacher unknown or attributed by competence alone"),
    (r"domaine annoncé à l'avance \(« fields represented will be… »\) : cours réel non attesté", "field announced in advance (“fields represented will be…”): actual course not attested"),
    (r"cours suivi ce trimestre-là d'après les fiches d'étudiants \(BMC Yearbook, bmcyearbook\.org\)", "course taken that term according to the student records (BMC Yearbook, bmcyearbook.org)"),
    (r"transposé d'une période éloignée ou d'un autre campus", "carried over from a distant period or another campus"),
    (r"équivalence de titre avec une année voisine probable mais non certaine", "title equivalence with a neighboring year probable but not certain"),
    (r"le catalogue 1936-38 le dit offert « last year » \(1935-36\)", "the 1936-38 catalog says it was offered “last year” (1935-36)"),
    (r"enseignant rattaché d'après Duberman \(texte corrigé\), pas d'après un document de l'année", "teacher attributed according to Duberman (corrected text), not according to a document of the year"),
]
def motif(t):
    out = []
    for p in t.split(" ; "):
        m = re.match(r"(.*?)(\s*\(\+\d+\))?$", p.strip()); x, pts = m.group(1), m.group(2) or ""
        for a, b in PHRASES:
            if re.fullmatch(a, x): out.append(re.sub(a, b, x) + pts); break
        else: return None
    return "; ".join(out)
for r in csv.reader(open(sys.argv[1], encoding="utf-8"), delimiter="\t"):
    if len(r) != 4 or r[0] == "id": continue
    e = motif(r[3])
    if e: print(f"{r[0]}\t{e}")
    else: print("RESTE", r[0], r[3], file=sys.stderr)
