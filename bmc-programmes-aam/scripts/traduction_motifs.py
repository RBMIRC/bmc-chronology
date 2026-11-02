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
# équivalences et rattachements de la reconstitution (« 1936-38 : deux semestres, 3 h, Mr Dreier ») : règles successives
EQ = [
    (r"«\s*", "“"), (r"\s*»", "”"), (r" ; ", "; "), (r"\s*:\s", ": "), (r"”([,.])", r"\1”"),
    (r"\bdeux semestres\b", "two semesters"), (r"\bun semestre\b", "one semester"), (r"\bun seul cours\b", "a single course"),
    (r"\b1 h de théorie\b", "1 hour of theory"), (r"\b(\d+) h de théorie\b", r"\1 hours of theory"),
    (r"\b(\d+) h de pratique\b", r"\1 hours of practice"), (r"\b(\d+) h de laboratoire\b", r"\1 hours of laboratory"),
    (r"\b(\d+) h de cours\b", r"\1 hours of class"), (r"\b1 h\b", "1 hour"), (r"\b(\d+) h\b", r"\1 hours"),
    (r"\bannées alternées\b", "alternate years"), (r"\ben alternance\b", "in alternation"), (r"\bheures non données\b", "hours not given"),
    (r"\bsans horaire\b", "no set schedule"), (r"\bune fois par semaine( chacun)?\b", lambda m: "once a week" + (" each" if m.group(1) else "")),
    (r"\bMrs (?=[A-Z])(?![^“]*”)", "Mrs. "), (r"\bMr (?=[A-Z])(?![^“]*”)", "Mr. "), (r"(?<=[A-Za-z.]) et (?=(Mr|Mrs|[A-Z]))", " and "),
    (r"^seul nom du groupe (\w+)", r"the only name in the \1 group"), (r"\bgroupe (\w+)", r"\1 group"),
    (r"\bnommée? pour l'équivalent en (\d{4}-\d\d)", r"named for the equivalent in \1"),
    (r"\bnommée? pour ce cours au catalogue\b", "named for this course in the catalog"), (r"\bnommée? pour ce cours en (\d{4}-\d\d)", r"named for this course in \1"),
    (r"\bnommés tous deux en (\d{4}-\d\d)", r"both named in \1"), (r"\bnommée? en (\d{4}-\d\d)", r"named in \1"),
    (r"\(approchés?\)", "(approximate)"), (r"\benseignant non nommé\b", "teacher not named"), (r"^idem\b", "same"),
    (r"^débutants$", "beginners"), (r"^pour les nouveaux venus$", "for newcomers"), (r"^pour toute la communauté$", "for the whole community"),
    (r"\brevenu de congé\b", "back from leave"), (r"\ben congé\b", "on leave"),
    (r"le texte transcrit du musée donne (\w+)", r"the museum's transcribed text gives \1"),
    (r"lu sur le scan p\. (\d+), absent du texte transcrit du musée", r"read on the scan p. \1, absent from the museum's transcribed text"),
    (r"\(corps enseignant\)", "(faculty list)"), (r"^un des trois cours avancés$", "one of the three advanced courses"),
    (r"\bp\. (\d+), scan\b", r"p. \1, scan"), (r"^— \(nouveau en (\d{4}-\d\d)\)", r"— (new in \1)"), (r"^— \(absent en (\d{4}-\d\d)\)", r"— (absent in \1)"),
    (r"\bchimie non enseignée en (\d{4}-\d\d)", r"chemistry not taught in \1"), (r"\bun seul cours, comme en (\d{4}-\d\d)", r"a single course, as in \1"),
    (r"^a single course, comme en (\d{4}-\d\d)$", r"a single course, as in \1"),
]
FR = re.compile(r"\b(le|la|les|des|du|de|d'|une?|pour|avec|dans|sur|est|sont|au|aux|seule?|enseignante?s?|cours|nommée?s?|par|qui|en|à|où|ou|et|sans|idem|deux|trois)\b|[éèêàùçô]", re.I)
def equiv(t):
    e = t
    for a, b in EQ: e = re.sub(a, b, e)
    sans = re.sub(r"“[^”]*”", " ", e)
    return None if FR.search(sans) else e
for r in csv.reader(open(sys.argv[1], encoding="utf-8"), delimiter="\t"):
    if len(r) != 4 or r[0] == "id": continue
    e = motif(r[3]) or equiv(r[3])
    if e: print(f"{r[0]}\t{e}")
    else: print("RESTE", r[0], r[3], file=sys.stderr)
