# Catalogue des JSON du dépôt (rangement du 2/11/2026)

1334 fichiers JSON (dont 377 métadonnées de fiches du musée). Liste complète : `catalogue.csv`. Généré par `bmc-programmes-aam/scripts/json_ranger.py`.

| statut | fichiers |
|---|---|
| source du semainier (synthèses du scénario) | 795 |
| source : fiche du musée (métadonnées) | 377 |
| texte des livres (OCR paginé) | 59 |
| interne à l'audit | 26 |
| interne à la chaîne bmc-scenario (hors semainier) | 16 |
| sortie numérotée (integrer_syntheses.py) | 15 |
| version rangée (remplacée par DATA_BMC/json/semainier/) | 14 |
| pièce de la correction du texte de Silver | 8 |
| hors semainier | 7 |
| hors semainier — version antérieure | 5 |
| source du semainier (compilé) | 4 |
| pièce du dépouillement de Duberman | 3 |
| source du semainier (fiches AAM) | 2 |
| source du semainier (base des personnes) | 1 |
| pièce du dépouillement de Rumaker | 1 |
| source du semainier (scénario) | 1 |

## Sources du semainier compilées (`DATA_BMC/json/semainier/`)

Un fichier par source, complet (toutes les variantes vérifiées, rien ne manque), unique (doublons marqués, pas de version concurrente en service) et autonome (`_meta` : description, champs, provenance avec sha1, contrôles, scripts qui le lisent). Les originaux et les variantes sont rangés dans `DATA_BMC/Chronos/_versions/` (git mv).

### duberman_chronologie.json

Duberman, Black Mountain: An Exploration in Community (1972) — chronologie extraite (« Chronos 2 »).

- Origine : `DATA_BMC/Chronos/_versions/bmc_chronology.json` (sha1 a1ef1efedf80).
- Contrôles : evenements 559, doublons_marques 0, sans_date 0, sans_citation 83.
- Variante `bmc_chronology_temp.json` : evenements duberman 556, absents du compile ajoutes 0, enrichissements repris {} (passage partiel antérieur).
- Variante `bmc_chronology_enriched.json` : evenements duberman 559, absents du compile ajoutes 0, enrichissements repris {'people_in_presence': 498} (version cumulée (Duberman + ferme + Harris + Asheville selon la version)).
- Variante `bmc_chronology_with_presence.json` : evenements duberman 559, absents du compile ajoutes 0, enrichissements repris {} (version cumulée (Duberman + ferme + Harris + Asheville selon la version)).
- Variante `bmc_chronology_final.json` : evenements duberman 559, absents du compile ajoutes 0, enrichissements repris {} (version cumulée (Duberman + ferme + Harris + Asheville selon la version)).
- Variante `bmc_chronology_complete.json` : evenements duberman 559, absents du compile ajoutes 0, enrichissements repris {} (version cumulée (Duberman + ferme + Harris + Asheville selon la version)).
- Variante `bmc_chronology_ultimate.json` : evenements duberman 559, absents du compile ajoutes 0, enrichissements repris {} (version cumulée (Duberman + ferme + Harris + Asheville selon la version)).
- Variante `bmc_chronology_wikipedia.json` : evenements duberman 559, absents du compile ajoutes 0, enrichissements repris {'people_wikipedia': 438} (version cumulée (Duberman + ferme + Harris + Asheville selon la version)).

### harris_entretiens.json

Entretiens de Mary Emma Harris (Black Mountain College Project) — faits extraits.

- Origine : `DATA_BMC/Chronos/_versions/harris_events.json` (sha1 ec1694ac0ed1).
- Contrôles : entretiens 165, faits 715, doublons_marques 0, transcriptions_presentes 165.
- Variante `harris_temp.json` : entretiens 160, entretiens absents ajoutes 0, faits absents ajoutes 0 (passage partiel antérieur).
- Variante `bmc_chronology_ultimate.json` : faits harris 715, absents du compile 0 (version cumulée : mêmes faits remis à plat (people_involved → people, interview_source)).

### ferme_silver.json

David Silver, The Farm at Black Mountain College (2024) — événements et documents extraits.

- Origine : `DATA_BMC/Chronos/_versions/farm_events.json` (sha1 bd9ab68273aa).
- Contrôles : evenements 193, documents 135, doublons_marques 1, evenements_sans_date 4.
- Variante `farm_temp.json` : evenements 177, documents 126, evenements absents ajoutes 0, documents absents ajoutes 0 (passage partiel antérieur).
- Variante `bmc_chronology_ultimate.json` : entrees ferme 303, dont documents remis a plat 110, absents du compile 0 (version cumulée : événements et documents datés remis à plat).

### asheville_documents.json

Collection Black Mountain College de l'Asheville Art Museum — 377 fiches lues automatiquement.

- Origine : `DATA_BMC/Chronos/_versions/asheville_events.json` (sha1 7d3a32433a88).
- Contrôles : documents 377, events 1906, calendar_dates 229, decisions 133, visitors_mentioned 838, faculty_listed 1443, students_listed 2147, courses_offered 1440, doublons_marques 0, documents_sans_fiche_musee 0.
- Variante `asheville_temp.json` : documents 350, documents absents ajoutes 0, faits absents ajoutes 0 (passage partiel antérieur).
- Variante `bmc_chronology_ultimate.json` : entrees asheville 3062, hors rubrique events 1158, dont retrouvees dans calendar dates decisions visitors 1158 (version cumulée : les rubriques calendar_dates, decisions et visitors_mentioned remises à plat en événements).

## Hors semainier (`DATA_BMC/json/hors_semainier/`)

- `DATA_BMC/json/hors_semainier/_versions/bmc_relations.json` — hors semainier — version antérieure
- `DATA_BMC/json/hors_semainier/_versions/bmc_relations_enriched.json` — hors semainier — version antérieure
- `DATA_BMC/json/hors_semainier/_versions/bmc_relations_normalized.json` — hors semainier — version antérieure
- `DATA_BMC/json/hors_semainier/_versions/enrichments_temp.json` — hors semainier — version antérieure
- `DATA_BMC/json/hors_semainier/_versions/people_enrichments.json` — hors semainier — version antérieure
- `DATA_BMC/json/hors_semainier/bmc_people_index.json` — hors semainier
- `DATA_BMC/json/hors_semainier/bmc_series_bible.json` — hors semainier
- `DATA_BMC/json/hors_semainier/personnes_enrichissements.json` — hors semainier
- `DATA_BMC/json/hors_semainier/personnes_relations.json` — hors semainier
- `DATA_BMC/json/hors_semainier/weather_py/bmc_weather_archive_template.json` — hors semainier
- `DATA_BMC/json/hors_semainier/wikipedia_cache.json` — hors semainier
- `DATA_BMC/json/hors_semainier/wikipedia_people_data.json` — hors semainier

## Autres JSON (en place)

- **source : fiche du musée (métadonnées)** (377) : `DATA_BMC/Chronos/asheville_bmc_collection/0001_Black_Mountain_College_Logo_Statement/metadata.json`, `DATA_BMC/Chronos/asheville_bmc_collection/0002_Black_Mountain_College_Logo_Statement/metadata.json`, `DATA_BMC/Chronos/asheville_bmc_collection/0003_Black_Mountain_College_1933-1934_catalog/metadata.json`, `DATA_BMC/Chronos/asheville_bmc_collection/0004_A_Foreword_Reprinted_from_the_First_Cata/metadata.json`, `DATA_BMC/Chronos/asheville_bmc_collection/0005_A_Foreword_Reprinted_from_the_First_Cata/metadata.json`, `DATA_BMC/Chronos/asheville_bmc_collection/0006_A_Foreword_Reprinted_from_the_First_Cata/metadata.json` …
- **pièce de la correction du texte de Silver** (8) : `DATA_BMC/_correction_farm/appels_force.json`, `DATA_BMC/_correction_farm/bandes.json`, `DATA_BMC/_correction_farm/lacunes.json`, `DATA_BMC/_correction_farm/pagemap.json`, `DATA_BMC/_correction_farm/pagenums_raw.json`, `DATA_BMC/_correction_farm/pages.json` …
- **source du semainier (base des personnes)** (1) : `DATA_BMC/bmcyearbook/001_biographies.jsonl`
- **pièce du dépouillement de Duberman** (3) : `bmc-programmes-aam/duberman/_appui/notes_by_id.json`, `bmc-programmes-aam/duberman/_appui/paged.json`, `bmc-programmes-aam/duberman/_appui/pages_notes.json`
- **source du semainier (fiches AAM)** (2) : `bmc-programmes-aam/fiches.json`, `bmc-programmes-aam/fiches_sondees.json`
- **interne à l'audit** (26) : `bmc-programmes-aam/programme/audit/lots/r1.json`, `bmc-programmes-aam/programme/audit/lots/r10.json`, `bmc-programmes-aam/programme/audit/lots/r11.json`, `bmc-programmes-aam/programme/audit/lots/r12.json`, `bmc-programmes-aam/programme/audit/lots/r13.json`, `bmc-programmes-aam/programme/audit/lots/r14.json` …
- **pièce du dépouillement de Rumaker** (1) : `bmc-programmes-aam/rumaker/paragraphes_pages.json`
- **sortie numérotée (integrer_syntheses.py)** (15) : `bmc-programmes-aam/scenario/002_chroniques_mois.json`, `bmc-programmes-aam/scenario/002_dossiers.json`, `bmc-programmes-aam/scenario/002_references.json`, `bmc-programmes-aam/scenario/003_chroniques_mois.json`, `bmc-programmes-aam/scenario/003_cours.json`, `bmc-programmes-aam/scenario/003_dossiers.json` …
- **interne à la chaîne bmc-scenario (hors semainier)** (16) : `bmc-scenario/comparaison/claude-haiku-5-5/annees/1949.json`, `bmc-scenario/comparaison/claude-haiku-5-5/personnes/John_Andrew_Rice.json`, `bmc-scenario/comparaison/claude-sonnet-5-5/annees/1949.json`, `bmc-scenario/comparaison/claude-sonnet-5-5/personnes/John_Andrew_Rice.json`, `bmc-scenario/comparaison/glm-5.2/personnes/John_Andrew_Rice.json`, `bmc-scenario/etat/echecs.jsonl` …
- **source du semainier (scénario)** (1) : `bmc-scenario/sortie/009_bmc_scenario_1933-1957.json.gz`
- **source du semainier (synthèses du scénario)** (795) : `bmc-scenario/syntheses/annees/1933.json`, `bmc-scenario/syntheses/annees/1934.json`, `bmc-scenario/syntheses/annees/1935.json`, `bmc-scenario/syntheses/annees/1936.json`, `bmc-scenario/syntheses/annees/1937.json`, `bmc-scenario/syntheses/annees/1938.json` …
- **texte des livres (OCR paginé)** (59) : `bmc-scenario/texte/001.jsonl.gz`, `bmc-scenario/texte/002.jsonl.gz`, `bmc-scenario/texte/003.jsonl.gz`, `bmc-scenario/texte/004.jsonl.gz`, `bmc-scenario/texte/005.jsonl.gz`, `bmc-scenario/texte/006.jsonl.gz` …
