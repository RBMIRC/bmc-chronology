#!/usr/bin/env python3
"""
Fix Summer Institute classification - Version 2
Based on historical research:
- Summer Art Institutes ran 1944-1953
- Guest Faculty who came for single year during this period = Summer Faculty
- Students whose bio mentions Summer Institute = Summer Student
"""

import json
import re

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
        start = data.get('start_year')
        end = data.get('end_year')
        bio = data.get('bio') or ''

        should_mark_summer = False

        # Rule 1: Guest Faculty for single year during 1944-1953 = Summer Faculty
        if 'guest' in role and 'faculty' in role:
            if start and end and start == end and 1944 <= start <= 1953:
                should_mark_summer = True

        # Rule 2: Bio explicitly mentions Summer Institute (1944+)
        if summer_regex.search(bio) and start and start >= 1944:
            if start == end:  # Single year = summer only
                should_mark_summer = True

        if should_mark_summer:
            old_role = data.get('role', '')
            if 'faculty' in old_role.lower():
                new_role = 'Summer Faculty'
            elif 'student' in old_role.lower():
                new_role = 'Summer Student'
            elif 'staff' in old_role.lower():
                new_role = 'Summer Staff'
            else:
                new_role = 'Summer Guest'

            people[name]['role'] = new_role
            updated += 1
            summer_people.append({
                'name': name,
                'old_role': old_role,
                'new_role': new_role,
                'year': start
            })

    # Print summary
    print(f"\nUpdated {updated} entries to Summer roles")
    print("\nBy year:")
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
            for n in data['faculty'][:15]:
                print(f"    - {n}")
            if len(data['faculty']) > 15:
                print(f"    ... and {len(data['faculty'])-15} more")
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
