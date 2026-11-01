import pickle, sys, re, statistics
sys.argv = ['x']
exec(open('/tmp/dub/build2.py').read().split('blocks = []; cur = None')[0])
out = []
for pi in BODY:
    head, lines = page_lines(pi)
    if not lines: continue
    lines, foot, left, right, mg = classify(pi, lines)
    i = 0
    while i < len(lines):
        if lines[i]['kind'] != 'block': i += 1; continue
        j = i
        while j < len(lines) and lines[j]['kind'] == 'block': j += 1
        z = lines[i:j]
        ns = sum(l['short'] for l in z)
        if ns >= 0.5 * len(z) and len(z) >= 2:
            out.append((pi, i, j, ns, len(z), [l['text'] for l in z]))
        i = j
for o in out:
    print(f'== p{o[0]} l{o[1]}-{o[2]} short {o[3]}/{o[4]}')
    for t in o[5][:6]: print('    ', t[:90])
