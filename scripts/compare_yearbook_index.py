#!/usr/bin/env python3
"""
Compare scraped yearbook data with existing people_index.
Shows differences for review before updating.
"""

import json
import re
from collections import defaultdict

def normalize_name(name):
    """Normalize name for comparison."""
    if not name:
        return ''
    # Remove quotes, parentheses, nicknames in quotes
    name = re.sub(r'"[^"]*"', '', name)
    name = re.sub(r'\([^)]*\)', '', name)
    # Remove Jr., Sr., etc.
    name = re.sub(r',?\s*(Jr\.?|Sr\.?|II|III|IV|V)\s*$', '', name, flags=re.IGNORECASE)
    # Normalize whitespace
    name = ' '.join(name.split())
    return name.lower().strip()

def name_matches(name1, name2):
    """Check if two names likely refer to the same person."""
    n1 = normalize_name(name1)
    n2 = normalize_name(name2)

    if n1 == n2:
        return True

    # Check last names match and first initial matches
    parts1 = n1.split()
    parts2 = n2.split()

    if len(parts1) >= 2 and len(parts2) >= 2:
        # Same last name
        if parts1[-1] == parts2[-1]:
            # First name or initial matches
            if parts1[0] == parts2[0] or parts1[0][0] == parts2[0][0]:
                return True

    return False

def main():
    # Load data
    with open('bmcyearbook_full.json', 'r') as f:
        yearbook = json.load(f)

    with open('bmc_people_index.json', 'r') as f:
        people_index = json.load(f)

    print("=" * 80)
    print("COMPARISON: BMC Yearbook vs People Index")
    print("=" * 80)
    print(f"Yearbook entries: {len(yearbook)}")
    print(f"People index entries: {len(people_index)}")

    # Build lookup by normalized name
    yearbook_by_name = {}
    for entry in yearbook:
        name = entry.get('name', '')
        if name:
            norm = normalize_name(name)
            yearbook_by_name[norm] = entry

    # Find matches and differences
    matched = []
    different_dates = []
    missing_from_index = []
    missing_from_yearbook = []

    for yb_name_norm, yb_entry in yearbook_by_name.items():
        found_match = False
        for idx_name, idx_data in people_index.items():
            if name_matches(yb_entry.get('name', ''), idx_name):
                found_match = True

                # Compare dates
                yb_start = yb_entry.get('start_year')
                yb_end = yb_entry.get('end_year')
                idx_start = idx_data.get('start_year')
                idx_end = idx_data.get('end_year')

                if yb_start and idx_start:
                    if yb_start != idx_start or yb_end != idx_end:
                        different_dates.append({
                            'yearbook_name': yb_entry.get('name'),
                            'index_name': idx_name,
                            'yearbook_dates': f"{yb_start}-{yb_end}",
                            'index_dates': f"{idx_start}-{idx_end}",
                            'yearbook_role': yb_entry.get('role', ''),
                            'index_role': idx_data.get('role', '')
                        })
                    else:
                        matched.append({
                            'name': idx_name,
                            'dates': f"{idx_start}-{idx_end}"
                        })
                break

        if not found_match:
            missing_from_index.append(yb_entry)

    # Check reverse - index entries not in yearbook
    for idx_name, idx_data in people_index.items():
        found = False
        for yb_entry in yearbook:
            if name_matches(yb_entry.get('name', ''), idx_name):
                found = True
                break
        if not found:
            missing_from_yearbook.append({
                'name': idx_name,
                'dates': f"{idx_data.get('start_year', '?')}-{idx_data.get('end_year', '?')}",
                'role': idx_data.get('role', '')
            })

    # Report
    print(f"\n{'=' * 80}")
    print(f"RESULTS")
    print(f"{'=' * 80}")
    print(f"Matched with same dates: {len(matched)}")
    print(f"Different dates: {len(different_dates)}")
    print(f"In yearbook but not index: {len(missing_from_index)}")
    print(f"In index but not yearbook: {len(missing_from_yearbook)}")

    # Show date differences (most important)
    if different_dates:
        print(f"\n{'=' * 80}")
        print(f"DATE DIFFERENCES (Yearbook vs Index)")
        print(f"{'=' * 80}")

        # Sort by role - Faculty first
        faculty_diff = [d for d in different_dates if 'faculty' in d.get('yearbook_role', '').lower() or 'faculty' in d.get('index_role', '').lower()]
        other_diff = [d for d in different_dates if d not in faculty_diff]

        if faculty_diff:
            print(f"\nFACULTY differences ({len(faculty_diff)}):")
            for d in faculty_diff[:30]:
                print(f"  {d['yearbook_name']}")
                print(f"    Yearbook: {d['yearbook_dates']} ({d['yearbook_role']})")
                print(f"    Index:    {d['index_dates']} ({d['index_role']})")

        if other_diff:
            print(f"\nOTHER differences ({len(other_diff)}):")
            for d in other_diff[:20]:
                print(f"  {d['yearbook_name']}: YB={d['yearbook_dates']} vs IDX={d['index_dates']}")

    # Show missing from index (important people not in our data)
    if missing_from_index:
        print(f"\n{'=' * 80}")
        print(f"IN YEARBOOK BUT NOT IN INDEX ({len(missing_from_index)})")
        print(f"{'=' * 80}")

        # Filter for faculty/guest faculty
        faculty_missing = [m for m in missing_from_index if 'faculty' in (m.get('role') or '').lower()]
        if faculty_missing:
            print(f"\nMissing FACULTY ({len(faculty_missing)}):")
            for m in faculty_missing[:30]:
                dates = f"{m.get('start_year', '?')}-{m.get('end_year', '?')}"
                print(f"  {m.get('name')}: {dates} ({m.get('role', 'unknown')})")

    # Save detailed report
    report = {
        'summary': {
            'matched': len(matched),
            'different_dates': len(different_dates),
            'missing_from_index': len(missing_from_index),
            'missing_from_yearbook': len(missing_from_yearbook)
        },
        'different_dates': different_dates,
        'missing_from_index': [{'name': m.get('name'), 'dates': f"{m.get('start_year')}-{m.get('end_year')}", 'role': m.get('role')} for m in missing_from_index],
        'missing_from_yearbook': missing_from_yearbook
    }

    with open('yearbook_comparison_report.json', 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\nDetailed report saved to: yearbook_comparison_report.json")

if __name__ == '__main__':
    main()
