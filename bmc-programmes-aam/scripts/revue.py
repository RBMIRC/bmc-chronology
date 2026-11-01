"""Affiche, document par document (ordre chronologique), les phrases datées « à vérifier » de l'audit des événements,
avec la date de référence (#ref) et les entrées déjà extraites. Usage : revue.py [n_documents] [à_partir_de_inventaire]"""
import csv, os, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
r = list(csv.DictReader(open(os.path.join(ROOT, "programme", "audit", "evenements_candidats.csv"), encoding="utf-8")))
par = collections.defaultdict(list)
for x in r:
    if x["statut"] == "à vérifier": par[x["inventaire"]].append(x)
def ref(inv):
    f = os.path.join(ROOT, "extraction", inv + ".txt")
    if not os.path.exists(f): return "????"
    for l in open(f, encoding="utf-8"):
        if l.startswith("#ref"): return l.split()[1]
    return "????"
ordre = sorted(par, key=lambda i: (ref(i), i))
n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
if len(sys.argv) > 2: ordre = ordre[ordre.index(sys.argv[2]):] if sys.argv[2] in ordre else ordre
print(f"{len(ordre)} documents restent à relire")
for inv in ordre[:n]:
    print(f"\n######## {inv}  #ref {ref(inv)}  ({len(par[inv])} phrases)")
    for x in par[inv]:
        print(f"  - [{x['reperes']}] {x['phrase'][:420]}")
    f = os.path.join(ROOT, "extraction", inv + ".txt")
    if os.path.exists(f):
        ex = [l.rstrip() for l in open(f, encoding="utf-8") if l[:2] in ("E|", "T|")]
        print(f"  déjà extrait ({len(ex)}) : " + " ¦ ".join(l[2:95] for l in ex))
