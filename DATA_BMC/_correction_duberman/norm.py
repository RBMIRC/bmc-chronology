import re
WORDFIX = {
 # verified against page images
 'Jobn':'John','Férbes':'Forbes','Schénberg':'Schönberg','Schdenberg':'Schönberg','Barték':'Bartók','Piége':'Piège',
 'matiére':'matière','Amedée':'Amedée','Laubiés':'Laubiès','crépe':'crêpe','créme':'crème','maché':'mâché','naiveté':'naïveté',
 'naive':'naïve','facade':'façade','Lim6én':'Limón','Limén':'Limón','Etude':'Étude',
 'agsence':'absence','archietects':'architects','aroynd':'around','assymptions':'assumptions','charteristic':'characteristic',
 'coltege':'college','comformity':'conformity','cummunity':'community','destribed':'described','enaugh':'enough',
 'fagulty':'faculty','inctified':'inclined','intuftively':'intuitively','minunderstood':'misunderstood','moyement':'movement',
 'pefson':'person','persondlity':'personality','quéstioning':'questioning','stafL':'staff','statenfent':'statement',
 'statjon':'station','structuréd':'structured','suest':'guest','taacher':'teacher','tarned':'turned','thése':'these',
 'variéd':'varied','vittimized':'victimized','woodwerk':'woodwork','wrete':'wrote','believéd':'believed','adoléscent':'adolescent',
 'semestér':'semester','eyen':'even','oyer':'over','stary':'story','thé':'the','haye':'have','ndme':'name','diyersity':'diversity',
 'eyil':'evil','Kahi':'Kahl','Drejer':'Dreier','Graafi’s':'Graaff’s','Jeft':'left','Jong':'long','tesolute':'resolute',
 'conyineed':'convinced','tun':'run','tible':'rible','writtea':'written','yague':'vague','yalue':'value','leaye':'leave',
 'seyeral':'several','moyes':'moves','subyersive':'subversive','obyiously':'obviously','canyassed':'canvassed','tisked':'risked',
 'yery':'very','themselyes':'themselves','yarious':'various','yain':'vain','tich':'rich','tipped':'ripped','dethands':'demands',
 'imto':'into','langhing':'laughing','lidn':'lion','idiosyneracies':'idiosyncracies','knowh':'known','edueation’s':'education’s',
 'muuch':'much','accotint':'account','Mofintain':'Mountain','decisian':'decision','cammunity’s':'community’s','exercisgs':'exercises',
 'afone':'alone','régularly':'regularly','editéd':'edited','yvo-':'vo-','gitl':'girl','Heil':'Hell','Pest!':'Yes.','Gop”':'GOD”',
}
LINEFIX = [  # (old, new) exact substrings
 ('the-fead', 'the lead'), ('Thot is veh-ree', 'That is veh-ree'), ('mem- ‘ber', 'member'), ('Zukofsky thought _ I', 'Zukofsky thought I'),
 ('* woman. I don’t think', 'woman. I don’t think'), ('* When the December meeting', 'When the December meeting'),
 ('tangled with Harold Ickes,', 'tangled with Harold Ickes.'), ('-* a candle in', 'a candle in'),
]
def fix_words(t):
    t = re.sub(r"[A-Za-zÀ-ÿ]+(?=’s\b)", lambda m: WORDFIX.get(m.group(0), m.group(0)), t)
    def rep(m):
        w = m.group(0)
        return WORDFIX.get(w, w)
    return re.sub(r"[A-Za-zÀ-ÿ0-9’!”-]+", lambda m: WORDFIX.get(m.group(0), m.group(0)) if m.group(0) in WORDFIX else re.sub(r"[A-Za-zÀ-ÿ0-9’]+", rep, m.group(0)), t)

def norm_quotes(t):
    t = t.replace("’'", '”').replace("'’", '”').replace('’’', '”').replace('‘‘', '“').replace(',,', ',')
    t = t.replace('”’”', '”’”')
    # straight double quotes
    t = re.sub(r'(^|[\s(\[—–])"', r'\1“', t)
    t = t.replace('"', '”')
    # straight single quote: apostrophe within words / closing; opening after space
    t = re.sub(r"(^|[\s(\[—“])'", r'\1‘', t)
    t = t.replace("'", '’')
    return t

def norm_ellipsis(t):
    def rep(m):
        s = m.group(0); n = s.count('.')
        lead = ' ' if s[0] == ' ' else ''
        if n < 3: return s
        core = ' '.join(['.'] * n)
        return lead + core
    t = re.sub(r' ?\.(?: ?\.){2,}', rep, t)
    return t

def norm_space(t):
    t = re.sub(r'[ \t]+', ' ', t)
    t = re.sub(r' ([,;:!?)\]])', r'\1', t)            # space before punctuation
    t = re.sub(r'([(\[]) ', r'\1', t)
    t = re.sub(r'(\w) \.(?!\s?\.)', r'\1.', t)         # "word ." -> "word."
    t = re.sub(r'([“‘]) (?=\w)', r'\1', t)
    t = re.sub(r'(?<=\w)\s+([”’])(?=[\s.,;:)]|$)', r'\1', t)
    return t

SPEAKERS = {}
def norm_speakers(t, known):
    def rep(m):
        w = m.group(1)
        if w.upper() in known: return w.upper() + m.group(2)
        return m.group(0)
    return re.sub(r'(?:(?<=^)|(?<=[.?!”] ))([A-Za-z][A-Za-z]{2,})(:)', rep, t)
