import csv,sys
R=list(csv.DictReader(open('programme/evenements.csv')))
for d in sys.argv[1:]:
    print(d+':', ' ¦ '.join(f"{e['debut']} {e['type']} {e['activite'][:70]} [{e['inventaire']}]" for e in R if e['date']==d and e['type']!='cours' and 'Record playing' not in e['activite'] and 'Music Library' not in e['activite']))
