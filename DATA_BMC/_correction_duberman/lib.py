import pickle, re, collections, sys
sys.path.insert(0, '/tmp/dub')
from wordfreq import zipf_frequency
from norm import *
SUP = str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹')
mid = collections.Counter()
def feed(lines):
    for t in lines:
        for w in t.split()[:-1]:
            mid[re.sub(r'^[^\w]+|[^\w]+$', '', re.sub(r'⟦\d+⟧', '', w)).lower()] += 1
def decide(a, b):
    j = (a + b).lower(); h = (a + '-' + b).lower()
    if mid[h] > mid[j]: return True
    if mid[j] > 0: return False
    if zipf_frequency(j, 'en') > 1.5: return False
    if zipf_frequency(a, 'en') >= 3 and zipf_frequency(b, 'en') >= 3: return True
    if a[:1].isupper() and b[:1].isupper(): return True
    return False
HY = []
def join(lines, sep=' '):
    lines = [x for x in lines if x.strip()]
    if not lines: return ''
    text = lines[0].strip()
    for nxt in lines[1:]:
        nxt = nxt.strip()
        m = re.search(r'([A-Za-zÀ-ÿ]+)-$', text); n = re.match(r'([A-Za-zÀ-ÿ]+)', nxt)
        if m and n:
            keep = decide(m.group(1), n.group(1)); HY.append((m.group(1), n.group(1), keep))
            text = (text if keep else text[:-1]) + nxt
        elif re.search(r'\d[-–—]$', text) and re.match(r'\d', nxt):
            text = text[:-1] + '–' + nxt          # number range broken across lines
        elif re.search(r'[—–]$', text) or re.match(r'^[—–]', nxt):
            text = text + nxt
        else:
            text = text + sep + nxt
    return text
KNOWN = {'ZEUCH','DUBERMAN','ALBERS','RICE','WEINRIB','DREIER','KNICKERBOCKER','MANGOLD','WUNSCH','KING','FRENCH','PORTELL','HARRINGTON',
         'JEANNE','CUNNINGHAM','EVARTS','BARBARA','SCHAWINSKY','HOWARD','RUMAKER','GAIR','WESTON','STEINAU','MORT','MARTIN','MOELLENHOFF',
         'GEORGIA','FAHY','GOLDENSON','CAGE','LITZ','STRAUS'}
def clean(t, speakers=True):
    for a, b in LINEFIX: t = t.replace(a, b)
    t = norm_quotes(t)
    t = fix_words(t)
    t = norm_ellipsis(t)
    t = norm_space(t)
    if speakers: t = norm_speakers(t, KNOWN)
    t = re.sub(r'⟦(\d+)⟧', lambda m: m.group(1).translate(SUP), t)
    return t.strip()
