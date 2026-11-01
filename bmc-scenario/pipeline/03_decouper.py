"""03 — Morceaux à envoyer au modèle, avec repères de page « [p. 123] ».

Écarte les pages de bruit (OCR d'images, index, crédits). Chaque morceau garde
la liste des pages qu'il couvre, pour que chaque fait extrait reste citable.
Sortie : morceaux/morceaux.jsonl + morceaux/_bilan.csv
"""
import csv
import gzip
import json
import re

from config import (CHEVAUCHEMENT_CARACTERES, INVENTAIRE, MORCEAU_CARACTERES,
                    MORCEAUX, TEXTE)

MOT = re.compile(r"^[A-Za-zÀ-ÿ'’\-]{2,}[.,;:!?)\"”]*$")
VOYELLE = re.compile(r"[aeiouyàâéèêëîïôöùûüAEIOUY]")


def qualite(t):
    """Part des jetons qui ressemblent à des mots (0 = bruit d'OCR, 1 = prose)."""
    jetons = t.split()
    if not jetons:
        return 0.0
    bons = sum(1 for j in jetons if MOT.match(j) and VOYELLE.search(j))
    return bons / len(jetons)


def est_index(t):
    """Index / table : beaucoup de lignes finissant par des numéros de page."""
    lignes = [l for l in t.splitlines() if l.strip()]
    if len(lignes) < 15:
        return False
    num = sum(1 for l in lignes if re.search(r"\d{1,3}(\s*[,–-]\s*\d{1,3})*\s*$", l))
    return num / len(lignes) > 0.6


def garder(p):
    t = p["texte"]
    if len(t) < 120:
        return "court"
    if qualite(t) < 0.55:
        return "bruit"
    if est_index(t):
        return "index"
    return "ok"


def main():
    MORCEAUX.mkdir(exist_ok=True)
    with open(INVENTAIRE, newline="") as f:
        sources = [r for r in csv.DictReader(f) if r["role"] != "doublon"]

    bilan, morceaux = [], []
    for s in sources:
        chemin = TEXTE / f"{s['id']}.jsonl.gz"
        if not chemin.exists():
            continue
        pages = [json.loads(l) for l in gzip.open(chemin, "rt", encoding="utf-8")]
        stats = {"ok": 0, "court": 0, "bruit": 0, "index": 0}
        tampon, pages_tampon, n = "", [], 0

        def vider():
            nonlocal tampon, pages_tampon, n
            if tampon.strip():
                n += 1
                morceaux.append({"id": f"{s['id']}-{n:03d}", "source": s["id"],
                                 "pages": pages_tampon, "texte": tampon})
            queue = tampon[-CHEVAUCHEMENT_CARACTERES:]
            tampon, pages_tampon = (queue, pages_tampon[-1:]) if queue.strip() else ("", [])

        for p in pages:
            etat = garder(p)
            stats[etat] += 1
            if etat != "ok":
                continue
            bloc = f"\n\n[p. {p['page']}]\n{p['texte']}"
            # un chapitre d'EPUB peut dépasser la taille d'un morceau : on le coupe
            while len(bloc) > MORCEAU_CARACTERES:
                coupe = bloc.rfind("\n", 0, MORCEAU_CARACTERES)
                coupe = coupe if coupe > MORCEAU_CARACTERES // 2 else MORCEAU_CARACTERES
                if len(tampon) + coupe > MORCEAU_CARACTERES:
                    vider()
                tampon += bloc[:coupe]
                pages_tampon.append(p["page"])
                vider()
                bloc = f"\n\n[p. {p['page']}, suite]\n" + bloc[coupe:]
            if len(tampon) + len(bloc) > MORCEAU_CARACTERES:
                vider()
            tampon += bloc
            if not pages_tampon or pages_tampon[-1] != p["page"]:
                pages_tampon.append(p["page"])
        if len(tampon) > CHEVAUCHEMENT_CARACTERES + 200:
            vider()
        bilan.append({"id": s["id"], "titre": s["court"], "role": s["role"], "priorite": s["priorite"],
                      "pages": len(pages), **stats, "morceaux": n,
                      "caracteres": sum(len(m["texte"]) for m in morceaux if m["source"] == s["id"])})

    with open(MORCEAUX / "morceaux.jsonl", "w", encoding="utf-8") as f:
        for m in morceaux:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")
    with open(MORCEAUX / "_bilan.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(bilan[0]))
        w.writeheader()
        w.writerows(bilan)

    car = sum(b["caracteres"] for b in bilan)
    print(f"{len(morceaux)} morceaux, {car/1e6:.1f} M caractères ≈ {car/4/1e6:.1f} M tokens")
    for k in ("ok", "court", "bruit", "index"):
        print(f"  pages {k:6s} {sum(b[k] for b in bilan)}")
    for prio in "ABC":
        sel = [b for b in bilan if b["priorite"] == prio]
        print(f"  priorité {prio} : {len(sel)} sources, {sum(b['morceaux'] for b in sel)} morceaux")


if __name__ == "__main__":
    main()
