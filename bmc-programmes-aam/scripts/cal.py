"""Vue resserrée d'une fiche : rubriques CALENDAR / SCHEDULE en entier, ailleurs seulement les
paragraphes porteurs d'un jour, d'une heure ou d'une date (tronqués). cal.py ACC [ACC...] [--n 400]"""
import sys, re, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voir  # noqa  (charge D)
N = 400
args = [a for a in sys.argv[1:]]
if "--n" in args:
    i = args.index("--n"); N = int(args[i + 1]); del args[i:i + 2]
TEMPS = re.compile(r"(?i)\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday|tonight|this (evening|afternoon|morning)|tomorrow|o.clock|\d{1,2}[:.]\d{2}|a\.?m\.|p\.?m\.|january|february|march|april|may|june|july|august|september|october|november|december|quarter|semester|term|vacation|class(es)?|course|schedule|period)\b")
for acc in args:
    f = voir.D[acc]
    print(f"##### {acc} | {f['title'][:110]}")
    full = False; suite = 0
    for l in f["description"].splitlines():
        l = l.strip()
        if not l: continue
        if suite > 0:
            print("    > " + l[:N]); suite -= 1; continue
        if re.match(r"^[A-Z][A-Z0-9 .’',:()&/-]{4,}$", l):
            full = bool(re.search(r"CALENDAR|SCHEDULE|PROGRAM|COURSES|CLASSES|TIMETABLE|DAILY|FUTURE|NEXT WEEK|DATES|REGULAR MEETINGS", l))
            print("== " + l); continue
        if full: print(l[:N * 2])
        elif TEMPS.search(l):
            print("  · " + l[:N])
            if len(l) < 70: suite = 3
