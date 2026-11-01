# Suivi — semainier BMC (branche `semainier-cloud`)

Reprise : lire ce fichier, puis `PROMPT_CLAUDE_CLOUD.md` (consigne complète).

## État par étape

| Étape | Objet | État | Commit |
|---|---|---|---|
| 0 | Chemins `~/Documents/...` → chemins relatifs à la racine du dépôt | fait | « chemins relatifs » |
| 1 | Intégrer Duberman au semainier | fait | « semainier : couche Duberman » |
| 2 | Couche spéculative 1949-50 → 1956-57 | en cours | une année = un commit |
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

| Année | État | Semaines | Entrées de gabarit (développées) | Part déduite moy. | Commit |
|---|---|---|---|---|---|
| 1949-50 | fait | 45 (aut. 18, print. 18, été 9) | 263 (~4 380) | 60,5 % (aut. 63, print. 65, été 42) | « speculation 1949-50 » |

### Notes 1949-50
- Sources : 2017.40.360 (corps enseignant de septembre 1949), 2017.40.048 (« courses given » 1949-50, sans semestre),
  2017.40.047 (automne 1949), 2017.40.049, 2017.40.359 (été 1950), 2017.40.282 (danse, 10 juin 1950) ; Duberman ch. 11
  pour Fiore, Larsen et les Jennerjahn (absents de la liste de septembre, présents dès la rentrée selon ¶1418).
- Non programmés : Seelye (théâtre, invitée, absente des cours donnés), Rosen (séminaire « not yet definite »),
  botanique (« at a neighboring college »). Olson : visiteur, rien de reconstitué.
- Réunions du corps enseignant : jours irréguliers chez Duberman, pas de créneau régulier reconstitué.
- Question : Flola / Flora Shepard (2017.40.360 écrit « Flora », 2017.40.049 et Duberman « Flola ») ; « Flola » retenu.

## Points à vérifier sur scan
(aucun pour l'instant)
