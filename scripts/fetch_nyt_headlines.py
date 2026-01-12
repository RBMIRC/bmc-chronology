#!/usr/bin/env python3
"""
Fetch NY Times front page headlines from September 1933 to October 1957.
Requires a free API key from https://developer.nytimes.com

Usage:
    python3 fetch_nyt_headlines.py YOUR_API_KEY
"""

import json
import sys
import time
import urllib.request
import urllib.error
import ssl
from datetime import datetime

# SSL context to handle certificate issues
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

API_BASE = "https://api.nytimes.com/svc/archive/v1"

def fetch_month(year, month, api_key):
    """Fetch all articles for a given month."""
    url = f"{API_BASE}/{year}/{month}.json?api-key={api_key}"

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'BMC Research Bot'})
        with urllib.request.urlopen(req, timeout=60, context=ssl_context) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('response', {}).get('docs', [])
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print(f"    Rate limited, waiting 60s...")
            time.sleep(60)
            return fetch_month(year, month, api_key)
        print(f"    HTTP Error {e.code}: {e.reason}")
        return []
    except Exception as e:
        print(f"    Error: {e}")
        return []

def is_front_page_news(article):
    """Check if article is front page or major news."""
    # Check print_page field
    print_page = article.get('print_page')
    if print_page and str(print_page) == '1':
        return True

    # Check news_desk for major sections
    news_desk = (article.get('news_desk') or '').lower()
    major_desks = ['front page', 'foreign', 'national', 'washington', 'politics', 'war news']
    if any(desk in news_desk for desk in major_desks):
        return True

    # Check section_name
    section = (article.get('section_name') or '').lower()
    if section in ['front page', 'world', 'national', 'politics']:
        return True

    # Check type_of_material
    material = (article.get('type_of_material') or '').lower()
    if material in ['front page', 'news']:
        return True

    return False

def extract_headline_data(article):
    """Extract relevant data from article."""
    headline = article.get('headline', {})
    main_headline = headline.get('main', '')

    if not main_headline:
        return None

    # Skip very short or administrative headlines
    if len(main_headline) < 10:
        return None
    if main_headline.upper() == main_headline and len(main_headline) < 30:
        return None  # Skip all-caps short headers

    pub_date = article.get('pub_date', '')[:10]  # YYYY-MM-DD

    # Get keywords/subjects
    keywords = []
    for kw in article.get('keywords', []):
        if kw.get('name') in ['subject', 'persons', 'organizations', 'glocations']:
            keywords.append(kw.get('value', ''))

    return {
        'date': pub_date,
        'headline': main_headline,
        'section': article.get('section_name') or article.get('news_desk') or '',
        'keywords': keywords[:5],  # Limit keywords
        'url': article.get('web_url', '')
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 fetch_nyt_headlines.py YOUR_API_KEY")
        print("\nGet your free API key at: https://developer.nytimes.com")
        sys.exit(1)

    api_key = sys.argv[1]

    print("=" * 70)
    print("NY Times Headlines Fetcher (1933-1957)")
    print("=" * 70)

    all_headlines = []

    # September 1933 to October 1957
    start_year, start_month = 1933, 9
    end_year, end_month = 1957, 10

    year, month = start_year, start_month

    while (year < end_year) or (year == end_year and month <= end_month):
        print(f"Fetching {year}-{month:02d}...", end=" ", flush=True)

        articles = fetch_month(year, month, api_key)
        print(f"got {len(articles)} articles", end=" ", flush=True)

        # Filter for front page news
        front_page = [a for a in articles if is_front_page_news(a)]
        print(f"({len(front_page)} front page)", end=" ", flush=True)

        # Extract headline data
        month_headlines = []
        for article in front_page:
            data = extract_headline_data(article)
            if data:
                month_headlines.append(data)

        # Keep top headlines per day (max 3 per day)
        by_date = {}
        for h in month_headlines:
            date = h['date']
            if date not in by_date:
                by_date[date] = []
            if len(by_date[date]) < 3:
                by_date[date].append(h)

        for headlines in by_date.values():
            all_headlines.extend(headlines)

        print(f"-> {sum(len(v) for v in by_date.values())} kept")

        # Rate limiting: 5 requests per minute max
        time.sleep(12)

        # Next month
        month += 1
        if month > 12:
            month = 1
            year += 1

    # Sort by date
    all_headlines.sort(key=lambda x: x['date'])

    # Save results
    output_file = 'nyt_headlines_1933-1957.json'
    with open(output_file, 'w') as f:
        json.dump(all_headlines, f, indent=2)

    print()
    print("=" * 70)
    print(f"COMPLETE")
    print("=" * 70)
    print(f"Total headlines: {len(all_headlines)}")
    print(f"Saved to: {output_file}")

    # Show sample
    print("\nSample headlines:")
    for h in all_headlines[:5]:
        print(f"  {h['date']}: {h['headline'][:60]}...")

if __name__ == '__main__':
    main()
