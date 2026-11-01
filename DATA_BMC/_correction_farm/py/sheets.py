import json,cv2,numpy as np
C=json.load(open('/tmp/farm/out/candidats.json'))
cells=[];cache={}
for i,c in enumerate(C):
    if not c['ou']: continue
    n,x,y=c['ou'].split(','); x=int(x); y=int(y)
    if n not in cache: cache[n]=cv2.imread(f'/tmp/farm/hd/pre/{n}.png',0)
    im=cache[n]
    cr=im[max(0,y-20):y+50, max(0,x-300):x+70]
    cr=cv2.resize(cr,(370,70))
    cell=np.full((100,370),255,np.uint8); cell[30:100]=cr
    lab=f"#{i} -> {c['num'] if c['num'] else 'X'} ({c['raw']})"
    cv2.putText(cell,lab,(4,22),cv2.FONT_HERSHEY_SIMPLEX,0.65,0,2)
    cells.append(cell)
per=48
for s in range(0,len(cells),per):
    grp=cells[s:s+per]
    while len(grp)%4: grp.append(np.full((100,370),255,np.uint8))
    cv2.imwrite(f'/tmp/farm/verif/sheet_{s//per:02d}.png',np.vstack([np.hstack(grp[i:i+4]) for i in range(0,len(grp),4)]))
print(len(cells))
