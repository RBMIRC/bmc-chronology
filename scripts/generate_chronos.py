#!/usr/bin/env python3
"""
Generate comprehensive daily chronology from chronos 2 data
"""

import json
import re
from collections import defaultdict
from datetime import datetime, timedelta

# Load the most comprehensive file
CHRONOS_PATH = "/Users/sylvain/Documents/DATA BMC/chronos 2/bmc_chronology_wikipedia.json"
PEOPLE_PATH = "/Users/sylvain/Documents/DATA BMC/chronos 2/bmc_people_index.json"
OUTPUT_PATH = "/Users/sylvain/Documents/BMC-RADIO-SITE/bmc_chronos_complete.json"

def parse_date(date_str, precision):
    """Parse various date formats and return list of (date_key, is_exact)"""
    dates = []

    if not date_str:
        return dates

    # Exact date: "1933-01-05" or "October 16, 1933"
    if precision in ['day', 'exact']:
        # Try ISO format
        match = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', date_str)
        if match:
            dates.append((date_str, True))
            return dates

        # Try "Month Day, Year" format
        match = re.match(r'^([A-Za-z]+)\s+(\d+),?\s+(\d{4})$', date_str)
        if match:
            month_name, day, year = match.groups()
            months = {'January': '01', 'February': '02', 'March': '03', 'April': '04',
                     'May': '05', 'June': '06', 'July': '07', 'August': '08',
                     'September': '09', 'October': '10', 'November': '11', 'December': '12'}
            if month_name in months:
                date_key = f"{year}-{months[month_name]}-{int(day):02d}"
                dates.append((date_key, True))
                return dates

    # Month precision: "March 1935"
    if precision == 'month':
        match = re.match(r'^([A-Za-z]+)\s+(\d{4})$', date_str)
        if match:
            month_name, year = match.groups()
            months = {'January': '01', 'February': '02', 'March': '03', 'April': '04',
                     'May': '05', 'June': '06', 'July': '07', 'August': '08',
                     'September': '09', 'October': '10', 'November': '11', 'December': '12'}
            if month_name in months:
                # Use first day of month
                date_key = f"{year}-{months[month_name]}-01"
                dates.append((date_key, False))
                return dates

    # Year precision: "1933"
    if precision == 'year':
        match = re.match(r'^(\d{4})$', date_str)
        if match:
            year = match.group(1)
            # Use January 1st
            date_key = f"{year}-01-01"
            dates.append((date_key, False))
            return dates

    # Academic year: "1933-1934" or "1946-47"
    match = re.match(r'^(\d{4})-(\d{2,4})$', date_str)
    if match:
        year1 = match.group(1)
        # Use September 1st (start of academic year)
        date_key = f"{year1}-09-01"
        dates.append((date_key, False))
        return dates

    # Approximate: "1930s", "early 1930s"
    match = re.search(r'(\d{4})s', date_str)
    if match:
        decade_start = match.group(1)
        date_key = f"{decade_start}-01-01"
        dates.append((date_key, False))
        return dates

    # Try to extract any year
    match = re.search(r'(\d{4})', date_str)
    if match:
        year = match.group(1)
        date_key = f"{year}-01-01"
        dates.append((date_key, False))
        return dates

    return dates

def get_certainty(event):
    """Calculate certainty based on source and precision"""
    precision = event.get('date_precision', 'approximate')
    source = event.get('source', '')
    confidence = event.get('confidence', '')

    base_certainty = {
        'exact': 95,
        'day': 90,
        'month': 75,
        'year': 60,
        'approximate': 40
    }.get(precision, 50)

    # Adjust based on source
    if 'Harris interview' in source or 'Oral history' in source:
        base_certainty = min(95, base_certainty + 10)
    elif 'Page' in source and 'Duberman' in str(event.get('context', '')):
        base_certainty = min(95, base_certainty + 5)

    if confidence == 'high':
        base_certainty = min(95, base_certainty + 10)

    return base_certainty

def main():
    print("Loading chronology data...")
    with open(CHRONOS_PATH, 'r') as f:
        chronos = json.load(f)

    print(f"Total events: {len(chronos['events'])}")

    # Build daily calendar
    daily_calendar = defaultdict(lambda: defaultdict(lambda: {
        'events': [],
        'people_present': set()
    }))

    events_processed = 0
    events_skipped = 0

    for event in chronos['events']:
        date_str = event.get('date', '')
        precision = event.get('date_precision', 'approximate')

        parsed_dates = parse_date(date_str, precision)

        if not parsed_dates:
            events_skipped += 1
            continue

        for date_key, is_exact in parsed_dates:
            try:
                year = date_key[:4]
                year_int = int(year)

                # Only include BMC era (1933-1957) plus some context
                if year_int < 1919 or year_int > 1960:
                    continue

                event_entry = {
                    'description': event.get('event', ''),
                    'category': event.get('category', 'other'),
                    'certainty': get_certainty(event),
                    'source': event.get('source', ''),
                    'location': event.get('location', ''),
                    'is_exact_date': is_exact
                }

                # Add people
                people = event.get('people', [])
                if people:
                    event_entry['people'] = people
                    daily_calendar[year][date_key]['people_present'].update(people)

                # Add quote if available
                if event.get('quote'):
                    event_entry['quote'] = event['quote']

                # Add farm info
                if event.get('farm_info'):
                    event_entry['details'] = event['farm_info']

                # Add Wikipedia info for people
                if event.get('people_wikipedia'):
                    notable_people = [p for p in event['people_wikipedia']
                                     if p.get('profession') and len(p.get('profession', [])) > 0]
                    if notable_people:
                        event_entry['notable_people'] = [
                            {
                                'name': p['name'],
                                'profession': p.get('profession', []),
                                'wikipedia': p.get('wikipedia_url', '')
                            }
                            for p in notable_people[:3]  # Limit to 3
                        ]

                daily_calendar[year][date_key]['events'].append(event_entry)
                events_processed += 1

            except Exception as e:
                events_skipped += 1
                continue

    print(f"Events processed: {events_processed}")
    print(f"Events skipped: {events_skipped}")

    # Convert to final structure
    output = {
        'metadata': {
            'title': 'Black Mountain College Complete Chronology',
            'source': 'chronos 2 - bmc_chronology_wikipedia.json',
            'total_events': events_processed,
            'date_generated': datetime.now().isoformat(),
            'sources': [
                'Martin Duberman - Black Mountain: An Exploration in Community (1972)',
                'BMC Farm archives',
                'Mary Emma Harris interviews (165 transcripts)',
                'Asheville BMC Collection (377 documents)',
                'Wikipedia enrichment'
            ]
        },
        'daily_calendar': {}
    }

    # Sort and structure
    years_with_data = 0
    for year in sorted(daily_calendar.keys()):
        year_data = {}
        for date_key in sorted(daily_calendar[year].keys()):
            day_data = daily_calendar[year][date_key]
            # Convert set to list
            people_list = list(day_data['people_present'])

            year_data[date_key] = {
                'events': day_data['events'],
                'people_count': len(people_list)
            }
            if people_list:
                year_data[date_key]['people'] = sorted(people_list)[:10]  # Top 10

        if year_data:
            output['daily_calendar'][year] = year_data
            years_with_data += 1

    print(f"Years with data: {years_with_data}")

    # Save
    print(f"Saving to {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Stats
    total_days = sum(len(dates) for dates in output['daily_calendar'].values())
    print(f"Total days with events: {total_days}")

    # Sample output
    print("\nSample data for 1948:")
    if '1948' in output['daily_calendar']:
        dates_1948 = list(output['daily_calendar']['1948'].keys())[:5]
        for d in dates_1948:
            events = output['daily_calendar']['1948'][d]['events']
            print(f"  {d}: {len(events)} events")
            if events:
                print(f"    - {events[0]['description'][:60]}...")

if __name__ == '__main__':
    main()
