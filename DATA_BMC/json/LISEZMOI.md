# DATA_BMC/json — JSON rangés (2/11/2026)

Rangement fait par `bmc-programmes-aam/scripts/json_ranger.py`. Inventaire de tous les JSON du dépôt et statut de
chacun : `CATALOGUE.md` (résumé) et `catalogue.csv` (liste complète, 1 334 fichiers).

## `semainier/` — un fichier par source, compilé, complet, unique, autonome

| fichier | source | contenu | lu par |
|---|---|---|---|
| `duberman_chronologie.json` | Duberman 1972 (« Chronos 2 ») | 559 événements avec page et citation ; enrichissements des versions cumulées (personnes présentes, Wikipedia), marqués comme tels | `chronos_duberman.py` |
| `harris_entretiens.json` | entretiens de Mary Emma Harris | 165 entretiens, 715 faits, cours, lieux, faits incertains (transcriptions : `DATA_BMC/Chronos/harris_transcripts/`) | `chronos_harris.py` |
| `ferme_silver.json` | Silver, *The Farm at Black Mountain College* (2024) | 193 événements, 135 documents cités, notes manuscrites | `chronos_ferme.py` |
| `asheville_documents.json` | 377 fiches de l'Asheville Art Museum | événements, calendrier, décisions, visiteurs, enseignants, étudiants, cours ; inventaire, titre et URL de chaque fiche | `chronos_asheville.py` |

- **Complet** : chaque variante (« _temp », « _enriched », « _with_presence », « _final », « _complete », « _ultimate »,
  « _wikipedia ») a été comparée enregistrement par enregistrement : rien ne manque ; les enrichissements qu'elles seules
  avaient sont repris. Chaque enregistrement d'origine est identique dans le fichier compilé (seules des clés s'ajoutent).
- **Unique** : une seule version en service ; un doublon (même date, même texte, même document) est gardé et marqué
  `doublon_de` (1 dans la ferme). Les originaux et les variantes sont rangés dans `DATA_BMC/Chronos/_versions/` (git mv).
- **Autonome** : clé `_meta` (description, champs, nature de la source, fichier d'origine avec sha1, variantes vérifiées,
  contrôles, scripts qui le lisent) et un identifiant stable par enregistrement (`id`).
- Contrôle : les quatre scripts relancés sur ces fichiers redonnent exactement les mêmes couches du semainier.

Ce sont des extractions automatiques (modèle de langage, décembre 2025) : dans le semainier, chaque entrée reste
confrontée à l'AAM, à Duberman et au texte cité.

## `hors_semainier/` — mis de côté (n'entre pas dans le semainier)

- `personnes_relations.json` : graphe des relations (compilé : version normalisée + les 100 relations détaillées
  perdues par elle ; les anciennes versions dans `_versions/`).
- `personnes_enrichissements.json` : résumés de personnes tirés de Duberman (256 ; quand deux passages diffèrent, le
  second est gardé en `autre_lecture`).
- `bmc_people_index.json` (index de 2 263 noms), `wikipedia_people_data.json`, `wikipedia_cache.json` : données de
  personnes en partie produites par Wikipedia ; la référence pour les personnes reste le BMC Yearbook
  (`DATA_BMC/bmcyearbook/`).
- `bmc_series_bible.json` : bible d'une série de fiction (24 saisons) — pas une source.
- `weather_py/` : scripts et modèle vide d'une archive météo — pas de données.

## Restent en place

Le BMC Yearbook (`DATA_BMC/bmcyearbook/`), les fiches du musée (`DATA_BMC/Chronos/asheville_bmc_collection/`), la
chaîne du scénario (`bmc-scenario/` : sortie, synthèses, texte ; `etat/` et `comparaison/` y sont internes) et les
pièces de travail des dépouillements (voir `CATALOGUE.md`).
