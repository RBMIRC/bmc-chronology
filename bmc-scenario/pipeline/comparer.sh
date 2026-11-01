#!/bin/zsh
# Essai comparatif Haiku 5.5 / Sonnet 5.5 sur deux synthèses (appels directs, quelques centimes).
# Résultats : ../comparaison/<modèle>/{personnes,annees}/ ; le GLM de Rice est dans ../syntheses/.
cd "${0:A:h}"
set -e
unset ANTHROPIC_AUTH_TOKEN ANTHROPIC_BASE_URL
if [ -z "$ANTHROPIC_API_KEY" ] && [ ! -s ~/.config/anthropic/cle_bmc_scenario ]; then
  read -s "ANTHROPIC_API_KEY?Clé API Anthropic : "; echo
  export ANTHROPIC_API_KEY
fi
for M in claude-haiku-5-5 claude-sonnet-5-5; do
  python3 06_synthese.py personnes --moteur claude --modele $M --cles "John Andrew Rice" --sortie ../comparaison/$M &
  python3 06_synthese.py annees --moteur claude --modele $M --cles 1949 --sortie ../comparaison/$M &
done
wait
ls -R ../comparaison
echo "=== COMPARAISON PRÊTE"
