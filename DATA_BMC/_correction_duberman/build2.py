import pickle, re, statistics
Q = pickle.load(open('/tmp/dub/annotated_fixed.pkl','rb'))
FM = pickle.load(open('/tmp/dub/fontm.pkl','rb'))
CHAPTERS = {21:(1,'The Rollins Fracas'),31:(2,'A Beginning'),61:(3,'Anni and Josef Albers'),84:(4,'The Thirties'),
            134:(5,'Schism'),173:(6,'A New Home'),192:(7,'The Split'),240:(8,'Aftermaths and Continuities'),
            261:(9,'New Definitions of Community'),309:(10,'Entries and Exits'),360:(11,'Transition'),
            380:(12,'A New Black Mountain'),425:(13,'Olson'),444:(14,'Expelled and Imploding')}
SPECIAL = {11:'INTRODUCTION', 17:'PREFACE', 477:'ACKNOWLEDGMENTS'}
PHOTO = set(range(217,225)) | set(range(393,401))
BODY = list(range(11,16)) + list(range(17,20)) + [i for i in range(21,477) if i not in PHOTO] + list(range(477,480))
SMALL = 32.8
VERSE = {380:range(5,9), 425:range(2,13), 433:range(16,24), 443:range(32,34), 452:range(4,9), 454:range(19,27), 456:range(35,39), 457:range(1,5)}

def page_lines(pi):
    L = Q[pi]['lines']; fm = FM.get(pi, [None]*len(L))
    start = 1; head = None
    if pi in CHAPTERS or pi in SPECIAL:
        start = 0
        while start < len(L):
            t = L[start]['text']; letters = [c for c in t if c.isalpha()]
            up = sum(c.isupper() for c in letters) / max(1, len(letters))
            if up < 0.7 and L[start]['h'] < 30: break
            start += 1
        head = CHAPTERS.get(pi) or SPECIAL.get(pi)
    lines = []
    for idx, (l, m) in list(enumerate(zip(L, fm)))[start:]:
        d = dict(l); d['s'] = (m[0] + m[1]) if (m and m[2] >= 12) else None
        ws = l.get('words') or []
        k0 = 0
        while k0 < len(ws) - 1 and not re.search(r'[A-Za-z0-9“‘"(\[—.…*]', ws[k0][4]): k0 += 1
        if k0:
            d['x0'] = ws[k0][0]
            d['text'] = ' '.join(w[4] for w in ws[k0:])
        d['verse'] = idx in VERSE.get(pi, ())
        if re.match(r'^[.,](?: [.,])?\s+(?=[\w“‘\[(])', d['text']) and not d['text'].startswith('. . .'):
            d['text'] = re.sub(r'^[.,](?: [.,])?\s+', '. . . ', d['text'])
        lines.append(d)
    return head, lines

def margins(pi, lines):
    xs = sorted(l['x0'] for l in lines)
    left = statistics.median(xs[:max(1, len(xs)//2)]) if len(lines) >= 6 else min(xs)
    x1s = sorted(l['x1'] for l in lines)
    right = statistics.median(x1s[len(x1s)//2:]) if len(lines) >= 4 else max(x1s)
    return left, right

# global margins per page parity to stabilise short pages
glob = {}
for pi in BODY:
    _, ls = page_lines(pi)
    if len(ls) >= 25: glob[pi] = margins(pi, ls)
def page_margins(pi, lines):
    x1s = sorted(l['x1'] for l in lines)
    if len(x1s) >= 5:
        right = x1s[int(0.75 * (len(x1s) - 1))]
        # refine: median of lines within 25px of that value
        near = [x for x in x1s if abs(x - right) < 25]
        right = statistics.median(near)
        xs = sorted(l['x0'] for l in lines)
        left = statistics.median(xs[:max(1, len(xs)//2)])
        if left - (right - 735) > 8 or len(lines) < 12: left = right - 735
        return left, right
    near = [glob[p] for p in sorted(glob, key=lambda p: abs(p - pi))][:1]
    return near[0] if near else margins(pi, lines)

def classify(pi, lines):
    left, right = page_margins(pi, lines)
    # footnotes (asterisk) at bottom
    fn = None
    for i, l in enumerate(lines):
        if i > 0 and re.match(r'^\*\s*[A-Z]', l['text']) and l['y0'] > 0.55 * Q[pi]['H'] and l['s'] is not None and l['s'] < 32.3:
            fn = i; break
    foot = lines[fn:] if fn is not None else []
    lines = lines[:fn] if fn is not None else lines
    gaps = [b['y0'] - a['y0'] for a, b in zip(lines, lines[1:])]
    mg = statistics.median(gaps) if gaps else 30.0
    for i, l in enumerate(lines):
        l['d'] = l['x0'] - left
        l['short'] = l['x1'] < right - 18
        l['gap'] = (l['y0'] - lines[i-1]['y0']) if i > 0 else None
        l['ind'] = l['d'] >= 12
    # runs of indented lines
    i = 0
    while i < len(lines):
        if not lines[i]['ind']:
            lines[i]['kind'] = 'body'; i += 1; continue
        j = i
        while j < len(lines) and lines[j]['ind']: j += 1
        run = lines[i:j]
        ss = [l['s'] for l in run if l['s'] is not None]
        ms = statistics.mean(ss) if ss else None
        if len(run) == 1:
            l = run[0]
            small = (ms is not None and ms < SMALL)
            spaced = (l['gap'] or 0) > 1.25 * mg
            nxt_spaced = j < len(lines) and (lines[j]['gap'] or 0) > 1.25 * mg
            kind = 'block' if (small and (spaced or nxt_spaced or ms < 31.8)) or (spaced and nxt_spaced and l['d'] > 40) else 'body'
        else:
            kind = 'block' if (ms is not None and ms < SMALL + 0.4) else 'body'
        for l in run: l['kind'] = kind
        if len(run) >= 2:
            sv = [l['s'] if l['s'] is not None else ms for l in run]
            cls = [None if v is None else v < SMALL for v in sv]
            for k in range(1, len(run) - 1):
                if cls[k-1] is not None and cls[k-1] == cls[k+1] and cls[k] != cls[k-1] and not run[k-1]['short']:
                    cls[k] = cls[k-1]
            if cls[0] is not None and cls[1] is not None and cls[0] != cls[1] and not run[0]['short']:
                cls[0] = cls[1]
            if cls[-1] is not None and cls[-2] is not None and cls[-1] != cls[-2] and not run[-2]['short']:
                cls[-1] = cls[-2]
            for k in range(len(run)):
                if cls[k] is not None:
                    run[k]['kind'] = 'block' if cls[k] else 'body'
        i = j
    # block zones: maximal consecutive block lines; determine mode
    i = 0
    while i < len(lines):
        if lines[i]['kind'] != 'block': i += 1; continue
        j = i
        while j < len(lines) and lines[j]['kind'] == 'block': j += 1
        zone = lines[i:j]
        E = min(l['d'] for l in zone)
        for l in zone: l['bd'] = l['d'] - E
        nlow = sum(l['bd'] < 12 for l in zone); nhigh = len(zone) - nlow
        nshort = sum(l['short'] for l in zone)
        verse = False
        mode = 'verse' if verse else ('hang' if nhigh > nlow and nlow >= 1 else 'normal')
        if len(zone) >= 3:
            zx1 = sorted(l['x1'] for l in zone)
            zr = zx1[int(0.7 * (len(zx1) - 1))]
            nearr = [x for x in zx1 if abs(x - zr) < 12]
            if zr < right - 18 and len(nearr) >= 0.5 * len(zone):
                for l in zone: l['short'] = l['x1'] < zr - 18
        for l in zone: l['mode'] = mode
        i = j
    for l in lines:
        if l['verse']: l['kind'] = 'block'; l['mode'] = 'verse'; l.setdefault('bd', 0)
    big = [ (l['gap'] or 0) > 2.2 * mg for l in lines]
    for l, b in zip(lines, big): l['bigbreak'] = b
    return lines, foot, left, right, mg

KNOWN = {'ZEUCH','DUBERMAN','ALBERS','RICE','WEINRIB','DREIER','KNICKERBOCKER','MANGOLD','WUNSCH','KING','FRENCH','PORTELL','HARRINGTON',
         'JEANNE','CUNNINGHAM','EVARTS','BARBARA','SCHAWINSKY','HOWARD','RUMAKER','GAIR','WESTON','STEINAU','MORT','MARTIN','MOELLENHOFF',
         'GEORGIA','FAHY','GOLDENSON','CAGE','LITZ','LIRZ','STRAUS','WONSCU','WOUNSCH','WUNSCX','ZEUCN','GEORCIA','FAUY','EYARTS','MRS'}
def is_speaker(t):
    m = re.match(r'^([A-Za-z]{3,})(?:\.? [A-Za-z]+){0,2}(?: \[[a-z ]+\])?\s?:', t)
    if not m: return False
    w = m.group(1)
    return w.upper() in KNOWN or sum(c.isupper() for c in w) >= len(w) - 1
blocks = []; cur = None; pending_foot = []
def flush():
    global cur
    if cur and cur['lines']:
        blocks.append(cur)
    cur = None
    if pending_foot:
        for f in pending_foot: blocks.append(dict(type='fn', lines=f))
        pending_foot.clear()
def newpara(kind, pi, mode=None):
    global cur
    flush()
    cur = dict(type='bq' if kind == 'block' else 'p', lines=[], xs=[], ys=[], page=pi, mode=mode)

prev = None
for pi in BODY:
    head, lines = page_lines(pi)
    if head:
        flush()
        if isinstance(head, tuple): blocks.append(dict(type='chapter', num=head[0], title=head[1], page=pi))
        else: blocks.append(dict(type='section', title=head, page=pi))
        prev = None
    if not lines: continue
    lines, foot, left, right, mg = classify(pi, lines)
    for k, l in enumerate(lines):
        kind = l['kind']
        hy = prev is not None and re.search(r'[A-Za-z]-$', prev['text'].rstrip()) is not None
        allcaps = lambda t: sum(c.isupper() for c in t) > 0.8 * max(1, sum(c.isalpha() for c in t))
        if l['verse']:
            start = prev is None or not prev.get('verse')
        elif prev is not None and prev.get('verse'):
            start = True
        elif prev is not None and kind == prev['kind'] and allcaps(l['text']) and allcaps(prev['text']) and not re.search(r'[.:]$', prev['text']) and len(l['text']) > 3:
            start = False
        elif prev is None:
            start = True
        elif l['bigbreak'] and k > 0:
            flush(); blocks.append(dict(type='break', page=pi)); start = True
        elif kind != prev['kind']:
            if k == 0 and kind == 'body' and not l['ind'] and not prev['short']:
                start = False
            elif k == 0 and kind == 'block' and prev['kind'] == 'block':
                start = False
            else:
                start = True
            if k == 0 and prev['kind'] == 'block' and kind == 'body' and not l['ind'] and not prev['short']:
                kind = 'block'   # extract continues at top of page, mis-measured
        elif kind == 'body':
            start = (l['ind'] or prev['short']) and not hy
        else:
            mode = l.get('mode')
            if mode == 'verse':
                start = (l['gap'] or 0) > 1.35 * mg if k > 0 else prev['short'] and l['bd'] >= 12
            else:
                start = (prev['short'] and not hy) or (l['bd'] < 12 and (is_speaker(l['text']) or (allcaps(l['text']) and not allcaps(prev['text']))))
        if start or cur is None:
            newpara(kind, pi, l.get('mode'))
        if l['verse']: cur['mode'] = 'verse'
        cur['lines'].append(l['text']); cur['xs'].append(l['x0']); cur['ys'].append(l['y0'])
        l['kind'] = kind
        prev = l
    if foot:
        fl = []
        for f in foot:
            if re.match(r'^\*', f['text']) and fl: pending_foot.append(fl); fl = []
            fl.append(f['text'])
        if fl: pending_foot.append(fl)
flush()
pickle.dump(blocks, open('/tmp/dub/blocks_raw.pkl', 'wb'))
import collections
print(collections.Counter(b['type'] for b in blocks), collections.Counter(b.get('mode') for b in blocks if b['type']=='bq'))
