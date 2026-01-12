#!/usr/bin/env python3
"""
Identify and update Summer Institute participants in the people index.
Changes their role to include 'Summer' prefix for proper categorization.
"""

import json
import re

def main():
    with open('bmc_people_index.json', 'r') as f:
        people = json.load(f)

    # Patterns indicating Summer Institute participation
    summer_patterns = [
        r'Summer Art Institute',
        r'Summer Music Institute',
        r'Summer Institute',
        r'Summer Session',
        r'summer of \d{4}',
        r'summer \d{4}'
    ]

    # Compile patterns
    summer_regex = re.compile('|'.join(summer_patterns), re.IGNORECASE)

    updated = 0
    summer_people = []

    for name, data in people.items():
        bio = data.get('bio', '') or ''
        role = data.get('role', '') or ''

        # Check if bio mentions summer institute
        if summer_regex.search(bio):
            # Check if they were ONLY at summer institute (single year, summer mention)
            start = data.get('start_year')
            end = data.get('end_year')

            # Only summer if single year or bio strongly indicates summer-only
            is_summer_only = False

            if start and end and start == end:
                # Single year attendance - likely summer only if bio mentions it
                if summer_regex.search(bio):
                    is_summer_only = True

            # Also check for explicit "for the Summer" phrasing
            if re.search(r'(was a student|was guest|taught|visited) for the (Summer|summer)', bio):
                is_summer_only = True
            if re.search(r'for the \d{4} Summer', bio):
                is_summer_only = True

            if is_summer_only and 'summer' not in role.lower():
                old_role = role
                # Update role to include Summer
                if 'faculty' in role.lower() or 'guest faculty' in role.lower():
                    new_role = 'Summer Faculty'
                elif 'student' in role.lower():
                    new_role = 'Summer Student'
                elif 'guest' in role.lower():
                    new_role = 'Summer Guest'
                else:
                    new_role = 'Summer ' + role if role else 'Summer Participant'

                people[name]['role'] = new_role
                updated += 1
                summer_people.append({
                    'name': name,
                    'old_role': old_role,
                    'new_role': new_role,
                    'years': f"{start}-{end}",
                    'bio_excerpt': bio[:100] + '...' if len(bio) > 100 else bio
                })

    # Print summary
    print("=" * 70)
    print("SUMMER INSTITUTE UPDATE")
    print("=" * 70)
    print(f"Total people in index: {len(people)}")
    print(f"Updated to Summer roles: {updated}")
    print()

    # Show updates by year
    print("Updated entries:")
    for p in sorted(summer_people, key=lambda x: x['years']):
        print(f"  {p['name']}")
        print(f"    {p['old_role']} -> {p['new_role']} ({p['years']})")

    # Save updated index
    with open('bmc_people_index.json', 'w') as f:
        json.dump(people, f, indent=2)

    print()
    print(f"Updated bmc_people_index.json with {updated} changes")

if __name__ == '__main__':
    main()
