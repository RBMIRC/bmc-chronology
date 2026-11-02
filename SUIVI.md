# Suivi — semainier BMC (branche `semainier-cloud`)

Reprise : lire ce fichier, puis `PROMPT_CLAUDE_CLOUD.md` (consigne complète).

## État par étape

| Étape | Objet | État | Commit |
|---|---|---|---|
| 0 | Chemins `~/Documents/...` → chemins relatifs à la racine du dépôt | fait | « chemins relatifs » |
| 1 | Intégrer Duberman au semainier | fait | « semainier : couche Duberman » |
| 2 | Couche spéculative 1949-50 → 1956-57 | fait (1955-57 sans semaines, faute de calendrier) | une année = un commit |
| 3 | Contrôles (`construire.py --verifier`, navigateur headless, avant/après) | fait | « contrôles finaux » |
| 4 | Scénario (bmc-scenario, 60 livres) reporté sur le semainier et recoupé | fait | « semainier : couche Scénario et recoupements » |
| 5 | Vérification des sources de chaque entrée, extrait dans chaque fiche | fait | « vérification des sources » |
| 6 | Synthèses du scénario : chroniques mensuelles, dossiers, références, cours | fait | « synthèses du scénario » |

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
| 1950-51 | fait | 45 (aut. 13+5, print. 18, été 4+5) | 357 (~3 820) | 50,1 % (aut. 47, print. 62, été 39-41) | « speculation 1950-51 » |
| 1951-52 | fait | 30 (aut. 15, print. 15 ; été non daté) | 112 (~1 680) | 65,1 % (cours seuls : 86 %) | « speculation 1951-52 » |
| 1952-53 | fait | 44 (aut. 19 en 5 morceaux, print. 16 en 2, été 9) | 497 (~2 600) | 64,7 % (été 40) | « speculation 1952-53 » |
| 1953-54 | fait (printemps et été 1954 seulement) | 22 (print. 11, été 11) | 29 (~320) | 66,1 % (print. 71, été 62) | « speculation 1953-54 » |
| 1954-55 | fait (Fall Quarter 1954 + fin de l'été 1954) | 12 (aut. 11, été 1) | 29 (~150) | 67,3 % (aut. 73) | « speculation 1954-55 » |
| 1955-56 | analyse seule : aucune période attestée | 0 | 0 | — | « speculation 1955-56 » |
| 1956-57 | analyse seule : fermeture, aucun trimestre | 0 | 0 | — | « speculation 1956-57 » |

### Notes 1949-50
- Sources : 2017.40.360 (corps enseignant de septembre 1949), 2017.40.048 (« courses given » 1949-50, sans semestre),
  2017.40.047 (automne 1949), 2017.40.049, 2017.40.359 (été 1950), 2017.40.282 (danse, 10 juin 1950) ; Duberman ch. 11
  pour Fiore, Larsen et les Jennerjahn (absents de la liste de septembre, présents dès la rentrée selon ¶1418).
- Non programmés : Seelye (théâtre, invitée, absente des cours donnés), Rosen (séminaire « not yet definite »),
  botanique (« at a neighboring college »). Olson : visiteur, rien de reconstitué.
- Réunions du corps enseignant : jours irréguliers chez Duberman, pas de créneau régulier reconstitué.
- Question : Flola / Flora Shepard (2017.40.360 écrit « Flora », 2017.40.049 et Duberman « Flola ») ; « Flola » retenu.

### Notes 1950-51
- Automne : liste annoncée de 2017.40.049. Printemps : reconduit (TERME_DEDUIT). Départs d'après Duberman seul :
  Levi en décembre 1950 (automne coupé au 12/12) ; Corkran, McCandless, les Hetherington, Trayer au printemps à 1 chance
  sur 2 (PRESENCE) ; suite de philosophie « par Levi » au printemps non reconstituée.
- Été 1951 : 2017.40.340 nomme Herbert Matter, Duberman Arthur Siegel (photographie) — l'annonce est gardée, l'écart noté.
- Cours d'écriture d'Olson (été 1951) : ligne S sourcée Duberman, jeudi 19-23 h choisi (JOUR).
- **Question** : date réelle du départ de Corkran et des quakers (avant ou après le 7 février 1951) ?

### Notes 1951-52
- Une seule source AAM (2017.40.361) : calendrier et **domaines** annoncés, sans enseignant ni titre. Un cours par domaine,
  titre inconnu, 1 chance sur 2 par semestre ; enseignants d'après Duberman (Sprague, Adams, Harrison, Olson) ou l'année
  voisine (Fiore, Larsen, Jalowetz, Huss, Shepard, Dehn + PRESENCE) ; inconnus pour céramique, imprimerie, tissage,
  bois, littérature.
- Nouveaux codes dans `scripts/speculer.py` : R_DUBERMAN (+10), ANNONCE (+15).
- Été 1952 : pas de période attestée dans `calendrier_periodes.csv` → non reconstitué (Duberman seul).
- **Questions** : M. C. Richards enseigne-t-elle en 1951-52 ? Dehn enseigne-t-il encore en 1951-52 ? Qui tient
  céramique, imprimerie, tissage et l'atelier du bois ?

### Notes 1952-53
- Catalogue 2017.40.050 (annonce) contre Duberman (« grotesquely padded ») : pas de conflit de dates ; titres gardés en
  ANNONCE avec chances réduites ; 18 titres non programmés (biologie et sciences de Goldowski, titres « fanciful » de Huss).
- Instituts en bandeaux sur leurs dates (Crafts, céramique, Theatre, New Sciences of Man, Natural Sciences).
- Été 1953 d'après Duberman (Cunningham : cours le matin, répétitions après-midi et soir ; Vicente) et 2017.40.051.
- **Questions** : dates réelles du séminaire « New Sciences of Man » (trois semaines) ; date du départ de Sprague ;
  date de la mort de Max Dehn (Duberman ne la donne pas).

### Notes 1953-54
- Automne 1953 et hiver 1954 : aucune date de trimestre attestée → non reconstitués.
- Plus de repas en commun (campus bas fermé à l'automne 1953, Duberman ¶1654) : aucun repas dans la grille.
- Printemps 1954 : Olson et Creeley (cours du soir, Duberman), revue mensuelle (2017.40.051), résidents reconduits
  depuis l'été (proches du plafond). Été 1954 d'après 2017.40.324 (Hellman : annonce 1954 contre Duberman 1955).
- **Questions** : l'annonce du Spring Quarter 1954 (« recent announcement », citée par 2017.40.051) existe-t-elle dans
  un autre fonds ? Dates des trimestres d'automne 1953 et d'hiver 1954 ?

### Notes 1954-57
- 1954-55 : Fall Quarter 1954 seulement (cours suspendus de Noël à mars 1955, hiver et printemps sans dates).
- 1955-56 et 1956-57 : aucun jour de cours dans `calendrier_periodes.csv` → `speculer.py` (modifié : année sans
  période = analyse seule, sans gabarit) ne produit que `annee_AAAA-AA.md`. Non-régression vérifiée : gabarits et
  semaines de 1933-1951 identiques après relance complète.
- **Question** : faut-il un calendrier spéculatif pour 1954-55 (hiver-printemps 1955) et 1955-56 (sessions d'hiver et
  de printemps 1956), transposé des trimestres de 1954 comme pour 1934-35 (30-45 % sur les dates) ?

## Étape 3 — contrôles (2/11/2026)
- `python3 scripts/construire.py --verifier` : « 5073 événements, 821 cours, 198 périodes », identique avant (état du
  début de session, 3c7a9b4~1) et après. Les CSV de `programme/` (evenements, cours_par_periode, calendrier_periodes)
  n'ont pas changé.
- `data.js` avant : 4 650 activités attestées, 16 années spéculatives, 324 documents.
  Après : 4 650 activités attestées (inchangé) + 484 événements Duberman dans la grille et 434 au panneau, 22 années
  spéculatives (1933-34 → 1954-55), 1 355 documents.
- Chromium headless : une semaine par année de 1933 à 1956 (Semaine et Présences), vues Liste et Mois, filtres de
  famille, de part déduite, recherche, cases « Couche spéculative » et « Duberman », fiche d'une entrée spéculative,
  analyse d'année : 0 erreur console.

## Étape 4 — scénario (2/11/2026)
- Source : `bmc-scenario/sortie/009_bmc_scenario_1933-1957.json.gz` (extraction **automatique** de 60 livres, non relue).
- `bmc-programmes-aam/scripts/integrer_scenario.py` → `bmc-programmes-aam/scenario/001_*` (événements, recoupements,
  divergences, cours, rapport). Barème propre : +10 d'office (extraction non relue), certitude, précision de la date.
- 7277 événements et scènes datés 1933-09 → 1957 ; 4252 reportés dans le semainier (283 dans la grille, 3 969 au
  panneau), part déduite moyenne 37.8 % ; 2 942 écartés (plus de 13 mois) ;
  83 fondus dans une fiche existante (1 AAM, 82 Duberman), 43 renvois « même jour, même personne ».
- Couche « Scénario » (prune, « S. ») dans `semainier/data_scenario.js` (fichier séparé : data.js reste inchangé).
- Recoupements notables : le scénario écrit « Robert » Lounsbury (Ralph dans l'AAM et Duberman) ; 2 divergences de date
  avec Duberman (`scenario/001_divergences_scenario.csv`) ; 708 fiches « cours » : 113 concordent avec l'AAM
  (titre + enseignant), 372 enseignants présents cette année-là mais titre absent de l'AAM, 71 absents de l'AAM.
- **Questions** : faut-il relire et valider à la main les 82 fusions avec Duberman ? Reporter le contenu des cours du
  scénario (objectifs, exercices) dans le panneau « Cours offerts » ?

## Étape 5 — vérification des sources (2/11/2026)
- `scripts/verifier_sources.py` → `programme/audit/001_verification_sources.csv/.md`, `semainier/verification.js`.
- Résultat (18 270 entrées) : aucune sans source, aucune référence introuvable.

| couche | entrées | retrouvé | indice faible | à relire | faux positifs (contrôle négatif) |
|---|---|---|---|---|---|
| AAM | 4 650 | 78 % | 21 % | 0,4 % | 11 % |
| Duberman | 935 | 91 % | 7 % | 2 % | 5 % |
| Scénario | 4 335 | 79 % | 17 % | 5 % | 7 % |
| Spéculatif | 8 350 | 70 % | 20 % | 10 % | 36 % (catalogues : mêmes enseignants d'une année à l'autre) |

- Périodes (203), cours (821), documents (1 355) : tous ont une source et un lien.
- Reste à relire à la main : les « à relire » et « indice faible » (listes dans le CSV, extrait dans chaque fiche).

## Étape 6 — synthèses du scénario (2/11/2026)
- 6a fait : `scripts/integrer_syntheses.py` → `scenario/002_*`, `semainier/data_syntheses.js`. 292 chroniques mensuelles,
  334 dossiers (champs factuels), 10 241 fiches référencées (2 introuvables). Présents probables : 3 322 mentions,
  709 (21 %) nommées le même mois dans l'AAM ou Duberman ; 1 marquée « invente_pour_le_recit_interdit », écartée.
- 6b fait : `verifier_sources.py` vérifie aussi les 7 213 fiches citées par les synthèses (couche « Scénario (fiches
  citées) », clé « f » + id) → `programme/audit/002_verification_sources.*` : 87 % retrouvées (4 % au hasard),
  citations : texte original cherché dans la page (1 158 citations, 95 % retrouvées) ; 2 fiches sans numéro de page.
  Lecture des pages améliorée (« pp. », « 90, 93 », « (note 11) », chapitres « ch17 » des livres numériques).
- 6c fait : 708 fiches « cours » à BMC (objectifs, exercices, matériaux, déroulé, propos, réactions) dans le
  panneau « Cours de AAAA-AA selon les livres », avec la concordance AAM (`scenario/001_cours_scenario.csv`) et la
  référence vérifiable ; sorties `scenario/003_*` (002 conservé), vérification `programme/audit/003_*`.

## Étape 7 — lieux, conflits, vie quotidienne, œuvres, idées (2/11/2026)
- `integrer_syntheses.py` (sorties `scenario/004_*`) : 18 lieux du collège (407 fiches), 509 conflits (≤ 3 ans),
  1 256 fiches de vie quotidienne (≤ 2 ans, 22 thèmes), 1 108 œuvres liées à BMC (≤ 2 ans), 784 idées enseignées à BMC
  rattachées aux dossiers. Écartés : échos (flash-back du scénario), relations (déjà dans les dossiers), œuvres sans lien
  avec BMC, fiches couvrant plus de 2 ou 3 ans.
- Semainier : « ⓘ » sur le lieu d'une activité → dossier du lieu, avec le nombre d'activités AAM situées là ; panneau :
  conflits de l'année, vie quotidienne par thème, œuvres ; dossiers : idées enseignées.
- Vérification `programme/audit/004_*` : 11 565 fiches citées, 81 % retrouvées (6 % au hasard), 3 sans page.
- Correctif : une fiche fermée pendant le chargement de la vérification ne se rouvre plus.

## Étape 8 — dossier Chronos (DATA_BMC/Chronos, versé le 2/11/2026), JSON un par un
Inventaire : extractions automatiques de décembre 2025 (GPT-4o pour la ferme). Sources de base, traitées une à une :
1. `asheville_events.json` (377 fiches du musée) — **fait**
2. `harris_events.json` (165 entretiens de Mary Emma Harris) — **fait**
3. `farm_events.json` (Silver, The Farm at BMC) — **fait**
4. `bmc_chronology.json` (Duberman, « Chronos 2 ») — **fait**
5. `BlackMountainPeople.txt` (1 299 personnes, rôles, années) — **fait**
Dérivés (inventoriés seulement, pour ne pas compter deux fois) : `bmc_chronology_{enriched,final,complete,ultimate,
wikipedia,with_presence,temp}.json`, `bmc_people_index.json`, `bmc_relations*.json`, `bmc_series_bible.json`,
`*_temp.json`, `people_enrichments.json`, `wikipedia_*.json`. Les scripts d'origine ne sont pas versés (clé d'API).

### 8.1 asheville_events.json
- `scripts/chronos_asheville.py` (+ `scripts/chronos_commun.py`) → `bmc-programmes-aam/chronos/001_asheville_*`.
- 1906 événements : confirmé 1120, absent de l'AAM 331, confirmé par un autre document AAM 172, confirmé (calendrier) 107, document hors corpus 105, date différente 51, date illisible 18, confirmé par Duberman 2.
- Couche « Chronos » du semainier (`semainier/data_chronos.js`, case « Chronos », olive, « C. ») : 215 entrées
  (absents de l'audit datés au jour, documents hors corpus), à relire ; rien n'est ajouté au programme attesté.
- Exemples : visite de Frank Porter Graham datée par Chronos du jour du bulletin (« Wednesday of last week » : l'AAM a
  le 30 mai 1945) ; départ de Kenneth Kurtz pour Yale (2017.40.173a-c) absent de notre extraction : oubli probable.

### 8.2 harris_events.json
- `scripts/chronos_harris.py` → `chronos/002_harris_*` (recoupement, cours, incertains, couche, rapport).
- 715 faits : citation retrouvée telle quelle dans la transcription 684, en partie 26, introuvable 3, vide 2.
- Recoupement : confirmés le même jour ou mois 4 (AAM 3, Duberman 1) ; présence de la personne attestée dans la
  période 215 ; non confirmés 417 ; dates illisibles 79 (« uncertain »). Dates surtout à l'année ou à la saison
  (22 au jour).
- Couche Chronos : 565 souvenirs (témoignage oral recueilli 20 à 60 ans après, +10) ; l'extrait de la fiche montre la
  citation dans la transcription (548/563 contrôlés).
- 300 cours cités : 187 titre et enseignant dans l'AAM, 16 enseignant cette année-là, 97 absents de l'AAM.
- 271 faits jugés incertains par l'extraction : `chronos/002_harris_incertains.csv` (hors couche).

### 8.3 farm_events.json
- `scripts/chronos_ferme.py` → `chronos/003_ferme_*`. 193 événements + 101 documents datés (lettres, rapports cités par
  Silver). Vérification dans l'OCR des deux pages du scan citées (`DATA_BMC/_correction_farm/pages.json`), pages du livre
  d'après `pagemap.json` : retrouvé 209, indice faible 79, à relire 6.
- Dates : écrites AAAA-MM-01 même au mois ou à l'année ; la précision déclarée est respectée (pas de faux jour).
- Recoupement (règle stricte : même date, personne commune ET mot commun) : 3 confirmés, 78 présences attestées,
  199 non confirmés, 14 dates illisibles. Couche Chronos : 248 entrées (1933-1957).
- Même règle stricte appliquée à Harris → `chronos/004_harris_*` (002 conservé) : 1 confirmation au lieu de 4
  (les 3 autres étaient de simples coïncidences de nom le même mois).

### 8.4 bmc_chronology.json (Duberman, « Chronos 2 »)
- `scripts/chronos_duberman.py` → `chronos/005_duberman_*`. Chaque citation (476 sur 559) est cherchée dans les
  paragraphes du texte corrigé : 471 retrouvées, ce qui donne ¶ et page de notre édition.
- Contre notre dépouillement (935) : retrouvés 385 (dont 24 par date et nom, 26 sans date lisible chez Chronos),
  absents 96 (73 vont dans la couche Chronos), dates différentes 14, sans citation 59, citation introuvable 5.
- Vérifié à la main : Wilder (1934, pas 1936) et Kazin (1944, pas 1945) — notre dépouillement est juste ; les autres
  « dates différentes » sont deux faits distincts du même paragraphe.

### 8.5 BlackMountainPeople.txt (base des personnes ; provenance : BMC Yearbook, voir 8.7)
- `scripts/chronos_personnes.py` → `chronos/007_personnes_presences.csv`, `_cours_suivis.csv`, `_rapport.md`,
  `semainier/data_personnes.js`.
- Présences (nom ET prénom contre l'AAM et Duberman) : concordant 285, débordement 74 (activités attestées hors des
  années de la base), non attesté 938 (surtout des étudiants), années incohérentes 2.
- Cours suivis : 355 fiches → 5 862 inscriptions par trimestre ; titre et enseignant dans l'AAM 3 517, enseignant dans
  l'AAM cette année-là 598, absent de l'AAM 709, enseignant non nommé 1 038.
- Semainier : panneau « Cours suivis (trimestre) selon les fiches d'étudiants » ; « ⓘ » ouvre aussi la fiche de la base
  (biographie, rôle, années, relations, cours suivis, recoupement).
- Provenance donnée le 2/11/2026 : https://bmcyearbook.org/biographies (voir 8.7).
- Piste : les cours suivis par semestre (1949-53 surtout) permettraient de corriger les « 2 chances sur 3 » de la couche
  spéculative. → fait, 8.6.

### 8.6 Cours suivis → couche spéculative 1949-50 → 1954-55 (2/11/2026)
- `chronos_personnes.py` corrigé (en-têtes « 1950 Spring Term (1949-50): », initiales « M.C. », « and »/« & » en tête,
  « —dropped », puce « o » collée) → `chronos/008_personnes_*` (3 775 inscriptions titre et enseignant dans l'AAM).
- `scripts/suivis_speculation.py` → `speculation/suivis/AAAA-AA.csv` : chaque cours suivi d'un trimestre rattaché à une
  unité du catalogue spéculatif (enseignant commun ; titre, ou équivalent d'une année voisine ; les mots de discipline
  seuls — « Anthropology », « Music » — ne confirment que le trimestre).
- `speculer.py`, directive `#suivis` (code SUIVI, 0) ajoutée aux six années ; aucun chevauchement (contrôle refait).
- Effet (unités du catalogue confirmées / abaissées, unités ajoutées, part déduite moyenne des cours avant → après) :
  - 1949-50 automne 27 / 4, +5, 70 → 56 % ; printemps 28 / 4, +8, 73 → 56 % ; été 6 / 0, +11 ; les « 2 chances
    sur 3 » passent de 17 à 3 (automne) et de 21 à 3 (printemps) ;
  - 1950-51 automne 20 / 3, +6 ; printemps 17 / 4, +9, 72 → 66 % ; été 1951 +23 (Motherwell, Vicente, Harrison,
    Tudor, Litz…, à 1/2 car l'été est coupé en deux périodes) ;
  - 1951-52 automne 8 / 1, +11, 87 → 63 % ; printemps 6 / 4, +10, 87 → 63 % ; été 1952 : 12 cours suivis mais pas de
    date attestée, rien n'est placé ;
  - 1952-53 automne 10 / 1, +6, 83 → 63 % ; printemps 8 / 2, +4, 83 → 66 % ; été 1953 +12 ;
  - 1953-54 et 1954-55 : quelques unités (Olson, Creeley, Fiore, Huss, Wolpe, Shepard) ; automne 1953 et printemps 1955
    sans date attestée : rien n'est placé.
- Corrections d'attribution du catalogue 1949-50 : « Plato » suivi avec Levi au printemps 1950 (2 étudiants ; MD4,
  Platon rattaché à Dehn par élimination, passe à 1/2) ; « Ethics » (printemps, 3 étudiants) et « Theory of Knowledge »
  (automne, 4 étudiants) suivis avec Dehn (BL1, Levi, abaissé au printemps).
- Questions : « Bookbinding with Dehn » (John Hamilton, printemps 1952) est-il une erreur de la fiche pour Jalowetz ?
  « Truman » (Algebra, printemps 1950) = l'étudiant Trueman MacHenry ? « William » (Social Science) = A. W. Levi ?
  Qui sont Kennedy (Intro to Mathematics, automne 1949), Oscar (Drawing II, été 1952), Pete (Light Sound Movement,
  printemps 1951) ? Ces noms sont repris tels quels.

### 8.7 BMC Yearbook (bmcyearbook.org/biographies), source de BlackMountainPeople.txt (2/11/2026)
- Projet du Black Mountain College Museum + Arts Center (Amanda Hartman, Heron Studio), notices compilées des archives
  (Western Regional Archives), beaucoup de Mary Emma Harris (Black Mountain College Project). Site « All rights
  reserved » : copie de travail, dépôt à garder privé.
- `scripts/yearbook_telecharger.py` → `DATA_BMC/bmcyearbook/001_biographies.jsonl` : 1 359 notices sur 1 361 (Robert
  Kumabe et Marie Mulholland en erreur 500 sur le site, deux essais ; une entrée de liste sans page).
- `scripts/chronos_personnes.py` lit désormais le site (le .txt en contrôle et en secours) → `chronos/009_personnes_*` :
  - 1 360 personnes ; contre le .txt : 59 seulement sur le site, 1 seulement dans le .txt (Ursula Lewis, reprise),
    40 listes de cours différentes (le site en a plus), 16 années différentes (le .txt met « 1933-1938 » à plusieurs
    John : John Cage, John Bailey, John Taylor… ; le site est plus juste) ; noms d'épouse rapprochés (Vera Baker
    Williams, Lorna Blaine Halper) ;
  - arrivée et départ au jour : pour moitié le premier ou le dernier jour d'une période de cours attestée, 70 % à une
    semaine près (ce sont des dates de trimestre, pas de voyage) ; contre l'AAM et Duberman : 192 personnes dans les
    dates, 118 citées après leur départ (nouvelles d'anciens dans les bulletins), 61 citées avant leur arrivée ;
  - 453 renvois des notices à des fiches de l'AAM (221 personnes) : nom retrouvé dans notre OCR 364, fiche connue mais
    nom non retrouvé 18, fiche absente de notre corpus 71 (surtout 2017.40.214, .218, .181, .217 : bulletins à
    ajouter au corpus) ;
  - 5 850 inscriptions à des cours (notes entre crochets gardées : « audit », « Evans taught a 6-week elementary
    math course »…).
- Couche spéculative : tables `speculation/suivis/AAAA-AA_2.csv` refaites depuis le site, directives `#suivis`
  pointées dessus, six années relancées, aucun chevauchement ; source des entrées : « BMC Yearbook ».
- Semainier : fiche de personne avec lien vers la notice, dates au jour, naissance et décès, documents de l'AAM cités ;
  panneau « Arrivées et départs cette semaine selon le BMC Yearbook ».

## Étape 9 — Rumaker, Black Mountain Days (DATA_BMC/Rumaker, texte corrigé v6)
- Alignement ¶ → pages du livre sur l'OCR paginé du scénario (`rumaker/paragraphes_pages.json`) : 829 ¶ sur 851.
- Dépouillement manuel des 151 phrases portant une date absolue : `rumaker/extraction/rumaker.txt` (62 faits, format de
  Duberman) → `rumaker/construire_rumaker.py` → `rumaker/001_evenements_rumaker.csv`, `001_rapport_rumaker.md`,
  `chronos/006_rumaker_couche.csv` (couche « Chronos, Rumaker » du semainier).
- Vérifiés dans leur ¶ : 47 retrouvés, 11 indice faible, 4 à relire ; recoupés par Duberman 30 ; présents aussi dans le
  scénario (mêmes pages, même personne) 56 — les deux restent affichés, la fiche Rumaker renvoie aux entrées du scénario.
- Désaccords notés : conférence de Shahn (hiver 1951 chez Rumaker, 1952 chez Duberman) ; diplôme de Rumaker (début
  septembre 1955 d'après Rumaker lui-même, août 1955 chez Duberman) ; retour de février 1954 « for the spring term »
  (Spring Quarter annoncé le 29 mars 1954 par 2017.40.051) ; Hellman (1954 ou 1955).
- Apport propre : horaires des cours de l'automne 1952 (Huss le soir, Morley l'après-midi, Goldowski le matin), lettres
  de 1955 au jour, Thanksgiving 1954 (25 novembre, confirmé par Silver).
- Reste possible : version 7 du texte (8 lignes parasites), dépouillement de la chronologie relative.

## Étape 10 — Livres et articles (textes des PDF, DATA_BMC/textes_pdf, 2/11/2026)
- 32 textes convertis sur l'ordinateur de Sylvain (`scripts/pdf_vers_texte.py`), versés dans `DATA_BMC/textes_pdf`.
  3 doublons écartés (deux copies de Díaz, de *Revisiting Black Mountain*, de *The Three Ecologies*).
- `scripts/livres_commun.py` : pages, colonnes recollées (pdftotext -layout entrelace les colonnes : Harris 1987 a
  136 pages à deux, trois ou quatre colonnes, notes comprises), paragraphes, phrases ; page imprimée retrouvée par le
  décalage avec la page du PDF (Harris : p. imprimée = p. PDF − 28).
- `scripts/livres_extraire.py` → `livres/001_inventaire.csv`, `001_evenements_livres.csv`, `001_rapport_livres.md`,
  `chronos/010_livres_couche.csv` : 1 357 faits datés de 1933 à 1957 (jour 502, mois 366, saison 486, plage 3),
  947 faits racontés et 410 documents cités en note (lettres, procès-verbaux, articles : la date est celle du
  document) ; personnes reconnues d'après la base du BMC Yearbook (804 faits) ; part déduite moyenne 37 %.
  - Par texte : Harris 780 (275 au jour), Canter 163, Díaz 92, Gilsanz Díaz 148 (traduction automatique, +20),
    Lane 46, Peifer 22, Benfey 19, autres moins de 15. Les articles généraux (Muir, Lindsay, Migašová…) n'ont pas de
    date au jour ; la Black Mountain College Review de 1951 n'en a aucune.
- **Révision du même jour (demande : « ne mets pas de dates à moitié vérifiées, les json sont de meilleure qualité »)** :
  `chronos/010_livres_couche.csv` (1 357 entrées, dont 505 dans la grille) est remplacée par `chronos/011_livres_couche.csv`,
  vide : aucun fait de ces textes n'entre seul dans le semainier.
  - Seuls les faits vérifiés au jour par une source qui fait foi (AAM, Duberman au jour, Rumaker au jour, fiche du
    musée au jour ; même jour exact, même personne avec le même prénom, mot commun ; pour une lettre citée, toutes ses
    personnes) deviennent des **renvois** « Aussi dans les livres » sur la fiche existante : 34 trouvés, tous relus
    à la main (`livres/revue_renvois.txt`) : 32 justes, 2 faux écartés (lettre d'Olson à Aydelotte du 26 mai 1955 ≠
    collecte de Mary Fiore ; bulletin du 20 novembre 1944 ≠ cours « Calculus »). Avant durcissement, 7 faux sur 40
    (plage de dates de Duberman, nom de famille seul : Anne / Frederick Mangold).
  - Témoin négatif (faits au jour décalés de 400 jours) : 0 vérification fausse sur 505.
  - Hors semainier : 180 faits qui ne s'accordent qu'au mois, la thèse en traduction automatique, et le reste :
    `livres/002_a_verifier.md` liste les 252 faits au jour qui nomment une personne, avec les indices (AAM ou Duberman
    au mois, scénario, autres livres) pour une relecture.
- Limites : l'activité affichée est la proposition du texte qui porte la date (en anglais) ; noms de famille partagés
  (Albers, Dreier, Beidler…) non attribués.

## Étape 11 — Rangement des JSON (2/11/2026)
- `bmc-programmes-aam/scripts/json_ranger.py` → `DATA_BMC/json/` (voir `DATA_BMC/json/LISEZMOI.md`, `CATALOGUE.md`,
  `catalogue.csv` : 1 334 JSON inventoriés, chacun avec son statut).
- `DATA_BMC/json/semainier/` : un JSON compilé par source Chronos (Duberman 559 événements, Harris 165 entretiens /
  715 faits, ferme 193 événements + 135 documents, Asheville 377 fiches) ; `_meta` (provenance avec sha1, champs,
  variantes vérifiées, contrôles) et `id` par enregistrement.
  - Les 7 variantes de la chronologie et les 3 « _temp » comparées une à une : aucun enregistrement manquant ; repris
    seulement les enrichissements (personnes présentes 498, Wikipedia 438). Les 1 158 entrées « en plus » d'Asheville
    dans `_ultimate` sont ses rubriques calendrier, décisions et visiteurs remises à plat ; les 110 de la ferme, ses
    documents.
  - Originaux identiques dans les fichiers compilés (seules des clés ajoutées) ; doublons marqués : 1 (ferme).
  - `chronos_asheville/harris/ferme/duberman.py` lisent les fichiers compilés : relancés, ils redonnent exactement les
    mêmes couches (215, 568, 248, 73 lignes).
- Rangés par `git mv` (rien supprimé) : originaux et variantes → `DATA_BMC/Chronos/_versions/` ; personnes, relations,
  Wikipedia, bible de série, météo → `DATA_BMC/json/hors_semainier/` (relations et enrichissements compilés, anciennes
  versions dans `_versions/`).
- Reste à exploiter : rubriques secondaires d'Asheville (calendrier 229 périodes, cours 1 440, enseignants 1 443,
  étudiants 2 147, visiteurs 838, décisions 133), à confronter au calendrier attesté et aux catalogues AAM.

## Étape 12 — Modèle du semainier pour la mise en ligne (2/11/2026)
- Constat (mesures sur les 1 062 semaines) : une semaine type porte ~3 faits AAM, 1 Duberman, 1 Chronos et ~120 cases
  spéculatives (jusqu'à 334, semaine du 27 mars 1944) ; dans la grille horaire, 8 à 10 cours à la même heure font des
  cases de 10 px, et la vue est inutilisable sur téléphone.
- Enquête de design : incertitude marquée par des signes discrets plutôt que par du flou (points de Priestley, *Chart of
  Biography*, 1765 ; Kräutli et Boyd Davis : un rendu flou suggère plus de confiance que les données n'en donnent) ;
  versions divergentes en colonnes parallèles (Lenglet Du Fresnoy) ; vue agenda plus lisible sur téléphone que la grille
  quand les événements se chevauchent.
- Nouvelle vue par défaut **« Journal »** (`semainier/index.html#AAAA-MM-JJ/journal`) : frise 1933-1957 (faits attestés
  par semaine, semaines reconstituées), puis 1. Attesté et rapporté, jour par jour (couche écrite, certitude ●●● à
  ○○○, part déduite, source courte ; récurrences de l'AAM regroupées en une ligne) ; 2. Emploi du temps reconstitué,
  replié, en tableau créneaux × jours (liste par jour sur téléphone) ; 3. contexte (colonne de droite inchangée).
  La grille horaire reste sous « Grille ». Filtres repliables ; aucune donnée modifiée.
- **Publication** (2/11/2026) : `bmc-programmes-aam/scripts/publier_semainier.py /home/user/week` → dépôt RBMIRC/week,
  branche `main` (site https://rbmirc.github.io/week, GitHub Pages à activer sur `main`, dossier racine).
  - Version publique : toutes les entrées, références exactes et parts déduites ; retirés : extraits de vérification
    (29 835, statut gardé), notes de Duberman recopiées (670), extraits Chronos et Rumaker (1 166), phrases des livres
    (32 renvois), biographies du BMC Yearbook (1 359, lien vers la notice gardé). Scénario et synthèses gardés (résumés
    rédigés avec références).
  - Couche spéculative découpée par année (`spec/AAAA-AA.js`, chargée à la demande) ; chargement initial ≈ 2 Mo
    compressés (42 Mo en tout au lieu de 61). L'adresse `#AAAA-MM-JJ/journal` se partage.
  - Version complète inchangée pour l'usage local (`bmc-programmes-aam/semainier/`, mêmes fichiers, même page :
    `window.BMC_PUBLIC` n'y est pas défini). Republier : relancer le script puis commiter et pousser dans RBMIRC/week.
- Corrections après relecture de Sylvain (2/11/2026) :
  - la couche spéculative semblait perdue : la page s'ouvrait sur le 23 octobre 1944 (semaine entièrement attestée,
    sans reconstitution) et l'emploi du temps reconstitué était replié. Le bloc 2 devient « Emploi du temps de la
    semaine », ouvert, qui réunit les cours attestés (● en romain, grille horaire) et les cours reconstitués (en
    italique, part déduite) ; ouverture sur le 27 mars 1944 ;
  - semaine « très parcellaire » (31 août 1936) : le Journal montre désormais aussi les faits datés au mois ou à la
    saison dont la période couvre la semaine (Duberman, Chronos, scénario ; ceux datés à l'année, repliés) ; les jours
    vides consécutifs sont regroupés.
  - « Le semainier n'est pas facile à lire : il faudrait les 7 jours, et selon l'option choisie on voit ou non ce
    qu'il y a chaque jour » (3/11/2026) : la vue « Semaine » (par défaut) montre les 7 jours en colonnes (4 puis 1 sur
    écran étroit). Options au-dessus, avec le nombre d'entrées de la semaine, mémorisées dans le navigateur : faits
    attestés (AAM), cours attestés, Duberman, Chronos et Rumaker, scénario, cours reconstitués, vie commune
    reconstituée, faits au mois ou à la saison (bande au-dessus des colonnes) ; raccourcis « tout », « rien »,
    « attesté seul ». Cours d'un même créneau réunis en une case ; récurrences de l'AAM en une ligne ; contexte (colonne
    de droite) ouvert à la demande ; fiches en fenêtre au clic, inchangées.

## Points à vérifier sur scan
Aucun : aucune entrée de 1949-57 ne repose sur une lecture de grille ou de scan (pas de grille horaire dans le
corpus pour ces années ; tous les horaires sont supposés et codés comme tels).
