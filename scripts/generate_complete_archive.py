#!/usr/bin/env python3
"""
Generate COMPLETE daily archive for Black Mountain College 1933-1957
Combines: People, Courses, Events, World History, Weather, Radio
"""

import json
import re
from collections import defaultdict
from datetime import datetime, date
from pathlib import Path

# Paths
DATA_BMC = Path("/Users/sylvain/Documents/DATA BMC")
CHRONOS2 = DATA_BMC / "chronos 2"
SITE_DIR = Path("/Users/sylvain/Documents/BMC-RADIO-SITE")

# Academic calendar patterns (approximate)
SEMESTERS = {
    'fall': {'start_month': 9, 'end_month': 12},
    'spring': {'start_month': 1, 'end_month': 5},
    'summer': {'start_month': 6, 'end_month': 8}
}

def parse_people_file():
    """Parse BlackMountainPeople.txt to extract people with dates and courses"""
    people = []
    people_path = CHRONOS2 / "BlackMountainPeople.txt"

    with open(people_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by NAME: entries
    entries = re.split(r'\nNAME: ', content)

    for entry in entries[1:]:  # Skip first empty split
        lines = entry.strip().split('\n')
        person = {'name': lines[0].strip()}

        for line in lines[1:]:
            if line.startswith('BIO: '):
                person['bio'] = line[5:].strip()
            elif line.startswith('Relations: '):
                person['relations'] = line[11:].strip()
            elif line.startswith('COURSE TAKEN: '):
                person['courses_raw'] = line[14:].strip()
            elif line.startswith('Focus: '):
                person['focus'] = line[7:].strip()
            elif line.startswith('Role: '):
                person['role'] = line[6:].strip()
            elif line.startswith('Start Year: '):
                try:
                    person['start_year'] = int(float(line[12:].strip()))
                except:
                    pass
            elif line.startswith('End Year: '):
                try:
                    person['end_year'] = int(float(line[10:].strip()))
                except:
                    pass

        # Parse courses into structured format
        if person.get('courses_raw'):
            person['courses'] = parse_courses(person['courses_raw'])

        people.append(person)

    print(f"Parsed {len(people)} people from BlackMountainPeople.txt")
    return people

def parse_courses(raw_courses):
    """Parse course strings like 'Fall 1935: Music with Evarts, Drawing with Albers'"""
    courses = []

    # Pattern: "Semester Year: Course with Teacher, Course with Teacher"
    semester_pattern = r'(Fall|Spring|Summer)\s+(\d{4}(?:-\d{2,4})?)[:\s]+([^/]+?)(?=/|$)'

    for match in re.finditer(semester_pattern, raw_courses, re.IGNORECASE):
        semester = match.group(1).lower()
        year_str = match.group(2)
        course_list = match.group(3)

        # Parse year
        if '-' in year_str:
            year = int(year_str.split('-')[0])
        else:
            year = int(year_str)

        # Parse individual courses
        course_items = re.split(r',\s*(?=\w)', course_list)
        for item in course_items:
            item = item.strip()
            if not item:
                continue

            # Try to extract "Course with Teacher"
            with_match = re.match(r'(.+?)\s+with\s+(\w+)', item, re.IGNORECASE)
            if with_match:
                courses.append({
                    'course': with_match.group(1).strip(),
                    'teacher': with_match.group(2).strip(),
                    'semester': semester,
                    'year': year
                })
            else:
                courses.append({
                    'course': item,
                    'semester': semester,
                    'year': year
                })

    return courses

def get_people_present(people, year, month):
    """Get list of people present at BMC for given year/month"""
    present = {'faculty': [], 'students': [], 'staff': [], 'guests': []}

    # Determine semester
    if month >= 9:
        semester = 'fall'
    elif month >= 6:
        semester = 'summer'
    else:
        semester = 'spring'

    for person in people:
        start = person.get('start_year')
        end = person.get('end_year')

        if not start:
            continue

        # Check if person was present
        if start <= year <= (end or start):
            role = person.get('role', '').lower()

            entry = {
                'name': person['name'],
                'focus': person.get('focus', ''),
                'bio': person.get('bio', '')[:200] if person.get('bio') else ''
            }

            if 'faculty' in role or 'professor' in role:
                present['faculty'].append(entry)
            elif 'student' in role:
                present['students'].append(entry)
            elif 'staff' in role:
                present['staff'].append(entry)
            elif 'guest' in role:
                present['guests'].append(entry)

    return present

def get_courses_for_semester(people, year, semester):
    """Get all courses being taught in a given semester"""
    courses_dict = {}

    for person in people:
        for course in person.get('courses', []):
            if course.get('year') == year and course.get('semester') == semester:
                key = (course.get('course', ''), course.get('teacher', ''))
                if key not in courses_dict:
                    courses_dict[key] = {
                        'course': course.get('course', ''),
                        'teacher': course.get('teacher', ''),
                        'students': []
                    }
                courses_dict[key]['students'].append(person['name'])

    return list(courses_dict.values())

def load_world_events():
    """Load world/national events from chronology file"""
    events_by_date = defaultdict(list)
    ongoing_by_year = {}

    chrono_path = DATA_BMC / "Chronos" / "bmc_chronology_1933-1957.json"

    with open(chrono_path, 'r') as f:
        data = json.load(f)

    for year_str, year_data in data.get('years', {}).items():
        # Store yearly context
        ongoing_by_year[year_str] = {
            'bmc_status': year_data.get('bmc_status', ''),
            'world_context': year_data.get('world_context', ''),
            'usa_context': year_data.get('usa_context', '')
        }

        # Store events by date
        for event in year_data.get('key_events', []):
            date_str = event.get('date', '')
            if date_str:
                events_by_date[date_str].append({
                    'event': event.get('event', ''),
                    'category': event.get('category', 'world'),
                    'certainty': event.get('certainty', 50)
                })

    print(f"Loaded world events for {len(ongoing_by_year)} years")
    return events_by_date, ongoing_by_year

def load_chronos_events():
    """Load BMC events from comprehensive chronology"""
    events_by_date = defaultdict(list)

    chrono_path = CHRONOS2 / "bmc_chronology_wikipedia.json"

    with open(chrono_path, 'r') as f:
        data = json.load(f)

    for event in data.get('events', []):
        date_str = event.get('date', '') or ''

        # Try to parse to standard format
        if date_str and re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            events_by_date[date_str].append({
                'event': event.get('event', ''),
                'category': event.get('category', 'bmc'),
                'people': event.get('people', []),
                'source': event.get('source', ''),
                'location': event.get('location', ''),
                'quote': event.get('quote', ''),
                'certainty': 80
            })
        elif date_str and re.match(r'^[A-Za-z]+\s+\d+,?\s+\d{4}$', date_str):
            # Convert "October 16, 1933" to ISO
            try:
                dt = datetime.strptime(date_str.replace(',', ''), '%B %d %Y')
                iso_date = dt.strftime('%Y-%m-%d')
                events_by_date[iso_date].append({
                    'event': event.get('event', ''),
                    'category': event.get('category', 'bmc'),
                    'people': event.get('people', []),
                    'source': event.get('source', ''),
                    'certainty': 90
                })
            except:
                pass

    print(f"Loaded {sum(len(v) for v in events_by_date.values())} BMC events")
    return events_by_date

def load_asheville_data():
    """Load faculty/courses from Asheville collection"""
    faculty_by_year = defaultdict(list)
    courses_by_year = defaultdict(list)

    ash_path = CHRONOS2 / "asheville_events.json"

    with open(ash_path, 'r') as f:
        data = json.load(f)

    for doc in data.get('documents', []):
        academic_year = doc.get('academic_year', '') or ''

        # Parse year from "1933-1934" format
        match = re.match(r'(\d{4})', academic_year) if academic_year else None
        if match:
            year = match.group(1)

            # Faculty
            for fac in doc.get('faculty_listed', []):
                entry = {
                    'name': fac.get('name', ''),
                    'title': fac.get('title', ''),
                    'department': fac.get('department', '')
                }
                if entry not in faculty_by_year[year]:
                    faculty_by_year[year].append(entry)

            # Courses
            for course in doc.get('courses_offered', []):
                entry = {
                    'name': course.get('name', ''),
                    'department': course.get('department', ''),
                    'instructor': course.get('instructor', '')
                }
                if entry not in courses_by_year[year]:
                    courses_by_year[year].append(entry)

    print(f"Loaded Asheville data for {len(faculty_by_year)} years")
    return faculty_by_year, courses_by_year

def generate_complete_archive():
    """Generate the complete daily archive"""
    print("=" * 60)
    print("Generating Complete BMC Daily Archive")
    print("=" * 60)

    # Load all data sources
    people = parse_people_file()
    world_events, yearly_context = load_world_events()
    bmc_events = load_chronos_events()
    asheville_faculty, asheville_courses = load_asheville_data()

    # Build archive structure
    archive = {
        'metadata': {
            'title': 'Black Mountain College Complete Daily Archive',
            'version': '2.0',
            'generated': datetime.now().isoformat(),
            'sources': [
                'BlackMountainPeople.txt (1299 people)',
                'bmc_chronology_wikipedia.json (4639 events)',
                'bmc_chronology_1933-1957.json (world events)',
                'asheville_events.json (377 documents)',
                'Weather: Open-Meteo historical API',
                'Radio: Billboard charts + WWNC Asheville'
            ],
            'date_range': '1933-1957'
        },
        'yearly_context': yearly_context,
        'daily_calendar': {}
    }

    # Generate daily entries for BMC period (1933-1957)
    from datetime import timedelta

    start_date = date(1933, 1, 1)
    end_date = date(1957, 12, 31)
    current = start_date

    days_processed = 0

    while current <= end_date:
        year_str = str(current.year)
        date_key = current.strftime('%Y-%m-%d')
        month = current.month

        # Determine semester
        if month >= 9:
            semester = 'fall'
        elif month >= 6:
            semester = 'summer'
        else:
            semester = 'spring'

        # Initialize year in calendar if needed
        if year_str not in archive['daily_calendar']:
            archive['daily_calendar'][year_str] = {}

        # Build day entry
        day_entry = {
            'day_of_week': current.strftime('%A'),
            'semester': semester
        }

        # People present this year
        people_present = get_people_present(people, current.year, month)
        day_entry['people'] = {
            'faculty_count': len(people_present['faculty']),
            'students_count': len(people_present['students']),
            'staff_count': len(people_present['staff']),
            'guests_count': len(people_present['guests'])
        }

        # Add sample names (not all, to save space)
        if people_present['faculty']:
            day_entry['people']['faculty_sample'] = [p['name'] for p in people_present['faculty'][:10]]
        if people_present['students']:
            day_entry['people']['students_sample'] = [p['name'] for p in people_present['students'][:10]]

        # Courses (from Asheville data)
        if year_str in asheville_courses:
            day_entry['courses_available'] = len(asheville_courses[year_str])

        # BMC Events for this date
        if date_key in bmc_events:
            day_entry['bmc_events'] = bmc_events[date_key]

        # World/National events
        world_today = []
        for date_pattern, events in world_events.items():
            # Exact match
            if date_pattern == date_key:
                world_today.extend(events)
            # Month match (e.g., "1936-04")
            elif date_pattern == date_key[:7]:
                world_today.extend(events)
            # Year match (e.g., "1936")
            elif date_pattern == year_str and not world_today:
                # Only add if nothing more specific
                pass

        if world_today:
            day_entry['world_events'] = world_today

        # Only store days that have some content beyond basic info
        has_content = (
            day_entry.get('bmc_events') or
            day_entry.get('world_events') or
            day_entry['people']['faculty_count'] > 0
        )

        if has_content:
            archive['daily_calendar'][year_str][date_key] = day_entry
            days_processed += 1

        current += timedelta(days=1)

    print(f"\nProcessed {days_processed} days with content")

    # Save archive
    output_path = SITE_DIR / "bmc_complete_archive.json"
    print(f"Saving to {output_path}...")

    with open(output_path, 'w') as f:
        json.dump(archive, f, ensure_ascii=False)

    # Also save separate files for quick loading

    # Save people index
    people_index = {}
    for p in people:
        people_index[p['name']] = {
            'role': p.get('role', ''),
            'focus': p.get('focus', ''),
            'years': f"{p.get('start_year', '?')}-{p.get('end_year', '?')}",
            'bio': p.get('bio', '')[:300] if p.get('bio') else ''
        }

    with open(SITE_DIR / "bmc_people_index.json", 'w') as f:
        json.dump(people_index, f, ensure_ascii=False)

    # Save courses by year
    courses_export = {}
    for year_str in sorted(asheville_courses.keys()):
        courses_export[year_str] = asheville_courses[year_str]

    with open(SITE_DIR / "bmc_courses_by_year.json", 'w') as f:
        json.dump(courses_export, f, ensure_ascii=False, indent=2)

    # Save yearly context
    with open(SITE_DIR / "bmc_yearly_context.json", 'w') as f:
        json.dump(yearly_context, f, ensure_ascii=False, indent=2)

    print("\nGenerated files:")
    print(f"  - bmc_complete_archive.json")
    print(f"  - bmc_people_index.json ({len(people_index)} people)")
    print(f"  - bmc_courses_by_year.json")
    print(f"  - bmc_yearly_context.json")

    # Stats
    total_size = sum(f.stat().st_size for f in SITE_DIR.glob("bmc_*.json"))
    print(f"\nTotal data size: {total_size / 1024 / 1024:.1f} MB")

if __name__ == '__main__':
    generate_complete_archive()
