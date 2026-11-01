#!/usr/bin/env python3
"""
Script de nettoyage de textes extraits de PDFs pour usage LLM.
- Reconstitue les mots coupés par tirets
- Fusionne les lignes orphelines
- Supprime les numéros de page
- Supprime les en-têtes/pieds de page répétés
- Normalise les paragraphes
"""

import re
import sys

def clean_text(text, title_patterns=None):
    """Nettoie le texte extrait d'un PDF."""

    lines = text.split('\n')

    # Étape 1: Supprimer les lignes qui ne sont que des numéros de page
    # (chiffres seuls, chiffres romains, ou avec peu de contexte)
    roman_pattern = r'^[ivxlcdmIVXLCDM]+$'
    page_num_pattern = r'^\d{1,4}$'

    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        # Ignorer les lignes qui sont juste des numéros
        if re.match(page_num_pattern, stripped):
            continue
        if re.match(roman_pattern, stripped):
            continue
        # Ignorer les lignes avec caractères parasites seuls
        if len(stripped) <= 2 and not stripped.isalpha():
            continue
        if stripped in ['a', 'i', 'w', 's', 'oS', 'on', 'ce', 'we', 'n']:
            continue
        cleaned_lines.append(line)

    # Étape 2: Supprimer les en-têtes/pieds de page répétés
    if title_patterns:
        filtered_lines = []
        for line in cleaned_lines:
            stripped = line.strip()
            skip = False
            for pattern in title_patterns:
                if re.match(pattern, stripped, re.IGNORECASE):
                    skip = True
                    break
            if not skip:
                filtered_lines.append(line)
        cleaned_lines = filtered_lines

    # Reconstituer le texte
    text = '\n'.join(cleaned_lines)

    # Étape 3: Reconstituer les mots coupés par tirets en fin de ligne
    # Pattern: mot- \n suite -> motsuite
    text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', text)

    # Étape 4: Fusionner les lignes orphelines (lignes courtes qui devraient être jointes)
    lines = text.split('\n')
    merged_lines = []
    buffer = ""

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Ligne vide = fin de paragraphe
        if not stripped:
            if buffer:
                merged_lines.append(buffer.strip())
                buffer = ""
            merged_lines.append("")
            continue

        # Si la ligne est très courte et ne finit pas par ponctuation finale
        # et n'est pas un titre (pas tout en majuscules), la fusionner
        is_title = stripped.isupper() and len(stripped) > 3
        ends_sentence = stripped[-1] in '.!?:' if stripped else False
        is_short = len(stripped) < 50

        if is_title:
            if buffer:
                merged_lines.append(buffer.strip())
                buffer = ""
            merged_lines.append(stripped)
        elif is_short and not ends_sentence and buffer:
            # Fusionner avec le buffer
            buffer = buffer.rstrip() + " " + stripped
        elif buffer:
            # Ajouter au buffer
            buffer = buffer.rstrip() + " " + stripped
        else:
            buffer = stripped

    if buffer:
        merged_lines.append(buffer.strip())

    # Étape 5: Nettoyer les espaces multiples et lignes vides consécutives
    text = '\n'.join(merged_lines)
    text = re.sub(r' +', ' ', text)  # Espaces multiples -> simple
    text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 lignes vides consécutives

    # Étape 6: Nettoyer les artefacts courants d'OCR
    text = re.sub(r'\bi]\b', '', text)  # Artefact "]"
    text = re.sub(r'\boS\b', '', text)
    text = re.sub(r'\s+,', ',', text)  # Espace avant virgule
    text = re.sub(r'\s+\.', '.', text)  # Espace avant point

    return text.strip()


def process_file(input_path, output_path, title_patterns=None):
    """Traite un fichier texte."""
    print(f"Traitement de {input_path}...")

    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()

    cleaned = clean_text(text, title_patterns)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(cleaned)

    # Stats
    original_lines = len(text.split('\n'))
    cleaned_lines = len(cleaned.split('\n'))
    original_size = len(text)
    cleaned_size = len(cleaned)

    print(f"  Lignes: {original_lines} -> {cleaned_lines}")
    print(f"  Taille: {original_size:,} -> {cleaned_size:,} caractères")
    print(f"  Sauvegardé: {output_path}")


if __name__ == "__main__":
    import os
    base_path = os.path.dirname(os.path.abspath(__file__))  # DATA_BMC/ dans le dépôt

    # Traiter farm_low_ocr.txt
    process_file(
        f"{base_path}/farm_low_ocr.txt",
        f"{base_path}/farm_low_clean.txt",
        title_patterns=[
            r'^The Farm at Black Mountain College$',
            r'^BLACK MOUNTAIN COLLEGE$',
        ]
    )

    # Traiter Duberman
    process_file(
        f"{base_path}/Duberman_Black_Mountain_College.txt",
        f"{base_path}/Duberman_clean.txt",
        title_patterns=[
            r'^BLACK MOUNTAIN$',
            r'^INTRODUCTION$',
            r'^Martin Duberman$',
        ]
    )

    print("\nTerminé!")
