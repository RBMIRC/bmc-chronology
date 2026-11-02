# Vérification des sources du semainier (006)

Pour chaque entrée affichée, le texte de la source citée est ouvert et on y cherche les noms des personnes, les mots du titre (anglais pour l'AAM) et l'année ou le mois. Méthode et statuts : en-tête de `scripts/verifier_sources.py`. « À relire » ne veut pas dire faux : le passage est souvent traduit ou paraphrasé (Duberman et le scénario sont en français, leurs sources en anglais), ou l'entrée est générique (repas, thé).

| couche | entrées | retrouvé | indice faible | à relire | référence introuvable | sans source |
|---|---|---|---|---|---|---|
| AAM | 5980 | 4840 (81 %) | 1127 (19 %) | 13 (0 %) | 0 (0 %) | 0 (0 %) |
| Duberman | 935 | 850 (91 %) | 68 (7 %) | 17 (2 %) | 0 (0 %) | 0 (0 %) |
| Scénario | 4335 | 3416 (79 %) | 721 (17 %) | 198 (5 %) | 0 (0 %) | 0 (0 %) |
| Scénario (fiches citées) | 11565 | 9313 (81 %) | 1559 (13 %) | 690 (6 %) | 3 (0 %) | 0 (0 %) |
| Spéculatif | 10072 | 7481 (74 %) | 2110 (21 %) | 462 (5 %) | 19 (0 %) | 0 (0 %) |

## Autres informations affichées

- Périodes (trimestres, vacances) : 203 ; sans source : 0 ; sans lien : 0.
- Cours offerts (panneau) : 821 ; sans source : 0 ; sans lien : 0.
- Documents datés : 324 fiches du musée (lien vers la fiche) ; 1031 documents cités dans les notes de Duberman, sans référence de note : 0.

## Contrôle négatif (fiabilité de la méthode)

Taux de « retrouvé » sur 500 entrées par couche, avec leur vraie source puis avec la source d'une autre entrée tirée au hasard. L'écart mesure ce que vaut « retrouvé » ; le taux avec une source au hasard est le taux de faux positifs.

| couche | vraie source | source au hasard |
|---|---|---|
| AAM | 81 % | 17 % |
| Duberman | 91 % | 4 % |
| Scénario | 83 % | 5 % |
| Scénario (fiches citées) | 79 % | 6 % |
| Spéculatif | 75 % | 40 % |

## Scénario (fiches citées) : références introuvables ou absentes (3)

- 1944 «  » — Duberman 1972, p. 
- 1955 «   » — Rumaker 2003, p. 
- 1910 « Robert Creeley Joel Oppenheimer » — Harris 2005, p. 

## Spéculatif : références introuvables ou absentes (19)

- 1950-51, été (09/07/1951 – 31/07/1951) « Cours d'écriture de Charles Olson (un soir par semaine) » — Duberman, ch. 14, p. 420-421 (¶1714-1715)
- 1950-51, été (01/08/1951 – 31/08/1951) « Cours d'écriture de Charles Olson (un soir par semaine) » — Duberman, ch. 14, p. 420-421 (¶1714-1715)
- 1951-52, automne « Cours d'écriture de Charles Olson (un soir par semaine) » — Duberman, ch. 14, p. 409-421 (¶1680-1715)
- 1951-52, printemps « Cours d'écriture de Charles Olson (un soir par semaine) » — Duberman, ch. 14, p. 409-421 (¶1680-1715)
- 1952-53, été « Répétitions de la compagnie Cunningham » — Duberman, ch. 14, p. 395-397 (¶1631-1635)
- 1952-53, été « Répétitions de la compagnie Cunningham » — Duberman, ch. 14, p. 395-397 (¶1631-1635)
- 1952-53, été « Répétitions de la compagnie Cunningham » — Duberman, ch. 14, p. 395-397 (¶1631-1635)
- 1952-53, été « Répétitions de la compagnie Cunningham » — Duberman, ch. 14, p. 395-397 (¶1631-1635)
- 1952-53, été « Répétitions de la compagnie Cunningham » — Duberman, ch. 14, p. 395-397 (¶1631-1635)
- 1952-53, été « Répétitions de la compagnie Cunningham (soir) » — Duberman, ch. 14, p. 395-397 (¶1631-1635)
- 1952-53, été « Répétitions de la compagnie Cunningham (soir) » — Duberman, ch. 14, p. 395-397 (¶1631-1635)
- 1952-53, été « Répétitions de la compagnie Cunningham (soir) » — Duberman, ch. 14, p. 395-397 (¶1631-1635)
- 1952-53, été « Répétitions de la compagnie Cunningham (soir) » — Duberman, ch. 14, p. 395-397 (¶1631-1635)
- 1952-53, été « Répétitions de la compagnie Cunningham (soir) » — Duberman, ch. 14, p. 395-397 (¶1631-1635)
- 1952-53, été « Spectacle de la compagnie Cunningham pour la communauté : possible » — Duberman, ch. 14, p. 397-399 (¶1635-1639)
- 1953-54, printemps « Cours d'écriture de Charles Olson (un soir par semaine) » — Duberman, ch. 14, p. 409-421 (¶1680-1715)
- 1953-54, printemps « Cours du soir de Robert Creeley » — Duberman, ch. 14, p. 428-434 (¶1740 ; ¶1757-1759)
- 1954-55, automne « Cours d'écriture de Charles Olson (un soir par semaine) » — Duberman, ch. 14, p. 409-421 (¶1680-1715)
- 1954-55, automne « Cours du soir de Robert Creeley » — Duberman, ch. 14, p. 435-436 (¶1764-1765)
