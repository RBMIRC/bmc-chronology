#!/usr/bin/env python3
"""Convertit un dossier de PDF en fichiers texte, page par page, pour l'analyse (à lancer sur l'ordinateur qui a les PDF).

Les PDF ne vont pas dans le dépôt (CLAUDE.md : texte et données seulement) ; seuls les .txt et l'inventaire y sont versés.

Pour chaque PDF du dossier (sous-dossiers compris) :
  - texte de chaque page par pdftotext (poppler), avec une marque « --- Page N --- » (N = page du PDF) ;
  - une page sans texte (scan) est passée à l'OCR : tesseract sur l'image de la page (pdftoppm, 300 dpi), langue
    « eng+fra » par défaut ; la marque devient « --- Page N (OCR) --- » ;
  - un fichier <sortie>/<nom du pdf>.txt, jamais écrasé (suffixe _2, _3… s'il existe déjà) ;
  - une ligne dans <sortie>/_inventaire.csv : fichier, pages, pages OCR, pages vides, octets, sha1 du PDF.

Prérequis (macOS) :  brew install poppler tesseract tesseract-lang
Usage :              python3 pdf_vers_texte.py <dossier des PDF> <dossier de sortie> [--langue eng+fra] [--sans-ocr]
"""
import csv, hashlib, os, shutil, subprocess, sys, tempfile


def lancer(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, errors="replace")


def nb_pages(pdf):
    r = lancer(["pdfinfo", pdf])
    for l in r.stdout.splitlines():
        if l.startswith("Pages:"): return int(l.split()[1])
    return 0


def texte_page(pdf, n):
    return lancer(["pdftotext", "-layout", "-f", str(n), "-l", str(n), pdf, "-"]).stdout


def ocr_page(pdf, n, langue):
    with tempfile.TemporaryDirectory() as d:
        base = os.path.join(d, "p")
        lancer(["pdftoppm", "-r", "300", "-f", str(n), "-l", str(n), "-png", pdf, base])
        imgs = sorted(f for f in os.listdir(d) if f.endswith(".png"))
        if not imgs: return ""
        return lancer(["tesseract", os.path.join(d, imgs[0]), "stdout", "-l", langue]).stdout


def sortie_libre(chemin):
    if not os.path.exists(chemin): return chemin
    racine, ext = os.path.splitext(chemin); k = 2
    while os.path.exists(f"{racine}_{k}{ext}"): k += 1
    return f"{racine}_{k}{ext}"


def main():
    if len(sys.argv) < 3: sys.exit(__doc__)
    src, dst = sys.argv[1], sys.argv[2]
    langue = sys.argv[sys.argv.index("--langue") + 1] if "--langue" in sys.argv else "eng+fra"
    ocr = "--sans-ocr" not in sys.argv
    for outil in ["pdfinfo", "pdftotext"] + (["pdftoppm", "tesseract"] if ocr else []):
        if not shutil.which(outil): sys.exit(f"outil manquant : {outil} (brew install poppler tesseract tesseract-lang)")
    os.makedirs(dst, exist_ok=True)
    inv = os.path.join(dst, "_inventaire.csv"); neuf = not os.path.exists(inv)
    pdfs = sorted(os.path.join(r, f) for r, _, fs in os.walk(src) for f in fs if f.lower().endswith(".pdf"))
    print(f"{len(pdfs)} PDF dans {src}")
    with open(inv, "a", encoding="utf-8", newline="") as fi:
        w = csv.writer(fi)
        if neuf: w.writerow(["fichier_txt", "pdf", "pages", "pages_ocr", "pages_vides", "octets_pdf", "sha1_pdf"])
        for pdf in pdfs:
            n = nb_pages(pdf); n_ocr = n_vide = 0; morceaux = []
            for k in range(1, n + 1):
                t = texte_page(pdf, k)
                if len(t.strip()) < 20 and ocr:
                    t2 = ocr_page(pdf, k, langue)
                    if t2.strip(): morceaux.append(f"--- Page {k} (OCR) ---\n{t2.strip()}\n"); n_ocr += 1; continue
                if not t.strip(): n_vide += 1
                morceaux.append(f"--- Page {k} ---\n{t.strip()}\n")
            nom = os.path.splitext(os.path.relpath(pdf, src))[0].replace(os.sep, "__")
            sortie = sortie_libre(os.path.join(dst, nom + ".txt"))
            with open(sortie, "w", encoding="utf-8") as f:
                f.write(f"SOURCE : {os.path.relpath(pdf, src)}\nPAGES : {n} (dont {n_ocr} par OCR, {n_vide} vides)\n{'=' * 70}\n\n")
                f.write("\n".join(morceaux))
            sha = hashlib.sha1(open(pdf, "rb").read()).hexdigest()
            w.writerow([os.path.basename(sortie), os.path.relpath(pdf, src), n, n_ocr, n_vide, os.path.getsize(pdf), sha])
            print(f"  {os.path.relpath(pdf, src)} : {n} pages ({n_ocr} OCR, {n_vide} vides) → {os.path.basename(sortie)}")


if __name__ == "__main__":
    main()
