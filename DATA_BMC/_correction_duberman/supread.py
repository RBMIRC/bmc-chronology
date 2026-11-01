import pickle, cv2, subprocess, os
from concurrent.futures import ThreadPoolExecutor
allm = pickle.load(open('/tmp/dub/markers.pkl','rb'))
jobs = []
for pi, ms in allm.items():
    for k, (li, x0, x1, y0, y1) in enumerate(ms):
        jobs.append((pi, k, li, x0, x1, y0, y1))
imgs = {}
def run(j):
    pi, k, li, x0, x1, y0, y1 = j
    im = cv2.imread(f'/tmp/dub/img/p-{pi:03d}.jpg', cv2.IMREAD_GRAYSCALE)
    crop = im[max(0,y0-3):y1+3, max(0,x0-3):x1+3]
    crop = cv2.resize(crop, None, fx=6, fy=6, interpolation=cv2.INTER_CUBIC)
    crop = cv2.copyMakeBorder(crop, 40, 40, 40, 40, cv2.BORDER_CONSTANT, value=255)
    fn = f'/tmp/dub/supcrops/{pi:03d}_{k:02d}.png'; cv2.imwrite(fn, crop)
    r = subprocess.run(['tesseract', fn, '-', '--psm', '7', '-c', 'tessedit_char_whitelist=0123456789'],
                       capture_output=True, env=dict(os.environ, OMP_THREAD_LIMIT='1'))
    return (pi, k), r.stdout.decode('utf-8','replace').strip()
with ThreadPoolExecutor(8) as ex: res = dict(ex.map(run, jobs))
pickle.dump(res, open('/tmp/dub/supread.pkl', 'wb'))
print(len(res))
