#!/bin/zsh
# Fin des synthèses (06) en lots (API Batches, −50 %) : Sonnet 5.5 pour personnages, années et cours,
# Haiku 5.5 pour les mois ; puis assemblage (07).
# À lancer dans un terminal : la clé est demandée au clavier, jamais écrite nulle part.
# Reprenable : relancer le script ne renvoie ni ce qui est fait, ni ce qui attend déjà dans un lot.
cd "${0:A:h}"
set -e
unset ANTHROPIC_AUTH_TOKEN ANTHROPIC_BASE_URL   # jeton z.ai : ne doit pas accompagner la clé Claude
if [ -z "$ANTHROPIC_API_KEY" ] && [ ! -s ~/.config/anthropic/cle_bmc_scenario ]; then
  read -s "ANTHROPIC_API_KEY?Clé API Anthropic : "; echo
  export ANTHROPIC_API_KEY
fi
caffeinate -i -w $$ &
M=claude-sonnet-5-5
MM=claude-haiku-5-5   # mois
journal=../etat/finir_claude.log
exec > >(tee -a $journal) 2>&1
echo "=== début $(date '+%Y-%m-%d %H:%M')"

# 1. un appel direct par passe pour valider schéma et accès (quelques centimes)
python3 06_synthese.py personnes --moteur claude --modele $M --min-mentions 5 --test 1
python3 06_synthese.py annees --moteur claude --modele $M --test 1
python3 06_synthese.py enseignements --moteur claude --modele $M --test 1

# 2. personnes, années, enseignements : en lots, en même temps
python3 06_synthese.py personnes --moteur claude --modele $M --min-mentions 5 --lot
python3 06_synthese.py annees --moteur claude --modele $M --lot
python3 06_synthese.py enseignements --moteur claude --modele $M --lot
for p in personnes annees enseignements; do python3 06_synthese.py $p --relever --attendre; done

# 3. les mois, qui s'appuient sur les chapitres d'années
python3 06_synthese.py mois --moteur claude --modele $MM --test 1
python3 06_synthese.py mois --moteur claude --modele $MM --lot
python3 06_synthese.py mois --relever --attendre

# 4. seconde chance pour les requêtes en erreur, puis assemblage
for p in personnes annees enseignements mois; do
  python3 06_synthese.py $p --moteur claude --modele $( [ $p = mois ] && echo $MM || echo $M ) --lot $( [ $p = personnes ] && echo --min-mentions 5 )
  python3 06_synthese.py $p --relever --attendre
done
python3 07_assembler.py
python3 etat.py
echo "=== TERMINÉ $(date '+%Y-%m-%d %H:%M')"
