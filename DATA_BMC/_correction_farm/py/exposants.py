"""Repère dans l'image les appels de note (chiffres en exposant), y compris ceux que l'OCR a omis :
composantes connexes « flottantes » (bas au-dessus de la ligne de base, hauteur de chiffre), groupées.
Écrit /tmp/farm/out/encre.json : clé "page|ligne|mot" (mot après lequel se trouve l'exposant)."""
import json, re, statistics as st, cv2, numpy as np

P = json.load(open('/tmp/farm/pages.json'))
res = {}
for p in P:
    n = p['n']
    if not (4 <= int(n) <= 168): continue
    im = cv2.imread(f'/tmp/farm/hd/pre/{n}.png', 0)
    if im is None: continue
    for li, e in enumerate(p['el']):
        if e['cls'] not in ('corps', 'grand', 'corps?', 'legende'): continue
        ws = e['ws']
        x0, x1 = e['x0'] - 5, e['x1'] + 70
        y0 = int(min(w[2] for w in ws) - 15)
        y1 = int(max(w[2] + w[4] for w in ws) + 10)
        x0, y0 = max(0, x0), max(0, y0)
        crop = (im[y0:y1, x0:x1] < 150).astype(np.uint8)
        if crop.shape[0] < 10 or crop.shape[1] < 10: continue
        nb, lab, stats, cent = cv2.connectedComponentsWithStats(crop, 8)
        comps = [stats[k] for k in range(1, nb) if stats[k][4] >= 12]
        if len(comps) < 8: continue
        # ligne de base inclinée : régression robuste du bas des composantes de taille « lettre »
        pts = np.array([(c[0] + c[2] / 2, c[1] + c[3], c[3]) for c in comps if 16 <= c[3] <= 60 and c[2] >= 6])
        if len(pts) < 8: continue
        a, b = 0.0, np.median(pts[:, 1])
        for _ in range(4):
            r = pts[:, 1] - (a * pts[:, 0] + b)
            ok = np.abs(r) <= max(3, np.percentile(np.abs(r), 50))
            if ok.sum() < 5: break
            a, b = np.polyfit(pts[ok, 0], pts[ok, 1], 1)
            if abs(a) > 0.02 or ok.sum() < 6:
                a, b = 0.0, float(np.median(pts[ok, 1]))
        B = lambda x: a * x + b
        hs = sorted(c[3] for c in comps if abs(c[1] + c[3] - B(c[0] + c[2] / 2)) <= 4)
        if len(hs) < 5: continue
        xh = hs[int(len(hs) * 0.35)]
        flott = []
        for cx, cy, cw, chh, area in comps:
            bottom = cy + chh; Bx = B(cx + cw / 2)
            if Bx - 0.95 * xh < bottom < Bx - 0.25 * xh and 0.6 * xh <= chh <= 1.2 * xh and cw <= 0.9 * xh and cy < Bx - xh:
                flott.append((x0 + cx, x0 + cx + cw, y0 + cy, y0 + bottom))
        flott.sort()
        groupes = []
        for f in flott:
            if groupes and f[0] - groupes[-1][1] < 10:
                g = groupes[-1]; groupes[-1] = (g[0], max(g[1], f[1]), min(g[2], f[2]), max(g[3], f[3]))
            else:
                groupes.append(f)
        for g in groupes:
            # mot qui précède (dont le début est avant la tache)
            wi = max([i for i, w in enumerate(ws) if w[1] <= g[0]], default=None)
            if wi is None: continue
            res[f"{n}|{li}|{wi}"] = {"x": int(g[0]), "y": int(g[2]), "w": int(g[1] - g[0]), "h": int(g[3] - g[2]), "mot": ws[wi][0]}
json.dump(res, open('/tmp/farm/out/encre.json', 'w'), indent=0)
print(len(res), "exposants repérés dans l'image")
