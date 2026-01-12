#!/usr/bin/env python3
"""
Categorize NY Times headlines into Culture, National, and International.
"""

import json
import re

# Keywords for categorization
CULTURE_KEYWORDS = [
    # Art
    'art', 'artist', 'painter', 'painting', 'sculpture', 'sculptor', 'museum', 'gallery', 'exhibition',
    'moma', 'metropolitan museum', 'guggenheim', 'whitney',
    # Music
    'music', 'musician', 'composer', 'symphony', 'orchestra', 'opera', 'concert', 'jazz', 'singer',
    'philharmonic', 'carnegie hall', 'conductor',
    # Theater & Film
    'theater', 'theatre', 'broadway', 'play', 'playwright', 'actor', 'actress', 'film', 'movie', 'cinema',
    'hollywood', 'director', 'premiere', 'curtain',
    # Dance
    'dance', 'dancer', 'ballet', 'choreograph',
    # Literature
    'book', 'author', 'novelist', 'poet', 'poetry', 'literary', 'publisher', 'novel', 'fiction',
    # Architecture & Design
    'architect', 'architecture', 'bauhaus', 'design',
    # Education & Culture
    'college', 'university', 'professor', 'academic',
]

INTERNATIONAL_KEYWORDS = [
    # Countries & Regions
    'germany', 'german', 'hitler', 'nazi', 'reich', 'berlin', 'munich',
    'france', 'french', 'paris', 'vichy',
    'britain', 'british', 'england', 'english', 'london', 'churchill',
    'italy', 'italian', 'rome', 'mussolini', 'fascist',
    'spain', 'spanish', 'franco', 'madrid',
    'russia', 'russian', 'soviet', 'moscow', 'stalin', 'kremlin',
    'japan', 'japanese', 'tokyo', 'hiroshima', 'nagasaki',
    'china', 'chinese', 'peking', 'shanghai', 'mao', 'chiang',
    'korea', 'korean', 'pyongyang', 'seoul',
    'mexico', 'mexican',
    'cuba', 'cuban', 'havana',
    'europe', 'european', 'asia', 'asian', 'africa', 'african',
    'middle east', 'palestine', 'israel', 'arab',
    'united nations', 'u.n.', 'nato', 'treaty',
    # War terms
    'invasion', 'allied', 'allies', 'axis', 'troops abroad', 'foreign',
    'd-day', 'normandy', 'dunkirk', 'pacific theater',
]

NATIONAL_KEYWORDS = [
    # US Politics
    'president', 'congress', 'senate', 'senator', 'representative', 'house of representatives',
    'white house', 'capitol', 'washington', 'democrat', 'republican', 'election', 'vote', 'ballot',
    'supreme court', 'justice', 'federal', 'legislation', 'bill', 'law passed',
    # Presidents
    'roosevelt', 'truman', 'eisenhower', 'fdr',
    # Economy
    'economy', 'economic', 'wall street', 'stock', 'market', 'depression', 'new deal',
    'unemployment', 'labor', 'strike', 'union', 'wage',
    # US Places
    'new york', 'california', 'texas', 'chicago', 'los angeles', 'boston',
    # Domestic
    'american', 'u.s.', 'united states', 'domestic', 'national',
]

# Exclude patterns (sports, local crime, obituaries, etc.)
EXCLUDE_PATTERNS = [
    r'\bgiant[s]?\b.*\b(beat|win|lose|game|score)',  # Baseball Giants
    r'\byankee[s]?\b.*\b(beat|win|lose|game|score)',
    r'\bdodger[s]?\b.*\b(beat|win|lose|game|score)',
    r'\bboxing\b', r'\bfight\b.*\bround\b',
    r'\btennis\b', r'\bgolf\b', r'\bracing\b', r'\bhorse\b',
    r'\bdies at\b', r'\bfuneral\b', r'\bobituary\b',
    r'\bwedding\b', r'\bengaged\b', r'\bmarried\b',
]

def categorize_headline(headline_data):
    """Categorize a single headline."""
    headline = headline_data['headline'].lower()
    keywords = [k.lower() for k in headline_data.get('keywords', [])]
    all_text = headline + ' ' + ' '.join(keywords)

    # Check exclusions first
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, all_text, re.IGNORECASE):
            return None

    # Score each category
    scores = {'culture': 0, 'national': 0, 'international': 0}

    for kw in CULTURE_KEYWORDS:
        if kw in all_text:
            scores['culture'] += 1

    for kw in INTERNATIONAL_KEYWORDS:
        if kw in all_text:
            scores['international'] += 1

    for kw in NATIONAL_KEYWORDS:
        if kw in all_text:
            scores['national'] += 1

    # Determine category based on highest score
    if max(scores.values()) == 0:
        return None  # No clear category

    # International takes priority over national (more specific)
    if scores['international'] > 0 and scores['international'] >= scores['national']:
        return 'international'
    elif scores['culture'] > scores['national'] and scores['culture'] > scores['international']:
        return 'culture'
    elif scores['national'] > 0:
        return 'national'
    elif scores['international'] > 0:
        return 'international'
    elif scores['culture'] > 0:
        return 'culture'

    return None

def main():
    with open('nyt_headlines_1933-1957.json', 'r') as f:
        headlines = json.load(f)

    print(f"Processing {len(headlines)} headlines...")

    # Categorize all headlines
    culture = []
    national = []
    international = []
    uncategorized = 0

    for h in headlines:
        category = categorize_headline(h)

        item = {
            'date': h['date'],
            'title': h['headline'][:200],  # Truncate long headlines
            'source': 'NY Times',
            'url': h['url']
        }

        if category == 'culture':
            culture.append(item)
        elif category == 'national':
            national.append(item)
        elif category == 'international':
            international.append(item)
        else:
            uncategorized += 1

    print(f"\nResults:")
    print(f"  Culture: {len(culture)}")
    print(f"  National: {len(national)}")
    print(f"  International: {len(international)}")
    print(f"  Uncategorized: {uncategorized}")

    # Save categorized headlines
    with open('nyt_culture.json', 'w') as f:
        json.dump(culture, f, indent=2)

    with open('nyt_national.json', 'w') as f:
        json.dump(national, f, indent=2)

    with open('nyt_international.json', 'w') as f:
        json.dump(international, f, indent=2)

    print("\nSaved to: nyt_culture.json, nyt_national.json, nyt_international.json")

    # Show samples
    print("\n--- Culture samples ---")
    for h in culture[:3]:
        print(f"  {h['date']}: {h['title'][:70]}...")

    print("\n--- National samples ---")
    for h in national[:3]:
        print(f"  {h['date']}: {h['title'][:70]}...")

    print("\n--- International samples ---")
    for h in international[:3]:
        print(f"  {h['date']}: {h['title'][:70]}...")

if __name__ == '__main__':
    main()
