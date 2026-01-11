#!/usr/bin/env python3
"""
Extract and verify faculty and courses from Asheville/Dreier Collection data
Creates a comprehensive verified JSON file
"""

import json
from collections import defaultdict
from pathlib import Path

# Paths
DATA_BMC = Path("/Users/sylvain/Documents/DATA BMC")
CHRONOS2 = DATA_BMC / "chronos 2"
SITE_DIR = Path("/Users/sylvain/Documents/BMC-RADIO-SITE")

def extract_verified_data():
    """Extract verified faculty and courses from asheville_events.json"""

    print("Loading Asheville/Dreier Collection data...")
    with open(CHRONOS2 / "asheville_events.json", 'r') as f:
        data = json.load(f)

    print(f"Total documents: {data['total_documents']}")

    # Organize by academic year
    faculty_by_year = defaultdict(dict)  # year -> {name: details}
    courses_by_year = defaultdict(list)  # year -> [courses]
    students_by_year = defaultdict(list)  # year -> [students]
    calendar_by_year = defaultdict(list)  # year -> [calendar dates]
    events_by_year = defaultdict(list)    # year -> [events]

    for doc in data['documents']:
        academic_year = doc.get('academic_year', '')
        if not academic_year:
            continue

        # Extract faculty
        for faculty in doc.get('faculty_listed', []):
            name = faculty.get('name', '')
            if name:
                # Keep the most detailed entry
                if name not in faculty_by_year[academic_year]:
                    faculty_by_year[academic_year][name] = faculty
                else:
                    # Merge details
                    existing = faculty_by_year[academic_year][name]
                    if not existing.get('title') and faculty.get('title'):
                        existing['title'] = faculty['title']
                    if not existing.get('department') and faculty.get('department'):
                        existing['department'] = faculty['department']

        # Extract courses
        for course in doc.get('courses_offered', []):
            if course not in courses_by_year[academic_year]:
                courses_by_year[academic_year].append(course)

        # Extract students
        for student in doc.get('students_listed', []):
            if student not in students_by_year[academic_year]:
                students_by_year[academic_year].append(student)

        # Extract calendar dates
        for cal in doc.get('calendar_dates', []):
            if cal not in calendar_by_year[academic_year]:
                calendar_by_year[academic_year].append(cal)

        # Extract events
        for event in doc.get('events', []):
            events_by_year[academic_year].append(event)

    # Build output structure
    verified_data = {
        'metadata': {
            'source': 'Theodore Dreier Sr., Black Mountain College Documents Collection',
            'total_documents': data['total_documents'],
            'url': 'https://collection.ashevilleart.org/objects-1/portfolio?query=Portfolios%20%3D%20%22579%22',
            'extracted_by': 'extract_verified_faculty.py'
        },
        'academic_years': {}
    }

    # Sort years and build output
    all_years = sorted(set(list(faculty_by_year.keys()) +
                           list(courses_by_year.keys()) +
                           list(students_by_year.keys())))

    for year in all_years:
        year_data = {
            'faculty': list(faculty_by_year[year].values()),
            'courses': courses_by_year[year],
            'students': students_by_year[year],
            'calendar': calendar_by_year[year],
            'events': events_by_year[year]
        }

        # Only include years with actual content
        if year_data['faculty'] or year_data['courses'] or year_data['students']:
            verified_data['academic_years'][year] = year_data

    # Statistics
    print("\n" + "="*60)
    print("VERIFIED DATA STATISTICS")
    print("="*60)

    total_faculty = 0
    total_courses = 0
    total_students = 0

    for year in sorted(verified_data['academic_years'].keys()):
        year_data = verified_data['academic_years'][year]
        faculty_count = len(year_data['faculty'])
        courses_count = len(year_data['courses'])
        students_count = len(year_data['students'])

        total_faculty += faculty_count
        total_courses += courses_count
        total_students += students_count

        if faculty_count > 0 or courses_count > 0:
            print(f"\n{year}:")
            if faculty_count > 0:
                print(f"  Faculty: {faculty_count}")
                for fac in year_data['faculty'][:5]:
                    print(f"    - {fac['name']}: {fac.get('title', 'N/A')}")
                if faculty_count > 5:
                    print(f"    ... and {faculty_count - 5} more")

            if courses_count > 0:
                print(f"  Courses: {courses_count}")

            if students_count > 0:
                print(f"  Students listed: {students_count}")

    print("\n" + "="*60)
    print(f"TOTALS:")
    print(f"  Academic years with data: {len(verified_data['academic_years'])}")
    print(f"  Faculty entries: {total_faculty}")
    print(f"  Course entries: {total_courses}")
    print(f"  Student entries: {total_students}")
    print("="*60)

    # Save verified data
    output_path = SITE_DIR / "bmc_verified_faculty_courses.json"
    print(f"\nSaving to {output_path}...")

    with open(output_path, 'w') as f:
        json.dump(verified_data, f, indent=2, ensure_ascii=False)

    # Also create a simple faculty index for the website
    faculty_index = {}
    for year, year_data in verified_data['academic_years'].items():
        for fac in year_data['faculty']:
            name = fac['name']
            if name not in faculty_index:
                faculty_index[name] = {
                    'title': fac.get('title', ''),
                    'department': fac.get('department', ''),
                    'years': [year]
                }
            else:
                if year not in faculty_index[name]['years']:
                    faculty_index[name]['years'].append(year)
                # Update title if more detailed
                if not faculty_index[name]['title'] and fac.get('title'):
                    faculty_index[name]['title'] = fac['title']

    # Sort years for each faculty and clean up
    for name in faculty_index:
        # Filter out non-academic years
        valid_years = [y for y in faculty_index[name]['years']
                       if y not in ['not applicable', 'Unknown'] and '-' in y]
        faculty_index[name]['years'] = sorted(valid_years)
        years = faculty_index[name]['years']
        if len(years) >= 2:
            # Extract just the start year from each academic year for cleaner display
            start_years = sorted([y.split('-')[0] for y in years])
            end_years = sorted([y.split('-')[1] if len(y.split('-')[1]) == 4 else y.split('-')[0][:2] + y.split('-')[1] for y in years])
            faculty_index[name]['period'] = f"{start_years[0]}-{end_years[-1]}"
        elif len(years) == 1:
            faculty_index[name]['period'] = years[0]
        else:
            faculty_index[name]['period'] = 'Unknown'

    faculty_output = SITE_DIR / "bmc_faculty_verified.json"
    print(f"Saving faculty index to {faculty_output}...")

    with open(faculty_output, 'w') as f:
        json.dump(faculty_index, f, indent=2, ensure_ascii=False)

    print(f"\nUnique faculty members: {len(faculty_index)}")

    return verified_data, faculty_index

if __name__ == '__main__':
    extract_verified_data()
