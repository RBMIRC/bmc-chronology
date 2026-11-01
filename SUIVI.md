# Suivi — semainier BMC (branche `semainier-cloud`)

Reprise : lire ce fichier, puis `PROMPT_CLAUDE_CLOUD.md` (consigne complète).

## État par étape

| Étape | Objet | État | Commit |
|---|---|---|---|
| 0 | Chemins `~/Documents/...` → chemins relatifs à la racine du dépôt | fait | « chemins relatifs » |
| 1 | Intégrer Duberman au semainier | en cours | |
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

## Couche spéculative par année (étape 2)

| Année | État | Semaines | Entrées | Part déduite moy. | Commit |
|---|---|---|---|---|---|

## Points à vérifier sur scan
(aucun pour l'instant)
