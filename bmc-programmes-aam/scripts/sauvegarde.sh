#!/bin/sh
# Sauvegarde additive : reconstruit les sorties puis archive extraction/, programme/, pages_txt/, scripts/
# dans backups/NNN_AAAA-MM-JJ_HHMM.zip (jamais d'écrasement).
cd "$(dirname "$0")/.." || exit 1
python3 scripts/selectionner.py >/dev/null && python3 scripts/construire.py | tail -1 && python3 scripts/export_ics.py && python3 scripts/speculer.py && python3 scripts/audit_semaines.py >/dev/null && python3 scripts/export_semainier.py
mkdir -p backups
n=$(ls backups 2>/dev/null | grep -c '\.zip$'); n=$(printf '%03d' $((n+1)))
f="backups/${n}_$(date +%Y-%m-%d_%H%M).zip"
zip -qr "$f" extraction speculation programme pages_txt scripts semainier liste_pages.csv liste_pages.txt LISEZMOI.md 2>/dev/null
echo "sauvegarde : $f ($(du -h "$f" | cut -f1))"
