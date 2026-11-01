#!/bin/zsh
# Chaîne complète sur z.ai (GLM-5.2), reprenable : relancer ce script reprend où il s'est arrêté.
# Suivi : tail -f ~/Documents/bmc-scenario/etat/lancer_zai.log ; état : python3 etat.py
cd "${0:A:h}"
set -e
for prio in A B C A,B,C; do            # le dernier passage reprend les morceaux échoués
  python3 04_extraire.py --moteur zai --priorite $prio --parallele 4
done
python3 05_fusionner.py
python3 06_synthese.py personnes --moteur zai --min-mentions 5 --parallele 3
python3 06_synthese.py annees --moteur zai --parallele 3
python3 06_synthese.py enseignements --moteur zai --parallele 3
python3 06_synthese.py mois --moteur zai --parallele 3
python3 07_assembler.py
echo "TERMINÉ $(date '+%Y-%m-%d %H:%M')"
