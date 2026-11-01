"""Ré-OCR des zones de légende (psm 6) en remontant de deux lignes : récupère les premières lignes collées
à la photo que tesseract a manquées. Écrit /tmp/farm/out/legendes_plus.json : "page|y0 de la 1re ligne" → lignes ajoutées."""
import json, csv, subprocess, os, cv2, re, collections
P = json.load(open('/tmp/farm/pages.json'))
os.makedirs('/tmp/farm/leg', exist_ok=True)
res = {}
for p in P[4:169]:
    n = p['n']
    els = [e for e in p['el'] if e['cls'] == 'legende']
    if not els: continue
    # groupes de lignes de légende contiguës
    G, g = [], []
    for e in sorted(els, key=lambda e: e['y0']):
        if g and e['y0'] - g[-1]['y1'] > 40: G.append(g); g = []
        g.append(e)
    if g: G.append(g)
    im = cv2.imread(f'/tmp/farm/hd/pre/{n}.png', 0)
    for k, g in enumerate(G):
        x0 = min(e['x0'] for e in g) - 15; x1 = max(e['x1'] for e in g) + 40
        y0 = g[0]['y0'] - 95; y1 = g[0]['y0'] - 2
        if y0 < 0: continue
        f = f'{n}_{k}.png'
        cv2.imwrite('/tmp/farm/leg/' + f, im[y0:y1, max(0, x0):x1])
        subprocess.run(['tesseract', f, f[:-4], '--psm', '6', 'tsv'], capture_output=True, cwd='/tmp/farm/leg')
        L = collections.OrderedDict()
        for r in csv.DictReader(open('/tmp/farm/leg/' + f[:-4] + '.tsv'), delimiter='\t', quoting=csv.QUOTE_NONE):
            if r['level'] == '5' and (r['text'] or '').strip():
                L.setdefault((r['block_num'], r['par_num'], r['line_num']), []).append((r['text'], float(r['conf']), int(r['top'])))
        plus = []
        for ws in L.values():
            t = ' '.join(w[0] for w in ws)
            conf = sum(w[1] for w in ws) / len(ws)
            alpha = sum(ch.isalpha() for ch in t) / max(1, len(t))
            if conf > 75 and alpha > 0.6 and len(t) > 15 and ws[0][2] > 25:
                plus.append(t)
        if plus:
            res[f"{n}|{g[0]['y0']}"] = plus
json.dump(res, open('/tmp/farm/out/legendes_plus.json', 'w'), ensure_ascii=False, indent=0)
for k, v in res.items(): print(k, v)
