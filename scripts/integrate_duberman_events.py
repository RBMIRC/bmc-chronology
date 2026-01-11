#!/usr/bin/env python3
"""
Integrate Duberman events into the main BMC archive.
Add proper ISO 690 citations.
"""

import json
import re
from datetime import datetime

DUBERMAN_FILE = "../duberman_extracted.json"
ARCHIVE_FILE = "../bmc_complete_archive.json"
OUTPUT_FILE = "../bmc_complete_archive.json"

# ISO 690 citation format
CITATION_BASE = "DUBERMAN, Martin. Black Mountain: An Exploration in Community. New York: E.P. Dutton, 1972."

# Month name to number
MONTHS = {
    'January': 1, 'February': 2, 'March': 3, 'April': 4,
    'May': 5, 'June': 6, 'July': 7, 'August': 8,
    'September': 9, 'October': 10, 'November': 11, 'December': 12
}

# Season to month approximation
SEASONS = {
    'spring': 3,   # March
    'summer': 6,   # June
    'fall': 9,     # September
    'winter': 12   # December
}


def date_to_key(date_info):
    """Convert date info to YYYY-MM-DD key"""
    if not date_info:
        return None

    date_type = date_info.get('type', '')

    if date_type == 'exact':
        month_num = MONTHS.get(date_info.get('month', ''), 1)
        return f"{date_info['year']}-{month_num:02d}-{date_info.get('day', 1):02d}"
    elif date_type == 'month':
        month_num = MONTHS.get(date_info.get('month', ''), 1)
        return f"{date_info['year']}-{month_num:02d}-01"
    elif date_type == 'season':
        raw = date_info.get('raw', '').lower()
        month = 1
        for season, m in SEASONS.items():
            if season in raw:
                month = m
                break
        return f"{date_info['year']}-{month:02d}-01"
    elif date_type == 'range':
        # Use start year, September 1 (academic year start)
        return f"{date_info['start_year']}-09-01"
    else:
        return None


def create_bmc_event(duberman_event):
    """Convert Duberman event to BMC archive event format"""
    page = duberman_event.get('page', 0)

    # Create ISO 690 citation
    citation = f"{CITATION_BASE} p. {page}."

    event = {
        'event': duberman_event.get('text', '')[:200] + ('...' if len(duberman_event.get('text', '')) > 200 else ''),
        'full_text': duberman_event.get('text', ''),
        'category': 'historical',
        'certainty': 90,  # High certainty for secondary source
        'people': duberman_event.get('people', []),
        'source': citation,
        'source_type': 'secondary',
        'page': page
    }

    return event


def main():
    print("=" * 70)
    print("INTEGRATING DUBERMAN EVENTS INTO BMC ARCHIVE")
    print("=" * 70)

    # Load data
    print("\nLoading data...")
    with open(DUBERMAN_FILE, 'r', encoding='utf-8') as f:
        duberman_data = json.load(f)

    with open(ARCHIVE_FILE, 'r', encoding='utf-8') as f:
        archive = json.load(f)

    duberman_events = duberman_data.get('events', [])
    print(f"  Duberman events: {len(duberman_events)}")
    print(f"  Archive years: {len(archive.get('daily_calendar', {}))}")

    # Ensure daily_calendar structure exists
    if 'daily_calendar' not in archive:
        archive['daily_calendar'] = {}

    # Track statistics
    added = 0
    skipped = 0
    by_year = {}

    # Process each Duberman event
    print("\nProcessing events...")
    for duberman_event in duberman_events:
        dates = duberman_event.get('dates', [])
        if not dates:
            skipped += 1
            continue

        # Use first date
        date_info = dates[0]
        date_key = date_to_key(date_info)

        if not date_key:
            skipped += 1
            continue

        year = date_key[:4]

        # Ensure year and date structures exist
        if year not in archive['daily_calendar']:
            archive['daily_calendar'][year] = {}

        if date_key not in archive['daily_calendar'][year]:
            archive['daily_calendar'][year][date_key] = {
                'bmc_events': [],
                'world_events': []
            }

        # Ensure bmc_events list exists
        if 'bmc_events' not in archive['daily_calendar'][year][date_key]:
            archive['daily_calendar'][year][date_key]['bmc_events'] = []

        # Create and add the event
        bmc_event = create_bmc_event(duberman_event)
        archive['daily_calendar'][year][date_key]['bmc_events'].append(bmc_event)

        added += 1
        by_year[year] = by_year.get(year, 0) + 1

    print(f"  Events added: {added}")
    print(f"  Events skipped (no date): {skipped}")

    # Update metadata
    archive['metadata'] = archive.get('metadata', {})
    archive['metadata']['duberman_integration'] = {
        'integrated_at': datetime.now().isoformat(),
        'events_added': added,
        'source': CITATION_BASE,
        'source_type': 'secondary'
    }

    # Save updated archive
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(archive, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Archive updated: {OUTPUT_FILE}")

    # Show distribution by year
    print("\nEvents added by year:")
    for year in sorted(by_year.keys()):
        print(f"  {year}: {by_year[year]}")


if __name__ == '__main__':
    main()
