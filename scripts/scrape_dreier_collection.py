#!/usr/bin/env python3
"""
Scraper for the Theodore Dreier Sr., Black Mountain College Documents Collection
From Asheville Art Museum: https://collection.ashevilleart.org
377 documents total
"""

import json
import re
import time
import urllib.request
import urllib.parse
import ssl
from datetime import datetime

# SSL context (bypass verification for this research project)
SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE

BASE_URL = "https://collection.ashevilleart.org/objects-1/info"
QUERY = "Portfolios = \"579\""
OUTPUT_FILE = "../dreier_collection_raw.json"
PROGRESS_FILE = "../dreier_scrape_progress.json"
TOTAL_DOCUMENTS = 377


def fetch_document(page_num, max_retries=3):
    """Fetch a single document page"""
    url = f"{BASE_URL}?query={urllib.parse.quote(QUERY)}&sort=0&page={page_num}"

    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            with urllib.request.urlopen(req, timeout=30, context=SSL_CONTEXT) as response:
                return response.read().decode('utf-8')
        except Exception as e:
            print(f"  Retry {attempt + 1}: {e}")
            time.sleep(2 ** attempt)

    return None


def parse_document_html(html, page_num):
    """Extract structured data from document HTML"""

    doc = {
        'page_num': page_num,
        'source_url': f"{BASE_URL}?query={urllib.parse.quote(QUERY)}&sort=0&page={page_num}",
        'source': 'Theodore Dreier Sr., Black Mountain College Documents Collection, Asheville Art Museum'
    }

    # Title from H1
    title_match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    if title_match:
        doc['title'] = re.sub(r'\s+', ' ', title_match.group(1)).strip()

    # Object ID / Accession Number
    id_match = re.search(r'<span[^>]*class="[^"]*heading-small[^"]*"[^>]*>\s*Object ID\s*</span>.*?<div[^>]*class="[^"]*object-info-section[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL | re.IGNORECASE)
    if id_match:
        doc['object_id'] = re.sub(r'<[^>]+>', '', id_match.group(1)).strip()
    else:
        # Alternative: look for accession number pattern
        acc_match = re.search(r'(\d{4}\.\d+\.\d+(?:\.\d+)?)', html)
        if acc_match:
            doc['object_id'] = acc_match.group(1)

    # Date
    date_match = re.search(r'<span[^>]*class="[^"]*heading-small[^"]*"[^>]*>\s*Date\s*</span>.*?<div[^>]*class="[^"]*object-info-section[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL | re.IGNORECASE)
    if date_match:
        doc['date'] = re.sub(r'<[^>]+>', '', date_match.group(1)).strip()

    # Medium
    medium_match = re.search(r'<span[^>]*class="[^"]*heading-small[^"]*"[^>]*>\s*Medium[^<]*</span>.*?<div[^>]*class="[^"]*object-info-section[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL | re.IGNORECASE)
    if medium_match:
        doc['medium'] = re.sub(r'<[^>]+>', '', medium_match.group(1)).strip()

    # Credit Line
    credit_match = re.search(r'<span[^>]*class="[^"]*heading-small[^"]*"[^>]*>\s*Credit Line\s*</span>.*?<div[^>]*class="[^"]*object-info-section[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL | re.IGNORECASE)
    if credit_match:
        doc['credit_line'] = re.sub(r'<[^>]+>', '', credit_match.group(1)).strip()

    # Description (in embarkInfoNotes)
    desc_match = re.search(r'<span[^>]*class="[^"]*heading-small[^"]*"[^>]*>\s*Description\s*</span>.*?<div[^>]*class="[^"]*embarkInfoNotes[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL | re.IGNORECASE)
    if desc_match:
        desc = re.sub(r'<[^>]+>', ' ', desc_match.group(1))
        desc = re.sub(r'\s+', ' ', desc).strip()
        doc['description'] = desc

    # Artist/Creator
    artist_match = re.search(r'<span[^>]*class="[^"]*heading-small[^"]*"[^>]*>\s*Artist\s*</span>.*?<div[^>]*class="[^"]*object-info-section[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL | re.IGNORECASE)
    if artist_match:
        doc['artist'] = re.sub(r'<[^>]+>', '', artist_match.group(1)).strip()

    # Dimensions
    dim_match = re.search(r'<span[^>]*class="[^"]*heading-small[^"]*"[^>]*>\s*Dimensions\s*</span>.*?<div[^>]*class="[^"]*object-info-section[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL | re.IGNORECASE)
    if dim_match:
        doc['dimensions'] = re.sub(r'<[^>]+>', '', dim_match.group(1)).strip()

    # Extract people mentioned in description
    if doc.get('description'):
        doc['extracted_people'] = extract_people(doc['description'])
        doc['extracted_dates'] = extract_dates(doc['description'])

    # Document type classification
    doc['document_type'] = classify_document(doc.get('title', ''), doc.get('medium', ''))

    return doc


def extract_people(text):
    """Extract potential people names from text"""
    people = []

    # Known BMC faculty/staff patterns
    known_patterns = [
        r'Josef Albers', r'Anni Albers', r'John Rice', r'Theodore Dreier',
        r'John Evarts', r'M\.?C\.? Richards', r'Charles Olson', r'Robert Creeley',
        r'Buckminster Fuller', r'John Cage', r'Merce Cunningham', r'Willem de Kooning',
        r'Franz Kline', r'Robert Rauschenberg', r'Cy Twombly', r'Ruth Asawa',
        r'Max Dehn', r'Stefan Wolpe', r'Josef Breitenbach', r'Hazel Larsen'
    ]

    for pattern in known_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            people.append(re.search(pattern, text, re.IGNORECASE).group(0))

    # General name pattern: First Last (avoiding common false positives)
    name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?[A-Z][a-z]{2,})\b'
    stopwords = {'Black Mountain', 'North Carolina', 'New York', 'United States',
                 'Fall Term', 'Spring Term', 'Summer Session', 'Art Museum',
                 'Blue Ridge', 'Advisory Council', 'Board Fellows', 'Lake Eden'}

    for match in re.finditer(name_pattern, text):
        name = match.group(1)
        if name not in stopwords and name not in people:
            people.append(name)

    return list(set(people))


def extract_dates(text):
    """Extract dates mentioned in text"""
    dates = []

    # Full dates: Month Day, Year
    for match in re.finditer(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})', text):
        dates.append({
            'type': 'exact',
            'raw': match.group(0),
            'month': match.group(1),
            'day': int(match.group(2)),
            'year': int(match.group(3))
        })

    # Year ranges: 1933-1934
    for match in re.finditer(r'\b(19[3-5]\d)[-–](19[3-5]\d|\d{2})\b', text):
        end_year = match.group(2)
        if len(end_year) == 2:
            end_year = match.group(1)[:2] + end_year
        dates.append({
            'type': 'range',
            'raw': match.group(0),
            'start_year': int(match.group(1)),
            'end_year': int(end_year)
        })

    # Single years
    seen_years = set()
    for d in dates:
        if 'year' in d:
            seen_years.add(d['year'])
        if 'start_year' in d:
            seen_years.add(d['start_year'])
            seen_years.add(d['end_year'])

    for match in re.finditer(r'\b(19[3-5]\d)\b', text):
        year = int(match.group(1))
        if year not in seen_years:
            dates.append({
                'type': 'year',
                'raw': match.group(0),
                'year': year
            })
            seen_years.add(year)

    return dates


def classify_document(title, medium):
    """Classify document type based on title and medium"""
    title_lower = title.lower() if title else ''
    medium_lower = medium.lower() if medium else ''

    if 'catalogue' in title_lower or 'catalog' in title_lower:
        return 'catalogue'
    elif 'bulletin' in title_lower:
        return 'bulletin'
    elif 'newsletter' in title_lower:
        return 'newsletter'
    elif 'letter' in title_lower or 'correspondence' in medium_lower:
        return 'correspondence'
    elif 'photograph' in medium_lower or 'photo' in title_lower:
        return 'photograph'
    elif 'announcement' in title_lower:
        return 'announcement'
    elif 'program' in title_lower:
        return 'program'
    elif 'report' in title_lower:
        return 'report'
    elif 'schedule' in title_lower or 'calendar' in title_lower:
        return 'schedule'
    elif 'pamphlet' in medium_lower:
        return 'pamphlet'
    else:
        return 'document'


def load_progress():
    """Load scraping progress"""
    try:
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {'last_page': 0, 'documents': []}


def save_progress(progress):
    """Save scraping progress"""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)


def main():
    print("=" * 70)
    print("DREIER COLLECTION SCRAPER")
    print("Theodore Dreier Sr., Black Mountain College Documents Collection")
    print("Asheville Art Museum - 377 documents")
    print("=" * 70)

    progress = load_progress()
    start_page = progress['last_page'] + 1
    documents = progress['documents']

    print(f"\nResuming from page {start_page}")
    print(f"Already scraped: {len(documents)} documents\n")

    for page in range(start_page, TOTAL_DOCUMENTS + 1):
        print(f"[{page:3d}/{TOTAL_DOCUMENTS}] ", end="", flush=True)

        html = fetch_document(page)

        if html:
            doc = parse_document_html(html, page)
            documents.append(doc)

            title = doc.get('title', 'No title')[:50]
            date = doc.get('date', 'No date')
            print(f"✓ {title}... ({date})")
        else:
            print("✗ FAILED")
            documents.append({'page_num': page, 'error': 'fetch_failed'})

        # Save progress every 10 documents
        if page % 10 == 0:
            progress['last_page'] = page
            progress['documents'] = documents
            save_progress(progress)
            print(f"    [Saved progress: {len(documents)} documents]")

        # Rate limiting - be respectful to the server
        time.sleep(0.5)

    # Final save
    progress['last_page'] = TOTAL_DOCUMENTS
    progress['documents'] = documents
    save_progress(progress)

    # Create final output
    output = {
        'metadata': {
            'source': 'Theodore Dreier Sr., Black Mountain College Documents Collection',
            'institution': 'Asheville Art Museum',
            'collection_url': 'https://collection.ashevilleart.org/objects-1/portfolio?query=Portfolios%20%3D%20%22579%22',
            'total_documents': len(documents),
            'scraped_at': datetime.now().isoformat(),
            'credit': 'Black Mountain College Collection, gift of Barbara Beate Dreier and Theodore Dreier Jr.'
        },
        'documents': documents
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Statistics
    doc_types = {}
    total_people = set()
    total_dates = 0

    for doc in documents:
        dt = doc.get('document_type', 'unknown')
        doc_types[dt] = doc_types.get(dt, 0) + 1

        for p in doc.get('extracted_people', []):
            total_people.add(p)

        total_dates += len(doc.get('extracted_dates', []))

    print(f"\n{'=' * 70}")
    print("SCRAPING COMPLETE")
    print(f"{'=' * 70}")
    print(f"\nTotal documents: {len(documents)}")
    print(f"Unique people extracted: {len(total_people)}")
    print(f"Dates extracted: {total_dates}")
    print(f"\nDocument types:")
    for dt, count in sorted(doc_types.items(), key=lambda x: -x[1]):
        print(f"  {dt}: {count}")
    print(f"\nOutput: {OUTPUT_FILE}")


if __name__ == '__main__':
    main()
