"""Résout les appels de note du corps : suite 1-263, calée sur les numéros lus (ancres), complétée par les
exposants repérés dans l'image. Remplace ⟦…⟧ par l'exposant Unicode ; signale les trous."""
import json, re, bisect

SUP = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
NB = 263


def valeur(raw):
    d = raw
    for a, b in (("'", '1'), ('’', '1'), ('‘', '1'), ('!', '1'), ('|', '1'), ('I', '1'), ('l', '1')):
        d = d.replace(a, b)
    return int(d) if d.isdigit() else None


def main():
    fl = json.load(open('/tmp/farm/out/corps.json'))
    cands = []
    for k, it in enumerate(fl):
        for m in re.finditer(r'⟦(.*?)⟧', it['x']):
            avant = it['x'][max(0, m.start() - 3):m.start()]
            raw, _, ou = m.group(1).partition('@')
            v = (int(raw[1:]) if raw[1:].isdigit() else None) if raw.startswith('b') else valeur(raw.lstrip('_'))
            cands.append({'k': k, 'pos': m.start(), 'raw': raw, 'ou': ou, 'v': v if v and 1 <= v <= NB else None,
                          'avant': avant, 'p': it['p'], 't': it['t']})
    # ancres : plus longue sous-suite strictement croissante des valeurs lues
    lus = [(i, c['v']) for i, c in enumerate(cands) if c['v']]
    tails, prev, tail_idx = [], {}, []
    for j, (i, v) in enumerate(lus):
        pos = bisect.bisect_left(tails, v)
        if pos == len(tails): tails.append(v); tail_idx.append(j)
        else: tails[pos] = v; tail_idx[pos] = j
        prev[j] = tail_idx[pos - 1] if pos > 0 else None
    seq, j = [], tail_idx[-1]
    while j is not None:
        seq.append(lus[j]); j = prev[j]
    ancres = dict(seq[::-1])
    bornes = [(-1, 0)] + sorted(ancres.items()) + [(len(cands), NB + 1)]
    attribue, trous = {}, []
    for (ia, va), (ib, vb) in zip(bornes, bornes[1:]):
        if ia >= 0: attribue[ia] = va
        besoin = vb - va - 1
        seg = list(range(ia + 1, ib))
        def score(i):
            c = cands[i]
            s = 0
            if c['raw'] not in ('?', 'b', '_'): s += 3
            if re.search(r'[.”’;:,!?)]$', c['avant']): s += 2
            if c['t'] == 'legende': s -= 1
            return s
        choix = sorted(sorted(seg, key=score, reverse=True)[:max(0, besoin)])
        for r, i in enumerate(choix):
            attribue[i] = va + 1 + r
        if len(choix) < besoin:
            trous.append((va, vb, besoin - len(choix), cands[ia]['p'] if ia >= 0 else None, cands[ib]['p'] if ib < len(cands) else None))
    # corrections vérifiées sur l'image (planches de contrôle) : ou → numéro, ou None pour rejeter
    import os
    FORCE = json.load(open('/tmp/farm/appels_force.json')) if os.path.exists('/tmp/farm/appels_force.json') else {}
    for i, c in enumerate(cands):
        if c['ou'] in FORCE:
            if FORCE[c['ou']] is None: attribue.pop(i, None)
            else: attribue[i] = FORCE[c['ou']]
    # réécriture
    par_k = {}
    for i, c in enumerate(cands):
        par_k.setdefault(c['k'], []).append(i)
    for k, idx in par_k.items():
        x = fl[k]['x']; parts = []; last = 0
        for i, m in zip(idx, re.finditer(r'⟦(.*?)⟧', x)):
            parts.append(x[last:m.start()])
            if i in attribue:
                parts.append(str(attribue[i]).translate(SUP))
            else:  # candidat rejeté : on rend le texte lu tel quel (« 1,500 », « 667 »)
                r = cands[i]['raw']
                if r.startswith('_'): parts.append(' ' + r[1:])
                elif not r.startswith('b') and r != '?': parts.append(r)
            last = m.end()
        parts.append(x[last:])
        fl[k]['x'] = "".join(parts)
    # appels restés dans le texte comme chiffres ordinaires (« Fellows. 25 », « 1933.9 ») : recherchés entre les voisins
    SUPS = "⁰¹²³⁴⁵⁶⁷⁸⁹"
    def places():
        d = {}
        for k, it in enumerate(fl):
            for m in re.finditer(r'[⁰¹²³⁴⁵⁶⁷⁸⁹]+', it['x']):
                d[int(''.join(str(SUPS.index(ch)) for ch in m.group(0)))] = (k, m.start())
        return d
    for v in range(1, NB + 1):
        d = places()
        if v in d: continue
        a_ = max([u for u in d if u < v], default=None); b_ = min([u for u in d if u > v], default=None)
        ka, pa = d[a_] if a_ else (0, 0)
        kb, pb = d[b_] if b_ else (len(fl) - 1, len(fl[-1]['x']))
        for k in range(ka, kb + 1):
            x = fl[k]['x']
            lo = pa if k == ka else 0; hi = pb if k == kb else len(x)
            rx = re.compile(r"(?<=[a-z.,”’?!)\]])\s?" + str(v) + r"(?=[\s|]|$)|(?<=\b1[89]\d\d[.,])" + str(v) + r"\b")
            m = rx.search(x, lo, hi)
            if m:
                fl[k]['x'] = x[:m.start()] + str(v).translate(SUP) + x[m.end():]
                break
    json.dump(fl, open('/tmp/farm/out/corps_appels.json', 'w'), ensure_ascii=False, indent=0)
    d = places(); attribue = {i: v for i, v in enumerate(sorted(d))}
    json.dump([{**cands[i], 'num': attribue.get(i), 'ctx': fl[cands[i]['k']]['x'][:0]} for i in range(len(cands))],
              open('/tmp/farm/out/candidats.json', 'w'), ensure_ascii=False, indent=0)
    vus = sorted(attribue.values())
    manque = [v for v in range(1, NB + 1) if v not in vus]
    doubles = [v for v in set(vus) if vus.count(v) > 1]
    print('manquants :', manque, '; doublons :', doubles)
    print(len(cands), 'candidats ;', len(ancres), 'ancres ;', len(vus), 'appels placés ;', len(cands) - len(vus), 'rejetés')
    print('trous (numéros sans appel repéré) :')
    for t in trous: print('  ', t)


if __name__ == '__main__':
    main()
