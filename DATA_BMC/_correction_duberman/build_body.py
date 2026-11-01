import pickle, re, statistics
Q = pickle.load(open('/tmp/dub/annotated_fixed.pkl','rb'))
S = 1.1111
CHAPTERS = {21:(1,'The Rollins Fracas'),31:(2,'A Beginning'),61:(3,'Anni and Josef Albers'),84:(4,'The Thirties'),
            134:(5,'Schism'),173:(6,'A New Home'),192:(7,'The Split'),240:(8,'Aftermaths and Continuities'),
            261:(9,'New Definitions of Community'),309:(10,'Entries and Exits'),360:(11,'Transition'),
            380:(12,'A New Black Mountain'),425:(13,'Olson'),444:(14,'Expelled and Imploding')}
SPECIAL = {11:'INTRODUCTION', 17:'PREFACE', 477:'ACKNOWLEDGMENTS'}
PHOTO = set(range(217,225)) | set(range(393,401))
BODY = list(range(11,16)) + list(range(17,20)) + [i for i in range(21,477) if i not in PHOTO] + list(range(477,480))

def page_lines(pi):
    L = Q[pi]['lines']
    start = 1
    head = None
    if pi in CHAPTERS or pi in SPECIAL:
        # skip title lines: everything until first normal-height text line that is not uppercase
        start = 0
        while start < len(L):
            t = L[start]['text']; letters = [c for c in t if c.isalpha()]
            up = sum(c.isupper() for c in letters) / max(1, len(letters))
            if up < 0.7 and L[start]['h'] < 30: break
            start += 1
        head = CHAPTERS.get(pi) or SPECIAL.get(pi)
    lines = [dict(l) for l in L[start:]]
    return head, lines

def classify(pi, lines):
    """returns list of (line, kind) where kind in body/block and flags para/sec"""
    if not lines: return []
    xs = sorted(l['x0'] for l in lines)
    left = xs[len(xs)//10] if len(lines) >= 5 else xs[0]
    x1s = sorted(l['x1'] for l in lines)
    right = statistics.median(x1s[len(x1s)//2:])
    gaps = [b['y0'] - a['y0'] for a, b in zip(lines, lines[1:])]
    mg = statistics.median(gaps) if gaps else 30
    # footnote lines (asterisk notes at the bottom)
    fn_start = None
    for i, l in enumerate(lines):
        if i > 0 and re.match(r'^\*\s*\S', l['text']) and l['h'] <= 22 and l['y0'] > 0.6 * Q[pi]['H']:
            fn_start = i; break
    foot = lines[fn_start:] if fn_start is not None else []
    lines = lines[:fn_start] if fn_start is not None else lines
    # zones split by large gaps
    zones = [[0]]
    for i in range(1, len(lines)):
        g = lines[i]['y0'] - lines[i-1]['y0']
        if g > 1.25 * mg: zones.append([i])
        else: zones[-1].append(i)
    out = []
    for zi, z in enumerate(zones):
        ds = [lines[i]['x0'] - left for i in z]
        n_ind = sum(d >= 12 for d in ds)
        block = n_ind >= max(2, 0.7 * len(z)) or (len(z) == 1 and ds[0] >= 12 and lines[z[0]]['h'] <= 22.5 and lines[z[0]]['x1'] < right - 30 and False)
        gap_before = (lines[z[0]]['y0'] - lines[z[0]-1]['y0']) if z[0] > 0 else None
        for k, i in enumerate(z):
            l = lines[i]; d = l['x0'] - left
            l['d'] = d; l['short'] = l['x1'] < right - 28
            l['kind'] = 'block' if block else 'body'
            l['zone'] = zi
            l['gap'] = (l['y0'] - lines[i-1]['y0']) if i > 0 else None
            l['bigbreak'] = (k == 0 and gap_before is not None and gap_before > 2.0 * mg)
        if block:
            base = min(ds)
            for k, i in enumerate(z):
                l = lines[i]
                l['bd'] = l['d'] - base
        out.append(z)
    return lines, foot, left, right, mg

blocks = []   # list of dict(type, text)
cur = None    # current paragraph dict
pending_foot = []
def flush():
    global cur
    if cur and cur['lines']:
        blocks.append(cur)
        if pending_foot:
            for f in pending_foot: blocks.append(dict(type='fn', lines=f))
            pending_foot.clear()
    cur = None
def newpara(kind, pi):
    global cur
    flush()
    cur = dict(type='bq' if kind == 'block' else 'p', lines=[], page=pi)

prev_line = None
for pi in BODY:
    head, lines = page_lines(pi)
    if head:
        flush()
        if isinstance(head, tuple):
            blocks.append(dict(type='chapter', num=head[0], title=head[1], page=pi))
        else:
            blocks.append(dict(type='section', title=head, page=pi))
        prev_line = None
    res = classify(pi, lines)
    if not res: continue
    lines, foot, left, right, mg = res
    for k, l in enumerate(lines):
        t = l['text']
        start = False
        kind = l['kind']
        if prev_line is None:
            start = True
        elif l['bigbreak'] and prev_line['kind'] == 'body' and kind == 'body':
            flush(); blocks.append(dict(type='break', page=pi)); start = True
        elif kind != prev_line['kind'] and (k > 0 and l['gap'] is not None and l['gap'] > 1.2 * mg or k == 0 and (kind == 'block' and l.get('bd', 0) >= 12 or kind == 'body' and l['d'] >= 12 or prev_line['short'])):
            start = True
        elif kind != prev_line['kind'] and k > 0:
            start = True
        elif kind == 'body':
            start = l['d'] >= 12 or prev_line['short']
        else:
            pbd = prev_line.get('bd', 0)
            start = prev_line['short'] or (l.get('bd', 0) >= pbd + 12 and not prev_line.get('pstart_low'))
        if kind == 'body' and k == 0 and prev_line is not None and prev_line['kind'] == 'block' and l['d'] < 12 and not prev_line['short']:
            kind = 'block'  # block continues on new page (its lines appear at body margin)
        if start or cur is None:
            newpara(kind, pi)
            l['pstart_low'] = (kind == 'block' and k + 1 < len(lines) and lines[k+1].get('bd', 0) >= l.get('bd', 0) + 12)
        cur['lines'].append(t)
        prev_line = l
    if foot:
        fl = []
        for f in foot:
            if re.match(r'^\*', f['text']) and fl: pending_foot.append(fl); fl = []
            fl.append(f['text'])
        if fl: pending_foot.append(fl)
flush()
pickle.dump(blocks, open('/tmp/dub/blocks_raw.pkl', 'wb'))
print(len(blocks), sum(b['type']=='p' for b in blocks), sum(b['type']=='bq' for b in blocks), sum(b['type']=='break' for b in blocks), sum(b['type']=='fn' for b in blocks))
