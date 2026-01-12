#!/usr/bin/env python3
"""
Fix Summer Institute classification.
Only mark people as Summer Institute if:
1. Their bio explicitly mentions "Summer Art Institute", "Summer Music Institute", etc.
2. Year is 1944 or later (first Summer Institute was 1944)
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
            # Revert to original role
            original = role.replace('Summer ', '')
            if original == 'Participant':
                original = 'Guest'
            elif original == 'Family':
                original = 'Guest'
            people[name]['role'] = original
            reverted += 1

    print(f"Reverted {reverted} entries to original roles")

    # Now, only mark as Summer Institute if explicitly mentioned
    # Summer Institutes ran 1944-1953
    summer_institute_patterns = [
        r'Summer Art Institute',
        r'Summer Music Institute',
        r'Summer Institute of \d{4}',
        r'\d{4} Summer Art Institute',
        r'\d{4} Summer Music Institute',
        r'\d{4} Summer Institute',
    ]

    summer_regex = re.compile('|'.join(summer_institute_patterns), re.IGNORECASE)

    updated = 0
    summer_people = []

    for name, data in people.items():
        bio = data.get('bio', '') or ''
        role = data.get('role', '') or ''
        start = data.get('start_year')
        end = data.get('end_year')

        # Only consider if bio explicitly mentions Summer Institute
        if summer_regex.search(bio):
            # Verify year is 1944 or later
            if start and start >= 1944:
                # Check it's a short stay (single year = summer only)
                if start == end:
                    old_role = role
                    if 'faculty' in role.lower():
                        new_role = 'Summer Faculty'
                    elif 'student' in role.lower():
                        new_role = 'Summer Student'
                    elif 'guest' in role.lower():
                        new_role = 'Summer Guest'
                    elif 'staff' in role.lower():
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

    # Print summary by year
    print(f"\nUpdated {updated} entries to Summer Institute roles")
    print("\nBy year:")
    by_year = {}
    for p in summer_people:
        y = p['year']
        if y not in by_year:
            by_year[y] = []
        by_year[y].append(p['name'])

    for year in sorted(by_year.keys()):
        print(f"  {year}: {len(by_year[year])} people")

    # Save
    with open('bmc_people_index.json', 'w') as f:
        json.dump(people, f, indent=2)

    print(f"\nSaved to bmc_people_index.json")

if __name__ == '__main__':
    main()
