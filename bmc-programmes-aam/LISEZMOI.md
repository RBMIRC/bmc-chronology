# BMC — programme jour par jour (Asheville Art Museum)

Source : collection.ashevilleart.org (fonds Theodore Dreier Sr. 2017.40.*, etc.), texte OCR des fiches.

## Livrables
- `liste_pages.txt` / `liste_pages.csv` : toutes les fiches retenues (catégories A catalogues/annonces, B bulletins hebdomadaires, C newsletters, D concerts/théâtre) avec URL.
- `pages_txt/<catégorie>/<n° inventaire>_<titre>.txt` : texte OCR de chaque fiche, en-tête titre/date/URL/images.
- `programme/evenements.csv` : programme jour par jour (date, jour, heure, fin, type, activité, qui, lieu, note, récurrent déduit, source, URL).
- `programme/programme_jour_par_jour.md` : même chose, lisible, par année et mois.
- `programme/cours_par_periode.csv` : cours offerts par trimestre/semestre/session, enseignants, volume horaire.
- `programme/calendrier_periodes.csv` : dates des trimestres, semestres, vacances, sessions d'été, instituts.
- `programme/ics/` : le programme en iCalendar (.ics) pour Apple Calendrier, Thunderbird, Nextcloud… :
  `bmc_tout.ics` (tout), `bmc_cours.ics`, `bmc_reunions.ics`, `bmc_concerts_theatre_danse.ics`, `bmc_conferences.ics`,
  `bmc_vie_communaute.ics`, `bmc_calendrier_examens.ics`, `bmc_periodes.ics` (trimestres, vacances, sessions en bandeaux).
  Heures locales « flottantes » ; activités sans heure précise = journée entière, avec « [soir] », « [matin] » dans le titre ;
  le titre porte « (25 % déduit) » quand l'entrée n'est pas attestée telle quelle ; la description donne qui, lieu, note,
  motifs de déduction, document source et lien. Regénérés par `scripts/export_ics.py` (et par `sauvegarde.sh`).
- `semainier/index.html` : **semainier** (agenda de la semaine) à ouvrir dans un navigateur, hors ligne (double-clic suffit).
  Bâti sur Event Calendar de vkurko (licence MIT, v5.18.1, copie locale dans `semainier/lib/` avec sa licence).
  Vues : Semaine (grille horaire), Présences (une ligne par personne ou groupe, un jour par colonne ; seules les
  personnes présentes ces jours-là apparaissent), Liste, Mois. Filtres : familles d'activités, part de déduction
  maximale, recherche (personne, cours, lieu). Boutons « ◀ doc. / doc. ▶ » : semaine documentée précédente/suivante ;
  menu « Repères » : semaines les plus documentées, débuts de trimestre. Panneau latéral : période en cours (trimestre,
  vacances) avec sa source, personnes présentes (clic = filtre), documents datés de ces jours (vignette et lien vers
  la fiche du musée ; images chargées depuis le site du musée, pas recopiées), autres sources des activités affichées,
  cours offerts dans l'année scolaire. Clic sur une activité : fiche avec qui, lieu, note, part déduite et motifs,
  récurrence, document source (lien), inventaire, vue du document.
  Lecture : couleur = famille ; atténué = 10–25 % déduit ; hachuré = 30 % et plus ; pointillé = heure indicative.
  Une activité notée « soir », « matin », « après-midi » est placée 20–22 h, 9–12 h, 14–17 h à titre indicatif ;
  sans heure de fin, une heure est affichée par défaut ; sans heure du tout, en journée entière. La fiche le dit
  (ligne « Affichage ») : ce placement n'ajoute rien à la part de déduction, qui ne porte que sur le contenu.
  Quelques graphies d'un même nom sont réunies pour la vue Présences (table `ALIAS` dans le script, ex. Bob/Robert
  Wunsch) ; le champ « qui » d'origine reste dans la fiche.
  Adresse partageable : `index.html#1944-10-23/presences`.
  Données : `semainier/data.js`, regénéré par `scripts/export_semainier.py` (et par `sauvegarde.sh`).
  Ajouter des documents datés (photos, lettres d'autres fonds) : une ligne dans `semainier/documents_extra.csv`
  (date, titre, url, image, type, datation, source, part_deduite_pct, inventaire), puis relancer le script.
- **Couche spéculative** (semaines reconstituées là où aucun document ne donne le programme) :
  `speculation/AAAA-MM-JJ.txt` (format `speculation/_FORMAT.txt`) → `scripts/speculer.py` →
  `programme/speculatif/semaine_AAAA-MM-JJ.csv` et `.md` (analyse, barème, programme jour par jour).
  Chaque entrée a des codes qui font sa part déduite (barème dans le script et dans le .md) : même année +0,
  rythme régulier +10, année voisine +10, période éloignée/autre campus +25, cours absent de la liste +15,
  enseignant déduit +15, volume supposé +10, cours d'un semestre +20, titre choisi +15, activité occasionnelle +25,
  jour choisi +20, heure dans un créneau attesté +10, heure sans source +20 (plafond 90 %).
  Les cours (lignes K) sont répartis automatiquement d'après la seule grille complète du corpus (automne 1944) :
  deux séances de 90 min, 8 h 30 / 10 h 30 / 16 h, samedi matin, labos l'après-midi, sans double emploi d'un enseignant.
  Dans le semainier : cadre pointillé et fond clair, « spéc. N % », case « Couche spéculative » pour la masquer,
  encadré « Semaine reconstituée » avec lien vers l'analyse, menu Repères → « Semaines reconstituées ».
  **Concordance des cours** (`speculation/catalogue_1935-36.txt`, directive `#catalogue` du fichier de semaine) :
  les 90 « Courses of Instruction » du catalogue 1935-36, titres relus sur les scans (`scans/011-08.jpg`, `011-09.jpg` ;
  le texte transcrit du musée omet Mangold et déforme plusieurs titres), chacun avec son équivalent 1934-35 (fiche 6577,
  scans 009-08/09), son équivalent 1936-38 (semestres, heures, enseignant), son enseignant et le mode de rattachement.
  Lignes U = unités d'enseignement (une case de la semaine, cours retenu + autres cours possibles + chance) ; lignes N =
  cours non programmés avec la raison. Le script refuse de tourner si un cours du catalogue n'est rattaché nulle part.
  Sortie : `programme/speculatif/catalogue_1935-36_concordance.csv/.md` (statut de chaque cours : programmé / candidat /
  non programmé) — base pour un futur syllabus. Chaque case de cours a deux parts : case (rattachement, structure,
  jour, heure) et titre (100 × (1 − chance)) ; total = 1 − (1 − case)(1 − titre), plafonné à 90 %.
  Fait : semaine du 2 au 8 mars 1936 (139 entrées dont 102 séances de cours, déduction moyenne 59 %), à partir des catalogues 2017.40.009
  (fiche 6577), 2017.40.011, 2017.40.012 et des bulletins 1943-44 pour les heures de repas.

- **Couche spéculative par année scolaire** (depuis le 31/10, remplace le format « une semaine ») :
  `speculation/annees/AAAA-AA.txt` (analyse, rythme de la journée, réunions) + `speculation/catalogues/AAAA-AA.txt`
  (concordance des cours, relue sur scan) → `scripts/speculer.py [AAAA]` → `programme/speculatif/annee_AAAA-AA.md`,
  `_gabarits.csv` (un gabarit de semaine par trimestre, ou par morceau de trimestre), `_semaines.csv` (semaines couvertes),
  `catalogue_AAAA-AA_concordance.csv/.md`. Le semainier développe les gabarits à la volée (pas d'événements stockés).
  Une semaine déjà « complète » en données attestées n'est pas reconstituée. Options : `termes` (fall, winter, spring,
  summer ; `fall@AAAA-MM-JJ..AAAA-MM-JJ` pour une partie de trimestre), `=UNITE` (mêmes créneaux qu'une autre unité,
  ex. Rice reprend le cours de Lounsbury), `#terme_deduit spring` (liste de cours reconduite, +15), codes PRESENCE,
  TERME_DEDUIT, HEURE (heure sans source au lieu de « créneau attesté »).
  **Calendrier spéculatif** (`speculation/calendrier_speculatif.csv`) : utilisé seulement pour une année sans période
  d'enseignement attestée (1934-35 : dates de 1933-34 transposées au même jour de la semaine, 30-45 %). L'audit, lui,
  ne lit que le calendrier attesté.
  Répartition des cours : placements fixes, puis cours déjà placés au trimestre précédent (mêmes créneaux toute
  l'année), puis unités avec laboratoire (labos à 16 h, cours le matin), puis le reste ; un enseignant qui a un
  laboratoire dans l'année garde ses après-midi libres ; aucun chevauchement (contrôlé).
  Faites : 1933-34 (35 semaines), 1934-35 (35, calendrier spéculatif), 1935-36 (34), 1936-37 (34), 1937-38 (33), 1938-39 (33), 1939-40 (32 ; liste de cours de 1938-39 reconduite : le texte transcrit de la fiche 2017.40.015 est celui du catalogue 1938-39), 1940-41 (32), 1941-42 (45 semaines dont l'été 1942 ; le catalogue 2017.40.017 n'a que ses pages liminaires, OCR refait sur ses 15 images `scans/017-*` : liste de 1940-41 reconduite et corrigée par les présences attestées ; Summer Quarter 1942 d'après la liste de 2017.40.076a-f ; vacances de printemps effectives du 2 au 5 avril 1942). 1942-43 (36 semaines de cours ; trimestres de onze semaines ; pas de liste de cours : cours attestés de l'année placés tels quels, souvent à leur heure — horaire spécial du 9 mars 1943 —, liste 1940-42 reprise pour les enseignants restés ; périodes de 55 min à 8:15, 9:20, 10:25, 11:30 grâce à la directive `#periodes` ; l'été 1943, connu par une grille complète, n'est pas reconstitué). 1943-44 (36 semaines ; liste complète des cours de l'année avec enseignant, heures et trimestres — Summer Bulletin 15, 2017.40.124a-e, et Annual Announcements, 2017.40.025 — : presque tout est MEME_ANNEE + R_ATTESTE, seuls le jour et l'heure sont supposés ; périodes déduites 8:15, 9:15, 10:15, 11:15 car la matinée finit à 12:15 ; volumes « 2x90 » quand la source donne la forme des séances ; l'été 1944, connu par la grille 2017.40.162a-e, n'est pas reconstitué). 1944-45 (37 semaines ; l'automne 1944 a sa grille — 2017.40.176a-h — étendue seulement à sa première et à sa dernière semaine ; hiver d'après la liste et l'horaire provisoire du 11 janvier 1945, cours de 50 min à l'heure pile ; printemps d'après les « courses given » du catalogue 1945-46 et les bulletins ; session régulière de l'été 1945 d'après 2017.40.036, sans les instituts). 1945-46 (36 semaines de cours + Art Institute de l'été 1946 ; seuls les titres des cours sont attestés — liste « courses given » de 2017.40.037 — : enseignants rattachés par leur notice ou par compétence, trimestres à 2 chances sur 3, horaire de 1944-45 reconduit ; mort de Jalowetz le 2 février 1946, relais par Marc Fax ; part déduite élevée). 1946-47 (retour aux semestres ; premier semestre d'après la liste par enseignant du bulletin de septembre 1946, second reconduit — TERME_DEDUIT — sauf les suites annoncées ; Summer Session 1947 d'après le programme annoncé, 2017.40.040). 1947-48 (aucun bulletin : cours « donnés » et corps enseignant d'avril 1948, 2017.40.041 ; semestres à 2 chances sur 3 ; vacances de Noël supposées du 14 décembre au 6 janvier, exclues des gabarits par `termes` ; Summer Session 1948 d'après son bilan, 2017.40.043). 1948-49 (ni bulletin ni liste de cours : titres de 1947-48 reconduits pour les enseignants présents ; deux corps enseignants — avril 1948, mars 1949 — pour les deux semestres ; arrivées du printemps 1949 : Olson, Bodky, Tsui ; Summer Session 1949 d'après son bilan, 2017.40.047 ; confiance faible).
  Reprise « =UNITE » dans une même saison (sous-périodes successives, ex. Margot Bergmann reprend la chimie de Lindsley à la mi-octobre 1941) : les créneaux de l'unité visée sont repris même s'ils sont pris par le même enseignant (ajout du 31/10, sans effet sur les années précédentes).
  Directive d'année `#periodes 08:15,09:20,10:25,11:30 16:00 55` : périodes du matin, de l'après-midi et durée ; une heure de cours = une période, 3 h = lundi-mercredi-vendredi ou mardi-jeudi-samedi, 4 h = deux doubles périodes ; aucun cours du matin ne déborde sur le déjeuner (12:30). Sans directive, les règles par défaut (8:30, 10:30, 16:00) s'appliquent. Volume « NxM » (ex. `2x90`, `1x120`, `1x180L` pour un après-midi de laboratoire) : N séances de M minutes, telles que la source les décrit. Placement sur plusieurs créneaux : `mar,jeu 10:30-12:30;ven 08:30-10:30` (grille attestée appliquée à une semaine qu'elle ne couvre pas).
  Vérification des catalogues : relecture des scans + OCR refait sur les images (tesseract, `tesseract stdin stdout < image`),
  qui a corrigé le texte transcrit du musée (1935-36 : Mangold, Play Writing… ; 1936-38 : american literature I = Wunsch,
  form in literature = Mangold, titres d'économie, « esthetics »).

## Méthode / reprise
- `scripts/aspirer.py` (recherches du site) + `scripts/sonder_ids.py` (sondage des identifiants 1-10000 : la recherche du site rate des fiches) → `fiches.json`, `fiches_sondees.json`, `cache/`, `cache_id/`.
- `scripts/selectionner.py` : tri + export des .txt.
- Extraction manuelle (lecture) : un fichier par fiche dans `extraction/<n° inventaire>.txt`, format décrit dans `extraction/_FORMAT.txt`.
- Grilles horaires illisibles à l'OCR : relues sur les scans (`scans/`), ex. 2017.40.162 (été 1944), 2017.40.176 (automne 1944).
- `scripts/construire.py` : assemble tout (dates relatives résolues, récurrences développées, doublons fusionnés). `--verifier` = contrôle seul.
- `scripts/sauvegarde.sh` : reconstruit et archive dans `backups/NNN_date.zip` (additif).
- Pour savoir ce qui reste : comparer `liste_pages.csv` aux fichiers de `extraction/`.

## Sources et part de déduction
Chaque entrée des quatre fichiers de `programme/` porte :
- `document_source` : titre exact de la fiche du musée, sa date catalogue et son n° d'inventaire (plusieurs documents séparés par « ; » quand une même activité est attestée par plusieurs sources, ex. bulletin + programme imprimé) ;
- `inventaire` et `url_source` : n° et lien direct vers la fiche ;
- `part_deduite_pct` : part de l'entrée qui n'est **pas** écrite telle quelle dans la source (0 % = attesté mot pour mot, date et heure comprises) ;
- `motifs_deduction` : les règles appliquées, avec leurs points.

Règles (`scripts/deduction.py`, additives, plafond 90 %) :
| motif | points |
|---|---|
| jour calculé à partir de la date du document (« mardi soir » dans un bulletin daté du lundi) | +5 |
| séance projetée sur chaque date d'après un horaire que la source donne comme régulier (grille, « chaque vendredi », réunion régulière) | +10 |
| séance projetée sur chaque date, régularité déduite par moi | +20 |
| récurrence ou période (début/fin) déduite | +10 |
| élément supposé par moi (heure, date d'entrée en vigueur…) | +15 |
| enseignant ou rattachement déduit (non écrit dans ce document) | +15 |
| annoncé à l'avance : réalisation non attestée (provisoire, prévu, proposé) | +15 |
| lecture corrigée d'une coquille de la source | +10 |
| date corrigée contre celle du musée ou du document | +20 |
| date approximative ou incomplète dans la source | +25 |
Quand plusieurs sources sont fusionnées, la ligne garde la part de déduction la plus basse. Les annonces reportées ou annulées sont signalées comme « statut » dans les motifs, sans points.

Répartition au 31/10/2026 (activités) : 0 % : 706 ; 5 % : 572 ; 10 % : 880 ; 15 % : 76 ; 20 % : 680 ; 25 % : 387 ; 30 % : 201 ; 35 % : 62 ; 45 % : 68.

### Convention pour l'agenda spéculatif à venir
Toute reconstitution ultérieure (agenda complété, découpage horaire, journées sans source) gardera les mêmes colonnes : `document_source` = les documents dont elle part, `part_deduite_pct` = part spéculative (ex. 60 % pour un cours placé dans un créneau vide d'après le volume horaire du catalogue), `motifs_deduction` = le raisonnement. Une entrée sans aucune source portera « aucune source directe » et 90 %.

## État
Voir la section « Avancement » ci-dessous (mise à jour à chaque sauvegarde).

## Avancement
- 31/10/2026 : toutes les fiches retenues (279) sont extraites ; 3 632 activités datées, 806 entrées de cours, 192 périodes de calendrier.
- `programme/par_annee/AAAA.md` : programme découpé par année.
- 31/10/2026 : semainier (Event Calendar, MIT) livré dans `semainier/`. Météo : non intégrée (à la demande de l'utilisateur) ;
  un relevé quotidien NOAA de la station d'Asheville (USW00013872, 1933-1957, complet) avait déjà été téléchargé dans `meteo/`, non utilisé.
- 31/10/2026 : **audit des événements, document par document** (demande : « analyser chaque document… noter chaque event… les reporter 1 à 1 »).
  - `scripts/audit_evenements.py` découpe le texte de chaque document en phrases, garde celles qui portent un repère de temps (jour, date, heure, « last week », « tomorrow »…) et cherche l'entrée qui les couvre (même document, documents jumeaux, ou toute source à la même date). Sorties : `programme/audit/EVENEMENTS.md`, `programme/audit/evenements_candidats.csv`.
  - `scripts/revue.py N` affiche les N documents suivants à relire (ordre chronologique) ; `scripts/marquer_revu.py lot.json` ajoute les lignes E/C/T/// décidées et marque le document `#revu_evenements`. Les 25 lots appliqués sont dans `programme/audit/lots/`.
  - Règles : toutes les allées et venues (membres, visiteurs), causeries, concerts, réunions, publications, résumés hebdomadaires du Work Program (sur la semaine qu'ils couvrent), nouvelles datées d'anciens marquées « hors BMC » ; jours non donnés notés comme tels (« last week » → semaine précédente) ; incohérences de la source signalées dans la note sans correction ; règles administratives non reportées (commentaire `//`).
  - Constat : beaucoup de bulletins 1943-45 n'avaient été dépouillés qu'en partie (calendriers de la semaine, visiteurs, Work Program) ; ils sont complétés.
  - Résultat : **324 documents relus, 3 466 phrases datées : 2 601 couvertes, 865 relues et non retenues (rien à dater, doublons, règles), 0 à vérifier** ; 4 650 activités datées (contre 3 885 avant l'audit).
