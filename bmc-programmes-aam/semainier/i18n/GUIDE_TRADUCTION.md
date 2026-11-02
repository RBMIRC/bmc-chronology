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
  Black Mountain College). « Mrs », « Mr » → « Mrs. », « Mr. ».

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

## Contrôles automatiques (scripts/traduction_en.py verifier)

Un lot n'est intégré que si, pour chaque chaîne : la traduction existe ; chaque citation de l'original s'y retrouve
mot pour mot ; chaque nom propre connu et chaque nombre de l'original s'y retrouvent ; il ne reste aucun mot outil
français hors citations et titres d'œuvres ; le glossaire est respecté (avertissement sinon). Les écarts sont listés ;
le lot est corrigé puis revérifié.
