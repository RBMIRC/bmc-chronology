#!/usr/bin/env python3
"""
Process scraped Dreier Collection documents into events.
Each document becomes an event (date of creation/edition).
"""

import json
import re
from datetime import datetime

INPUT_FILE = "../dreier_collection_raw.json"
OUTPUT_FILE = "../dreier_events.json"
PEOPLE_INDEX = "../bmc_people_index.json"


def parse_date_string(date_str):
    """Parse various date formats into structured date"""
    if not date_str:
        return None

    date_str = date_str.strip()

    # Year range: 1933-1934
    match = re.match(r'^(\d{4})-(\d{4})$', date_str)
    if match:
        return {
            'type': 'academic_year',
            'start_year': int(match.group(1)),
            'end_year': int(match.group(2)),
            'display': date_str
        }

    # Year range short: 1933-34
    match = re.match(r'^(\d{4})-(\d{2})$', date_str)
    if match:
        start = int(match.group(1))
        end = int(match.group(1)[:2] + match.group(2))
        return {
            'type': 'academic_year',
            'start_year': start,
            'end_year': end,
            'display': f"{start}-{end}"
        }

    # Single year: 1945
    match = re.match(r'^(\d{4})$', date_str)
    if match:
        return {
            'type': 'year',
            'year': int(match.group(1)),
            'display': date_str
        }

    # Month Year: September 1945
    match = re.match(r'^(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})$', date_str)
    if match:
        months = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
                  'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}
        return {
            'type': 'month',
            'year': int(match.group(2)),
            'month': months[match.group(1)],
            'display': date_str
        }

    # Full date: September 25, 1933
    match = re.match(r'^(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})$', date_str)
    if match:
        months = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
                  'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}
        return {
            'type': 'exact',
            'year': int(match.group(3)),
            'month': months[match.group(1)],
            'day': int(match.group(2)),
            'display': date_str
        }

    # Circa/approximate
    match = re.match(r'^c\.?\s*(\d{4})$', date_str, re.IGNORECASE)
    if match:
        return {
            'type': 'circa',
            'year': int(match.group(1)),
            'display': f"c. {match.group(1)}"
        }

    return {'type': 'unknown', 'raw': date_str, 'display': date_str}


def normalize_name(name, people_index):
    """Try to match a name to the people index"""
    if not name:
        return None

    name_lower = name.lower()

    # Direct match
    if name in people_index:
        return name

    # Case-insensitive match
    for indexed_name in people_index.keys():
        if indexed_name.lower() == name_lower:
            return indexed_name

    # Partial match (last name)
    name_parts = name.split()
    if len(name_parts) >= 2:
        last_name = name_parts[-1].lower()
        for indexed_name in people_index.keys():
            if last_name in indexed_name.lower():
                return indexed_name

    return name  # Return original if no match


def create_document_event(doc, people_index):
    """Create an event from a document"""
    event = {
        'event_type': 'document_created',
        'source': {
            'collection': 'Theodore Dreier Sr., Black Mountain College Documents Collection',
            'institution': 'Asheville Art Museum',
            'object_id': doc.get('object_id', ''),
            'url': doc.get('source_url', ''),
            'credit': doc.get('credit_line', '')
        },
        'document': {
            'title': doc.get('title', '').replace('&amp;', '&').replace('&quot;', '"'),
            'type': doc.get('document_type', 'document'),
            'medium': doc.get('medium', ''),
            'dimensions': doc.get('dimensions', '')
        },
        'description': doc.get('description', ''),
        'certainty': 95  # High certainty for primary source documents
    }

    # Parse date
    date_info = parse_date_string(doc.get('date', ''))
    if date_info:
        event['date'] = date_info

    # Extract and normalize people
    people = []
    for name in doc.get('extracted_people', []):
        normalized = normalize_name(name, people_index)
        if normalized:
            people.append(normalized)
    event['people'] = list(set(people))

    # Add dates mentioned in description
    if doc.get('extracted_dates'):
        event['dates_mentioned'] = doc['extracted_dates']

    # Classify event category based on document type
    doc_type = doc.get('document_type', '')
    if doc_type == 'catalogue':
        event['category'] = 'administrative'
        event['subcategory'] = 'publication'
    elif doc_type == 'bulletin':
        event['category'] = 'administrative'
        event['subcategory'] = 'publication'
    elif doc_type == 'correspondence':
        event['category'] = 'communication'
    elif doc_type == 'photograph':
        event['category'] = 'documentation'
    elif doc_type == 'program':
        event['category'] = 'performance'
    elif doc_type == 'announcement':
        event['category'] = 'administrative'
    else:
        event['category'] = 'administrative'

    return event


def main():
    print("=" * 70)
    print("PROCESSING DREIER COLLECTION INTO EVENTS")
    print("=" * 70)

    # Load data
    print("\nLoading data...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        dreier_data = json.load(f)

    with open(PEOPLE_INDEX, 'r', encoding='utf-8') as f:
        people_index = json.load(f)

    documents = dreier_data.get('documents', [])
    print(f"  Documents: {len(documents)}")
    print(f"  People index: {len(people_index)} people")

    # Process documents into events
    print("\nProcessing documents...")
    events = []
    by_year = {}

    for doc in documents:
        if doc.get('error'):
            continue

        event = create_document_event(doc, people_index)
        events.append(event)

        # Organize by year
        date_info = event.get('date', {})
        year = date_info.get('year') or date_info.get('start_year')
        if year:
            if year not in by_year:
                by_year[year] = []
            by_year[year].append(event)

    print(f"  Events created: {len(events)}")
    print(f"  Years covered: {min(by_year.keys()) if by_year else 'N/A'} - {max(by_year.keys()) if by_year else 'N/A'}")

    # Statistics
    categories = {}
    doc_types = {}
    total_people = set()

    for event in events:
        cat = event.get('category', 'unknown')
        categories[cat] = categories.get(cat, 0) + 1

        dt = event.get('document', {}).get('type', 'unknown')
        doc_types[dt] = doc_types.get(dt, 0) + 1

        for p in event.get('people', []):
            total_people.add(p)

    print(f"\nStatistics:")
    print(f"  Unique people mentioned: {len(total_people)}")
    print(f"\n  By category:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"    {cat}: {count}")
    print(f"\n  By document type:")
    for dt, count in sorted(doc_types.items(), key=lambda x: -x[1]):
        print(f"    {dt}: {count}")

    # Save output
    output = {
        'metadata': {
            'source': 'Theodore Dreier Sr., Black Mountain College Documents Collection',
            'processed_at': datetime.now().isoformat(),
            'total_events': len(events),
            'years_covered': sorted(by_year.keys()) if by_year else []
        },
        'events': events,
        'by_year': {str(k): v for k, v in sorted(by_year.items())}
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Output saved to: {OUTPUT_FILE}")


if __name__ == '__main__':
    main()
