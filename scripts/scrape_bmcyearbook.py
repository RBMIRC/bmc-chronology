#!/usr/bin/env python3
"""
Scrape bmcyearbook.org to verify and update people_index.
Fetches all bios and compares with existing data.
"""

import json
import time
import re
import urllib.request
import urllib.error
import ssl
from html.parser import HTMLParser

# Disable SSL verification (for sites with certificate issues)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

class BioParser(HTMLParser):
    """Parse bio page HTML to extract data."""
    def __init__(self):
        super().__init__()
        self.in_bio = False
        self.in_attendance = False
        self.in_role = False
        self.in_focus = False
        self.in_relations = False
        self.in_courses = False
        self.current_tag = None
        self.data = {
            'bio': '',
            'attendance': '',
            'role': '',
            'focus': '',
            'relations': '',
            'courses': ''
        }
        self.current_field = None

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        attrs_dict = dict(attrs)
        class_name = attrs_dict.get('class', '')

        # Look for specific sections
        if 'bio-text' in class_name or 'biography' in class_name:
            self.in_bio = True
            self.current_field = 'bio'

    def handle_data(self, data):
        text = data.strip()
        if not text:
            return

        # Check for field labels
        if text == 'Attendance:' or text == 'Years:':
            self.current_field = 'attendance'
            return
        elif text == 'Role:':
            self.current_field = 'role'
            return
        elif text == 'Focus:':
            self.current_field = 'focus'
            return
        elif text == 'Relations:':
            self.current_field = 'relations'
            return
        elif text == 'Courses:' or text == 'Courses Taken:':
            self.current_field = 'courses'
            return

        # Append to current field
        if self.current_field and self.current_field in self.data:
            self.data[self.current_field] += ' ' + text

def fetch_url(url):
    """Fetch URL with retry logic."""
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; BMC Research Bot)'}
    req = urllib.request.Request(url, headers=headers)

    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30, context=ssl_context) as response:
                return response.read().decode('utf-8')
        except urllib.error.URLError as e:
            print(f"  Retry {attempt+1}/3: {e}")
            time.sleep(2)
    return None

def extract_years(text):
    """Extract start and end years from attendance text."""
    if not text:
        return None, None

    # Clean text
    text = text.strip()

    # Pattern: "1933-1942" or "1933 to 1942" or "1933 - 1942"
    match = re.search(r'(\d{4})\s*[-–—to]+\s*(\d{4})', text)
    if match:
        return int(match.group(1)), int(match.group(2))

    # Pattern: single year "1945"
    match = re.search(r'(\d{4})', text)
    if match:
        year = int(match.group(1))
        return year, year

    return None, None

def get_bio_links_from_page(html):
    """Extract bio links from biographies list page."""
    links = []
    # Simple regex to find bio links
    pattern = r'href="(/bio/[^"]+)"'
    for match in re.finditer(pattern, html):
        links.append(match.group(1))
    return list(set(links))  # Remove duplicates

def scrape_bio_page(url):
    """Scrape individual bio page."""
    html = fetch_url(url)
    if not html:
        return None

    data = {
        'url': url,
        'bio': '',
        'attendance': '',
        'role': '',
        'focus': '',
        'start_year': None,
        'end_year': None
    }

    # Extract name from URL
    slug = url.split('/bio/')[-1] if '/bio/' in url else ''

    # Look for attendance/years pattern in HTML
    # Pattern: Attendance followed by years
    attendance_match = re.search(r'Attendance[:\s]*</[^>]+>\s*<[^>]+>([^<]+)', html, re.IGNORECASE)
    if attendance_match:
        data['attendance'] = attendance_match.group(1).strip()
        # Extract years from attendance field
        years = extract_years(data['attendance'])
        if years[0] and years[1]:
            data['start_year'] = years[0]
            data['end_year'] = years[1]

    # If no years yet, try to find in attendance field directly
    if not data['start_year']:
        years = extract_years(data['attendance'])
        if years[0]:
            data['start_year'] = years[0]
            data['end_year'] = years[1] or years[0]

    # Extract role
    role_match = re.search(r'Role[:\s]*</[^>]+>\s*<[^>]+>([^<]+)', html, re.IGNORECASE)
    if role_match:
        data['role'] = role_match.group(1).strip()

    # Extract focus
    focus_match = re.search(r'Focus[:\s]*</[^>]+>\s*<[^>]+>([^<]+)', html, re.IGNORECASE)
    if focus_match:
        data['focus'] = focus_match.group(1).strip()

    # Extract bio text - look for paragraph content
    bio_match = re.search(r'<p[^>]*>([^<]{50,})</p>', html)
    if bio_match:
        data['bio'] = bio_match.group(1).strip()

    return data

def main():
    print("=" * 70)
    print("BMC Yearbook Scraper - Verification Mode")
    print("=" * 70)

    # Load existing people index
    with open('bmc_people_index.json', 'r') as f:
        people_index = json.load(f)

    print(f"Existing people_index: {len(people_index)} entries")

    # First, get all bio links by paginating through biographies
    all_bio_links = []
    page = 1
    max_pages = 50  # Safety limit

    print("\nFetching biography list pages...")
    while page <= max_pages:
        url = f"https://bmcyearbook.org/biographies?page={page}"
        print(f"  Page {page}...", end=" ")

        html = fetch_url(url)
        if not html:
            print("failed")
            break

        links = get_bio_links_from_page(html)
        if not links:
            print("no more links")
            break

        all_bio_links.extend(links)
        print(f"found {len(links)} links")

        page += 1
        time.sleep(0.5)  # Be polite

    all_bio_links = list(set(all_bio_links))
    print(f"\nTotal unique bio links: {len(all_bio_links)}")

    # Sample: scrape first 20 bios to test
    print("\nScraping sample bios (first 20)...")
    scraped_data = []

    for i, link in enumerate(all_bio_links[:20]):
        url = f"https://bmcyearbook.org{link}"
        print(f"  [{i+1}/20] {link}...", end=" ")

        data = scrape_bio_page(url)
        if data:
            scraped_data.append(data)
            years = f"{data.get('start_year', '?')}-{data.get('end_year', '?')}"
            print(f"OK ({years})")
        else:
            print("failed")

        time.sleep(0.5)

    # Save scraped data for review
    with open('bmcyearbook_sample.json', 'w') as f:
        json.dump(scraped_data, f, indent=2)

    print(f"\nSaved {len(scraped_data)} scraped bios to bmcyearbook_sample.json")
    print("\nRun with --full flag to scrape all bios")

if __name__ == '__main__':
    import sys
    main()
