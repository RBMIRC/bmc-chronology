#!/usr/bin/env python3
"""
Parse Duberman's "Black Mountain: An Exploration in Community" (1972)
Extract events, people, and dates with page number citations.
"""

import json
import re
import PyPDF2
from datetime import datetime

PDF_PATH = "/Users/sylvain/Documents/DATA BMC/Duberman_Martin_Black_Mountain_College_An_Exploration_in_Community_1972-avec compression.pdf"
OUTPUT_FILE = "../duberman_extracted.json"
PROGRESS_FILE = "../duberman_parse_progress.json"

# Known BMC people for matching
KNOWN_PEOPLE = [
    "Josef Albers", "Anni Albers", "John Rice", "John Andrew Rice",
    "Theodore Dreier", "Ted Dreier", "Bobbie Dreier",
    "John Evarts", "M.C. Richards", "Mary Caroline Richards",
    "Charles Olson", "Robert Creeley", "Robert Duncan",
    "Buckminster Fuller", "Bucky Fuller", "John Cage", "Merce Cunningham",
    "Willem de Kooning", "Franz Kline", "Robert Rauschenberg",
    "Cy Twombly", "Ruth Asawa", "Max Dehn", "Stefan Wolpe",
    "Josef Breitenbach", "Hazel Larsen", "Eric Bentley",
    "Clement Greenberg", "Walter Gropius", "Albert Einstein",
    "Erwin Straus", "Heinrich Jalowetz", "Edward Lowinsky",
    "Xanti Schawinsky", "Robert Wunsch", "Frederick Georgia",
    "Molly Gregory", "Joseph Martin", "Ralph Lounsbury",
    "William Hinckley", "Emily Zastrow", "Frank Rice", "Nell Rice",
    "Natasha Goldowski", "John Wallen", "Trude Guermonprez",
    "Karen Karnes", "David Weinrib", "Arthur Penn",
    "Paul Williams", "Fielding Dawson", "Jonathan Williams",
    "Joel Oppenheimer", "Francine du Plessix", "Vera Williams"
]

# Month patterns
MONTHS = r'(?:January|February|March|April|May|June|July|August|September|October|November|December)'

def extract_dates(text):
    """Extract dates from text"""
    dates = []

    # Full date: January 15, 1945
    pattern1 = rf'({MONTHS})\s+(\d{{1,2}}),?\s+(19[3-5]\d)'
    for match in re.finditer(pattern1, text):
        dates.append({
            'type': 'exact',
            'raw': match.group(0),
            'month': match.group(1),
            'day': int(match.group(2)),
            'year': int(match.group(3)),
            'position': match.start()
        })

    # Month Year: January 1945
    pattern2 = rf'({MONTHS})\s+(19[3-5]\d)'
    for match in re.finditer(pattern2, text):
        # Check not already captured as full date
        already_captured = any(d['position'] == match.start() for d in dates)
        if not already_captured:
            dates.append({
                'type': 'month',
                'raw': match.group(0),
                'month': match.group(1),
                'year': int(match.group(2)),
                'position': match.start()
            })

    # Year range in text: 1933-1934 or 1933-34
    pattern3 = r'\b(19[3-5]\d)[-–](19[3-5]\d|\d{2})\b'
    for match in re.finditer(pattern3, text):
        end = match.group(2)
        if len(end) == 2:
            end = match.group(1)[:2] + end
        dates.append({
            'type': 'range',
            'raw': match.group(0),
            'start_year': int(match.group(1)),
            'end_year': int(end),
            'position': match.start()
        })

    # Seasons: fall 1945, spring of 1946
    pattern4 = r'(?:fall|spring|summer|winter)\s+(?:of\s+)?(19[3-5]\d)'
    for match in re.finditer(pattern4, text, re.IGNORECASE):
        dates.append({
            'type': 'season',
            'raw': match.group(0),
            'year': int(match.group(1)),
            'position': match.start()
        })

    return dates


def extract_people(text):
    """Extract people names from text"""
    found = []

    for person in KNOWN_PEOPLE:
        if person.lower() in text.lower():
            # Find actual case in text
            pattern = re.compile(re.escape(person), re.IGNORECASE)
            match = pattern.search(text)
            if match:
                found.append(match.group(0))

    return list(set(found))


def extract_events(text, page_num):
    """Extract potential events from text"""
    events = []

    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)

    for sentence in sentences:
        # Skip very short or very long sentences
        if len(sentence) < 30 or len(sentence) > 500:
            continue

        # Look for sentences with dates
        dates = extract_dates(sentence)
        if not dates:
            continue

        # Look for action verbs indicating events
        event_verbs = r'\b(?:arrived|left|came|went|visited|founded|opened|closed|began|started|ended|died|born|married|hired|fired|resigned|elected|appointed|performed|exhibited|taught|lectured|wrote|published|built|constructed|moved|returned)\b'

        if re.search(event_verbs, sentence, re.IGNORECASE):
            people = extract_people(sentence)

            events.append({
                'text': sentence.strip(),
                'dates': dates,
                'people': people,
                'page': page_num,
                'source': f'Page {page_num}'
            })

    return events


def is_readable_text(text):
    """Check if extracted text is readable (not garbled OCR)"""
    if not text or len(text) < 100:
        return False

    # Count readable words vs garbage
    words = text.split()
    readable_words = sum(1 for w in words if re.match(r'^[a-zA-Z]{2,}$', w))

    return readable_words / max(len(words), 1) > 0.5


def load_progress():
    """Load parsing progress"""
    try:
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {'last_page': 0, 'pages_data': [], 'events': []}


def save_progress(progress):
    """Save parsing progress"""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, ensure_ascii=False)


def main():
    print("=" * 70)
    print("PARSING DUBERMAN'S BLACK MOUNTAIN COLLEGE")
    print("617 pages - Extracting events, people, dates")
    print("=" * 70)

    progress = load_progress()
    start_page = progress['last_page']
    all_events = progress['events']
    pages_data = progress['pages_data']

    print(f"\nResuming from page {start_page}")
    print(f"Already extracted: {len(all_events)} events\n")

    # Open PDF
    with open(PDF_PATH, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        total_pages = len(reader.pages)

        print(f"Total pages: {total_pages}")

        readable_pages = 0

        for page_num in range(start_page, total_pages):
            # Extract text
            try:
                text = reader.pages[page_num].extract_text()
            except Exception as e:
                print(f"[{page_num+1:3d}] Error: {e}")
                continue

            if not is_readable_text(text):
                if page_num % 50 == 0:
                    print(f"[{page_num+1:3d}] Skipped (image/garbled)")
                continue

            readable_pages += 1

            # Clean text
            text = ' '.join(text.split())

            # Extract events
            events = extract_events(text, page_num + 1)  # 1-indexed pages

            if events:
                all_events.extend(events)
                print(f"[{page_num+1:3d}] Found {len(events)} events")
            elif page_num % 100 == 0:
                print(f"[{page_num+1:3d}] Readable, no events")

            # Store page data
            pages_data.append({
                'page': page_num + 1,
                'text_length': len(text),
                'dates_found': len(extract_dates(text)),
                'people_found': len(extract_people(text))
            })

            # Save progress every 50 pages
            if page_num % 50 == 0:
                progress['last_page'] = page_num
                progress['events'] = all_events
                progress['pages_data'] = pages_data
                save_progress(progress)

    # Final save
    progress['last_page'] = total_pages
    progress['events'] = all_events
    progress['pages_data'] = pages_data
    save_progress(progress)

    # Create output
    output = {
        'metadata': {
            'source': 'DUBERMAN, Martin. Black Mountain: An Exploration in Community. New York: E.P. Dutton, 1972.',
            'total_pages': total_pages,
            'readable_pages': readable_pages,
            'total_events': len(all_events),
            'parsed_at': datetime.now().isoformat()
        },
        'events': all_events
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Statistics
    all_people = set()
    all_dates = []
    for event in all_events:
        all_people.update(event.get('people', []))
        all_dates.extend(event.get('dates', []))

    print(f"\n{'=' * 70}")
    print("PARSING COMPLETE")
    print(f"{'=' * 70}")
    print(f"\nReadable pages: {readable_pages}/{total_pages}")
    print(f"Events extracted: {len(all_events)}")
    print(f"Unique people mentioned: {len(all_people)}")
    print(f"Date references: {len(all_dates)}")
    print(f"\nOutput: {OUTPUT_FILE}")


if __name__ == '__main__':
    main()
