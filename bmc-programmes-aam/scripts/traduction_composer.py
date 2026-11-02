"""Notes composées « préfixe Recoupement — Duberman : D « titre tronqué » Scénario, mêmes pages : ID « titre tronqué » ; … ».
  composer.py besoins LOT…      → préfixes et titres du scénario à traduire (absents de pieces_en.tsv)
  composer.py ecrire LOT        → id<TAB>anglais pour les notes composées du lot (titres complets, tirés de revu_en.tsv et pieces_en.tsv)"""
import csv, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); SC = os.path.join(ROOT, "semainier", "i18n")
def charge(n):
    s = open(f"{ROOT}/semainier/{n}", encoding="utf-8").read(); return json.loads(s[s.index("{"): s.rstrip().rstrip(";").rindex("}") + 1])
S = charge("data_scenario.js"); TIT = {e["id"][1:]: e["title"] for e in S["grille"] + S["panneau"]}
D = charge("data.js"); DUB = [e["title"] for e in D["duberman"] + D["duberman_panneau"]]
REVU = {}
for l in open(f"{ROOT}/semainier/i18n/revu_en.tsv", encoding="utf-8"):
    if "\t" in l and not l.startswith("#"): a, b = l.rstrip("\n").split("\t", 1); REVU[a] = b
P = {}
if os.path.exists(f"{SC}/pieces_en.tsv"):
    for l in open(f"{SC}/pieces_en.tsv", encoding="utf-8"):
        if "\t" in l: a, b = l.rstrip("\n").split("\t", 1); P[a] = b
RX = re.compile(r"^(.*?)\s*(?:(Recoupement — Duberman : (\S+) « (.*?) »)\s*)?(?:(Scénario, mêmes pages : .*))?$")
def decoupe(t):
    m = RX.match(t); pre, rec, dd, dt, sc = m.groups()
    scen = [(i, TIT.get(i, x)) for i, x in re.findall(r"((?:EV|SC)-\d+) « (.*?) »(?= ;|$)", sc or "")]
    dub = None
    if rec:
        c = [x for x in DUB if x.startswith(dt.rstrip())]
        dub = c[0] if c else dt
    return pre, dd, dub, scen
def lot(n): return [r for r in csv.reader(open(f"{ROOT}/semainier/i18n/lots/lot_{n}.tsv", encoding="utf-8"), delimiter="\t") if len(r) == 4 and r[0] != "id"]
def compose(t):
    pre, dd, dub, scen = decoupe(t)
    if not (dub or scen): return None
    out = []
    if pre: out.append(P[pre] if pre in P else None)
    if dub: out.append(f"Cross-check — Duberman: {dd} “{REVU.get(dub) or P.get(dub)}”")
    if scen: out.append("Scenario, same pages: " + "; ".join(f"{i} “{P.get(x)}”" for i, x in scen))
    s = " ".join(x or "§" for x in out)
    return None if "§" in s or "“None”" in s else s
if sys.argv[1] == "besoins":
    vus = set()
    for n in sys.argv[2:]:
        for i, _, _, t in lot(n):
            pre, dd, dub, scen = decoupe(t)
            if not (dub or scen): continue
            for x in ([pre] if pre else []) + [x for _, x in scen] + ([dub] if dub and dub not in REVU else []):
                if x not in P and x not in vus: vus.add(x); print(x)
else:
    for i, _, _, t in lot(sys.argv[2]):
        e = compose(t)
        if e: print(f"{i}\t{e}")
