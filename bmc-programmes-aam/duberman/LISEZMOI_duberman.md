# Duberman pour le semainier

Dépouillement chronologique complet de Martin Duberman, *Black Mountain: An Exploration in Community*
(Dutton 1972 ; édition Anchor 1973), à partir du texte corrigé
`~/Documents/DATA BMC/Duberman_Black_Mountain_corrige.txt`.

## Fichiers

| Fichier | Contenu |
|---|---|
| `extraction/*.txt` | Lecture manuelle, chapitre par chapitre (lignes `E|…`, format dans `_FORMAT.txt`). C'est la source : on corrige ici. |
| `construire_duberman.py` | Convertit les extractions et produit tous les CSV ci-dessous. |
| `evenements_duberman.csv` | 935 événements. Les 15 premières colonnes sont celles de `programme/evenements.csv`. Colonnes en plus : `date_fin`, `precision`, `date_livre`, `categorie`, `chapitre`, `page`, `paragraphe`, `notes_citees`, `notes_texte` (texte intégral des notes de Duberman), `recoupement_aam`. |
| `documents_duberman.csv` | 2 156 documents datés cités dans les notes : lettres, procès-verbaux, entretiens de 1967-1971, publications. Pour chacun : date, type, contexte, fonds (Raleigh, courtesy X), chapitre, note et page. Extraction automatique. |
| `documents_extra_duberman.csv` | Les mêmes documents, d'avant 1958 et sans les entretiens, au format de `semainier/documents_extra.csv`. |
| `recoupements_duberman.csv` | Correspondances le même jour avec les données AAM, et vérification contre l'ancienne extraction Chronos 2. |
| `rapport_duberman.txt` | Chiffres et contrôles : format, pages, recoupements, événements Chronos non retrouvés. |
| `pages_notes.py`, `_appui/` | Calcul de la page de chaque note à partir de l'OCR, et copies des tables paragraphe → page. |

## Règles

- Chaque événement cite le livre au chapitre, à la page et au paragraphe (¶ du texte corrigé), ainsi que la source
  primaire donnée par la note de Duberman.
- `part_deduite_pct` suit le barème du projet :
  - calc +5, rel +10, ded/prévu +15, corr +20, approx +25 ;
  - +25 automatiquement si la date est plus grossière que le jour ;
  - plafond 90.
- Pour une date au mois, à la saison ou à l'année, `date` porte le premier jour et `date_fin` le dernier.
  La `precision` le signale.
- Incohérences internes du livre corrigées et signalées dans `note` :
  - Wunsch : 1934 au lieu de février 1935 ;
  - mica : 1942 au lieu de 1943 ;
  - Wallen à Rogers : « January 1, 1945 » au lieu de 1946 ;
  - mort de Jalowetz : « about a year later » contre « early in 1946 » ;
  - Pageant : 1957, pas 1956.

## Reconstruire

```bash
python3 construire_duberman.py
```

Le script ne touche ni à `programme/` ni à `semainier/`. **Ne pas le relancer dans le dépôt cloud** : Chronos 2
(`DATA_BMC/Chronos 2/`) n'y est pas recopié, et `recoupements_duberman.csv` perdrait sa partie Chronos.

## Intégration au semainier (1/11/2026)

`scripts/export_semainier.py` lit `evenements_duberman.csv`, `documents_extra_duberman.csv` et
`001_doublons_aam.csv` :

- **`001_doublons_aam.csv`** (décision à la main sur les 94 rapprochements AAM de `recoupements_duberman.csv`) :
  `doublon` (15) = même événement, la ligne AAM est gardée et sa fiche reçoit le « Renvoi Duberman » (texte, page,
  notes) ; `possible` (13) = les deux restent, avec renvoi mutuel (surtout « réunion du corps enseignant » de Duberman
  contre « Faculty and Student Officers » de l'AAM, deux instances distinctes qui siègent parfois le même jour) ;
  `rejeté` (66) = activités différentes le même jour (rapprochement automatique par nom ou type seulement).
- Événements datés au jour (et plages de 14 jours au plus) : dans la grille, couleur sarcelle, préfixe « D. »,
  `part_deduite_pct` du CSV. Datés au mois, à la saison ou à l'année : panneau latéral « Duberman : … datés de façon
  imprécise » (plus de 4 mois : bloc replié). Case « Duberman » dans l'en-tête ; les filtres de famille (d'après le
  type), de part déduite et la recherche s'appliquent aussi (« duberman » dans la recherche les isole).
- Fiche : source = livre, chapitre, page, paragraphe ; notes de Duberman (source primaire) ; date telle que dans le livre.
- Documents datés des notes (1 031) : panneau « Documents datés de ces jours », avec la référence de la note.
