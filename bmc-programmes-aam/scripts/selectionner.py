"""Sélectionne les fiches qui concernent l'organisation des cours, écrit un .txt OCR par fiche
et la liste des pages (liste_pages.csv / .txt). Relançable, n'efface rien."""
import json, re, os, csv
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = json.load(open(os.path.join(ROOT, "fiches.json")))
_vus = {f["accession"] for f in F}
if os.path.exists(os.path.join(ROOT, "fiches_sondees.json")):
    F += [f for f in json.load(open(os.path.join(ROOT, "fiches_sondees.json"))) if f["accession"] not in _vus]

def categorie(f):
    t = f["title"]; tl = t.lower()
    if f["object_type"] not in ("Archival Documents", "Manuscripts"):
        return None
    if re.search(r"community bulletin|faculty meeting bulletin|everybody reads the bulletin|not a community bulletin|mid-summer report", tl):
        return "B_bulletins_hebdomadaires"
    if not re.search(r"\brecital\b", tl) and re.search(r"audit|\bletter\b|class notes|rollins|krenek|schoenberg|josef albers'|ray nash|handweaving today|"
                 r"view across|new studies building|necklaces|prehistoric|converting the impossible|constitution|"
                 r"physics for liberal|art as a fourth|the idea of black mountain|photo booklet|views of and from|"
                 r"evolution of housing|my consultants|reunion|poem|beyond the duration|bulletin [245]\b|"
                 r"bulletin 6: the building|review june 1951|college that built itself|these artists have chosen|"
                 r"invitation from the black mountain association|admission card|dalton school|palmer memorial|"
                 r"wartime scholar|cheers|postcard|enclosure|greeting card|portrait of|untitled|notes triangle|ode to|address for|education in a time|meaning of art|forget it|huellas|lake eden inn|fundamentalism|building project", tl) or re.match(r"(\d+ page )?(hand|typed|letter)", tl):
        return None
    if re.search(r"concert|recital|\bplays?\b|winterset|frome|invalid|moliere|medecin|plautus|wilde|odets|danse|"
                 r"shakespeare|carroll|outward bound|quare medicine|dance program|thank|thursday evening|steurmann|choral|"
                 r"reading of two|quartet|good and obedient|college (saturday|sunday)|demonstration of the light", tl):
        return "D_evenements_concerts_theatre"
    if re.search(r"newsletter", tl):
        return "C_newsletters"
    if re.search(r"catalog|announcements|insert|supplement|summer session|institute|summer program|seminar on america|"
                 r"work camp|list of faculty|bulletin|summary of information|foreword|"
                 r"bmc education|summer of music|summer 1954 poster|design, april, 1946|friends magazine|work camp|fifteen years report|bmc sheet", tl):
        return "A_catalogues_annonces"
    return "?"

def slug(s, n=70):
    s = re.sub(r"[^\w\s-]", "", s, flags=re.U).strip()
    return re.sub(r"\s+", "_", s)[:n]

if __name__ == "__main__":
    out = os.path.join(ROOT, "pages_txt")
    rows = []
    for f in F:
        c = categorie(f)
        if not c: continue
        if c == "?": print("à trier :", f["accession"], f["title"][:90]); continue
        d = os.path.join(out, c); os.makedirs(d, exist_ok=True)
        fn = f"{f['accession']}_{slug(f['title'])}.txt"
        with open(os.path.join(d, fn), "w", encoding="utf-8") as fh:
            fh.write(f"TITRE : {f['title']}\nDATE : {f['date']}\nN° D'INVENTAIRE : {f['accession']}\n"
                     f"TYPE : {f['object_type']}\nURL : {f['url']}\nCRÉDIT : {f['credit']}\n"
                     f"IMAGES : {', '.join('https://collection.ashevilleart.org' + i for i in f['images'])}\n"
                     + "=" * 72 + "\n\n" + f["description"] + "\n")
        rows.append({"categorie": c, "accession": f["accession"], "date": f["date"], "titre": f["title"],
                     "url": f["url"], "fichier": f"pages_txt/{c}/{fn}", "caracteres": len(f["description"])})
    rows.sort(key=lambda r: (r["categorie"], r["accession"]))
    with open(os.path.join(ROOT, "liste_pages.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    with open(os.path.join(ROOT, "liste_pages.txt"), "w", encoding="utf-8") as fh:
        cur = None
        for r in rows:
            if r["categorie"] != cur:
                cur = r["categorie"]; fh.write(f"\n## {cur}\n\n")
            fh.write(f"{r['accession']}\t{r['date']}\t{r['titre']}\n\t{r['url']}\n")
    import collections
    print(collections.Counter(r["categorie"] for r in rows), len(rows))
