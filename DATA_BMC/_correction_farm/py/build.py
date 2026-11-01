"""Silver, The Farm at Black Mountain College : reconstruction du texte à partir de l'OCR HD (pages PDF 000-201).
Étape 1 : chaque page → éléments typés (en-tête, titre, corps, citation, légende) ; écrit /tmp/farm/pages.json."""
import re, json, statistics as st, sys
from hl import lines

TITRES = ["Foreword", "Introduction", "Before Black Mountain", "The Founding of the Farm", "Pigs and Place",
          "Moving to Lake Eden", "Barn Raising", "Molly Gregory Raises the Roof", "The Quakers",
          "No more of this community horseshit", "Collapse", "Endnotes", "Image Credits", "Index"]
RX_TETE = re.compile(r"(Farm at Bla|Black Mountain Col+eg|" + "|".join(re.escape(t[:12]) for t in TITRES) + ")", re.I)


def ah(l):
    hs = [w['h'] for w in l['ws'] if re.fullmatch(r'[a-z]*[bdfhklt][a-z]*[.,;:]?', w['t'])
          and not re.search('[gjpqy]', w['t']) and len(w['t']) >= 3]
    return st.median(hs) if hs else None


def bruit(l):
    t = l['text']
    lettres = len(re.sub(r'[^A-Za-z]', '', t))
    cs = sorted(w['c'] for w in l['ws'])
    med = cs[len(cs) // 2]
    return lettres < 2 or (l['alpha'] < 0.45 and max(cs) < 85) or med < 40


def rogne(l):
    """Retire les jetons parasites en début/fin de ligne (traits de photo, accolades…) et recalcule la boîte."""
    ws = l['ws']
    while len(ws) > 1 and not re.search(r"[A-Za-z0-9]", ws[0]['t']): ws = ws[1:]
    while len(ws) > 1 and not re.search(r"[A-Za-z0-9.,;:!?”’)\]]", ws[-1]['t']): ws = ws[:-1]
    l['ws'] = ws
    l['x0'] = min(w['x'] for w in ws); l['x1'] = max(w['x'] + w['w'] for w in ws)
    l['text'] = ' '.join(w['t'] for w in ws)
    return l


def page(n):
    L = [rogne(l) for l in lines(n) if not bruit(l)]
    L.sort(key=lambda l: (l['y0'], l['x0']))
    out = {"n": n, "num": None, "tete": None, "el": []}
    if not L: return out
    # en-tête courant : première ligne courte qui ressemble au titre courant
    t0 = L[0]
    if RX_TETE.search(t0['text']) and len(t0['text']) < 60 and (t0['xh'] is None or t0['xh'] < 27):
        m = re.findall(r'\b(\d{1,3})\b', t0['text'])
        out["num"] = int(m[-1]) if m else None
        out["tete"] = t0['text']
        L = L[1:]
    for l in L:
        l['ah'] = ah(l)
        if l['xh'] and l['xh'] <= 20.5 or (l['ah'] and l['ah'] <= 29.5):
            l['cls'] = 'legende'
        elif l['xh'] and l['xh'] >= 27.5 or (l['ah'] and l['ah'] >= 40):
            l['cls'] = 'grand'
        elif l['xh'] or l['ah']:
            l['cls'] = 'corps'
        else:
            l['cls'] = None
    # lignes sans mesure : on hérite du bloc tesseract, sinon du voisin
    par_bloc = {}
    for l in L:
        if l['cls']: par_bloc.setdefault(l['k'][0], []).append(l['cls'])
    for i, l in enumerate(L):
        if not l['cls']:
            b = par_bloc.get(l['k'][0])
            if b: l['cls'] = max(set(b), key=b.count)
            else:
                lettres = re.sub(r'[^A-Za-z]', '', l['text'])
                l['cls'] = 'titre' if lettres.isupper() and len(l['text']) < 50 else 'corps?'
    for l in L:
        lettres = re.sub(r'[^A-Za-z]', '', l['text'])
        if l['cls'] in ('corps', 'corps?') and lettres.isupper() and len(lettres) >= 4 and len(l['text']) < 50:
            l['cls'] = 'titre'
    corps = [l for l in L if l['cls'] in ('corps', 'grand')]
    marge = sorted(l['x0'] for l in corps)[len(corps) // 4] if corps else 0
    droite = sorted(l['x1'] for l in corps)[3 * len(corps) // 4] if corps else 0
    for l in L:
        l['retrait'] = l['x0'] - marge
        out["el"].append({"cls": l['cls'], "text": l['text'], "x0": l['x0'], "x1": l['x1'], "y0": l['y0'], "y1": l['y1'],
                          "retrait": l['x0'] - marge, "court": droite - l['x1'], "xh": l['xh'], "ah": l['ah'],
                          "bloc": l['k'][0], "ws": [[w['t'], w['x'], w['y'], w['w'], w['h'], w['c']] for w in l['ws']]})
    out["marge"], out["droite"] = marge, droite
    return out


if __name__ == "__main__":
    P = [page(f"{i:03d}") for i in range(202)]
    json.dump(P, open("/tmp/farm/pages.json", "w"))
    for p in P:
        print(p["n"], p["num"], (p["tete"] or "")[:40], len(p["el"]))
