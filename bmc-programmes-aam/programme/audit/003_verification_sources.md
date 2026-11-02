# Vérification des sources du semainier (003)

Pour chaque entrée affichée, le texte de la source citée est ouvert et on y cherche les noms des personnes, les mots du titre (anglais pour l'AAM) et l'année ou le mois. Méthode et statuts : en-tête de `scripts/verifier_sources.py`. « À relire » ne veut pas dire faux : le passage est souvent traduit ou paraphrasé (Duberman et le scénario sont en français, leurs sources en anglais), ou l'entrée est générique (repas, thé).

| couche | entrées | retrouvé | indice faible | à relire | référence introuvable | sans source |
|---|---|---|---|---|---|---|
| AAM | 4650 | 3649 (78 %) | 981 (21 %) | 20 (0 %) | 0 (0 %) | 0 (0 %) |
| Duberman | 935 | 849 (91 %) | 69 (7 %) | 17 (2 %) | 0 (0 %) | 0 (0 %) |
| Scénario | 4335 | 3416 (79 %) | 720 (17 %) | 199 (5 %) | 0 (0 %) | 0 (0 %) |
| Scénario (fiches citées) | 7789 | 6788 (87 %) | 835 (11 %) | 164 (2 %) | 2 (0 %) | 0 (0 %) |
| Spéculatif | 8350 | 5807 (70 %) | 1702 (20 %) | 841 (10 %) | 0 (0 %) | 0 (0 %) |

## Autres informations affichées

- Périodes (trimestres, vacances) : 203 ; sans source : 0 ; sans lien : 0.
- Cours offerts (panneau) : 821 ; sans source : 0 ; sans lien : 0.
- Documents datés : 324 fiches du musée (lien vers la fiche) ; 1031 documents cités dans les notes de Duberman, sans référence de note : 0.

## Contrôle négatif (fiabilité de la méthode)

Taux de « retrouvé » sur 500 entrées par couche, avec leur vraie source puis avec la source d'une autre entrée tirée au hasard. L'écart mesure ce que vaut « retrouvé » ; le taux avec une source au hasard est le taux de faux positifs.

| couche | vraie source | source au hasard |
|---|---|---|
| AAM | 76 % | 11 % |
| Duberman | 90 % | 5 % |
| Scénario | 83 % | 7 % |
| Scénario (fiches citées) | 88 % | 5 % |
| Spéculatif | 68 % | 35 % |

## Scénario (fiches citées) : références introuvables ou absentes (2)

- 1944 «  » — Duberman 1972, p. 
- 1910 « Robert Creeley Joel Oppenheimer » — Harris 2005, p. 
