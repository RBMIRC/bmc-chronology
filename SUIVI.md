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
| 1950-51 | fait | 45 (aut. 13+5, print. 18, été 4+5) | 357 (~3 820) | 50,1 % (aut. 47, print. 62, été 39-41) | « speculation 1950-51 » |
| 1951-52 | fait | 30 (aut. 15, print. 15 ; été non daté) | 112 (~1 680) | 65,1 % (cours seuls : 86 %) | « speculation 1951-52 » |
| 1952-53 | fait | 44 (aut. 19 en 5 morceaux, print. 16 en 2, été 9) | 497 (~2 600) | 64,7 % (été 40) | « speculation 1952-53 » |
| 1953-54 | fait (printemps et été 1954 seulement) | 22 (print. 11, été 11) | 29 (~320) | 66,1 % (print. 71, été 62) | « speculation 1953-54 » |

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

## Points à vérifier sur scan
(aucun pour l'instant)
