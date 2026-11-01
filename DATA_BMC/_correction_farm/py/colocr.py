"""Ré-OCR colonne par colonne (psm 6) des pages à deux colonnes ; TSV dans /tmp/farm/hd/col/NNN_{0,1}.tsv
avec coordonnées ramenées à la page."""
import cv2, subprocess, os, csv, sys
from cols import mots, colonnes

os.makedirs('/tmp/farm/hd/col', exist_ok=True)


def ocr_cols(n, force=False):
    W = [w for w in mots(n) if w['c'] > 20]
    x0, x1 = min(w['x'] for w in W), max(w['x'] + w['w'] for w in W)
    y0, y1 = min(w['y'] for w in W), max(w['y'] + w['h'] for w in W)
    g = colonnes(W, x0, x1)
    im = cv2.imread(f'/tmp/farm/hd/pre/{n}.png', 0)
    out = []
    for side, (a, b) in enumerate([(max(0, x0 - 80), g), (g, min(im.shape[1], x1 + 60))]):
        base = f'/tmp/farm/hd/col/{n}_{side}'
        if force or not os.path.exists(base + '.tsv'):
            cv2.imwrite(base + '.png', im[max(0, y0 - 30):y1 + 30, a:b])
            subprocess.run(['tesseract', os.path.basename(base) + '.png', os.path.basename(base), '--psm', '6', 'tsv'], capture_output=True, cwd='/tmp/farm/hd/col')
        rows = []
        for r in csv.DictReader(open(base + '.tsv'), delimiter='\t', quoting=csv.QUOTE_NONE):
            if r['level'] == '5' and (r['text'] or '').strip():
                rows.append(dict(t=r['text'], x=int(r['left']) + a, y=int(r['top']) + max(0, y0 - 30), w=int(r['width']),
                                 h=int(r['height']), c=float(r['conf']), k=(int(r['block_num']), int(r['par_num']), int(r['line_num']))))
        out.append(rows)
    return out


if __name__ == '__main__':
    for i in range(int(sys.argv[1]), int(sys.argv[2]) + 1):
        ocr_cols(f'{i:03d}')
        print(i, end=' ', flush=True)
