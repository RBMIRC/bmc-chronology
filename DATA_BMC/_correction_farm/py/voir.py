"""Planche des lignes contenant des expressions données : python voir.py "expr1" "expr2" ... → /tmp/farm/voir.png"""
import json, sys, cv2, numpy as np
P = json.load(open('/tmp/farm/pages.json'))
crops = []
for q in sys.argv[1:]:
    found = False
    for p in P:
        els = p['el']
        for i, e in enumerate(els):
            txt = e['text'] + ' ' + (els[i + 1]['text'] if i + 1 < len(els) else '')
            if q in txt:
                im = cv2.imread(f"/tmp/farm/hd/pre/{p['n']}.png", 0)
                y0 = max(0, e['y0'] - 12); y1 = e['y1'] + (60 if q not in e['text'] else 12)
                c = im[y0:y1, max(0, e['x0'] - 20):e['x1'] + 90]
                c = cv2.resize(c, (int(c.shape[1] * 0.75), int(c.shape[0] * 0.75)))
                lab = np.full((28, c.shape[1]), 255, np.uint8)
                cv2.putText(lab, f"{p['n']}: {q[:40]}", (4, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 0, 1)
                crops.append(np.vstack([lab, c])); found = True; break
        if found: break
    if not found: print("introuvable :", q)
W = max(c.shape[1] for c in crops)
out = np.vstack([np.hstack([c, np.full((c.shape[0], W - c.shape[1]), 255, np.uint8)]) for c in crops])
cv2.imwrite('/tmp/farm/voir.png', out)
