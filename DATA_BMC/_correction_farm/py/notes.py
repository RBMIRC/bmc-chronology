"""Notes de fin (pages PDF 170-187, p. 207-224), d'après l'OCR par colonne (colocr.py).
Numérotation continue sur tout le livre (1-263). Les débuts de note sont repérés par le numéro lu, par
l'encre dans la marge des numéros, et calés sur les numéros lus de façon sûre (ancres)."""
import re, json, csv, collections
import cv2
from assemble import fusion

pm = json.load(open('/tmp/farm/pagemap.json'))
RX_NUM = re.compile(r"^([0-9OIlTi!|SBo]{1,3}|Tis)[.,:;]$")


def lignes_col(n, side):
    L = collections.OrderedDict()
    for r in csv.DictReader(open(f'/tmp/farm/hd/col/{n}_{side}.tsv'), delimiter='\t', quoting=csv.QUOTE_NONE):
        if r['level'] == '5' and (r['text'] or '').strip():
            L.setdefault((int(r['block_num']), int(r['par_num']), int(r['line_num'])), []).append(
                dict(t=r['text'], x=int(r['left']), y=int(r['top']), h=int(r['height']), c=float(r['conf'])))
    return sorted([{'x0': ws[0]['x'], 'y': min(w['y'] for w in ws), 'h': max(w['h'] for w in ws), 'ws': ws,
                    'text': ' '.join(w['t'] for w in ws)} for ws in L.values()], key=lambda l: l['y'])


def lire_num(tok):
    m = RX_NUM.match(tok)
    if not m: return None
    d = m.group(1)
    for a, b in (('O', '0'), ('o', '0'), ('I', '1'), ('l', '1'), ('i', '1'), ('!', '1'), ('|', '1'), ('T', '1'), ('S', '5'), ('B', '8')):
        d = d.replace(a, b)
    return int(d) if d.isdigit() else None


def main():
    tout = []  # toutes les lignes, dans l'ordre de lecture
    for i in range(170, 188):
        n = f"{i:03d}"
        for side in (0, 1):
            L = lignes_col(n, side)
            L = [l for l in L if not re.search(r"Farm at Bl|^\W*Endnotes\W*\d*\W*$|^\W*ENDNOTES\W*$|^\W*\d{3}\W*$|^\W*Appendix", l['text'])]
            L = [l for l in L if re.search(r"[A-Za-z0-9]{2}", l['text'])]
            if not L: continue
            img = cv2.imread(f'/tmp/farm/hd/col/{n}_{side}.png', 0)
            xs = sorted(l['x0'] for l in L)
            xcont = xs[len(xs) * 3 // 4]
            for l in L:
                zone = img[max(0, l['y'] + 3):l['y'] + max(20, l['h'] - 3), max(0, xcont - 170):max(1, xcont - 20)]
                l['encre'] = int((zone < 120).sum())
                l['decal'] = xcont - l['x0']
                l['page'] = pm.get(n)
                l['src'] = f"{n}_{side}"
                tout.append(l)
    # chapitres
    for j, l in enumerate(tout):
        m = re.match(r"^\W*Chapter\s*(\d+)\W*$", l['text'].strip())
        l['chapitre'] = int(m.group(1)) if m else None
    titres = {}
    for j, l in enumerate(tout):
        if l['chapitre']:
            t = []
            k = j - 1
            while k >= 0 and len(tout[k]['text']) < 45 and not lire_num(tout[k]['ws'][0]['t']) and not tout[k]['text'].rstrip().endswith(('.', ',', ';')) and len(t) < 2:
                t.insert(0, tout[k]['text']); tout[k]['titre'] = True; k -= 1
            titres[l['chapitre']] = " ".join(t)
    # candidats début de note
    for l in tout:
        l['lu'] = lire_num(l['ws'][0]['t'])
        l['debut'] = not l.get('titre') and not l['chapitre'] and (l['lu'] is not None or l['decal'] > 60 or l['encre'] > 80)
    # ancres : numéros lus formant une suite croissante plausible (plus longue sous-suite croissante)
    lus = [(j, l['lu']) for j, l in enumerate(tout) if l['debut'] and l['lu']]
    best = []
    import bisect
    # LIS sur les valeurs, avec contrainte j croissant (déjà ordonné)
    pile, prev, idx = [], {}, []
    for k, (j, v) in enumerate(lus):
        pos = bisect.bisect_left([lus[x][1] for x in idx], v)
        if pos == len(idx): idx.append(k)
        else: idx[pos] = k
        prev[k] = idx[pos - 1] if pos > 0 else None
    k = idx[-1] if idx else None
    while k is not None:
        best.append(lus[k]); k = prev[k]
    ancres = dict(best[::-1])  # j → numéro
    # entre deux ancres, il faut exactement (b - a - 1) débuts ; on ajoute/retire selon l'encre
    js = sorted(ancres)
    bornes = [(-1, 0)] + [(j, ancres[j]) for j in js] + [(len(tout), 264)]
    for (ja, va), (jb, vb) in zip(bornes, bornes[1:]):
        seg = [j for j in range(ja + 1, jb) if not tout[j].get('titre') and not tout[j]['chapitre']]
        besoin = vb - va - 1
        cands = sorted(seg, key=lambda j: (tout[j]['debut'], tout[j]['encre'] + 10 * tout[j]['decal']
                                           + (300 if j > 0 and tout[j - 1]['text'].rstrip().endswith('.') else 0)), reverse=True)
        choix = set(cands[:max(0, besoin)])
        for j in seg:
            tout[j]['debut'] = j in choix
        if len([j for j in seg if tout[j]['debut']]) != besoin:
            print("segment incomplet", va, vb, len(seg))
    for j, v in ancres.items():
        tout[j]['debut'] = True
    # construction
    notes, chap, num = [], 0, 0
    for l in tout:
        if l['chapitre']:
            chap = l['chapitre']; continue
        if l.get('titre'): continue
        if l['debut']:
            num += 1
            corps = " ".join(w['t'] for w in l['ws'][1:]) if l['lu'] is not None or RX_NUM.match(l['ws'][0]['t']) else l['text']
            notes.append({'n': num, 'lu': l['lu'], 'chap': chap, 'x': corps.strip(), 'p': l['page'], 'src': l['src']})
        elif notes:
            a = notes[-1]['x']
            notes[-1]['x'] = fusion(a, l['text']) if a.endswith('-') else a + ' ' + l['text']
    json.dump({'chapitres': titres, 'notes': notes}, open('/tmp/farm/out/notes.json', 'w'), ensure_ascii=False, indent=0)
    print(len(notes), 'notes ;', dict(collections.Counter(x['chap'] for x in notes)))
    print('titres', titres)
    print('lus ≠ rang :', [(x['n'], x['lu']) for x in notes if x['lu'] and x['lu'] != x['n']])


if __name__ == '__main__':
    main()
