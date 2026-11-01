import json, statistics
def merged_pages():
    P = json.load(open('/tmp/dub/pages.json'))
    out = []
    for p in P:
        frags = sorted(p['lines'], key=lambda l: (l['y0']+l['y1'])/2)
        rows = []
        for f in frags:
            yc = (f['y0']+f['y1'])/2
            if rows and abs(rows[-1]['yc'] - yc) < 9:
                rows[-1]['f'].append(f); continue
            rows.append(dict(yc=yc, f=[f]))
        lines = []
        for r in rows:
            fs = sorted(r['f'], key=lambda f: f['x0'])
            words = [w for f in fs for w in f['words']]
            words.sort(key=lambda w: w[0])
            lines.append(dict(x0=min(f['x0'] for f in fs), x1=max(f['x1'] for f in fs),
                              y0=min(f['y0'] for f in fs), y1=max(f['y1'] for f in fs),
                              h=statistics.median([w[3]-w[1] for w in words]),
                              words=[list(w) for w in words],
                              text=' '.join(w[4] for w in words)))
        out.append(dict(W=p['W'], H=p['H'], lines=lines))
    return out
if __name__ == '__main__':
    import pickle
    P = merged_pages(); pickle.dump(P, open('/tmp/dub/merged.pkl', 'wb'))
