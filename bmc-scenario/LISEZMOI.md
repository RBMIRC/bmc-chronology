# Black Mountain College 1933-1957 — matière de scénario à l'échelle 1

Corpus : `~/Downloads/BMC exo theory BOOKS` (60 fichiers, 2 doublons écartés).
But : un JSON qui permet de raconter vingt-quatre ans mois par mois, avec des flash-back (avant 1933, avant l'arrivée de chacun) et des flash-forward (après le départ, après 1957). Chaque fait garde sa source, ses folios et son degré de certitude.

## Les sept étapes (`pipeline/`)

| étape | script | appel au modèle | sortie |
|---|---|---|---|
| 01 inventaire | `01_inventaire.py` | non | `sources.csv` (numéro, rôle, priorité A/B/C) |
| 02 texte | `02_texte.py` | non | `texte/NNN.jsonl.gz`, page par page, OCR des scans |
| 03 morceaux | `03_decouper.py` | non | `morceaux/morceaux.jsonl` (~5,5 k tokens, repères `[p. 123]`) |
| 04 extraction | `04_extraire.py` | **oui** | `extractions/<morceau>.json` (12 catégories, schéma `schema.py`) |
| 05 fusion | `05_fusionner.py` | non | `fusion/*.json` : noms canoniques, dates, doublons réunis |
| 06 synthèses | `06_synthese.py` | **oui** | `syntheses/{personnes,annees,enseignements,mois}/` |
| 07 assemblage | `07_assembler.py` | non | `sortie/NNN_bmc_scenario_1933-1957.json` (jamais écrasé) |

`python3 pipeline/etat.py` dit où on en est et ce que ça a coûté.

Rôles des sources (`config.py`) : histoire, témoignage, biographie, enseignement, écrits, catalogue, contexte. Chacun oriente l'extraction : les témoignages vers les scènes et la psychologie, les écrits (Goodman, Anni Albers, E. de Kooning…) vers « ce qu'un cours aurait pu contenir », marqué `atteste_a_bmc`.

## Ce que contient une extraction

`evenements`, `personnes` (apparence, tempérament, psychologie, voix, habitudes, convictions, contradictions, avant / après), `relations`, `cours` (consignes exactes, matériaux, déroulé), `idees`, `lieux` (lumière, sons, saisons), `quotidien` (22 thèmes), `scenes` (déroulé, paroles paraphrasées, atmosphère, enjeu), `citations` (25 mots au plus + traduction), `oeuvres`, `conflits`, `echos` (liens explicites entre deux époques : la charpente des flash-back/forward), `motifs`, plus `cadre_temporel` du passage pour dater ce qui ne l'est pas.

## Lancer l'extraction complète

Moteur Claude (clé API à saisir soi-même dans le terminal, lots à −50 %) :

```bash
cd ~/Documents/bmc-scenario/pipeline
read -s ANTHROPIC_API_KEY && export ANTHROPIC_API_KEY
python3 04_extraire.py --estimer
python3 04_extraire.py --moteur claude --modele claude-opus-5-5 --lot     # envoi, ~1 h à 24 h
python3 04_extraire.py --moteur claude --relever                          # récupération
python3 05_fusionner.py
python3 06_synthese.py personnes --moteur claude --lot      # puis --relever
python3 06_synthese.py annees --moteur claude --lot         # puis --relever
python3 06_synthese.py enseignements --moteur claude --lot  # puis --relever
python3 06_synthese.py mois --moteur claude --lot           # après annees ; puis --relever
python3 07_assembler.py
```

Moteur z.ai (forfait GLM, jeton lu dans `~/.claude/settings.json`) : mêmes commandes avec `--moteur zai` et sans `--lot` (appels directs, `--parallele 4`).

## À relire à la main

- `fusion/_noms.csv` : rattachements de noms automatiques et noms seuls non résolus → compléter `referentiel/alias.csv` (même personne) ou `referentiel/distincts.csv` (deux personnes à ne jamais fondre), puis relancer 05 et 07 (gratuit).
- Les identifiants de fiches restent stables d'une fusion à l'autre : ils sont repris de `fusion/_reference/` (la fusion sur laquelle les synthèses ont été rédigées) ; les fiches absorbées sont listées dans `fusion/_redirections.json`, que 07 applique aux synthèses.
- Les romans (`config.FICTION`, aujourd'hui *Making Do* de Goodman) : leurs personnages restent à part, « Terry (personnage, Goodman 1963) ».
- les fiches `conteste` et les `autres_versions` : les endroits où les sources divergent.

## Mesures du test (10 morceaux, GLM-5.2, 30/10/2026)

21 à 79 entrées par morceau (moyenne 53), 4 à 15 k tokens en sortie. Citations de 4 à 17 mots. Les témoignages (Rumaker) et l'histoire (Duberman) donnent le plus ; les catalogues et le contexte, peu (« marginale »).
