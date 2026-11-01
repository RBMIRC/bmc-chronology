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

Le script ne touche ni à `programme/` ni à `semainier/`. L'intégration dans `scripts/export_semainier.py` reste à décider.
