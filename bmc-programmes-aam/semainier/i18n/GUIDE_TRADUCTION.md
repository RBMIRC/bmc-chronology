# Guide de traduction anglaise du semainier

But : un anglais irréprochable, fidèle et homogène pour tout ce que le semainier affiche en anglais. Circuit :
`scripts/traduction_en.py` (préparer → traduire → vérifier → intégrer → état), puis `scripts/traduire_en.py`
(qui écrit `semainier/data_en.js`) et `scripts/publier_semainier.py`.

## Ce qu'on traduit, ce qu'on ne traduit pas

- On traduit **seulement nos textes rédigés en français** : résumés et titres (Duberman, AAM, reconstitution,
  compléments, livres), notes, barème, interface.
- On ne traduit **jamais** ce qui est déjà en anglais : sources, titres de documents, citations, titres de cours,
  faits rédigés en anglais. Une chaîne déjà anglaise n'entre pas dans les lots.
- Les citations (« … », “ … ”, " … ") sont **recopiées à l'identique**, entre “ ”. Les titres d'œuvres et de livres
  gardent leur langue (*Le Malade imaginaire*, *Pelléas et Mélisande*).

## Langue et style

- **Anglais américain** (le collège, ses documents et ses historiens sont américains) : program, theater, color,
  catalog, center, neighboring, organize.
- Ton : notice d'archive, sobre et exact ; phrases courtes comme l'original ; pas d'ajout, pas d'omission, pas
  d'interprétation. Garder les points-virgules qui séparent les faits.
- Majuscule initiale, pas de point final pour un titre (comme l'original).
- Dates : « 26 juin 1936 » → « June 26, 1936 » ; « (puis 10 février) » → « (then February 10) » ; « été 1944 » →
  « summer 1944 » ; saisons et mois en minuscules/majuscules selon l'usage anglais (summer, June).
- Heures : « 20 h » → « 8 p.m. » ; « 16 h 30 » → « 4:30 p.m. ».
- « X à Y » (lettre) → « X to Y » ; « X à Y : … » → « X to Y: … ». Espaces françaises avant « : ; ! ? » supprimées.
- Noms de personnes, de lieux et d'institutions : **inchangés** (Lake Eden, Blue Ridge, Lee Hall, Studies Building,
  Black Mountain College). « Mrs », « Mr », « Dr », « St » → « Mrs. », « Mr. », « Dr. », « St. » (St. Elizabeths).
- Guillemets : “ ” ; à l'intérieur d'une citation ou d'un titre entre guillemets, ‘ ’ (usage américain). Les traductions
  peuvent garder “ ” imbriqués : `traduire_en.py` les convertit en ‘ ’ en écrivant `data_en.js`.
- Virgule de série (« Rice, Albers, and Dreier »), virgule dans les nombres (« $1,500 »), « 21% », « 4:30 p.m. ».
- Étage : le « deuxième étage » français est le « third floor » américain.
- Titres d'œuvres français gardés tels quels : liste `TITRES_FR` dans `scripts/traduction_en.py` (à compléter au besoin) ;
  noms anglais qui contiennent un mot outil français (Big Sur, La Luz, Le Nain, avant-garde) : liste voisine.
- Phrase française entre guillemets qui traduit des paroles ou un écrit anglais (« Vous avez dansé comme une baleine »,
  « une personne parfaite si… ») : on ne connaît pas les mots exacts ; en anglais, **pas de guillemets** (discours
  indirect ou formule neutre), pour ne pas fabriquer une fausse citation. Seules les citations restées en anglais dans
  nos textes sont reprises entre “ ”.
- Mots français entre guillemets dans nos textes (« clandestines », « question Goodman ») : ce ne sont pas des citations
  des sources, on les traduit (le vérificateur le signale seulement par un avertissement).

## Glossaire du collège (obligatoire)

| français | anglais |
|---|---|
| réunion du corps enseignant, réunion de la faculté | faculty meeting |
| corps enseignant, la faculté | the faculty |
| réunion générale, réunion de la communauté | general meeting, community meeting |
| Board of Fellows, conseil | Board of Fellows |
| recteur | rector |
| programme de travail | work program |
| bulletin de la communauté | Community Bulletin |
| officiers étudiants | student officers |
| modérateur, modératrice (étudiants) | moderator |
| trimestre (quarter) / semestre | quarter / semester (selon l'année) |
| session d'été, institut d'été | summer session, summer institute |
| Institut de musique, Institut d'art | Music Institute, Art Institute |
| ferme | the farm |
| salle à manger | dining hall |
| conférence (exposé) | lecture |
| causerie | talk |
| répétition | rehearsal |
| démission | resignation |
| renvoi | dismissal |
| admission refusée | admission refused |
| diplôme (obtention) | graduation |
| les Albers | the Alberses |
| part déduite | deduced share |
| reconstitué | reconstructed |

## Outils de brouillon

Pour les notes répétitives, un brouillon est produit puis vérifié comme une traduction faite à la main :
- `scripts/traduction_modeles.py lots/lot_NNN.tsv` : « présence attestée », souvenirs du BMC Yearbook, « document daté »,
  cours suivis (fiches d'étudiants) ; ce qui ne suit pas un modèle est listé (RESTE) et se traduit à la main ;
- `scripts/traduction_composer.py besoins NNN…` puis `ecrire NNN` : notes de recoupement « Recoupement — Duberman … Scénario,
  mêmes pages : EV-… » ; chaque pièce (préfixe, titre du scénario) est traduite une fois dans `i18n/pieces_en.tsv`, et les
  titres tronqués sont rendus en entier.

## Contrôles automatiques (scripts/traduction_en.py verifier)

Un lot n'est intégré que si, pour chaque chaîne : la traduction existe ; chaque citation anglaise de l'original s'y
retrouve mot pour mot (la plus intérieure en cas de guillemets imbriqués) ; chaque nom propre connu et chaque nombre de
l'original s'y retrouvent, les dates « 25/09/1933 » et « 23/02 » rendues en mois anglais, les heures « 14:30 » / « 16 h 30 »
en « 2:30 p.m. » ; il ne reste aucun mot outil français hors citations, titres d'œuvres et particules de noms (du Plessix) ;
le glossaire est respecté (avertissement sinon). Les écarts sont listés ; le lot est corrigé puis revérifié.
Une correction ultérieure s'ajoute à `revu_en.tsv` (la dernière ligne pour un même original l'emporte) : `verifier NNN
--remplacer`, ou une ligne « original<TAB>traduction » ajoutée à la fin.

Tolérances du vérificateur, à compléter au besoin dans `scripts/traduction_en.py` :
- `ORTHO_NOMS` : nom mal orthographié dans la source et corrigé en silence dans la traduction (Frederic → Fredric,
  Fiola → Flola, Hore → Fiore, Emanuel → Emanu-El…) ;
- noms français d'organisations et de lieux (`LIEUX_FR`, liste d'exclusion) et titres d'œuvres français (`TITRES_FR`) ;
- mesures métriques rendues dans les unités américaines d'origine (« 2,75 m » → « 9 feet ») : le nombre métrique n'est
  pas exigé si la traduction emploie inch, foot, feet, gallon, pound, mile ;
- « 1 000 » ou « 1000 » ↔ « 1,000 » ; dates ISO « 1953-11-24 » ↔ « November 24, 1953 » ; heures « 21h » ↔ « 9 p.m. » ;
  durées « 1h30 » ↔ « an hour and a half ».
Citation française qui traduit des paroles anglaises : si l'anglais exact figure dans une notice voisine (même scène
racontée deux fois), on le reprend entre “ ” ; sinon discours indirect, sans guillemets.

## État

Novembre 2026 : les 14 045 chaînes françaises affichées (Duberman, documents de l'AAM, reconstitution, compléments,
notes, fiches d'étudiants, livres et études, résumés) sont traduites, vérifiées et intégrées (lots 001 à 143). La
traduction automatique (Argos) ne sert plus que de filet pour une chaîne nouvelle, signalée ≈ ;
`traduction_en.py preparer` en fait un nouveau lot, `traduction_en.py etat` donne le décompte.
