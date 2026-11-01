import glob,re,sys
inv=sys.argv[1]; f=glob.glob(f'pages_txt/*/{inv}_*')[0]; s=re.sub(r'\s+',' ',open(f).read())
for k in sys.argv[2:]:
    key,_,n=k.partition('@'); av,ap=(map(int,n.split(','))) if n else (200,300)
    i=s.find(key); print(f'--- [{key}]', s[max(0,i-av):i+ap] if i>=0 else 'INTROUVABLE')
