Tu travailles sur la branche `semainier-cloud`. Lis d'abord `CLAUDE.md`, `bmc-programmes-aam/LISEZMOI.md` en entier, puis `bmc-programmes-aam/duberman/LISEZMOI_duberman.md`, `speculation/_FORMAT.txt` et `scripts/deduction.py`. Ne commence à écrire qu'après ces lectures.

## Contexte
Le semainier du Black Mountain College (`bmc-programmes-aam/semainier/index.html`, données dans `data.js`, généré par `scripts/export_semainier.py`) est livré et fonctionne. Il combine :
- les événements attestés (`programme/evenements.csv`, 4 650 activités, 324 documents audités) ;
- une couche spéculative par année scolaire (`speculation/annees/AAAA-AA.txt` + `speculation/catalogues/AAAA-AA.txt`, traités par `scripts/speculer.py`), faite de 1933-34 à 1948-49 ;
- un dépouillement de Duberman (`duberman/evenements_duberman.csv`, 935 événements 1933-1957), pas encore intégré au semainier.

## Ce qui reste (dans cet ordre, une étape = un commit)

### Étape 1 — Intégrer Duberman au semainier
1. Lis `scripts/export_semainier.py` et `duberman/construire_duberman.py`.
2. Intègre `evenements_duberman.csv` comme source supplémentaire du semainier : famille/couleur reconnaissable (« Duberman »), `part_deduite_pct` conservée, source = chapitre + page + paragraphe, filtre dédié dans l'interface.
3. Pas de doublon avec l'attesté AAM : s'appuyer sur `recoupements_duberman.csv` ; si un événement existe dans les deux, garder la ligne AAM et ajouter le renvoi Duberman dans sa fiche.
4. Intègre aussi `documents_extra_duberman.csv` dans le panneau « documents datés » (même format que `semainier/documents_extra.csv`).
5. Régénère `semainier/data.js` ; ne modifie pas les CSV existants du dossier `programme/`.

### Étape 2 — Couche spéculative 1949-50 à 1956-57
Pour chaque année scolaire, dans l'ordre chronologique :
1. Rassemble les sources : `pages_txt/`, `extraction/`, `programme/par_annee/AAAA.md`, `duberman/` (année concernée), `fiches.json`.
2. Écris `speculation/catalogues/AAAA-AA.txt` puis `speculation/annees/AAAA-AA.txt`, sur le modèle de `1948-49` (cadre attesté, personnes, horaire, rythme de la journée, réunions).
3. Lance `python3 scripts/speculer.py AAAA`, vérifie : pas de chevauchement, sorties `programme/speculatif/annee_AAAA-AA.md`, `_gabarits.csv`, `_semaines.csv`.
4. Commit par année : `speculation 1949-50`, etc.

Particularités à traiter :
- Après 1949, le collège se réduit (Olson recteur, puis déclin) : n'invente pas de cours. Si la source n'atteste qu'une activité, la couche ne reconstitue que cela.
- Pour les années faiblement documentées, reste prudent : part déduite élevée, plafond 90 %, et dis-le dans l'analyse.
- Une semaine déjà complète en données attestées n'est pas reconstituée.

### Étape 3 — Contrôles
- `python3 scripts/construire.py --verifier`
- Ouvre `semainier/index.html` (navigateur headless) et vérifie : la vue Semaine, la vue Présences, un jour par année, les filtres, aucune erreur console.
- Compare avant/après : le nombre d'activités attestées ne doit pas diminuer.

## Règles (non négociables)
- Rien de supprimé ni écrasé : tout fichier modifié est conservé dans `backups/NNN_...` (crée `backups/`) ou versionné par git ; les nouvelles sorties numérotées `NNN_`.
- Jamais d'événement sans source. Chaque entrée porte `document_source`, `inventaire`, `part_deduite_pct`, `motifs_deduction` (barème de `deduction.py` et de `speculer.py`).
- Ordre de confiance en cas de conflit : document daté attesté > Duberman corrigé > spéculation.
- Les scans (`scans/`) ne sont pas dans ce dépôt. Tu ne peux pas relire les grilles sur image. Quand une lecture exigerait le scan, écris `[à vérifier sur scan]` dans la note de l'entrée et augmente la part déduite de 15.
- Les scripts contiennent des chemins `~/Documents/...` en dur (`scripts/selectionner.py`, `duberman/construire_duberman.py`) : remplace-les par des chemins relatifs à la racine du dépôt, dans un commit à part.
- N'invente pas de nom, de date ni de lieu. Dans le doute, demande dans le compte rendu final.
- Français pour tous les textes et commentaires.

## Suivi
- Crée et tiens à jour `SUIVI.md` à la racine : étape, année, fait / reste, points à vérifier sur scan.
- Travaille par lots : une année = un commit + une ligne dans `SUIVI.md`. Si la session s'interrompt, la suivante reprend avec `SUIVI.md`.
- Pousse sur `semainier-cloud` uniquement. Ne touche jamais à `main`.

## Fin de session
Termine par un compte rendu : ce qui est fait, les chiffres (activités, entrées spéculatives par année, part déduite moyenne), ce qui reste, la liste des `[à vérifier sur scan]`.
