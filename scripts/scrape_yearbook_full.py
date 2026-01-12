#!/usr/bin/env python3
"""
Full scrape of bmcyearbook.org to get precise dates for all people.
Saves results to bmcyearbook_full.json for review before updating.
"""

import json
import time
import re
import urllib.request
import ssl
from datetime import datetime

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

def fetch_url(url, retries=3):
    """Fetch URL with retry logic."""
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; BMC Research Bot)'}
    req = urllib.request.Request(url, headers=headers)

    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30, context=ssl_context) as response:
                return response.read().decode('utf-8')
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
            else:
                return None
    return None

def get_all_bio_links():
    """Fetch all bio links from paginated biographies page."""
    all_links = []
    page = 1
    max_pages = 50

    print("Fetching biography list pages...")
    while page <= max_pages:
        url = f"https://bmcyearbook.org/biographies?page={page}"
        print(f"  Page {page}...", end=" ", flush=True)

        html = fetch_url(url)
        if not html:
            print("failed")
            break

        # Extract bio links
        pattern = r'href="(/bio/[^"]+)"'
        links = list(set(re.findall(pattern, html)))

        if not links:
            print("no more links")
            break

        all_links.extend(links)
        print(f"found {len(links)} links")

        page += 1
        time.sleep(0.3)

    return list(set(all_links))

def extract_name_from_html(html):
    """Extract person's name from bio page."""
    # Try h1 tag
    match = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
    if match:
        return match.group(1).strip()
    return None

def extract_field(html, field_name):
    """Extract a specific field from bio page HTML."""
    # Pattern: Field name followed by value in next tag
    patterns = [
        rf'{field_name}[:\s]*</[^>]+>\s*<[^>]+>([^<]+)',
        rf'{field_name}[:\s]*</span>\s*<span[^>]*>([^<]+)',
        rf'{field_name}[:\s]*([^<\n]+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None

def extract_bio_text(html):
    """Extract biography paragraph text."""
    # Look for substantial paragraph text
    matches = re.findall(r'<p[^>]*>([^<]{100,})</p>', html)
    if matches:
        # Return longest paragraph
        return max(matches, key=len).strip()
    return None

def parse_attendance(attendance_str):
    """Parse attendance string into start/end dates."""
    if not attendance_str:
        return None, None, None, None

    # Try to find date range: "1933-09-25 - 1949-06-15" or "1933 - 1949"
    # Full date pattern
    full_match = re.search(r'(\d{4}-\d{2}-\d{2})\s*[-–—]\s*(\d{4}-\d{2}-\d{2})', attendance_str)
    if full_match:
        return full_match.group(1), full_match.group(2), None, None

    # Year-month pattern: "1948-06 - 1948-09"
    month_match = re.search(r'(\d{4}-\d{2})\s*[-–—]\s*(\d{4}-\d{2})', attendance_str)
    if month_match:
        start = month_match.group(1) + "-01"
        end = month_match.group(2) + "-28"  # Approximate end of month
        return start, end, None, None

    # Year pattern: "1933 - 1949"
    year_match = re.search(r'(\d{4})\s*[-–—]\s*(\d{4})', attendance_str)
    if year_match:
        start_year = int(year_match.group(1))
        end_year = int(year_match.group(2))
        return None, None, start_year, end_year

    # Single year: "1948"
    single_match = re.search(r'(\d{4})', attendance_str)
    if single_match:
        year = int(single_match.group(1))
        return None, None, year, year

    return None, None, None, None

def scrape_bio_page(url, slug):
    """Scrape individual bio page for all data."""
    html = fetch_url(url)
    if not html:
        return None

    data = {
        'url': url,
        'slug': slug,
        'name': extract_name_from_html(html),
        'attendance': extract_field(html, 'Attendance'),
        'role': extract_field(html, 'Role'),
        'focus': extract_field(html, 'Focus'),
        'relations': extract_field(html, 'Relations'),
        'bio': extract_bio_text(html),
    }

    # Parse attendance into dates
    start_date, end_date, start_year, end_year = parse_attendance(data['attendance'])

    if start_date:
        data['start_date'] = start_date
        data['end_date'] = end_date
    if start_year:
        data['start_year'] = start_year
        data['end_year'] = end_year

    return data

def main():
    print("=" * 70)
    print("BMC Yearbook Full Scraper")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Get all bio links
    all_links = get_all_bio_links()
    print(f"\nTotal unique bio links: {len(all_links)}")

    # Scrape all bios
    print(f"\nScraping {len(all_links)} bios...")
    all_data = []
    errors = []

    for i, link in enumerate(all_links):
        slug = link.replace('/bio/', '')
        url = f"https://bmcyearbook.org{link}"

        if (i + 1) % 50 == 0:
            print(f"  Progress: {i + 1}/{len(all_links)} ({100*(i+1)//len(all_links)}%)")

        data = scrape_bio_page(url, slug)
        if data:
            all_data.append(data)
        else:
            errors.append(link)

        # Be polite - small delay between requests
        time.sleep(0.2)

    # Save results
    output_file = 'bmcyearbook_full.json'
    with open(output_file, 'w') as f:
        json.dump(all_data, f, indent=2)

    print(f"\n" + "=" * 70)
    print(f"COMPLETE")
    print(f"=" * 70)
    print(f"Scraped: {len(all_data)} bios")
    print(f"Errors: {len(errors)}")
    print(f"Saved to: {output_file}")
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if errors:
        print(f"\nFailed URLs:")
        for e in errors[:10]:
            print(f"  - {e}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")

    # Quick stats
    with_dates = sum(1 for d in all_data if d.get('start_date') or d.get('start_year'))
    with_precise = sum(1 for d in all_data if d.get('start_date'))

    print(f"\nDate coverage:")
    print(f"  With any dates: {with_dates}/{len(all_data)}")
    print(f"  With precise dates: {with_precise}/{len(all_data)}")

if __name__ == '__main__':
    main()
