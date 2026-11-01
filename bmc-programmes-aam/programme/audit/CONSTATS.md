# Audit du 31/10/2026 : les semaines sont-elles remplies ?

Réponse courte : **non**. Le programme attesté couvre bien les années des bulletins hebdomadaires (1942-45), très mal le reste. Les chiffres détaillés, semaine par semaine, sont dans `AUDIT.md` et `semaines.csv` (régénérés à chaque sauvegarde par `scripts/audit_semaines.py`).

## 1. Le calendrier lui-même a des trous

Sur 1 255 semaines (sept. 1933 → sept. 1957) :
- 772 sont des semaines de cours ;
- 142 sont des vacances ;
- 8 sont du Work Camp seul ;
- **333 ne sont couvertes par aucune période attestée.**

Ces dernières se répartissent ainsi :
- 1934-35 entier : aucun calendrier. Le catalogue 1934-35 (fiche 6577) imprime celui de 1935-36, pas le sien.
- 1953-54 (automne, hiver), puis tout 1954-55 après décembre, et 1955-57 : aucun document.
- Les intersessions d'été non documentées, pour chaque année.

## 2. Remplissage des 772 semaines de cours (activités attestées seulement)

| période | complètes | partielles | maigres | vides |
|---|---|---|---|---|
| 1933-41, Blue Ridge | 0 | 1 | 31 | 198 |
| 1941-46, Lake Eden, bulletins hebdomadaires | 28 | 51 | 109 | 27 |
| 1946-57 | 0 | 9 | 101 | 217 |
| **total** | **28** | **61** | **241** | **442** |

Définitions :
- *complète* : des cours sur au moins 5 jours et au moins 15 séances ;
- *partielle* : au moins 10 activités, ou des cours sur au moins 2 jours ;
- *maigre* : 1 à 9 activités ;
- *vide* : aucune activité.

Il y a 92 semaines où toutes les activités viennent de la projection d'une grille ou d'une récurrence. Elles sont signalées à 10–25 % de déduction.

## 3. Les vides ne viennent pas d'oublis d'extraction

Vérifications faites :
- **Les 324 fiches retenues sont toutes passées.** Les 37 qui ne donnent aucune ligne ont chacune une justification écrite.
- **Les 14 « doublons » annoncés le sont bien.** Comparaison du texte : ratio 0,98 à 1,00, les seules différences étant des variantes d'OCR.
- **Les années vides sont celles où le musée n'a presque rien.** Le nombre de documents par année le montre :
  - 1933-38 : 1 à 5 documents par an, des catalogues ;
  - 1947-49 : 5 à 9 par an, des annonces d'été ;
  - 1951-54 : 1 à 3 par an.
- **Les sondages des identifiants 1-10000 sont faits** : les fiches que la recherche du site ne trouvait pas sont incluses.

## 4. Contrôles de cohérence et corrections faites

- **Grille de l'automne 1944 projetée jusqu'au 15 décembre**, alors que le trimestre finit le 14 et que les vacances commencent le 15 (2017.40.184a-d). Corrigé : 33 lignes, 7 séances retirées.
- **Enseignants des grilles non déclarés comme déduits.** Les grilles de l'été 1943 (2017.40.114), de l'été 1944 (2017.40.162) et de l'automne 1944 (2017.40.176) ne nomment **aucun enseignant**, vérifié sur les scans 162-05 et 176-08. Les noms venaient d'autres listes. Ajout de la directive `#grille_sans_noms` : ces séances portent maintenant « enseignant déduit », à +15 %.
- **Règle de déduction** : « enseignants déduits », « enseignants probables » au pluriel n'étaient pas reconnus. Corrigé dans `scripts/deduction.py`.
- **Récital Eduard Steuermann du 12/12/1939 (2017.40.286)** : il était extrait, mais absent de `liste_pages`, parce que le filtre écartait tout titre contenant « Schoenberg ». Corrigé dans `scripts/selectionner.py`.
- **Catalogues 1934-35 et 1935-36 relus sur scan** (corrections du texte transcrit du musée) : voir `speculation/catalogue_1935-36.txt`.

## 5. Ce qui reste signalé et qui est juste

- **25 « même personne à deux endroits »** : ils sont dans les grilles elles-mêmes, vérifiées sur scan.
  - Wunsch le samedi de l'automne 1944 : « Drama I » 10 h 30–12 h 30 et « Rom Drama » 11 h 30–12 h 30.
  - Elsa Kahl le jeudi de l'été 1944 : elle est rattachée par déduction à l'Operatic Workshop, que la grille ne nomme pas.
  - Kazin : l'écoute de disques qu'il « supervise » avec deux étudiantes le jeudi soir chevauche son cours sur Melville.
- **10 cours pendant des vacances.** La source le dit (interlude de mai 1943, cours de dramatique hebdomadaire de l'été 1943), ou bien il s'agit d'activités hors du collège (Albers à la Lowthorpe School, de Graaff à un institut de linguistique, stage syndical accueilli à l'intersession).
- **61 cours sans enseignant nommé**, tels que dans la source.

## 6. Pour remplir les semaines

Seule la couche spéculative peut remplir les semaines vides, sur le modèle de la semaine du 2 au 8 mars 1936 : concordance des cours de l'année, relue sur scan, et rythme de la journée, avec une part déduite par case. Les ressources par période :
- **1933-41** : un catalogue par an (2017.40.006 à .016), avec la liste des cours et le corps enseignant. On peut donc construire une concordance par année, comme pour 1935-36.
- **1941-46** : les grilles attestées couvrent certains trimestres. Ailleurs, les listes de cours des annonces de chaque trimestre permettent de compléter.
- **1946-57** : annonces des sessions d'été et quelques catalogues (1946-47, 1948-49, 1949-50, 1950-51, 1951-52, 1952-53). La part déduite sera nettement plus élevée.
- **Années sans calendrier** (1934-35, 1953-57) : un calendrier spéculatif serait à poser d'abord, avec sa part déduite, avant tout remplissage.
