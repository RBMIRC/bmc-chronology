import pickle, re, collections
from wordfreq import zipf_frequency
blocks = pickle.load(open('/tmp/dub/blocks_raw.pkl','rb'))
SUP = str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹')
# corpus of mid-line tokens
mid = collections.Counter()
for b in blocks:
    for t in b.get('lines', []):
        ws = t.split()
        for w in ws[:-1]:
            mid[re.sub(r'^[^\w]+|[^\w]+$', '', w).lower()] += 1
def decide(a, b):
    j = (a + b).lower(); h = (a + '-' + b).lower()
    cj, ch = mid[j], mid[h]
    if ch > cj: return True
    if cj > 0: return False
    zj = zipf_frequency(j, 'en')
    if zj > 1.5: return False
    if zipf_frequency(a, 'en') >= 3 and zipf_frequency(b, 'en') >= 3: return True
    return False
HY = []
def join(lines):
    text = lines[0].strip()
    for nxt in lines[1:]:
        nxt = nxt.strip()
        if not nxt: continue
        m = re.search(r'([A-Za-z]+)-$', text)
        n = re.match(r'([A-Za-z]+)', nxt)
        if m and n and not text.endswith('--'):
            keep = decide(m.group(1), n.group(1))
            HY.append((m.group(1), n.group(1), keep))
            text = (text if keep else text[:-1]) + nxt
        elif text.endswith(('—', '–')) or nxt.startswith(('—', '–')):
            text = text + nxt
        else:
            text = text + ' ' + nxt
    return text
def fmt(t):
    t = re.sub(r'⟦(\d+)⟧', lambda m: m.group(1).translate(SUP), t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t
out = []
for b in blocks:
    ty = b['type']
    if ty == 'chapter':
        out.append(f"\n\nCHAPTER {b['num']}\n{b['title'].upper()}\n")
    elif ty == 'section':
        out.append(f"\n\n{b['title']}\n")
    elif ty == 'break':
        out.append('* * *')
    elif ty == 'p':
        out.append(fmt(join(b['lines'])))
    elif ty == 'bq':
        out.append('    ' + fmt(join(b['lines'])))
    elif ty == 'fn':
        out.append(fmt(join(b['lines'])))
txt = '\n\n'.join(out)
txt = re.sub(r'\n{3,}', '\n\n\n', txt)
open('/tmp/dub/body_draft.txt', 'w').write(txt.strip() + '\n')
pickle.dump(HY, open('/tmp/dub/hy.pkl', 'wb'))
print(len(txt), len(HY), sum(k for _,_,k in HY))
