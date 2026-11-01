set -e
cd /tmp/farm/py
P=/tmp/dub/venv/bin/python
$P build.py >/dev/null
$P -u exposants.py
cd /tmp/farm && rm -f out/blob_ocr.json blob/*.png && $P - <<'PY'
import json,cv2,subprocess
E=json.load(open('out/encre.json')); cache={}; out={}
for k,v in E.items():
    n=k.split('|')[0]
    if n not in cache: cache[n]=cv2.imread(f'hd/pre/{n}.png',0)
    im=cache[n]; x,y,w,h=v['x'],v['y'],v['w'],v['h']
    cr=im[max(0,y-6):y+h+6, max(0,x-6):x+w+6]
    cr=cv2.copyMakeBorder(cv2.resize(cr,None,fx=4,fy=4,interpolation=cv2.INTER_CUBIC),30,30,30,30,cv2.BORDER_CONSTANT,value=255)
    f=k.replace('|','_')+'.png'; cv2.imwrite('blob/'+f,cr)
    out[k]=subprocess.run(['tesseract',f,'-','--psm','7','-c','tessedit_char_whitelist=0123456789'],capture_output=True,text=True,cwd='/tmp/farm/blob').stdout.strip()
json.dump(out,open('out/blob_ocr.json','w'))
PY
cd /tmp/farm/py
$P legendes.py >/dev/null
$P assemble.py
$P appels.py | head -1
$P final.py
