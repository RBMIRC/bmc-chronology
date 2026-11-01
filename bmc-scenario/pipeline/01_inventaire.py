"""01 — Inventaire des sources : un numéro stable par fichier, son rôle, sa priorité.

Relancer après avoir ajouté des fichiers : les numéros déjà donnés ne bougent pas.
Sortie : sources.csv (id, fichier, role, priorite, court, format, pages).
"""
import csv
import sys

import fitz

from config import CLASSEMENT, INVENTAIRE, SOURCES

FORMATS = {".pdf", ".epub", ".mobi"}


def classer(nom):
    bas = nom.lower()
    for motif, role, prio, court in CLASSEMENT:
        if motif in bas:
            return role, prio, court
    return "a_classer", "B", nom[:40]


def pages(chemin):
    if chemin.suffix.lower() != ".pdf":
        return ""
    try:
        return fitz.open(chemin).page_count
    except Exception:
        return "illisible"


def main():
    anciens = {}
    if INVENTAIRE.exists():
        with open(INVENTAIRE, newline="") as f:
            for r in csv.DictReader(f):
                anciens[r["fichier"]] = r
    suivant = max((int(r["id"]) for r in anciens.values()), default=0) + 1

    fichiers = sorted(p for p in SOURCES.rglob("*")
                      if p.is_file() and p.suffix.lower() in FORMATS and not p.name.startswith("."))
    lignes = []
    for p in fichiers:
        rel = str(p.relative_to(SOURCES))
        role, prio, court = classer(p.name)
        if rel in anciens:
            r = anciens[rel]
            # le rôle se règle dans config.py ; on le relit à chaque passage
            r.update(role=role, priorite=prio, court=court)
        else:
            r = {"id": f"{suivant:03d}", "fichier": rel, "role": role, "priorite": prio,
                 "court": court, "format": p.suffix.lower()[1:], "pages": pages(p)}
            suivant += 1
        lignes.append(r)

    lignes.sort(key=lambda r: r["id"])
    with open(INVENTAIRE, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "fichier", "role", "priorite", "court", "format", "pages"])
        w.writeheader()
        w.writerows(lignes)

    a_classer = [r for r in lignes if r["role"] == "a_classer"]
    print(f"{len(lignes)} sources → {INVENTAIRE}")
    for role in sorted({r["role"] for r in lignes}):
        print(f"  {role:13s} {sum(r['role'] == role for r in lignes)}")
    if a_classer:
        print("À classer dans config.CLASSEMENT :", *[r["fichier"] for r in a_classer], sep="\n  ")
        sys.exit(1)


if __name__ == "__main__":
    main()
