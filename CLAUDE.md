# BMC — semainier (copie de travail pour Claude cloud)

Copie (pas les originaux) de `~/Documents/bmc-programmes-aam/`, `~/Documents/DATA BMC/` et `~/Documents/bmc-scenario/` au 1/11/2026.
Texte et données seulement : pas de PDF, de scans, de caches, de sauvegardes ni d'images.

## Objectif
Construire / compléter le semainier du Black Mountain College (1933-1957) : programme jour par jour, avec part déduite.

## Contenu
- `bmc-programmes-aam/` : projet principal. Lire d'abord `LISEZMOI.md`. `semainier/` (index.html + data.js), `programme/`, `speculation/`, `scripts/`, `duberman/` (935 événements dépouillés, voir `LISEZMOI_duberman.md`), `extraction/` et `pages_txt/` (OCR des fiches), `fiches.json`.
- `DATA_BMC/json/` : JSON rangés (2/11/2026) : `semainier/` (un JSON compilé par source Chronos), `hors_semainier/`, `CATALOGUE.md` ; variantes et originaux dans `DATA_BMC/Chronos/_versions/`.
- `DATA_BMC/` : textes corrigés (Duberman, Silver *The Farm*, Rumaker v6) et scripts de nettoyage ; `_correction_*` = pièces de la correction.
- `bmc-scenario/` : scénario JSON 24 ans ; `sortie/009_...json.gz` est la dernière version (décompresser pour lire).

## Règles
- Ne jamais supprimer ni écraser une sortie existante : sorties additives numérotées `NNN_`.
- Toute entrée non attestée garde sa `part_deduite_pct` et ses motifs (barème dans `scripts/speculer.py`).
- Source qui fait foi en cas de conflit : document daté attesté > Duberman corrigé > spéculation.
- Les scripts contiennent des chemins `~/Documents/...` en dur : les adapter à la racine du dépôt avant de les lancer.
- Écrire en français.
