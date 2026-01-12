#!/usr/bin/env python3
"""
Verify specific problematic instructors by checking bmcyearbook.org.
Shows discrepancies between courses data and verified bio data.
"""

import json
import time
import re
import urllib.request
import ssl

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Instructors to verify (from earlier analysis)
PROBLEM_INSTRUCTORS = [
    ("John Evarts", "/bio/john-evarts", "Chorus 1948", "1933-1942"),
    ("Katherine Litz", "/bio/katherine-litz", "Dance 1946", "1950-1952"),
    ("Ben Shahn", "/bio/ben-shahn", "Painting 1951", "1952-1952"),
    ("Clement Greenberg", "/bio/clement-greenberg", "Art History 1946", "1950-1950"),
    ("Theodore Stamos", "/bio/theodoros-stamos", "Painting 1946", "1950-1950"),
    ("Paul Radin", "/bio/paul-radin", "History 1940", "1941-1944"),
    ("Harold Sproul", "/bio/harold-sproul", "Music 1946", "1947-1947"),
    ("Robert Klein", "/bio/robert-klein", "Theatre 1946", "1950-1950"),
    ("Trude Guermonprez", "/bio/trude-guermonprez", "Weaving 1946", "1947-1949"),
    ("John Wallen", "/bio/john-wallen", "Psychology 1948", "1945-1947"),
    ("Alfred Einstein", "/bio/alfred-einstein", "Music 1945", "1950-1950"),
    ("John Cage", "/bio/john-cage", "Music 1948", "not in index"),
    ("Joseph Fiore", "/bio/joseph-fiore", "Painting 1954-1956", "1946-1953"),
]

def fetch_url(url):
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; BMC Research)'}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30, context=ssl_context) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"  Error: {e}")
        return None

def extract_attendance(html):
    """Extract attendance years from bio page."""
    match = re.search(r'Attendance[:\s]*</[^>]+>\s*<[^>]+>([^<]+)', html, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def extract_role(html):
    """Extract role from bio page."""
    match = re.search(r'Role[:\s]*</[^>]+>\s*<[^>]+>([^<]+)', html, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def extract_bio_text(html):
    """Extract biography text."""
    # Look for main bio paragraph
    match = re.search(r'<p[^>]*>([^<]{100,})</p>', html)
    if match:
        return match.group(1).strip()[:200] + "..."
    return None

def main():
    print("=" * 80)
    print("VERIFICATION: Problem Instructors vs BMC Yearbook")
    print("=" * 80)

    results = []

    for name, bio_url, course_info, index_years in PROBLEM_INSTRUCTORS:
        url = f"https://bmcyearbook.org{bio_url}"
        print(f"\n{name}")
        print(f"  Course data says: {course_info}")
        print(f"  People index says: {index_years}")
        print(f"  Checking {url}...")

        html = fetch_url(url)
        if not html:
            print("  FAILED to fetch")
            continue

        attendance = extract_attendance(html)
        role = extract_role(html)
        bio = extract_bio_text(html)

        print(f"  BMC Yearbook says: {attendance} ({role})")
        if bio:
            print(f"  Bio: {bio}")

        # Determine verdict
        if attendance:
            results.append({
                'name': name,
                'course_info': course_info,
                'index_years': index_years,
                'yearbook_years': attendance,
                'yearbook_role': role
            })

        time.sleep(0.5)

    print("\n" + "=" * 80)
    print("SUMMARY - Which source is correct?")
    print("=" * 80)

    for r in results:
        print(f"\n{r['name']}:")
        print(f"  Courses says: {r['course_info']}")
        print(f"  People index: {r['index_years']}")
        print(f"  BMC Yearbook: {r['yearbook_years']} ({r['yearbook_role']})")

        # Parse yearbook years
        yb_match = re.search(r'(\d{4})\s*[-–]\s*(\d{4})', r['yearbook_years'])
        if yb_match:
            yb_start, yb_end = int(yb_match.group(1)), int(yb_match.group(2))

            # Parse index years
            idx_match = re.search(r'(\d{4})-(\d{4})', r['index_years'])
            if idx_match:
                idx_start, idx_end = int(idx_match.group(1)), int(idx_match.group(2))

                if (yb_start, yb_end) == (idx_start, idx_end):
                    print(f"  >>> PEOPLE INDEX IS CORRECT - courses data may be wrong")
                else:
                    print(f"  >>> DISCREPANCY: Index={idx_start}-{idx_end}, Yearbook={yb_start}-{yb_end}")

if __name__ == '__main__':
    main()
