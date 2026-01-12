#!/usr/bin/env python3
"""
Verify consistency between course instructors and faculty in people index.
Shows inconsistencies WITHOUT making changes.
"""

import json
from collections import defaultdict

def get_last_name(full_name):
    """Extract last name from full name."""
    if not full_name:
        return ''
    # Handle multiple instructors
    names = []
    for name in full_name.split(','):
        name = name.strip()
        # Remove suffixes
        for suffix in ['Jr.', 'Jr', 'Sr.', 'Sr', 'II', 'III', 'IV', 'V']:
            name = name.replace(suffix, '').strip()
        parts = name.split()
        if parts:
            names.append(parts[-1])
    return names

def normalize_name(name):
    """Normalize name for comparison."""
    # Remove quotes, parentheses, nicknames
    name = name.replace('"', '').replace("'", '')
    # Handle nicknames like "Joe" in "Joseph \"Joe\" Fiore"
    if '(' in name:
        name = name.split('(')[0].strip()
    return name.lower().strip()

def main():
    # Load data
    with open('bmc_courses_by_year.json', 'r') as f:
        courses_data = json.load(f)

    with open('bmc_people_index.json', 'r') as f:
        people_data = json.load(f)

    print("=" * 70)
    print("VERIFICATION: Faculty vs Course Instructors")
    print("=" * 70)

    all_issues = []

    for year in range(1933, 1958):
        year_str = str(year)
        courses = courses_data.get(year_str, [])

        if not courses:
            continue

        # Get instructors from courses
        course_instructors = {}
        for course in courses:
            instructor = course.get('instructor', '')
            if instructor:
                last_names = get_last_name(instructor)
                for ln in last_names:
                    course_instructors[ln.lower()] = {
                        'full_name': instructor,
                        'course': course.get('name', 'Unknown')
                    }

        # Get faculty from people index for this year
        faculty_last_names = {}
        for name, data in people_data.items():
            start_year = data.get('start_year', 9999)
            end_year = data.get('end_year', 0)
            role = (data.get('role', '') or '').lower()

            if year >= start_year and year <= end_year:
                if 'faculty' in role or 'admin' in role:
                    # Extract last name
                    norm_name = normalize_name(name)
                    parts = norm_name.split()
                    if parts:
                        last_name = parts[-1].lower()
                        faculty_last_names[last_name] = {
                            'full_name': name,
                            'start': start_year,
                            'end': end_year,
                            'focus': data.get('focus', '')
                        }

        # Find instructors NOT in faculty
        issues_year = []
        for instructor_ln, info in course_instructors.items():
            if instructor_ln not in faculty_last_names:
                # Check if they're a guest or in people index at all
                found_in_index = False
                person_info = None
                for name, data in people_data.items():
                    norm_name = normalize_name(name)
                    parts = norm_name.split()
                    if parts and parts[-1].lower() == instructor_ln:
                        found_in_index = True
                        person_info = {
                            'name': name,
                            'start': data.get('start_year'),
                            'end': data.get('end_year'),
                            'role': data.get('role', '')
                        }
                        break

                issue = {
                    'year': year,
                    'instructor': info['full_name'],
                    'course': info['course'],
                    'last_name': instructor_ln,
                    'in_index': found_in_index,
                    'person_info': person_info
                }
                issues_year.append(issue)

        if issues_year:
            all_issues.extend(issues_year)

    # Display issues grouped by type
    print("\n" + "=" * 70)
    print("INSTRUCTORS NOT IN FACULTY FOR THEIR YEAR")
    print("(Course shows instructor but they're not listed as faculty that year)")
    print("=" * 70)

    # Group by person
    by_person = defaultdict(list)
    for issue in all_issues:
        by_person[issue['instructor']].append(issue)

    for instructor, issues in sorted(by_person.items()):
        years = sorted(set(i['year'] for i in issues))
        year_range = f"{min(years)}-{max(years)}" if len(years) > 1 else str(years[0])
        courses = sorted(set(i['course'] for i in issues))

        info = issues[0]['person_info']
        if info:
            print(f"\n{instructor}")
            print(f"  Teaches: {', '.join(courses)} ({year_range})")
            print(f"  In people_index: {info['name']}")
            print(f"  Current years: {info['start']}-{info['end']}")
            print(f"  Role: {info['role']}")
            if max(years) > (info['end'] or 0):
                print(f"  >>> SUGGESTED FIX: Change end_year to {max(years)}")
            if min(years) < (info['start'] or 9999):
                print(f"  >>> SUGGESTED FIX: Change start_year to {min(years)}")
        else:
            print(f"\n{instructor}")
            print(f"  Teaches: {', '.join(courses)} ({year_range})")
            print(f"  >>> NOT FOUND IN PEOPLE INDEX - needs to be added")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total instructors with issues: {len(by_person)}")

    needs_date_fix = sum(1 for i, issues in by_person.items() if issues[0]['person_info'])
    needs_adding = sum(1 for i, issues in by_person.items() if not issues[0]['person_info'])

    print(f"  - Need date correction: {needs_date_fix}")
    print(f"  - Need to be added to index: {needs_adding}")

if __name__ == '__main__':
    main()
