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

## Points à vérifier sur scan
Aucun : aucune entrée de 1949-57 ne repose sur une lecture de grille ou de scan (pas de grille horaire dans le
corpus pour ces années ; tous les horaires sont supposés et codés comme tels).
