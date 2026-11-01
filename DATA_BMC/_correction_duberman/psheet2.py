import pickle, cv2, numpy as np, sys
M = pickle.load(open('/tmp/dub/merged.pkl','rb')); S = 1.1111
A, B = pickle.load(open('/tmp/dub/pcand.pkl','rb'))
items = A + B
CW, CH, COLS, ROWS = 330, 84, 5, 12; per = COLS * ROWS
for s in range(0, len(items), per):
    sheet = np.full((ROWS*CH, COLS*CW), 255, np.uint8)
    for j, (pi, li, wi, t, nxt, f) in enumerate(items[s:s+per]):
        im = cv2.imread(f'/tmp/dub/img/p-{pi:03d}.jpg', cv2.IMREAD_GRAYSCALE)
        l = M[pi]['lines'][li]; w = l['words'][wi]
        crop = im[int(l["y0"]*S)+4:int(l["y1"]*S)+8, max(0, int(w[2]*S)-90):int(w[2]*S)+60]
        crop = cv2.resize(crop, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)[:CH-14, :CW-4]
        r, c = divmod(j, COLS); oy, ox = r*CH, c*CW
        sheet[oy:oy+crop.shape[0], ox+2:ox+2+crop.shape[1]] = crop
        cv2.putText(sheet, str(s+j), (ox+2, oy+CH-3), cv2.FONT_HERSHEY_SIMPLEX, 0.4, 0, 1)
        cv2.line(sheet, (ox, oy+CH-1), (ox+CW, oy+CH-1), 150, 1); cv2.line(sheet, (ox+CW-1, oy), (ox+CW-1, oy+CH), 150, 1)
    cv2.imwrite(f'/tmp/dub/sheets/p{s//per:02d}.png', sheet)
print(len(items))
