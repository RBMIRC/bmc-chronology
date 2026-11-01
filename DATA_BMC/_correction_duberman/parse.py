import re, json, html
src = open('bbox.html', encoding='utf-8').read()
pages = []
for pm in re.finditer(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', src, re.S):
    W, H, body = float(pm.group(1)), float(pm.group(2)), pm.group(3)
    lines = []
    for bm, blk in enumerate(re.findall(r'<block[^>]*>(.*?)</block>', body, re.S)):
        for lm in re.finditer(r'<line xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</line>', blk, re.S):
            words = [(float(a), float(b), float(c), float(d), html.unescape(t)) for a, b, c, d, t in
                     re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', lm.group(5))]
            if not words: continue
            lines.append(dict(x0=float(lm.group(1)), y0=float(lm.group(2)), x1=float(lm.group(3)), y1=float(lm.group(4)),
                              blk=bm, text=' '.join(w[4] for w in words), words=words))
    lines.sort(key=lambda l: (l['y0']+l['y1'])/2)
    pages.append(dict(W=W, H=H, lines=lines))
json.dump(pages, open('pages.json', 'w'))
print(len(pages))
