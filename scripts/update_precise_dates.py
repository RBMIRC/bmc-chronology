#!/usr/bin/env python3
"""
Update people_index with precise dates from BMC Yearbook.
Adds start_date, end_date, and periods for guest faculty.
"""

import json

# Precise dates verified from BMC Yearbook
PRECISE_DATES = {
    "Josef Albers": {
        "start_date": "1933-09-25",
        "end_date": "1949-06-15",
        "note": "Faculty. Arrived with wife Anni."
    },
    "Anni Albers": {
        "start_date": "1933-09-25",
        "end_date": "1949-06-15",
        "note": "Faculty. Arrived with husband Josef."
    },
    "John Cage": {
        "periods": [
            {"start": "1948-04-01", "end": "1948-04-15", "type": "visit", "note": "April visit with Merce Cunningham"},
            {"start": "1948-06-22", "end": "1948-09-01", "type": "summer", "note": "Summer Art Institute"},
            {"start": "1952-06-24", "end": "1952-09-11", "type": "summer", "note": "Summer session, Theatre Piece No. 1"},
            {"start": "1953-06-15", "end": "1953-09-01", "type": "summer", "note": "Summer in residence"}
        ],
        "note": "Guest Faculty - multiple summer sessions"
    },
    "Ben Shahn": {
        "start_date": "1952-06-24",
        "end_date": "1952-09-11",
        "note": "Guest Faculty - Summer 1952 only"
    },
    "Merce Cunningham": {
        "periods": [
            {"start": "1948-04-01", "end": "1948-04-15", "type": "visit", "note": "April visit with John Cage"},
            {"start": "1948-06-22", "end": "1948-09-01", "type": "summer", "note": "Summer Art Institute"},
            {"start": "1952-06-24", "end": "1952-09-11", "type": "summer", "note": "Summer session"},
            {"start": "1953-06-15", "end": "1953-09-01", "type": "summer", "note": "Summer in residence"}
        ],
        "note": "Guest Faculty - multiple summer sessions with Cage"
    },
    "Buckminster Fuller": {
        "periods": [
            {"start": "1948-06-22", "end": "1948-09-01", "type": "summer", "note": "Summer Art Institute, first dome attempt"},
            {"start": "1949-06-15", "end": "1949-08-30", "type": "summer", "note": "Summer session"}
        ],
        "note": "Guest Faculty - Summer sessions"
    },
    "Willem de Kooning": {
        "start_date": "1948-06-22",
        "end_date": "1948-09-01",
        "note": "Guest Faculty - Summer Art Institute 1948"
    },
    "Robert Motherwell": {
        "periods": [
            {"start": "1945-07-02", "end": "1945-09-08", "type": "summer", "note": "Summer Art Institute 1945"},
            {"start": "1951-06-18", "end": "1951-09-01", "type": "summer", "note": "Summer 1951"}
        ],
        "note": "Guest Faculty - Summer sessions"
    },
    "Clement Greenberg": {
        "start_date": "1950-06-19",
        "end_date": "1950-08-25",
        "note": "Guest Faculty - Summer 1950 only"
    },
    "Katherine Litz": {
        "periods": [
            {"start": "1950-06-19", "end": "1950-08-25", "type": "summer", "note": "Summer 1950"},
            {"start": "1951-06-18", "end": "1951-09-01", "type": "summer", "note": "Summer 1951"},
            {"start": "1952-06-24", "end": "1952-09-11", "type": "summer", "note": "Summer 1952"}
        ],
        "note": "Faculty - multiple summer sessions"
    },
    "John Evarts": {
        "start_date": "1933-09-25",
        "end_date": "1942-06-10",
        "note": "Faculty. Left to join military."
    },
    "Charles Olson": {
        "start_date": "1951-03-01",
        "end_date": "1956-10-01",
        "note": "Faculty, then Rector from 1951"
    },
    "Robert Creeley": {
        "start_date": "1954-03-01",
        "end_date": "1955-10-01",
        "note": "Faculty of English and Writing, Editor Black Mountain Review"
    },
    "Stefan Wolpe": {
        "start_date": "1952-09-01",
        "end_date": "1956-06-01",
        "note": "Faculty of Music"
    }
}

def main():
    with open('bmc_people_index.json', 'r') as f:
        people = json.load(f)

    updates = 0

    for name, dates in PRECISE_DATES.items():
        # Find matching entry (handle nicknames)
        matched_key = None
        for key in people.keys():
            # Check if name matches
            if name.lower() in key.lower() or key.lower() in name.lower():
                matched_key = key
                break

        if matched_key:
            # Update with precise dates
            if 'start_date' in dates:
                people[matched_key]['start_date'] = dates['start_date']
            if 'end_date' in dates:
                people[matched_key]['end_date'] = dates['end_date']
            if 'periods' in dates:
                people[matched_key]['periods'] = dates['periods']
            if 'note' in dates:
                people[matched_key]['date_note'] = dates['note']

            updates += 1
            print(f"Updated: {matched_key}")
            if 'periods' in dates:
                for p in dates['periods']:
                    print(f"  - {p['start']} to {p['end']} ({p['type']})")
            else:
                print(f"  - {dates.get('start_date', '?')} to {dates.get('end_date', '?')}")
        else:
            print(f"NOT FOUND: {name}")

    with open('bmc_people_index.json', 'w') as f:
        json.dump(people, f, indent=2)

    print(f"\nTotal updates: {updates}")

if __name__ == '__main__':
    main()
