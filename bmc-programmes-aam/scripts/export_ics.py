"""Exporte le programme en iCalendar (.ics) dans programme/ics/ :
bmc_tout.ics, un fichier par famille d'activités, bmc_periodes.ics (trimestres, vacances, sessions).
Heures « flottantes » (heure locale de Black Mountain, sans fuseau) ; activités sans heure précise
(matin, soir…) = événements « journée entière » avec le moment indiqué dans le titre."""
import csv, os, re, hashlib, datetime as dt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROG = os.path.join(ROOT, "programme"); OUT = os.path.join(PROG, "ics")
FAMILLES = {
    "cours": ("BMC – cours et ateliers", {"cours", "atelier"}),
    "reunions": ("BMC – réunions (faculté, Board, étudiants, communauté)", {"reunion"}),
    "concerts_theatre_danse": ("BMC – concerts, théâtre, danse", {"concert", "theatre", "danse"}),
    "conferences": ("BMC – conférences et radio", {"conference", "radio"}),
    "vie_communaute": ("BMC – vie de la communauté (travail, fêtes, expos, visites, sorties)", {"social", "travail", "expo", "visite", "sortie", "autre"}),
    "calendrier_examens": ("BMC – calendrier scolaire et examens", {"calendrier", "examen"}),
}
STAMP = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def esc(s):
    return (s or "").replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")

def fold(line):
    b = line.encode("utf-8"); out = []
    while len(b) > 75:
        cut = 75 if not out else 74
        while (b[cut] & 0xC0) == 0x80: cut -= 1      # ne pas couper un caractère UTF-8
        out.append(b[:cut].decode("utf-8")); b = b[cut:]
    out.append(b.decode("utf-8"))
    return "\r\n ".join(out)

def hm(h):
    m = re.fullmatch(r"(\d{1,2}):(\d{2})", (h or "").strip())
    return (int(m.group(1)), int(m.group(2))) if m else None

def vevent(uid, date, debut, fin, summary, desc, lieu, url, cat):
    L = ["BEGIN:VEVENT", f"UID:{uid}@bmc-programmes-aam", f"DTSTAMP:{STAMP}"]
    d = dt.date.fromisoformat(date); a = hm(debut)
    if a:
        s = dt.datetime(d.year, d.month, d.day, *a)
        b = hm(fin)
        e = dt.datetime(d.year, d.month, d.day, *b) if b else s + dt.timedelta(hours=1)
        if e <= s: e = s + dt.timedelta(hours=1)
        L += [f"DTSTART:{s:%Y%m%dT%H%M%S}", f"DTEND:{e:%Y%m%dT%H%M%S}"]
    else:
        L += [f"DTSTART;VALUE=DATE:{d:%Y%m%d}", f"DTEND;VALUE=DATE:{d + dt.timedelta(days=1):%Y%m%d}",
              "TRANSP:TRANSPARENT"]
    L += [f"SUMMARY:{esc(summary)}", f"DESCRIPTION:{esc(desc)}"]
    if lieu: L.append(f"LOCATION:{esc(lieu)}")
    if url: L.append(f"URL:{url}")
    if cat: L.append(f"CATEGORIES:{esc(cat)}")
    L.append("END:VEVENT")
    return L

def ecrire(nom, titre, evs):
    L = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//bmc-programmes-aam//programme BMC//FR",
         "CALSCALE:GREGORIAN", f"X-WR-CALNAME:{esc(titre)}",
         "X-WR-CALDESC:" + esc("Black Mountain College d'après les documents de l'Asheville Art Museum. "
                               "Chaque événement cite sa source et sa part de déduction.")]
    for e in evs: L += e
    L.append("END:VCALENDAR")
    with open(os.path.join(OUT, nom), "w", encoding="utf-8", newline="") as fh:
        fh.write("\r\n".join(fold(x) for x in L) + "\r\n")

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    rows = list(csv.DictReader(open(os.path.join(PROG, "evenements.csv"), encoding="utf-8")))
    par_fam = {k: [] for k in FAMILLES}; tout = []
    for i, r in enumerate(rows):
        pct = int(r["part_deduite_pct"])
        moment = "" if hm(r["debut"]) else (f"[{r['debut']}] " if r["debut"] else "")
        marque = "" if pct == 0 else f" ({pct} % déduit)"
        summary = f"{moment}{r['activite'][:110]}{'…' if len(r['activite']) > 110 else ''}{marque}"
        desc = "\n".join(x for x in [
            r["activite"],
            f"Qui : {r['qui']}" if r["qui"] else "",
            f"Lieu : {r['lieu']}" if r["lieu"] else "",
            f"Note : {r['note']}" if r["note"] else "",
            f"Type : {r['type']}" + (" — séance récurrente déduite" if r["recurrent_deduit"] else ""),
            f"Part déduite : {pct} % — {r['motifs_deduction']}",
            f"Source : {r['document_source']}",
            f"Lien : {r['url_source']}",
        ] if x)
        uid = hashlib.sha1(f"{r['date']}|{r['debut']}|{r['type']}|{r['activite']}|{r['inventaire']}".encode()).hexdigest()[:20]
        ev = vevent(uid, r["date"], r["debut"], r["fin"], summary, desc, r["lieu"],
                    r["url_source"].split(" ; ")[0], r["type"])
        tout.append(ev)
        for k, (_, types) in FAMILLES.items():
            if r["type"] in types: par_fam[k].append(ev)
    ecrire("bmc_tout.ics", "BMC – programme complet", tout)
    for k, (titre, _) in FAMILLES.items():
        ecrire(f"bmc_{k}.ics", titre, par_fam[k])
    # périodes (trimestres, vacances, sessions, instituts) en événements de plusieurs jours
    per = []
    for r in csv.DictReader(open(os.path.join(PROG, "calendrier_periodes.csv"), encoding="utf-8")):
        if not r["debut"]: continue
        d0 = dt.date.fromisoformat(r["debut"]); d1 = dt.date.fromisoformat(r["fin"]) if r["fin"] else d0
        uid = hashlib.sha1(f"{r['debut']}|{r['libelle']}|{r['inventaire']}".encode()).hexdigest()[:20]
        desc = "\n".join(x for x in [r["libelle"], f"Note : {r['note']}" if r["note"] else "",
                                     f"Part déduite : {r['part_deduite_pct']} % — {r['motifs_deduction']}",
                                     f"Source : {r['document_source']}", f"Lien : {r['url_source']}"] if x)
        per.append(["BEGIN:VEVENT", f"UID:{uid}@bmc-programmes-aam", f"DTSTAMP:{STAMP}",
                    f"DTSTART;VALUE=DATE:{d0:%Y%m%d}", f"DTEND;VALUE=DATE:{d1 + dt.timedelta(days=1):%Y%m%d}",
                    "TRANSP:TRANSPARENT", f"SUMMARY:{esc(r['libelle'][:140])}", f"DESCRIPTION:{esc(desc)}",
                    f"URL:{r['url_source'].split(' ; ')[0]}", "END:VEVENT"])
    ecrire("bmc_periodes.ics", "BMC – trimestres, vacances, sessions", per)
    print(f"{len(tout)} événements, {len(per)} périodes ->", ", ".join(sorted(os.listdir(OUT))))
