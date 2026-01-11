#!/usr/bin/env python3
"""
Integrate Dreier Collection events into the main BMC archive.
"""

import json
import re
from datetime import datetime

DREIER_FILE = "../dreier_events.json"
ARCHIVE_FILE = "../bmc_complete_archive.json"
OUTPUT_FILE = "../bmc_complete_archive.json"

def date_to_key(date_info):
    """Convert date info to YYYY-MM-DD key"""
    if not date_info:
        return None

    date_type = date_info.get('type', '')

    if date_type == 'exact':
        return f"{date_info['year']}-{date_info['month']:02d}-{date_info['day']:02d}"
    elif date_type == 'month':
        return f"{date_info['year']}-{date_info['month']:02d}-01"
    elif date_type == 'year':
        return f"{date_info['year']}-01-01"
    elif date_type == 'academic_year':
        # Use start of academic year (September 1)
        return f"{date_info['start_year']}-09-01"
    elif date_type == 'circa':
        return f"{date_info['year']}-01-01"
    else:
        return None


def create_bmc_event(dreier_event):
    """Convert Dreier event to BMC archive event format"""
    event = {
        'event': f"Document: {dreier_event['document']['title']}",
        'category': dreier_event.get('category', 'administrative'),
        'certainty': dreier_event.get('certainty', 95),
        'people': dreier_event.get('people', []),
        'source': f"Dreier Collection, {dreier_event['source']['object_id']}",
        'source_url': dreier_event['source']['url'],
        'document_type': dreier_event['document'].get('type', 'document')
    }

    # Add description if available (truncate for display)
    desc = dreier_event.get('description', '')
    if desc:
        event['description'] = desc[:500] + '...' if len(desc) > 500 else desc

    return event


def main():
    print("=" * 70)
    print("INTEGRATING DREIER EVENTS INTO BMC ARCHIVE")
    print("=" * 70)

    # Load data
    print("\nLoading data...")
    with open(DREIER_FILE, 'r', encoding='utf-8') as f:
        dreier_data = json.load(f)

    with open(ARCHIVE_FILE, 'r', encoding='utf-8') as f:
        archive = json.load(f)

    dreier_events = dreier_data.get('events', [])
    print(f"  Dreier events: {len(dreier_events)}")
    print(f"  Archive years: {len(archive.get('daily_calendar', {}))}")

    # Ensure daily_calendar structure exists
    if 'daily_calendar' not in archive:
        archive['daily_calendar'] = {}

    # Track statistics
    added = 0
    skipped = 0
    by_year = {}

    # Process each Dreier event
    print("\nProcessing events...")
    for dreier_event in dreier_events:
        date_info = dreier_event.get('date', {})
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
        bmc_event = create_bmc_event(dreier_event)
        archive['daily_calendar'][year][date_key]['bmc_events'].append(bmc_event)

        added += 1
        by_year[year] = by_year.get(year, 0) + 1

    print(f"  Events added: {added}")
    print(f"  Events skipped (no date): {skipped}")

    # Update metadata
    archive['metadata'] = archive.get('metadata', {})
    archive['metadata']['dreier_integration'] = {
        'integrated_at': datetime.now().isoformat(),
        'events_added': added,
        'source': 'Theodore Dreier Sr., Black Mountain College Documents Collection',
        'institution': 'Asheville Art Museum'
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
