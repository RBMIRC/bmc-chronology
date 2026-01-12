#!/usr/bin/env python3
"""
Fix Summer Institute classification - Version 3
Extended criteria:
- Guest Faculty single year 1944-1953 = Summer Faculty
- Faculty single year 1944-1953 (likely summer only) = Summer Faculty
- Guest Faculty multi-year but only summers (1948-1953 like Cage) = Summer Faculty
- Students with Summer Institute in bio = Summer Student
"""

import json
import re

# Known summer-only faculty who had multi-year summer visits
KNOWN_SUMMER_FACULTY = [
    'John Cage',
    'John Cage, Jr.',
    'Merce Cunningham',
    'R. Buckminster Fuller',
    'Buckminster Fuller',
]

def main():
    with open('bmc_people_index.json', 'r') as f:
        people = json.load(f)

    # First, revert all "Summer" roles back to original
    reverted = 0
    for name, data in people.items():
        role = data.get('role', '') or ''
        if role.startswith('Summer '):
            original = role.replace('Summer ', '')
            if original in ['Participant', 'Family']:
                original = 'Guest'
            people[name]['role'] = original
            reverted += 1

    print(f"Reverted {reverted} entries to original roles")

    # Summer Institute patterns for bio matching
    summer_patterns = [
        r'Summer Art Institute',
        r'Summer Music Institute',
        r'Summer Institute',
        r'for the summer of \d{4}',
        r'for the \d{4} Summer',
        r'student for the Summer',
        r'was guest for the Summer',
    ]
    summer_regex = re.compile('|'.join(summer_patterns), re.IGNORECASE)

    updated = 0
    summer_people = []

    for name, data in people.items():
        role = (data.get('role') or '').lower()
        original_role = data.get('role', '')
        start = data.get('start_year')
        end = data.get('end_year')
        bio = data.get('bio') or ''

        should_mark_summer = False

        # Rule 1: Known summer faculty (multi-year summer visitors)
        if any(known in name for known in KNOWN_SUMMER_FACULTY):
            should_mark_summer = True

        # Rule 2: Guest Faculty for single year during 1944-1953
        if 'guest' in role and 'faculty' in role:
            if start and end and start == end and 1944 <= start <= 1953:
                should_mark_summer = True

        # Rule 3: Faculty (not guest) for single year during 1944-1953
        # These are likely summer-only appointments
        if 'faculty' in role and 'guest' not in role:
            if start and end and start == end and 1944 <= start <= 1953:
                should_mark_summer = True

        # Rule 4: Bio explicitly mentions Summer Institute (1944+)
        if summer_regex.search(bio) and start and start >= 1944:
            if start == end:  # Single year = summer only
                should_mark_summer = True

        if should_mark_summer:
            if 'faculty' in original_role.lower():
                new_role = 'Summer Faculty'
            elif 'student' in original_role.lower():
                new_role = 'Summer Student'
            elif 'staff' in original_role.lower():
                new_role = 'Summer Staff'
            else:
                new_role = 'Summer Guest'

            people[name]['role'] = new_role
            updated += 1
            summer_people.append({
                'name': name,
                'old_role': original_role,
                'new_role': new_role,
                'year': start,
                'end_year': end
            })

    # Print summary
    print(f"\nUpdated {updated} entries to Summer roles")
    print("\nBy year (start year):")
    by_year = {}
    for p in summer_people:
        y = p['year']
        if y not in by_year:
            by_year[y] = {'faculty': [], 'students': [], 'other': []}
        if 'Faculty' in p['new_role']:
            by_year[y]['faculty'].append(p['name'])
        elif 'Student' in p['new_role']:
            by_year[y]['students'].append(p['name'])
        else:
            by_year[y]['other'].append(p['name'])

    for year in sorted(by_year.keys()):
        data = by_year[year]
        total = len(data['faculty']) + len(data['students']) + len(data['other'])
        print(f"\n=== {year} ({total} total) ===")
        if data['faculty']:
            print(f"  Faculty ({len(data['faculty'])}):")
            for n in sorted(data['faculty'])[:20]:
                print(f"    - {n}")
            if len(data['faculty']) > 20:
                print(f"    ... and {len(data['faculty'])-20} more")
        if data['students']:
            print(f"  Students: {len(data['students'])}")
        if data['other']:
            print(f"  Other: {len(data['other'])}")

    # Save
    with open('bmc_people_index.json', 'w') as f:
        json.dump(people, f, indent=2)

    print(f"\nSaved to bmc_people_index.json")

if __name__ == '__main__':
    main()
