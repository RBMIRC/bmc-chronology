#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
clean_bmd_v6.py — Black Mountain Days PDF→TXT cleanup, v6.

Changes vs v5:
  • Fix 1: footnote relocation — detect `*`-prefixed paragraphs BEFORE
    strip_garble_tokens strips the `*`. Now footnotes are correctly pulled
    to end-of-chapter under "Notes:".
  • Fix 2: strip_glued_prefix() — removes short garble prefixes at paragraph
    starts (Zo., ih, py,, va, Ta, LS., LiF, ZZ, AE, Zit, PA, Baa, Zoik,
    213., 252., 433,, 238., 257., 74., 8&8, 8&9, IY), 49 (OAT).
  • Fix 3: is_garble_dense_line() — catches long garble lines (>24 chars)
    that escaped drop_decorative_block's short-line run detection.

Run on the ORIGINAL pdftotext -layout output.

Usage:
    python3 clean_bmd_v6.py [input.txt] [output.txt]

If no args:
    input  = black_mountain_days.txt  (current dir)
    output = black_mountain_days_v6.txt (current dir)
"""

from __future__ import annotations
import os
import re
import sys
from typing import List, Tuple

# ===================================================================
# Config
# ===================================================================

DEFAULT_IN  = "black_mountain_days.txt"
DEFAULT_OUT = "black_mountain_days_v6.txt"

# Section header words we want to keep as standalone headings.
SECTION_RE = re.compile(r'^(Preface|Epilogue|Afterword|Coda|Postscript)\b', re.I)

# A real chapter that starts with a year: "1952 My mother..."  →  keep "1952" as heading.
YEAR_CHAPTER_RE = re.compile(r'^(19\d{2})\s+([A-Z][a-z])')

# Footnote: a paragraph (line) starting with one or more asterisks.
FOOTNOTE_RE = re.compile(r'^\*+\s*\S')

# Whitelist of short words that look like garble but are real English.
# Do NOT strip these even if they are short.
SAFE_SHORT = {
    "I","a","A","an","An","as","As","at","At","be","Be","by","By","do","Do",
    "go","Go","he","He","if","If","in","In","is","Is","it","It","me","Me",
    "my","My","no","No","of","Of","on","On","or","Or","so","So","to","To",
    "up","Up","us","Us","we","We","yes","Yes","and","And","but","But","for",
    "For","not","Not","the","The","yet","Yet","all","All","are","Are","ask",
    "Ask","boy","Boy","but","cat","Cat","dog","Dog","ear","Ear","eye","Eye",
    "few","Few","fit","Fit","fly","Fly","get","Get","god","God","had","Had",
    "has","Has","her","Her","him","Him","his","His","hot","Hot","how","How",
    "let","Let","man","Man","may","May","new","New","now","Now","old","Old",
    "one","One","our","Our","out","Out","own","Own","run","Run","say","Say",
    "see","See","she","She","sun","Sun","ten","Ten","too","Too","top","Top",
    "two","Two","use","Use","war","War","was","Was","way","Way","who","Who",
    "why","Why","you","You","any","Any","art","Art","bad","Bad","big","Big",
    "box","Box","bus","Bus","car","Car","cup","Cup","cut","Cut","day","Day",
    "die","Die","dry","Dry","eat","Eat","end","End","era","Era","eye","Eye",
    "far","Far","fee","Fee","fit","Fit","fix","Fix","fun","Fun","gap","Gap",
    "get","Get","gut","Gut","guy","Guy","ham","Ham","hat","Hat","hen","Hen",
    "hey","Hey","hit","Hit","hop","Hop","hot","Hot","hug","Hug","ice","Ice",
    "ill","Ill","ink","Ink","inn","Inn","jam","Jam","jar","Jar","jet","Jet",
    "job","Job","joy","Joy","key","Key","kid","Kid","lab","Lab","law","Law",
    "lay","Lay","led","Led","leg","Leg","let","Let","lie","Lie","lip","Lip",
    "log","Log","lot","Lot","low","Low","mad","Mad","man","Man","map","Map",
    "mat","Mat","mid","Mid","mix","Mix","mom","Mom","mud","Mud","net","Net",
    "nip","Nip","nod","Nod","nor","Nor","not","Not","nut","Nut","odd","Odd",
    "oil","Oil","ore","Ore","our","Our","owl","Owl","pad","Pad","pan","Pan",
    "pat","Pat","pay","Pay","pet","Pet","pie","Pie","pig","Pig","pin","Pin",
    "pit","Pit","pop","Pop","pot","Pot","pub","Pub","pun","Pun","pus","Pus",
    "put","Put","rag","Rag","ram","Ram","rat","Rat","raw","Raw","red","Red",
    "rib","Rib","rid","Rid","rig","Rig","rim","Rim","rip","Rip","rod","Rod",
    "rot","Rot","row","Row","rub","Rub","rug","Rug","run","Run","sad","Sad",
    "sap","Sap","saw","Saw","say","Say","sea","Sea","set","Set","sew","Sew",
    "shy","Shy","sir","Sir","sit","Sit","six","Six","ski","Ski","sky","Sky",
    "sly","Sly","sob","Sob","sod","Sod","son","Son","sow","Sow","spa","Spa",
    "spy","Spy","sum","Sum","tab","Tab","tag","Tag","tan","Tan","tap","Tap",
    "tar","Tar","tax","Tax","tea","Tea","tee","Tee","ten","Ten","the","The",
    "tic","Tic","tie","Tie","tin","Tin","tip","Tip","toe","Toe","ton","Ton",
    "tow","Tow","toy","Toy","try","Try","tub","Tub","tug","Tug","two","Two",
    "urn","Urn","van","Van","vet","Vet","vex","Vex","via","Via","vie","Vie",
    "vow","Vow","wad","Wad","wag","Wag","war","War","was","Was","wax","Wax",
    "way","Way","web","Web","wed","Wed","wet","Wet","who","Who","why","Why",
    "wig","Wig","win","Win","wit","Wit","woe","Woe","wok","Wok","won","Won",
    "woo","Woo","yak","Yak","yam","Yam","yaw","Yaw","yea","Yea","yen","Yen",
    "yes","Yes","yet","Yet","you","You","zap","Zap","zip","Zip","zoo","Zoo",
    "Ms","Mr","Dr","Jr","Sr","St","Mt","No",
}

# Whitelist of 4-consonant clusters that occur in real English words.
# If a 4+ consonant cluster is in this set, the token is NOT garble.
# Includes compound-word clusters like "ndsh" (windshield), "ndsp" (handspring).
SAFE_CLUSTERS = {
    # Suffixes & inflections
    "ngth","ghts","ngths","tche","tchs","ngle","ngles","stle","stles",
    "mpt","mpts","ndle","ndles","rst","rsts","lft","lfts","lfst","mpst",
    "ftw","dths","nth","nths","tch","ght","mps","nds","lst","nks",
    "nkt","rks","nct","ncts","ctor","ptly","bly","cly","fly","gly",
    "ply","tly","rlds","rld","nstr","nscr","rts",
    # Compound boundaries (rare but real)
    "ndsh","ndsp","ndst","ndsk","ndsl","ndsm","ndsn",  # windshield, handspring, grandstand
    "ldsh","ldsp","ldst",  # shield-spring, etc.
    "rshm","rshn","rshp",  # relationship, worship
    "lshm","lshn",  # flash-ship
    "mpsh",  # bump-shaft
    "nksh",  # bank-shot
    "ntsh",  # print-shop
    "ndth",  # thousandth
    "sch","scht","spl","scr","str",  # 3-consonant safe prefixes (harmless here)
}

# Pre-compute lowercase version of SAFE_SHORT for fast lookup.
SAFE_SHORT_LOWER = {w.lower() for w in SAFE_SHORT}

# ===================================================================
# Garble detection
# ===================================================================

VOWELS = set("aeiouyAEIOUY")

def is_garble_token(tok: str) -> bool:
    """Conservative: True only if token is CLEARLY OCR garbage.

    Returns False for any normal English word, including short ones.
    """
    if not tok:
        return False
    # Strip surrounding punctuation/quotes (preserve internal hyphens/apostrophes).
    s = tok.strip(".,;:!?\"'“”‘’()[]|_-—–* \t")
    if not s:
        return False
    L = len(s)

    # Never strip whitelisted short words.
    if s in SAFE_SHORT:
        return False

    # Pattern A: digit immediately adjacent to letter INSIDE the token,
    # e.g. "18g", "1l", "52500", "ISBN9", "0a", "9g".
    # Real exceptions: "19th", "4-F", "1940-41", "WW2", "2nd", "3rd".
    if re.search(r'[A-Za-z]\d|\d[A-Za-z]', s):
        # Allow ordinals: 19th, 21st, 32nd, 103rd
        if re.fullmatch(r'\d+(th|st|nd|rd)', s, re.I):
            return False
        # Allow military class: 4-F
        if re.fullmatch(r'\d-[A-Z]', s):
            return False
        # Allow year ranges: 1940-41, 1952-53
        if re.fullmatch(r'\d{4}-\d{2}', s):
            return False
        # Allow "WW2" / "WW1"
        if re.fullmatch(r'WW[12]', s):
            return False
        # Allow "$7" / "$1,600" / "$25" (currency)
        if s.startswith('$') and re.fullmatch(r'\$[\d,]+(\.\d+)?', s):
            return False
        # Otherwise: digit+letter mix = garble
        return True

    # Pattern B: 5+ consonants in a row, NOT in whitelist.
    # Catches garble like "mspw" (4 cons) is caught by Pattern C instead (low vowel).
    # We use 5+ here to be conservative — "windshield" has "ndsh" (4 cons) and is real.
    clusters = re.findall(r'[bcdfghjklmnpqrstvwxz]{5,}', s, re.I)
    for cl in clusters:
        if cl.lower() not in SAFE_CLUSTERS:
            return True

    # Pattern C: very low vowel ratio AND length ≥ 4 (catches vowel-less garble).
    if L >= 4:
        alpha = sum(c.isalpha() for c in s)
        if alpha >= 4:
            vows = sum(c in VOWELS for c in s if c.isalpha())
            if vows / alpha < 0.15:
                return True

    return False


def is_suspect_line(line: str) -> bool:
    """Heuristic: line is likely a decorative/cover garble line.

    Conservative: returns True only for lines that are clearly garble on their own.
    For run-of-short-lines detection, see is_short_for_run().
    """
    s = line.strip()
    if not s:
        return False
    L = len(s)

    # Standalone year (chapter marker candidate): not suspect.
    if re.fullmatch(r'19\d{2}', s):
        return False
    # Real year range "1940-41." etc.: not suspect.
    if re.fullmatch(r'19\d{2}-\d{2}\.?', s):
        return False
    # Section header words: not suspect.
    if SECTION_RE.match(s) and L <= 30:
        return False

    # Short line with both letters and digits = likely garble
    if L <= 16 and re.search(r'[A-Za-z]', s) and re.search(r'\d', s):
        # Allow: page-range like "393-394", "1-12", "39-44"
        if re.fullmatch(r'\d+-\d+', s):
            return False
        # Allow: pure currency like "$7"
        if re.fullmatch(r'\$[\d,]+(\.\d+)?', s):
            return False
        return True

    # Very short line with weird OCR punctuation (curly quotes, pipes, brackets)
    if L <= 8 and re.search(r'[|“”‘’\[\]\{\}\(\)<>]', s) and not re.search(r'[A-Za-z]{3,}', s):
        return True

    # All-letter short line where MOST tokens are garble.
    if L <= 30 and re.fullmatch(r"[A-Za-z'‘’\-\s:.!?;,]+", s):
        tokens = re.findall(r"[A-Za-z']+", s)
        if tokens and len(tokens) <= 5:
            garble_count = sum(1 for t in tokens if is_garble_token(t))
            if garble_count >= 1 and garble_count >= len(tokens) / 2:
                return True

    return False


def is_short_for_run(line: str) -> bool:
    """Lines that count toward 'short run' detection.

    A line counts if it's ≤ 24 chars and not a clear chapter marker / section header.
    We don't care whether it's a real short paragraph or garble — the point is that
    runs of 3+ such lines in a row are almost always decorative garble in this book.
    """
    s = line.strip()
    if not s:
        return False
    if len(s) > 24:
        return False
    if re.fullmatch(r'19\d{2}', s) or re.fullmatch(r'19\d{2}-\d{2}\.?', s):
        return False
    if SECTION_RE.match(s) and len(s) <= 30:
        return False
    return True


def is_garble_dense_line(line: str) -> bool:
    """Detect a garble line regardless of length (v6 fix 3).

    A line is garble-dense if >35% of its tokens are short (≤3 chars) AND not
    in SAFE_SHORT, OR are flagged by is_garble_token(). This catches long garble
    lines (>24 chars) that escaped is_short_for_run's length check.

    Examples caught:
      "ct ' be bola rn wc wa Role om ei uve eenamram: mene tyof" (51 chars)
      "Tega. ee aM ah ROE Ail arletadeeeyiteg sg eter woth aMa" (54 chars)
      "ievaery £3 4 it Meee — ia mr ea Maggi oe —- S 4" (46 chars)

    Examples NOT caught (preserved):
      "I was glad we were going too." (all short words are in SAFE_SHORT)
      "Ed had fun." (only 1 non-SAFE_SHORT token out of 3)
    """
    s = line.strip()
    if not s:
        return False
    if SECTION_RE.match(s) or YEAR_CHAPTER_RE.match(s):
        return False
    tokens = re.findall(r'[A-Za-z0-9]+', s)
    if len(tokens) < 2:
        return False
    garble_short = sum(
        1 for t in tokens
        if len(t) <= 3 and t.lower() not in SAFE_SHORT_LOWER
    )
    garble_token = sum(1 for t in tokens if is_garble_token(t))
    garble_total = garble_short + garble_token
    return garble_total / len(tokens) > 0.35


# ===================================================================
# Step 1: find_frontmatter_start — cut everything before "Preface"
# ===================================================================

def find_frontmatter_start(lines: List[str]) -> int:
    """Return index of the line that begins the actual book body.

    Strategy: find the first line whose stripped content is exactly "Preface"
    OR that starts with "Preface" preceded only by garble tokens on the same line.
    Falls back to the first "1952" chapter marker if Preface is missing.
    """
    for i, ln in enumerate(lines):
        s = ln.strip()
        # Pure "Preface" line (possibly with leading garble that we'll strip later)
        # Accept: "Preface", "the mspwrer Preface", "Preface "
        m = re.search(r'\bPreface\b', s)
        if m:
            # Make sure it's not inside a real sentence (i.e. line is short or it's at end)
            if len(s) <= 40 or s.endswith('Preface') or m.end() == len(s):
                return i
    # Fallback: first year-chapter line.
    for i, ln in enumerate(lines):
        if YEAR_CHAPTER_RE.match(ln.strip()):
            return i
    # Last resort: keep everything.
    return 0


# ===================================================================
# Step 2: drop_decorative_block — drop runs of suspect short lines
# ===================================================================

def drop_decorative_block(lines: List[str]) -> List[str]:
    """Remove runs of short/suspect/garble-dense lines.

    Drop a run when ANY of these is true:
      - ≥2 suspect lines (clear garble) in the run
      - ≥3 short-for-run lines (≤24 chars) in the run
      - ≥3 garble-dense lines (any length, high short-token density) in the run
    Blank lines inside a run don't break it.
    """
    out: List[str] = []
    i = 0
    n = len(lines)
    while i < n:
        ln = lines[i]
        if is_suspect_line(ln) or is_short_for_run(ln) or is_garble_dense_line(ln):
            j = i
            suspect_count = 0
            short_count = 0
            garble_dense_count = 0
            while j < n:
                cur = lines[j]
                if is_suspect_line(cur):
                    suspect_count += 1
                    short_count += 1
                    j += 1
                elif is_garble_dense_line(cur):
                    garble_dense_count += 1
                    short_count += 1
                    j += 1
                elif is_short_for_run(cur):
                    short_count += 1
                    j += 1
                elif cur.strip() == '':
                    j += 1
                else:
                    break
            if suspect_count >= 2 or short_count >= 3 or garble_dense_count >= 3:
                # Drop the entire run.
                i = j
                if out and out[-1].strip() != '':
                    out.append('')
                continue
            else:
                while i < j:
                    out.append(lines[i])
                    i += 1
                continue
        else:
            out.append(lines[i])
            i += 1
    return out


# ===================================================================
# Step 3: strip page numbers (standalone + glued-at-paragraph-start)
# ===================================================================

def is_pagenum_line(s: str) -> bool:
    """Standalone page-number line: just digits, optionally with prefix/suffix."""
    s = s.strip()
    if not s:
        return False
    # Pure number
    if re.fullmatch(r'\d{1,4}', s):
        return True
    # "- 541", "— 541", "541.", "-541"
    if re.fullmatch(r'[-–—]\s*\d{1,4}\.?', s):
        return True
    # Page-with-range like "541-542"
    if re.fullmatch(r'\d{1,4}-\d{1,4}', s):
        return True
    return False


# Page-number patterns glued at start of a paragraph.
# Catches: "541 and more open", "- 541 and more", "Si and needed", "Is Feeling", "1l ..."
# Strategy: if the FIRST token of a paragraph looks like a number/garble-page-num
# AND the second token continues the previous sentence (lowercase, or starts with
# a participle/conjunction indicating a fragment), strip the first token.
GLUED_PAGENUM_RE = re.compile(
    r'^\s*(?:'
    r'-\s*\d{1,4}\s+'                  # "- 541 word"
    r'|—\s*\d{1,4}\s+'                 # "— 541 word"
    r'|\d{1,4}\s+(?=[a-z])'            # "541 word" (next word lowercase)
    r'|(?:Si|Is|1l|18g)\s+(?=[a-z])'   # garbled pagenum + lowercase word
    r'|(?:Si|Is)\s+(?=[A-Z][a-z]+\s+[a-z])'  # "Is Feeling inexplicably" → fragment
    r')'
)


def strip_glued_pagenum(paragraph: str) -> str:
    """Strip a glued page-number prefix from a paragraph."""
    m = GLUED_PAGENUM_RE.match(paragraph)
    if m:
        return paragraph[m.end():].lstrip()
    return paragraph


def strip_trailing_garble(paragraph: str) -> str:
    """Strip a garble cluster appended after the last sentence-ending punctuation.

    Two cases handled:
      A) Tail of ≥3 short tokens (≤4 alphabetic chars each), mostly non-English.
         Catches "vue ony Aa A yw th" appended after a period.
      B) Tail of 1-2 short tokens after a closing quote, none in SAFE_SHORT.
         Catches "ako" appended after `."` in the end-matter blurbs.
    """
    # --- Case A: tail of ≥3 short tokens after sentence-ending punct ---
    matches = list(re.finditer(r'([.!?]["\']?)\s+(\S[^.!?]*)$', paragraph))
    if matches:
        m = matches[-1]
        tail = m.group(2).strip()
        tokens = tail.split()
        if len(tokens) >= 3:
            bare_tokens = [re.sub(r'[^A-Za-z]', '', t) for t in tokens]
            if all(len(b) <= 4 for b in bare_tokens):
                real_count = 0
                for b in bare_tokens:
                    if not b:
                        continue
                    if b in SAFE_SHORT or b.lower() in SAFE_SHORT or b.capitalize() in SAFE_SHORT:
                        real_count += 1
                if real_count < len(tokens) / 2:
                    return paragraph[:m.start() + len(m.group(1))].rstrip()

    # --- Case B: 1-2 short tokens after a closing quote ---
    m2 = re.search(r'(["\u201c\u201d\'\u2018\u2019]\s+\S{1,4}(?:\s+\S{1,4})?)\s*$', paragraph)
    if m2:
        # Strip leading quote chars from the tail.
        tail = m2.group(1)
        tail = re.sub(r'^["\u201c\u201d\'\u2018\u2019]\s+', '', tail).strip()
        tokens = tail.split()
        if tokens and len(tokens) <= 2:
            bare_tokens = [re.sub(r'[^A-Za-z]', '', t) for t in tokens]
            if all(len(b) <= 4 for b in bare_tokens):
                real_count = sum(
                    1 for b in bare_tokens
                    if b and (b in SAFE_SHORT or b.lower() in SAFE_SHORT or b.capitalize() in SAFE_SHORT)
                )
                if real_count == 0:
                    # Keep up to and including the closing quote.
                    return paragraph[:m2.start() + 1].rstrip()

    return paragraph


# ===================================================================
# Step 3b (v6 fix 2): strip garble prefixes at paragraph start
# ===================================================================

# Pattern: 1-3 digit page-number + optional punct + space + word
# (4-digit years like 1952 are excluded — they're chapter headings, not page numbers)
# Catches: "213. ous", "252. something", "433, writing", "238. The summer", "257. thing", "74. much"
_PREFIX_DIGIT_RE = re.compile(
    r'^(\d{1,3}[.,;:!?\)]?\s+)(?=[a-z]|[A-Z][a-z]+\s+[a-z])'
)

# Pattern: digits + symbol + digits + space + word
# Catches: "8&8 ment", "8&9 belly"
_PREFIX_DIGSYM_RE = re.compile(
    r'^(\d+[&+\-]\d+\s+)(?=[a-z])'
)

# Pattern: letters/digits + ")" + space + word
# Catches: "IY) Something"
_PREFIX_PAREN_RE = re.compile(
    r'^([A-Za-z]{1,4}\)\s+)(?=[A-Z][a-z]+\s+[a-z]|[a-z])'
)

# Pattern: digits + space + "(CAPS" + optional ")" + space + word
# Catches: "49 (OAT 1953 Just" (no closing paren) or "49 (OAT) Just"
_PREFIX_DIGPARENS_RE = re.compile(
    r'^(\d+\s*\([A-Z]+\)?\s+)(?=[A-Z]|\d)'
)

# Pattern: 2-4 letter token + optional punct + space + lowercase word
# Catches: "py, wide", "Zo. of", "va so", "Ta rubber", "LS. psychology", "AE per"
_PREFIX_LOWER_RE = re.compile(
    r'^([A-Za-z]{2,4}[.,;:!?\)]?\s+)(?=[a-z])'
)

# Pattern: 2-4 letter token + optional punct + space + Capital+lowercase+space+lowercase
# Catches: "ih Saturday night", "LiF It also", "ZZ Jonathan Williams"
_PREFIX_CAP_RE = re.compile(
    r'^([A-Za-z]{2,4}[.,;:!?\)]?\s+)(?=[A-Z][a-z]+\s+[a-z])'
)


def strip_glued_prefix(paragraph: str) -> str:
    """Strip a short garble prefix at the start of a paragraph (v6 fix 2).

    Catches patterns like:
      "ih Saturday night" → "Saturday night"
      "py, wide double" → "wide double"
      "Zo. of making" → "of making"
      "213. ous lips" → "ous lips"
      "8&8 ment in" → "ment in"
      "IY) Something of" → "Something of"
      "49 (OAT Just prior" → "Just prior"

    Preserves real English short words (I, In, As, Be, To, etc.) via SAFE_SHORT.
    """
    if not paragraph or len(paragraph) < 3:
        return paragraph

    # Pattern 1: digits + optional punct + space + word
    m = _PREFIX_DIGIT_RE.match(paragraph)
    if m:
        return paragraph[m.end():].lstrip()

    # Pattern 2: digits + symbol + digits + space + word
    m = _PREFIX_DIGSYM_RE.match(paragraph)
    if m:
        return paragraph[m.end():].lstrip()

    # Pattern 3: letters + ")" + space + word
    m = _PREFIX_PAREN_RE.match(paragraph)
    if m:
        token = re.sub(r'[^A-Za-z]', '', m.group(1))
        if token.lower() not in SAFE_SHORT_LOWER:
            return paragraph[m.end():].lstrip()

    # Pattern 4: digits + "(CAPS)" + space + word
    m = _PREFIX_DIGPARENS_RE.match(paragraph)
    if m:
        return paragraph[m.end():].lstrip()

    # Pattern 5: 2-4 letter token + optional punct + space + lowercase word
    m = _PREFIX_LOWER_RE.match(paragraph)
    if m:
        token = re.sub(r'[^A-Za-z]', '', m.group(1))
        if token.lower() not in SAFE_SHORT_LOWER:
            return paragraph[m.end():].lstrip()

    # Pattern 6: 2-4 letter token + optional punct + space + Capital fragment
    m = _PREFIX_CAP_RE.match(paragraph)
    if m:
        token = re.sub(r'[^A-Za-z]', '', m.group(1))
        if token.lower() not in SAFE_SHORT_LOWER:
            return paragraph[m.end():].lstrip()

    return paragraph


# ===================================================================
# Step 4: detect & relocate footnotes
# ===================================================================

def split_paragraphs(lines: List[str]) -> List[str]:
    """Convert raw lines into a list of paragraphs (blank-separated)."""
    paras: List[str] = []
    cur: List[str] = []
    for ln in lines:
        if ln.strip() == '':
            if cur:
                paras.append(' '.join(cur).strip())
                cur = []
        else:
            cur.append(ln.strip())
    if cur:
        paras.append(' '.join(cur).strip())
    return paras


# ===================================================================
# Step 5 & 6: hyphen-join and paragraph join
# ===================================================================

HYPHEN_BREAK_RE = re.compile(r'(\w+)-\s*$')


def join_hyphen_breaks(text: str) -> str:
    """Join words split by a hyphen at end of line: 'sum-\\nmer' → 'summer'."""
    # Operate on the joined paragraph string (newlines already → spaces).
    # We can't easily distinguish real hyphens from break-hyphens after join,
    # so do this BEFORE the paragraph-join step instead (see pipeline).
    return text


# ===================================================================
# Conservative token-level garble strip
# ===================================================================

# Characters that are almost never part of real prose tokens.
# When a token is mostly these, drop it. When a token has them at edges,
# strip them.
NOISE_CHARS = set("|=©~}*_<>[]{}\\/")
NOISE_PURE_RE = re.compile(r'^[\|=\u00A9~\}*_<>\[\]\{\}\\/]+$')


def clean_token(tok: str) -> str:
    """Strip noise chars from token edges. Return '' if token is pure noise."""
    if not tok:
        return ''
    # Pure noise → drop entirely.
    if NOISE_PURE_RE.fullmatch(tok):
        return ''
    # Strip noise chars from the edges (but keep internal apostrophes/hyphens).
    cleaned = tok.strip('|=\u00A9~}*_<>[]{}\\/')
    # If after stripping the token is empty, drop it.
    if not cleaned:
        return ''
    # If the token still has internal noise chars (e.g. "Field=ing"), leave it
    # for the user to fix manually.
    return cleaned


def strip_garble_tokens(paragraph: str) -> str:
    """Strip clearly-garbled tokens from a paragraph.

    Two passes:
      1. Drop tokens that are pure noise punctuation (|=©~}*_<>[]).
      2. Strip noise chars from the edges of otherwise-normal tokens.
      3. Drop tokens that match is_garble_token() (digit-letter mix, etc.).
    Never removes whitelisted short words.
    """
    out_tokens: List[str] = []
    for tok in paragraph.split():
        # Pass 1+2: clean edges, drop pure-noise tokens.
        cleaned = clean_token(tok)
        if not cleaned:
            continue
        # Pass 3: drop garble tokens.
        if is_garble_token(cleaned):
            continue
        out_tokens.append(cleaned)
    return ' '.join(out_tokens)


# ===================================================================
# Main pipeline
# ===================================================================

def is_chapter_start(paragraph: str) -> Tuple[bool, str]:
    """Detect a chapter heading. Returns (is_chapter, heading_text).

    Recognizes:
      - "Preface", "Epilogue", "Afterword", "Coda", "Postscript" as standalone
        (possibly with a leading lowercase article like "the" left over from
        garble stripping — that prefix is removed from the heading).
      - "1952 My mother..." (year + capital) → chapter "1952"
    """
    s = paragraph.strip()
    if not s:
        return False, ''
    # Pure section header word, possibly with leading "the"/"a"/"an" prefix
    # left over from earlier garble (e.g. "the Preface").
    m = re.match(r'^(?:the\s+|a\s+|an\s+)?(Preface|Epilogue|Afterword|Coda|Postscript)\b', s, re.I)
    if m and len(s) <= 40:
        return True, m.group(1).capitalize()
    # Year-chapter: "1952 My mother was..."
    m = YEAR_CHAPTER_RE.match(s)
    if m:
        return True, m.group(1)
    return False, ''


def process(input_path: str, output_path: str) -> None:
    # --- Read input ---
    with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
        raw = f.read()

    # Normalize line endings.
    raw = raw.replace('\r\n', '\n').replace('\r', '\n')
    lines = raw.split('\n')

    # --- Step 1: cut frontmatter ---
    start = find_frontmatter_start(lines)
    body_lines = lines[start:]

    # --- Step 2: drop decorative blocks ---
    body_lines = drop_decorative_block(body_lines)

    # --- Step 5 (early): join hyphenated word breaks at end of lines ---
    # Operate on the line list before paragraph joining.
    joined_lines: List[str] = []
    i = 0
    while i < len(body_lines):
        ln = body_lines[i]
        # If a line ends with "word-", look at the next non-blank line.
        m = HYPHEN_BREAK_RE.search(ln)
        if m and i + 1 < len(body_lines):
            # Find next non-blank line.
            j = i + 1
            while j < len(body_lines) and body_lines[j].strip() == '':
                j += 1
            if j < len(body_lines):
                nxt = body_lines[j]
                # If next line starts with lowercase letters, this is a hyphen-break.
                first_word_match = re.match(r'^\s*([a-z][a-z]+)', nxt)
                if first_word_match:
                    # Re-join: keep everything before the word, glue word + first word of next line.
                    word_part = m.group(1)            # e.g. "experi"
                    suffix_word = first_word_match.group(1)  # e.g. "ment"
                    prefix = ln[:m.start(1)]           # everything before "experi"
                    rest_of_next = nxt[first_word_match.end():]
                    new_line = prefix + word_part + suffix_word + rest_of_next
                    joined_lines.append(new_line)
                    # Skip the next line (we consumed its first word).
                    # But preserve any blank lines between.
                    for k in range(i + 1, j):
                        joined_lines.append(body_lines[k])
                    i = j + 1
                    continue
        joined_lines.append(ln)
        i += 1
    body_lines = joined_lines

    # --- Step 3 (page numbers, standalone) ---
    cleaned: List[str] = []
    for ln in body_lines:
        if is_pagenum_line(ln):
            # Drop standalone page-number lines, but keep a blank separator
            # if the previous line was non-blank (so paragraphs don't merge).
            if cleaned and cleaned[-1].strip() != '':
                cleaned.append('')
            continue
        cleaned.append(ln)
    body_lines = cleaned

    # --- Step 6: split into paragraphs (blank-separated) ---
    paragraphs = split_paragraphs(body_lines)

    # --- Step 3 (page numbers, glued) + Step 3b (garble prefix) + trailing garble + token strip ---
    # v6 fix 1: Detect footnote (*) on the ORIGINAL paragraph BEFORE strip_garble_tokens
    #           strips the leading *. Pass the is_footnote flag to the chapter loop.
    # v6 fix 2: strip_glued_prefix removes short garble prefixes (Zo., ih, 213., etc.)
    processed_paras: List[Tuple[str, bool, bool]] = []  # (paragraph, is_footnote, had_prefix_stripped)
    for p in paragraphs:
        is_footnote = bool(FOOTNOTE_RE.match(p))  # check on ORIGINAL (before * strip)
        p = strip_glued_pagenum(p)
        p = strip_trailing_garble(p)
        p = strip_garble_tokens(p)   # removes noise chars (|, =, etc.) — MUST run before strip_glued_prefix
        p_before_prefix = p
        p = strip_glued_prefix(p)    # v6 fix 2: strip garble prefixes (now that noise chars are gone)
        had_prefix_stripped = (p != p_before_prefix)
        p = p.strip()
        if p:
            processed_paras.append((p, is_footnote, had_prefix_stripped))

    # --- Step 4: relocate footnotes to end of chapter ---
    # Walk through paragraphs. Track current chapter. Footnotes (starting with *)
    # are pulled out and appended at end of current chapter.
    output_blocks: List[str] = []
    current_chapter_paras: List[str] = []
    current_chapter_heading: str = ''
    current_footnotes: List[str] = []

    def flush_chapter():
        """Emit current chapter + its footnotes (if any)."""
        if current_chapter_heading:
            output_blocks.append(current_chapter_heading)
        output_blocks.extend(current_chapter_paras)
        if current_footnotes:
            output_blocks.append('')  # blank separator
            output_blocks.append('Notes:')
            output_blocks.extend(current_footnotes)

    for p, is_footnote, had_prefix in processed_paras:
        is_chap, heading = is_chapter_start(p)
        # v6: Don't treat as chapter heading if a garble prefix was stripped.
        # This prevents mid-text years (e.g. "1953 Just prior...") from being
        # misdetected as chapter headings after their garble prefix is removed.
        if is_chap and had_prefix:
            is_chap = False
        if is_chap:
            # Flush previous chapter.
            flush_chapter()
            # Start new chapter.
            current_chapter_heading = heading
            current_chapter_paras = []
            current_footnotes = []
            # If the chapter heading was a prefix (e.g. "1952 My mother..."),
            # the rest of the paragraph is the chapter's first paragraph.
            # Find the heading inside the paragraph and take everything after it.
            m = re.search(r'\b' + re.escape(heading) + r'\b', p)
            if m:
                rest = p[m.end():].strip()
            else:
                rest = p[len(heading):].strip()
            if rest:
                current_chapter_paras.append(rest)
            continue

        # Is this paragraph a footnote? (v6 fix 1: use flag from original detection)
        if is_footnote:
            current_footnotes.append(p)
            continue

        # Normal paragraph.
        current_chapter_paras.append(p)

    # Flush last chapter.
    flush_chapter()

    # --- Write output ---
    out_text = '\n\n'.join(output_blocks) + '\n'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(out_text)

    # --- Report stats ---
    print(f"v6 cleanup complete.")
    print(f"  Input:           {input_path}")
    print(f"  Output:          {output_path}")
    print(f"  Input lines:     {len(lines)}")
    print(f"  Body start line: {start + 1}  (\"{lines[start].strip()[:60]}\")")
    print(f"  Output blocks:   {len(output_blocks)}")
    print(f"  Output chars:    {len(out_text):,}")


# ===================================================================
# CLI
# ===================================================================

def main(argv: List[str]) -> int:
    if len(argv) >= 2:
        input_path = argv[1]
    else:
        input_path = DEFAULT_IN
    if len(argv) >= 3:
        output_path = argv[2]
    else:
        # Default output next to input.
        base, ext = os.path.splitext(input_path)
        output_path = base + '_v5' + (ext or '.txt')

    if not os.path.exists(input_path):
        print(f"ERROR: input file not found: {input_path}", file=sys.stderr)
        return 1

    process(input_path, output_path)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
