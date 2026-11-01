#!/bin/zsh
# Pose la clé API Anthropic dans un fichier privé (lisible par vous seul), pour que les
# scripts du pipeline puissent être lancés depuis la conversation sans jamais l'afficher.
# Pour la retirer : rm ~/.config/anthropic/cle_bmc_scenario
f=~/.config/anthropic/cle_bmc_scenario
mkdir -p ~/.config/anthropic && chmod 700 ~/.config/anthropic
read -s "K?Clé API Anthropic (rien ne s'affiche) : "; echo
umask 077; print -r -- "$K" > $f; chmod 600 $f; unset K
echo "Clé posée dans $f ($(wc -c < $f | tr -d ' ') caractères)."
