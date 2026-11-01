#!/bin/sh
# vue resserrée : cal.py sans les rubriques anciens élèves / visiteurs / comptes rendus
python3 "$(dirname "$0")/cal.py" "$@" | grep -v ' writes' | awk '/^#####/{s=0; print; next} /^== (WITH FORMER|WITH THE 19|ROSTER|VISITORS|EXPECTED|ARRIVALS|DEPARTURES|ADDRESSES|NEW ADDRESSES|ALUMNI|GUESTS)/{s=1;next} /^==/{s=0} !s'
