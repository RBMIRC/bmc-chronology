import pickle, cv2, numpy as np
allm = pickle.load(open('/tmp/dub/markers2.pkl','rb'))
items = [(pi, k, m) for pi in sorted(allm) for k, m in enumerate(allm[pi])]
pickle.dump([(pi,k) for pi,k,m in items], open('/tmp/dub/sheet_index.pkl','wb'))
SC = 3; CW, CH = 330, 90; COLS, ROWS = 6, 12
cache = {}
def crop(pi, m):
    if pi not in cache: cache.clear(); cache[pi] = cv2.imread(f'/tmp/dub/img/p-{pi:03d}.jpg', cv2.IMREAD_GRAYSCALE)
    im = cache[pi]
    y0 = int(m['base'] - 1.5*m['cap']); y1 = int(m['base'] + 0.35*m['cap'])
    x0 = m['x0'] - 45; x1 = m['x1'] + 14
    c = im[max(0,y0):y1, max(0,x0):x1]
    return cv2.resize(c, None, fx=SC, fy=SC, interpolation=cv2.INTER_CUBIC)
per = COLS*ROWS
for s in range(0, len(items), per):
    sheet = np.full((ROWS*CH, COLS*CW), 255, np.uint8)
    for j, (pi, k, m) in enumerate(items[s:s+per]):
        r, cidx = divmod(j, COLS)
        c = crop(pi, m)[:CH-4, :CW-70]
        oy, ox = r*CH, cidx*CW
        sheet[oy:oy+c.shape[0], ox+66:ox+66+c.shape[1]] = c
        cv2.putText(sheet, str(s+j), (ox+2, oy+50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, 0, 2)
        cv2.line(sheet, (ox, oy+CH-1), (ox+CW, oy+CH-1), 180, 1)
    cv2.imwrite(f'/tmp/dub/sheets/s{s//per:02d}.png', sheet)
print(len(items))
