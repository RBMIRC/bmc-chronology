import pickle, re, sys, collections
sys.path.insert(0, '/tmp/dub')
import lib
from lib import join, clean, feed, SUP
blocks = pickle.load(open('/tmp/dub/blocks_raw.pkl','rb'))
chapters, notes = pickle.load(open('/tmp/dub/notes_struct.pkl','rb'))
iseq = pickle.load(open('/tmp/dub/index_seq.pkl','rb'))
for b in blocks: feed(b.get('lines', []))
for n in notes:
    for p in n['paras']: feed(p)
def dash_ranges(t):
    t = re.sub(r'(?<=\d)\s?[-—–]\s?(?=\d)', '–', t)   # numeric ranges -> en dash
    return t
def final(t, speakers=True):
    t = clean(t, speakers)
    t = re.sub(r'(?<![\d,.])(\d{1,4})[-—](\d{1,4})(?![\d])', r'\1–\2', t)
    t = re.sub(r'(\d{4})– (\d{4})', r'\1–\2', t)
    return t
out = []
W = out.append
# ---------------- front matter
W("""BLACK MOUNTAIN
AN EXPLORATION IN COMMUNITY

Martin Duberman


Martin Duberman is Distinguished Service Professor of History at Lehman College, City University of New York. Mr. Duberman is the author of Charles Francis Adams, 1807–1886, which was awarded the Bancroft Prize in 1962, and James Russell Lowell, which was a nominee for the National Book Award in 1966. His documentary play, In White America, won the 1963–64 Vernon Rice-Drama Desk Award. In 1971 Mr. Duberman received a prize from the National Academy of Arts and Letters for his contributions to literature. His other works include The Uncompleted Past, The Memory Bank (a play), and The Antislavery Vanguard: New Essays on the Abolitionists, which he edited.


BLACK MOUNTAIN
AN EXPLORATION IN COMMUNITY

Martin Duberman

ANCHOR BOOKS
Anchor Press / Doubleday, Garden City, New York
1973


Black Mountain: An Exploration in Community was originally published in hardcover by E. P. Dutton & Co., Inc., in 1972. This edition is published by arrangement with E. P. Dutton.

ANCHOR BOOKS EDITION: 1973

ISBN: 0-385-07059-4
Library of Congress Catalog Card Number: 73-79735
Copyright © 1972 by Martin Duberman
All Rights Reserved
Printed in the United States of America


For Cindy Degener—and bridges


CONTENTS

        INTRODUCTION                       xi
        PREFACE                            xvii
     1. The Rollins Fracas                 1
     2. A Beginning                        11
     3. Anni and Josef Albers              41
     4. The Thirties                       64
     5. Schism                             114
     6. A New Home                         153
     7. The Split                          172
     8. Aftermaths and Continuities        212
     9. New Definitions of Community       233
    10. Entries and Exits                  281
    11. Transition                         332
    12. A New Black Mountain               352
    13. Olson                              389
    14. Expelled and Imploding             408
        ACKNOWLEDGMENTS                    441
        NOTES                              445
        INDEX                              547


    In most books, the I, or first person, is omitted; in this it will be retained; that, in respect to egotism, is the main difference. We commonly do not remember that it is, after all, always the first person that is speaking. I should not talk so much about myself if there were anybody else whom I knew as well.
                                        —Thoreau, Walden

    I would be an historian as Herodotus was, looking for oneself for the evidence of what is said . . .
                                        —Charles Olson Letter 23,
                                         The Maximus Poems
""")
CAPS1 = """[PHOTOGRAPHS 1–16]

1. John Andrew Rice. Spring, 1932. Ted Dreier seated on left in back of boat. Courtesy Frank Rice.

2. Front of Lee Hall. Courtesy The State Archives, Raleigh.

3. Josef Albers discussing student drawings.

4. Ted Dreier. Courtesy State Archives, Raleigh.

5. A group setting out for the farm (porch of Lee Hall in foreground). Courtesy State Archives, Raleigh.

6. John Andrew Rice and a group of students. Courtesy State Archives, Raleigh.

7. Lake Eden (dining hall left foreground). Courtesy State Archives, Raleigh.

8. Construction of Studies Building by students and faculty. Courtesy State Archives, Raleigh.

9. Saturday night dancing. Erwin Straus and Elsa Kahl (foreground), Josef Albers, with eyes toward the floor (far right). Courtesy State Archives, Raleigh.

10. Jalowetz conducting. Courtesy Will Hamlin.

11. Left to right: Jalowetz, Straus, Wunsch, Johanna Jalowetz, Trudi Straus, unidentified woman, John Evarts. Courtesy State Archives, Raleigh.

12. Eric Bentley leading a seminar, 1944. Courtesy State Archives, Raleigh.

13. Nell Rice. April, 1942. Photograph by Howard Dearstyne.

14. John Wallen and his son, Kurt, in front of the Wallen’s apartment at Black Mountain, 1945–46. Courtesy Wallen.

15. Bill Levi, Levi’s daughter by his first marriage, and Mary Caroline Richards. Courtesy Richards.

16. Summer Institute, 1946. Left to right: Leo Amino, Jacob Lawrence, Leo Lionni, Ted Dreier, Bobbie Dreier, Beaumont Newhall, Gwendolyn Lawrence, Mrs. Gropius, Varda (in tree), Nan Newhall, Walter Gropius, Molly Gregory, Josef Albers, Anni Albers. Courtesy State Archives, Raleigh."""
CAPS2 = """[PHOTOGRAPHS 17–26]

17. Summer Institute, 1948. Buckminster Fuller and Merce Cunningham in Satie’s The Ruse of the Medusa. Courtesy State Archives, Raleigh.

18. The cast of The Ruse of the Medusa. Left to right: Isaac Rosenfeld (identification uncertain), Alvin Charles Few, unidentified woman, Buckminster Fuller, John Cage, Elaine de Kooning, Bill Shrauger, Merce Cunningham. Courtesy State Archives, Raleigh.

19. Attempting to raise the “Supine Dome.” Summer, 1948. Model of Dome in foreground. Fuller (white-haired) in center background. Photograph by Beaumont Newhall.

20. Charles Olson writing Maximus, 1951. Photograph by Jonathan Williams.

21. Francine du Plessix and Joel Oppenheimer. Summer, 1951. Photograph by Jonathan Williams.

22. A performance of Banjo. Summer, 1953. Left to right: Timothy La Farge, Jo Anne Melsher, Remy Charlip, Marianne Simon, Carolyn Brown, Merce Cunningham, Anita Dencks. (Viola Farber and Paul Taylor were in the first performance given on August 22, 1953.) Photograph by Arnold Eagle. Courtesy David Vaughan.

23. Robert Creeley. Black Mountain, 1955. (“Portrait as a Spanish Assassin.”) Photograph by Jonathan Williams.

24. Dan Rice and Robert Creeley. Black Mountain, 1955. Photograph by Jonathan Williams.

25. Farewell party for Hilda Morley and Stefan Wolpe. Left to right: Joe Dunn, Ann Simone, Grey Stone, Eloise Mixon, Bea Huss and baby, Wes Huss, Tom Field and Huss child, Jonathan Williams, Anita Landreau, Joe Fiore and child, Tony Landreau and child. Charles Olson and his son, Stefan Wolpe, Robert Duncan, Betty Kaiser. Photograph courtesy Gerald van de Wiele.

26. Betty Kaiser, Charles Olson, and their son, Charles Peter. Black Mountain, Summer, 1956. Courtesy Gerald van de Wiele."""
# ---------------- body
done1 = done2 = False
for b in blocks:
    ty = b['type']; pg = b.get('page', 0)
    if not done1 and pg >= 225 and ty != 'fn': W(CAPS1); done1 = True
    if not done2 and pg >= 401 and ty != 'fn': W(CAPS2); done2 = True
    if ty == 'chapter': W(f"\n\nCHAPTER {b['num']}\n\n{b['title'].upper()}\n")
    elif ty == 'section': W(f"\n\n{b['title']}\n")
    elif ty == 'break': W('* * *')
    elif ty == 'p': W(final(join(b['lines'])))
    elif ty == 'bq':
        if b.get('mode') == 'verse':
            x0 = min(b['xs'])
            ys = b['ys']; gaps = [ys[i+1] - ys[i] for i in range(len(ys) - 1) if ys[i+1] > ys[i]]
            g0 = min(gaps) if gaps else 30
            vl = []
            for i, (t_, x_) in enumerate(zip(b['lines'], b['xs'])):
                if i and (ys[i] < ys[i-1] or ys[i] - ys[i-1] > 1.35 * g0): vl.append('')
                vl.append('    ' + ' ' * int(round((x_ - x0) / 14)) + final(t_))
            W('\n'.join(vl))
        else:
            W('    ' + final(join(b['lines'])))
    elif ty == 'fn': W(final(join(b['lines'])))
# ---------------- notes
W('\n\nNOTES\n')
chtitle = dict(chapters)
last = None
for n in notes:
    if n['ch'] != last:
        W(f"\nCHAPTER {n['ch']}: {chtitle[n['ch']]}\n"); last = n['ch']
    parts = []
    for p in n['paras']:
        if not p: continue
        if p[0].startswith('\x00TABLE'): parts.append('\x00' + p[0][6:]); continue
        q = final(join(p), speakers=False)
        if parts and not parts[-1].startswith('\x00') and re.match(r'^(\. \. \.|[a-z])', q) and not re.search(r'[.?!:;”’)\]…]$', parts[-1]):
            parts[-1] = parts[-1] + ' ' + q
        else:
            parts.append(q)
    first = True; buf = []
    for p in parts:
        if p.startswith('\x00'):
            buf.append(p[1:])
        elif first:
            buf.append(f"{n['n']}. {p}"); first = False
        else:
            buf.append('    ' + p)
    W('\n\n'.join(buf))
# ---------------- index
IDEC = collections.defaultdict(list)
for l in open('/tmp/dub/idec.txt'):
    l = l.rstrip('\n')
    if l: pi, a, b2 = l.split('|'); IDEC[int(pi)].append((a, b2))
used = set()
for s in iseq:
    for k, (a, b2) in enumerate(IDEC.get(s['pi'], [])):
        if (s['pi'], k) in used: continue
        if a.startswith('^'):
            if re.fullmatch(a[1:-1], s['text']): s['text'] = b2; used.add((s['pi'], k))
        elif a in s['text']: s['text'] = s['text'].replace(a, b2, 1); used.add((s['pi'], k))
miss = [(pi, a) for pi, lst in IDEC.items() for k, (a, _) in enumerate(lst) if (pi, k) not in used]
if miss: print('IDEC MISS', miss)
entries = []
for s in iseq:
    if s['lev'] == 2 and entries: entries[-1][1].append(s['text'])
    else: entries.append([s['lev'], [s['text']]])
W('\n\nINDEX\n')
idx = []
for lev, lines in entries:
    t = final(join(lines), speakers=False)
    idx.append(('  ' if lev == 1 else '') + t)
W('\n'.join(idx))
# ---------------- back cover
W("""\n\n[BACK COVER]

history

Black Mountain
Martin Duberman

This is the first complete story of Black Mountain College, perhaps the most important community of artists and intellectuals in American history. During its twenty-three-year existence (1933–1956) in the foothills of North Carolina, this experimental community attracted such well-known figures as John Cage, Merce Cunningham, Buckminster Fuller, Charles Olson, Josef Albers, Paul Goodman, and Robert Rauschenberg—people whose profound impact on American culture is still being felt.

Black Mountain was more than a nurturing ground for some of the major talents of our time. It was also a forerunner of the innovative educational and social communities of more recent times—including the experimental communes of the counter culture. As such, Black Mountain may well prove to be a crucial turning point in American history.

“[Duberman’s] book cannot be overpraised; it is at once a landmark of scholarship in the history of ideas and a pioneer model of how the vexing problem of subjectivity and objectivity in historical interpretation should be handled...And the style remains withal, both elegant and casual...A rich chronicle of the sweet uses of adversity.”
—Edgar Z. Freidenberg, in The New York Review of Books

“A ground-breaking venture in historical method, perhaps the most intimate, tender history an institution...has ever inspired...It raises terrifying questions, illuminating the tragic, at times almost manic, quality of utopian quest...In our present proliferation of experimental educational programs and communal forms, no book could be more relevant...”
—Judson Jerome, Saturday Review

Black Mountain “leaps beyond the discipline of history in its significance...Henceforth debates about the relation between historian and sources will have to take account of this radically new model for doing history.”
—Jesse Lemisch, The New York Times Book Review

“Fascinating history with a resonance that far exceeds the experience of the Black Mountaineers themselves.”
—Newsweek

“Reading the book, it is hard to imagine how it might have been done more intelligently.”
—Catharine R. Stimpson, The Nation

“The most perceptive study of the dynamics of the communal process that I’ve ever come across.”
—Marty Jezer, Liberation

“if I should ever again do anything of interest to myself, this book will have stirred me to it...”
—Eric Weinberger, Win

Cover Design by Jim McWilliams. Cover Photograph by Jonathan Williams.
A Doubleday Anchor Book   ISBN: 0-385-07059-4
""")
QDEC = {}
_cells = pickle.load(open('/tmp/dub/qcells.pkl','rb'))
for _l in open('/tmp/dub/qdec.txt'):
    _i, _v = _l.split(); QDEC[_cells[int(_i)][0]] = _v
def apply_qdec(txt):
    out_parts = []; ch = 0
    for p in txt.split('\n\n'):
        m = re.match(r'\s*CHAPTER (\d+)\s*$', p)
        if m: ch = int(m.group(1))
        if p.strip() == 'NOTES': ch = 999
        if ch and ch != 999:
            def rep(mm):
                n = int(''.join(str('⁰¹²³⁴⁵⁶⁷⁸⁹'.index(c)) for c in mm.group(3)))
                v = QDEC.get((ch, n))
                if v is None or v == 'K': return mm.group(0)
                q = {'Q': '”', 'N': '', 'S': '’”'}[v]
                return mm.group(1) + q + mm.group(3)
            p = re.sub(r'([^”’"\']*?[.,;:!?)\w])([”’"\']*)([⁰¹²³⁴⁵⁶⁷⁸⁹]+)', rep, p)
        out_parts.append(p)
    return '\n\n'.join(out_parts)
POST = [('de Graaft’s', 'de Graaff’s'), ('a Jocal level', 'a local level'), ('Moellenhofis', 'Moellenhoffs'), ('Nelf Rice', 'Nell Rice'), ('Milton Rdse', 'Milton Rose'),
 ('Tworkoy', 'Tworkov'), ('Walfen sent', 'Wallen sent'), ('enrphasizes', 'emphasizes'), ('interviewswith', 'interview with'), ('make’a good', 'make a good'),
 ('ninecompoops', 'nincompoops'), ('sesponded', 'responded'), ('thafa hierarchy', 'that a hierarchy'), ('an- . nounced', 'announced'), ('de- ‘cisive', 'decisive'),
 ('fo rmal', 'formal'), ('intelligence.t the point', 'intelligence to the point'), ('this is it: ll try', 'this is it: I’ll try'), ('her “the. college', 'her “the college'), ('mid-forties. and his', 'mid-forties, and his'), ('Raleigh Archives. i\n', 'Raleigh Archives.\n'), ('courtesy Forbes. i\n', 'courtesy Forbes.\n'), ('June 12, 1967. a\n', 'June 12, 1967.\n'), ('books, but. how', 'books, but how'), ('On the other. hand', 'On the other hand'), ('it throws. not', 'it throws not'), ('between. them', 'between them'), ('by the. contrast', 'by the contrast'), ('said to me, “, . he', 'said to me, “. . . he'), ('Gropius—-Breuer', 'Gropius–Breuer'), ('279-—280', '279–280'), ('Johanna, my - wife', 'Johanna, my wife'), ('Peggy - Bennett', 'Peggy Bennett'),
 ('Boyden, whose- Vassar', 'Boyden, whose Vassar'), ('at the- University', 'at the University'), ('p.. 171.', 'p. 171.'), ('uncommented on.. And', 'uncommented on. And'), ('March 24, 1967..', 'March 24, 1967.'),
 ('students. . . .whose', 'students. . . . whose'), ('a crack-up) .²⁵', 'a crack-up).²⁵'), ('And M.C. read—— LITZ:\n\n    And M.C.', 'And M.C. read——\n\n    LITZ: And M.C.'), ('The M.1.T. Press', 'The M.I.T. Press'), ('ERWIN sTRAUS:', 'ERWIN STRAUS:'), ('expound thesis:.. 2:5\n\n    I was not trying to indict you. . .', 'expound a thesis. . . .\n\n    RICE: I was not trying to indict you . . .'), ('something new and superior,', 'something new and superior.'), ('on a small scale),', 'on a small scale).'), ('a lawyer.’” ‘', 'a lawyer.’”'), ('for hay-ing put', 'for having put'), ('selfabnegation', 'self-abnegation'), ('selfcaricaturing', 'self-caricaturing'), ('shortcircuiting', 'short-circuiting'), ('slatbottomed', 'slat-bottomed'), ('Eightteenth', 'Eighteenth'), ('Literaure', 'Literature'), ('lecture,“Relations', 'lecture, “Relations'),
('“«well”', '“well”'), ('people «at', 'people at'), ('(Neu- « mann)', '(Neumann)'),
 ('for it?”®', 'for it?”'), ('things ¢hat', 'things that'), ('board ° and', 'board and'), ('tape, ° October', 'tape, October'),
 ('253, ° 505', '253, 505'), ('301°\n', '301\n'), ('Expo °67', 'Expo ’67'), ('Austin §. Edwards', 'Austin S. Edwards'), ('Arthur §. Adams', 'Arthur S. Adams'),
 ('whistles blew#', 'whistles blew,'), ('{or eager', '(or eager'), ('rector.}', 'rector.'), ('the absence of students. |', 'the absence of students.'),
 ('SEASONGOOD: | think', 'SEASONGOOD: I think'), ('right? | answer', 'right? I answer'), ('proof <wasn’t', 'proof wasn’t'),
 ('¥ 526, 527 “>', '526, 527'), ('Mountain~the', 'Mountain—the'), ('herds ~were', 'herds were'), ('sent me. ~~', 'sent me.'),
 ('fifties_for', 'fifties—for'), ('279–280 _&', '279–280'),
 ('two wings. =', 'two wings.'), ('he said © sounded', 'he said sounded'), ('Noguchi™!⁷¹', 'Noguchi⁷¹'), ('also taught -regularly', 'also taught regularly'),
 ('Holt to” the Trustees', 'Holt to the Trustees'), ('autobiography, 1 Came Out', 'autobiography, I Came Out')]
txt = '\n\n'.join(out)
txt = apply_qdec(txt)
def merge_body(txt):
    i = txt.index('\n\n\nNOTES\n')
    body, rest = txt[:i], txt[i:]
    ps = body.split('\n\n')
    out2 = []
    for p in ps:
        s = p.strip()
        if s.startswith('. Albers believed'): p = p.replace('. Albers believed', 'Albers believed', 1); s = p.strip()
        # restore paragraph-initial ellipsis mangled by OCR
        if re.match(r'^\.(?: \.)?\s+(?=\S)', s) and not s.startswith('. . .'):
            p = re.sub(r'^(\s*)\.(?: \.)?\s+', r'\1. . . ', p); s = p.strip()
        if out2:
            prev = out2[-1].rstrip()
            if '\n' not in prev.strip() and '\n' not in s and prev.strip() not in ('*',) and not re.match(r'^\s*(CHAPTER|\[PHOTO)', prev) \
               and not re.search(r'[.?!:;”’)\]…⁰¹²³⁴⁵⁶⁷⁸⁹*]$', prev) and (re.match(r'^(\. |[a-z])', s)):
                if prev.endswith('-') and re.match(r'[a-z]', s): out2[-1] = prev[:-1] + s
                else: out2[-1] = prev + ' ' + s
                continue
        out2.append(p)
    return '\n\n'.join(out2) + rest
txt = merge_body(txt)
txt = re.sub(r' _ ', ' ', txt)
txt = re.sub(r'(?<=[a-z]),(?=[a-z])', ', ', txt)
txt = re.sub(r'\b(else|became|discuss)\.(could|impossible|the)\b', r'\1 \2', txt)
txt = re.sub(r'\b([xvi]{1,5})[-—]([xvi]{1,5})\b', r'\1–\2', txt)
txt = txt.replace('“high art,’?', '“high art,”')
for a_, b_ in [('I”d invested', 'I’d invested'), ('French and Russian.“¹⁴', 'French and Russian.¹⁴'), ('at the college). “\n', 'at the college).\n'),
               ('adhered to them. “1\n', 'adhered to them.\n'), ('December 29, 1971). “\n', 'December 29, 1971).\n'), ('I“hoped', 'I “hoped'), ('been“calmer', 'been “calmer'),
               ('Curiously“enough', 'Curiously enough'), ('(““A Note', '(“A Note'), ('from it”” (Anni', 'from it” (Anni'), ('remark, ““There', 'remark, “There'), ('Phfft!””', 'Phfft!”')]:
    if a_ not in txt: print('MISS3', repr(a_))
    txt = txt.replace(a_, b_)
txt = re.sub(r'(?<=[a-z])”(?=[a-z])', '’', txt)
txt = txt.replace('they should be. .\n', 'they should be.\n').replace('watering it. * . . It’s', 'watering it. . . . It’s')
txt = re.sub(r'(?<!\.) \. \.(?! \.)', ' . . .', txt)
txt = re.sub(r'(?m)^(\s*)\. \.(?! \.) ', r'\1. . . ', txt)
for a_, b_ in [('\n\n        spired/the aspirate\n       the aspirant almost\n       without breath\n', '\n\n      in\n\n        spired/the aspirate\n        the aspirant almost\n        without breath\n'),
               ('    it is a breath out\n       breathed)', '      it is a breath out\n        breathed)'),
               ('        For Love—I would\n        split open your head and put\n    a candle in\n        behind the eyes.\n\n     Love is dead', '    For Love—I would\n    split open your head and put\n    a candle in\n    behind the eyes.\n    Love is dead'),
               ('     if we forget\n     the virtues of an amulet\n     and quick surprise.', '    if we forget\n    the virtues of an amulet\n    and quick surprise.')]:
    if a_ not in txt: print('MISS5', repr(a_[:40]))
    txt = txt.replace(a_, b_)
for a_, b_ in [('better than itis.', 'better than it is.'), ('as time goes on. .\n', 'as time goes on. . . .\n'), ('John Andrew Rice, / Came Out', 'John Andrew Rice, I Came Out'), ('252, 399, 425 -\n', '252, 399, 425\n')]:
    if a_ not in txt: print('MISS4', repr(a_))
    txt = txt.replace(a_, b_)
txt = re.sub(r'(?m)^(\s*[A-Z]{3,}(?: [A-Z]{3,})?(?: \[[a-z ]+\])?);(?= )', r'\1:', txt)
txt = re.sub(r'([“‘])T(?= [a-z])', r'\1I', txt)
txt = re.sub(r'(?<![A-Za-z.’])J(?= [a-z])', 'I', txt)
txt = txt.replace('que8tions', 'questions').replace('resigned a8 treasurer', 'resigned as treasurer').replace('poLice', 'POLICE')
txt = txt.replace('intensely. ”m not', 'intensely. I’m not')
for a_, b_ in [('the J Ching', 'the I Ching'), ('wrote in J Came Out', 'wrote in I Came Out'), ('“Tt got', '“It got'), ('—Tt was', '—It was'), ('“IT want', '“I want'),
               ('(Vol. Il, no. If)', '(Vol. II, no. II)'), ('World War Il,', 'World War II,'), ('. . . 1 am in Jove', '. . . I am in love')]:
    if a_ not in txt: print('MISS2', a_)
    txt = txt.replace(a_, b_)
txt = txt.replace('“ ‘', '“‘').replace('’ ”', '’”')
for a_, b_ in POST:
    if a_ not in txt: print('POST MISS', a_)
    txt = txt.replace(a_, b_)
txt = re.sub(r'\n{4,}', '\n\n\n', txt)
open('/tmp/dub/out/draft.txt', 'w').write(txt.strip() + '\n')
pickle.dump(lib.HY, open('/tmp/dub/hy.pkl', 'wb'))
print(len(txt))
