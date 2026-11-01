# Suivi — semainier BMC (branche `semainier-cloud`)

Reprise : lire ce fichier, puis `PROMPT_CLAUDE_CLOUD.md` (consigne complète).

## État par étape

| Étape | Objet | État | Commit |
|---|---|---|---|
| 0 | Chemins `~/Documents/...` → chemins relatifs à la racine du dépôt | fait | « chemins relatifs » |
| 1 | Intégrer Duberman au semainier | fait | « semainier : couche Duberman » |
| 2 | Couche spéculative 1949-50 → 1956-57 | à faire | |
| 3 | Contrôles (`construire.py --verifier`, navigateur headless, avant/après) | à faire | |

## Étape 0 — chemins
- `scripts/selectionner.py` : déjà relatif (`ROOT` calculé depuis le script), rien à changer.
- `duberman/construire_duberman.py` : `CHRONOS` → `DATA_BMC/Chronos 2/bmc_chronology.json` (absent du dépôt).
  **Ne pas relancer ce script** dans le dépôt : sans Chronos 2, il réécrirait `recoupements_duberman.csv`
  et `rapport_duberman.txt` sans la partie Chronos.
- `programme/audit/lots/maj_index.py`, `DATA_BMC/clean_text.py` : chemins relatifs au script.
- Non modifiés (hors périmètre, cibles absentes du dépôt) : `duberman/pages_notes.py` (`/tmp/dub/tess`, OCR non recopié),
  `DATA_BMC/weather_py/generate_radio_json.py` (sortie `METEO BMC/`), `bmc-scenario/pipeline/config.py` (`~/Downloads/...`).

## Étape 1 — Duberman (fait)
- Avant : `data.js` = 4 650 activités attestées, 324 documents. Après : 4 650 activités attestées (inchangé),
  + 484 événements Duberman dans la grille, 434 au panneau (date imprécise), 15 doublons fondus, 2 sans date
  (non affichés) ; 1 355 documents (324 AAM + 1 031 Duberman).
- Décisions de doublon : `bmc-programmes-aam/duberman/001_doublons_aam.csv` (15 doublons, 13 possibles, 66 rejetés).
- Contrôle navigateur headless (Chromium) : semaines 1933-10-16, 1944-07-17, 1944-08-28, 1951-07-02, 1956-10-01,
  vues Semaine et Présences, case Duberman, fiches : 0 erreur console.
- `programme/` non modifié.

## Couche spéculative par année (étape 2)

| Année | État | Semaines | Entrées | Part déduite moy. | Commit |
|---|---|---|---|---|---|

## Points à vérifier sur scan
(aucun pour l'instant)
