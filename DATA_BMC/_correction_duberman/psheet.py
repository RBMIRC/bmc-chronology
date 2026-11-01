import pickle, re, cv2, numpy as np, sys, random
M = pickle.load(open('/tmp/dub/merged.pkl','rb')); S = 1.1111
res = pickle.load(open('/tmp/dub/punct.pkl','rb'))
mode = sys.argv[1]; out = sys.argv[2]; start = int(sys.argv[3]) if len(sys.argv) > 3 else 0
items = []
for pi, li, wi, t, g in res:
    o = re.search(r'([.,])[”’)\]]*$', t).group(1)
    if g and o != g[0] and (mode == 'all' or o == mode):
        items.append((pi, li, wi, t, g))
items = items[start:start+60]
CW, CH, COLS = 440, 70, 3
rows = (len(items) + COLS - 1) // COLS
sheet = np.full((rows*CH, COLS*CW), 255, np.uint8)
for j, (pi, li, wi, t, g) in enumerate(items):
    im = cv2.imread(f'/tmp/dub/img/p-{pi:03d}.jpg', cv2.IMREAD_GRAYSCALE)
    l = M[pi]['lines'][li]; w = l['words'][wi]
    crop = im[int(l['y0']*S)-4:int(l['y1']*S)+6, max(0,int(w[0]*S)-60):int(w[2]*S)+70]
    crop = cv2.resize(crop, None, fx=1.5, fy=1.5)[:CH-20, :CW-6]
    r, c = divmod(j, COLS); oy, ox = r*CH, c*CW
    sheet[oy:oy+crop.shape[0], ox+3:ox+3+crop.shape[1]] = crop
    lab = f"{start+j} ocr'{t[-3:]}' geo{g[0]} d{g[1]} r{g[2]}".encode('ascii','replace').decode()
    cv2.putText(sheet, lab, (ox+3, oy+CH-5), cv2.FONT_HERSHEY_SIMPLEX, 0.42, 0, 1, cv2.LINE_AA)
    cv2.line(sheet, (ox, oy+CH-1), (ox+CW, oy+CH-1), 160, 1); cv2.line(sheet, (ox+CW-1, oy), (ox+CW-1, oy+CH), 160, 1)
cv2.imwrite(out, sheet)
print(len(items))
