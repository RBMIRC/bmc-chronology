"""02 — Texte page par page (PDF : PyMuPDF, scans : Tesseract ; EPUB/MOBI : chapitres).

Sortie : texte/NNN.jsonl.gz, une ligne par page {"i", "page", "texte", "ocr"}.
"page" est le folio imprimé quand le PDF le donne, sinon le rang (1, 2, …) ;
pour les EPUB, "ch3" = 3e chapitre. Saute les sources déjà faites.
"""
import csv
import gzip
import json
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import fitz

from config import INVENTAIRE, SOURCES, TEXTE

SEUIL_SCAN = 40  # caractères : en dessous, la page est une image → OCR


def nettoyer(t):
    t = t.replace("­", "")
    t = re.sub(r"(\w)-\n(\w)", r"\1\2", t)        # coupures de fin de ligne
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def ocr_page(page):
    pix = page.get_pixmap(dpi=300, colorspace=fitz.csGRAY)
    with tempfile.NamedTemporaryFile(suffix=".png") as f:
        pix.save(f.name)
        r = subprocess.run(["tesseract", f.name, "-", "-l", "eng", "--psm", "3"],
                           capture_output=True, text=True)
    return r.stdout


def pages_pdf(chemin):
    doc = fitz.open(chemin)
    for i, page in enumerate(doc):
        t = page.get_text()
        ocr = False
        if len(t.strip()) < SEUIL_SCAN and page.get_images():
            t, ocr = ocr_page(page), True
        yield {"i": i, "page": page.get_label() or str(i + 1), "texte": nettoyer(t), "ocr": ocr}


def pages_epub(chemin):
    import ebooklib
    from bs4 import BeautifulSoup
    from ebooklib import epub
    livre = epub.read_epub(str(chemin), options={"ignore_ncx": True})
    n = 0
    for item in livre.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        soupe = BeautifulSoup(item.get_content(), "html.parser")
        t = nettoyer(soupe.get_text("\n"))
        if len(t) < 30:
            continue
        n += 1
        yield {"i": n - 1, "page": f"ch{n}", "texte": t, "ocr": False}


def pages_mobi(chemin):
    with tempfile.TemporaryDirectory() as d:
        sortie = Path(d) / "livre.epub"
        subprocess.run(["ebook-convert", str(chemin), str(sortie)], capture_output=True, check=True)
        yield from pages_epub(sortie)


def traiter(ligne):
    dest = TEXTE / f"{ligne['id']}.jsonl.gz"
    if dest.exists():
        return ligne["id"], "déjà fait", 0, 0
    chemin = SOURCES / ligne["fichier"]
    lecteur = {"pdf": pages_pdf, "epub": pages_epub, "mobi": pages_mobi}[ligne["format"]]
    tmp = dest.with_suffix(".tmp")
    n = n_ocr = 0
    with gzip.open(tmp, "wt", encoding="utf-8") as f:
        for p in lecteur(chemin):
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
            n += 1
            n_ocr += p["ocr"]
    tmp.rename(dest)
    return ligne["id"], "ok", n, n_ocr


def main():
    TEXTE.mkdir(exist_ok=True)
    with open(INVENTAIRE, newline="") as f:
        lignes = [r for r in csv.DictReader(f) if r["role"] != "doublon"]
    if len(sys.argv) > 1:
        lignes = [r for r in lignes if r["id"] in sys.argv[1:]]
    with ProcessPoolExecutor(6) as ex:
        for id_, etat, n, n_ocr in ex.map(traiter, lignes):
            print(f"{id_} {etat:9s} {n:4d} p.{f'  ({n_ocr} OCR)' if n_ocr else ''}", flush=True)


if __name__ == "__main__":
    main()
