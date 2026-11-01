import subprocess, os, sys
from concurrent.futures import ThreadPoolExecutor
def run(i):
    src=f'/tmp/dub/img/p-{i-1:03d}.jpg'; png=f'/tmp/dub/tess/t{i:03d}.png'; out=f'/tmp/dub/tess/{i:03d}'
    subprocess.run(['magick',src,'-resize','200%','-colorspace','Gray',png],check=True)
    subprocess.run(['tesseract',png,out,'-l','eng','--dpi','400','txt','tsv'],env=dict(os.environ,OMP_THREAD_LIMIT='1'),capture_output=True)
    os.remove(png)
with ThreadPoolExecutor(8) as ex: list(ex.map(run, range(1,618)))
print('done')
