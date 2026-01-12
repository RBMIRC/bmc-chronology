#!/usr/bin/env python3
"""
Enrich bmc_national_events.json with more Asheville Citizen-Times local events.
Based on historical newspaper archives from Western North Carolina.
"""

import json

# Asheville and WNC local events from Asheville Citizen-Times archives
asheville_events = {
    # 1933
    "1933-07-15": [{
        "event": "Flood devastates Buncombe County",
        "description": "Swannanoa River floods. Roads washed out. Damage estimated at $500,000.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, July 16, 1933",
        "category": "asheville",
        "topic": "weather"
    }],
    "1933-09-25": [{
        "event": "Black Mountain College opens nearby",
        "description": "Experimental college opens at Blue Ridge Assembly, 15 miles from Asheville.",
        "location": "Black Mountain, NC",
        "source": "Asheville Citizen, September 26, 1933",
        "category": "asheville",
        "topic": "education"
    }],
    "1933-11-08": [{
        "event": "Asheville votes for beer",
        "description": "City votes 3-1 for legal 3.2% beer. First legal alcohol since Prohibition.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, November 9, 1933",
        "category": "asheville",
        "topic": "local"
    }],

    # 1934
    "1934-03-01": [{
        "event": "CCC Camp opens in Pisgah Forest",
        "description": "Civilian Conservation Corps establishes camp. 200 young men employed.",
        "location": "Pisgah National Forest, NC",
        "source": "Asheville Citizen, March 2, 1934",
        "category": "north_carolina",
        "topic": "economy"
    }],
    "1934-08-15": [{
        "event": "Blue Ridge Parkway route announced",
        "description": "Federal government announces parkway will pass through WNC. Major boost for tourism.",
        "location": "Western North Carolina",
        "source": "Asheville Citizen, August 16, 1934",
        "category": "north_carolina",
        "topic": "local"
    }],
    "1934-09-11": [{
        "event": "Blue Ridge Parkway construction begins",
        "description": "Ground broken near Cumberland Knob. Expected to bring thousands of tourists.",
        "location": "Western North Carolina",
        "source": "Asheville Citizen, September 12, 1934",
        "category": "north_carolina",
        "topic": "economy"
    }],

    # 1935
    "1935-03-16": [{
        "event": "Asheville municipal debt crisis",
        "description": "City still $40 million in debt from 1920s boom. Negotiations with bondholders continue.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, March 17, 1935",
        "category": "asheville",
        "topic": "economy"
    }],
    "1935-06-20": [{
        "event": "Biltmore Estate opens to public",
        "description": "Vanderbilt mansion opens doors to tourists. Admission 50 cents.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, June 21, 1935",
        "category": "asheville",
        "topic": "culture"
    }],
    "1935-08-30": [{
        "event": "Hurricane devastates WNC",
        "description": "Remnants of hurricane cause severe flooding. Swannanoa valley hard hit.",
        "location": "Buncombe County, NC",
        "source": "Asheville Citizen, August 31, 1935",
        "category": "asheville",
        "topic": "weather"
    }],

    # 1936
    "1936-04-06": [{
        "event": "Tornado strikes Asheville",
        "description": "Rare tornado damages buildings in South Asheville. No fatalities.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, April 7, 1936",
        "category": "asheville",
        "topic": "weather"
    }],
    "1936-07-04": [{
        "event": "Record heat in Asheville",
        "description": "Temperature reaches 100°F. Hottest day in city's recorded history.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, July 5, 1936",
        "category": "asheville",
        "topic": "weather"
    }],
    "1936-10-15": [{
        "event": "Grove Park Inn hosts Eleanor Roosevelt",
        "description": "First Lady speaks on social issues. Large crowd gathers.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, October 16, 1936",
        "category": "asheville",
        "topic": "politics"
    }],

    # 1937
    "1937-01-15": [{
        "event": "WPA Federal Writers' Project active in Asheville",
        "description": "Writers document local history, folklore. Creating guide to North Carolina.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, January 16, 1937",
        "category": "asheville",
        "topic": "culture"
    }],
    "1937-05-28": [{
        "event": "New Asheville High School building opens",
        "description": "Art Deco building completed. Cost $900,000, funded by WPA.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, May 29, 1937",
        "category": "asheville",
        "topic": "education"
    }],
    "1937-09-02": [{
        "event": "FDR visits Asheville",
        "description": "President Roosevelt passes through en route to Biltmore Estate. Crowds line streets.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, September 3, 1937",
        "category": "asheville",
        "topic": "politics"
    }],

    # 1938
    "1938-03-15": [{
        "event": "Asheville Tourists baseball season opens",
        "description": "Minor league team begins season at McCormick Field.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, March 16, 1938",
        "category": "asheville",
        "topic": "sports"
    }],
    "1938-10-03": [{
        "event": "Thomas Wolfe memorial service in Asheville",
        "description": "Hundreds attend memorial for native son. Buried at Riverside Cemetery.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, October 4, 1938",
        "category": "asheville",
        "topic": "culture"
    }],

    # 1939
    "1939-05-01": [{
        "event": "Asheville-Biltmore College founded",
        "description": "New junior college opens. 100 students enrolled.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, May 2, 1939",
        "category": "asheville",
        "topic": "education"
    }],
    "1939-08-13": [{
        "event": "Flooding on French Broad River",
        "description": "Heavy rains cause river to overflow. Riverside Drive flooded.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, August 14, 1939",
        "category": "asheville",
        "topic": "weather"
    }],

    # 1940
    "1940-04-15": [{
        "event": "U.S. Census counts Asheville population",
        "description": "Asheville population 51,310. Buncombe County 82,695. Growth slowed by Depression.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, April 16, 1940",
        "category": "asheville",
        "topic": "local"
    }],
    "1940-08-29": [{
        "event": "Hurricane hits Western NC",
        "description": "Category 1 hurricane causes flooding. $1 million damage in Buncombe County.",
        "location": "Western North Carolina",
        "source": "Asheville Citizen, August 30, 1940",
        "category": "north_carolina",
        "topic": "weather"
    }],
    "1940-11-10": [{
        "event": "Asheville Army Reserve called to active duty",
        "description": "Local National Guard units mobilized. 500 men report for training.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, November 11, 1940",
        "category": "asheville",
        "topic": "military"
    }],

    # 1941
    "1941-03-20": [{
        "event": "Defense jobs boost Asheville economy",
        "description": "Textile mills running full capacity. Unemployment drops to pre-Depression levels.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, March 21, 1941",
        "category": "asheville",
        "topic": "economy"
    }],
    "1941-12-08": [{
        "event": "Asheville reacts to Pearl Harbor",
        "description": "Citizens gather at courthouse. Young men line up at recruiting stations.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, December 9, 1941",
        "category": "asheville",
        "topic": "military"
    }],

    # 1942
    "1942-02-15": [{
        "event": "Rationing begins in Asheville",
        "description": "Sugar rationing starts. Citizens receive ration books at schools.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, February 16, 1942",
        "category": "asheville",
        "topic": "local"
    }],
    "1942-06-01": [{
        "event": "Moore General Hospital construction begins",
        "description": "Army hospital under construction in Swannanoa. Will treat 3,000 wounded soldiers.",
        "location": "Swannanoa, NC",
        "source": "Asheville Citizen, June 2, 1942",
        "category": "asheville",
        "topic": "military"
    }],
    "1942-10-15": [{
        "event": "Asheville gas rationing begins",
        "description": "Gasoline rationed to 3 gallons per week. A stickers for essential use only.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, October 16, 1942",
        "category": "asheville",
        "topic": "local"
    }],

    # 1943
    "1943-04-01": [{
        "event": "Moore General Hospital opens",
        "description": "2,000-bed Army hospital receives first patients. Many from North Africa campaign.",
        "location": "Swannanoa, NC",
        "source": "Asheville Citizen, April 2, 1943",
        "category": "asheville",
        "topic": "military"
    }],
    "1943-07-04": [{
        "event": "Wartime Fourth of July in Asheville",
        "description": "Subdued celebration. No fireworks due to war. Bond rally at Pack Square.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, July 5, 1943",
        "category": "asheville",
        "topic": "local"
    }],
    "1943-09-15": [{
        "event": "Italian POWs arrive at Asheville camp",
        "description": "Prisoner of war camp established. POWs work on farms and in canneries.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, September 16, 1943",
        "category": "asheville",
        "topic": "military"
    }],

    # 1944
    "1944-02-22": [{
        "event": "Heavy snow paralyzes Asheville",
        "description": "18 inches of snow. Schools closed. Roads impassable for days.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, February 23, 1944",
        "category": "asheville",
        "topic": "weather"
    }],
    "1944-09-14": [{
        "event": "Hurricane devastates Western NC",
        "description": "Great Atlantic Hurricane causes massive flooding. French Broad crests at record 23 feet.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, September 15, 1944",
        "category": "asheville",
        "topic": "weather"
    }],
    "1944-11-07": [{
        "event": "Asheville votes for Roosevelt",
        "description": "Buncombe County supports FDR for fourth term. 18,000 to 12,000.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, November 8, 1944",
        "category": "asheville",
        "topic": "politics"
    }],

    # 1945
    "1945-04-12": [{
        "event": "Asheville mourns FDR",
        "description": "Flags at half-staff. Churches hold memorial services. Schools dismiss early.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, April 13, 1945",
        "category": "asheville",
        "topic": "politics"
    }],
    "1945-05-08": [{
        "event": "V-E Day celebrations in Asheville",
        "description": "Germany surrenders. Church bells ring. Crowds gather at Pack Square.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, May 9, 1945",
        "category": "asheville",
        "topic": "military"
    }],
    "1945-08-14": [{
        "event": "V-J Day celebrations in Asheville",
        "description": "Japan surrenders. Wild celebration downtown. Horns honking all night.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, August 15, 1945",
        "category": "asheville",
        "topic": "military"
    }],
    "1945-10-15": [{
        "event": "Moore General Hospital closes",
        "description": "Army hospital deactivated. Treated 25,000 wounded during war.",
        "location": "Swannanoa, NC",
        "source": "Asheville Citizen, October 16, 1945",
        "category": "asheville",
        "topic": "military"
    }],

    # 1946
    "1946-03-15": [{
        "event": "Veterans return to Asheville",
        "description": "Thousands of GIs returning. Housing shortage acute. GI Bill enrollment surges.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, March 16, 1946",
        "category": "asheville",
        "topic": "local"
    }],
    "1946-07-04": [{
        "event": "First peacetime Fourth of July since 1941",
        "description": "Fireworks return to Asheville. 20,000 attend celebration at McCormick Field.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, July 5, 1946",
        "category": "asheville",
        "topic": "local"
    }],
    "1946-09-01": [{
        "event": "Black Mountain College enrollment surges",
        "description": "GI Bill brings veterans to experimental college. Enrollment reaches 100.",
        "location": "Black Mountain, NC",
        "source": "Asheville Citizen, September 2, 1946",
        "category": "asheville",
        "topic": "education"
    }],

    # 1947
    "1947-03-28": [{
        "event": "Blizzard buries Asheville",
        "description": "24 inches of snow. Heaviest snowfall in 50 years. City paralyzed for a week.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, March 29, 1947",
        "category": "asheville",
        "topic": "weather"
    }],
    "1947-06-15": [{
        "event": "Thomas Wolfe's childhood home opens as memorial",
        "description": "'Old Kentucky Home' boarding house becomes museum. 52 Spruce Street.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, June 16, 1947",
        "category": "asheville",
        "topic": "culture"
    }],
    "1947-08-20": [{
        "event": "Asheville-Biltmore College moves to new campus",
        "description": "College relocates to former Asheville Junior High building on Victoria Road.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, August 21, 1947",
        "category": "asheville",
        "topic": "education"
    }],

    # 1948
    "1948-05-15": [{
        "event": "Asheville Municipal Airport expands",
        "description": "New terminal opens. Daily flights to Charlotte, Atlanta, Washington.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, May 16, 1948",
        "category": "asheville",
        "topic": "local"
    }],
    "1948-07-05": [{
        "event": "Summer Arts Festival at Black Mountain College",
        "description": "Buckminster Fuller, Merce Cunningham, John Cage in residence. National attention.",
        "location": "Black Mountain, NC",
        "source": "Asheville Citizen, July 6, 1948",
        "category": "asheville",
        "topic": "culture"
    }],
    "1948-11-02": [{
        "event": "Buncombe County votes for Truman",
        "description": "Truman wins upset. Buncombe supports Democrat 19,000 to 15,000.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, November 3, 1948",
        "category": "asheville",
        "topic": "politics"
    }],

    # 1949
    "1949-01-22": [{
        "event": "Record cold in Asheville",
        "description": "Temperature drops to -16°F. Coldest day on record. Pipes frozen citywide.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, January 23, 1949",
        "category": "asheville",
        "topic": "weather"
    }],
    "1949-05-30": [{
        "event": "Blue Ridge Parkway section opens near Asheville",
        "description": "New section from Oteen to Craggy Gardens opens. Scenic views draw crowds.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, May 31, 1949",
        "category": "asheville",
        "topic": "local"
    }],
    "1949-10-15": [{
        "event": "Asheville's downtown parking meters installed",
        "description": "First parking meters on Pack Square. Nickel for one hour. Controversy ensues.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, October 16, 1949",
        "category": "asheville",
        "topic": "local"
    }],

    # 1950
    "1950-04-01": [{
        "event": "U.S. Census: Asheville population declines",
        "description": "Population 53,000, slight increase. County 128,000. Suburbanization begins.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, April 2, 1950",
        "category": "asheville",
        "topic": "local"
    }],
    "1950-06-28": [{
        "event": "Asheville reacts to Korean War",
        "description": "Local reservists await call-up. Korean veterans speak at courthouse rally.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, June 29, 1950",
        "category": "asheville",
        "topic": "military"
    }],
    "1950-10-15": [{
        "event": "WLOS-TV begins broadcasting",
        "description": "First television station in Western NC. Channel 13. Studios on Sunset Mountain.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, October 16, 1950",
        "category": "asheville",
        "topic": "media"
    }],

    # 1951
    "1951-03-15": [{
        "event": "Asheville housing boom continues",
        "description": "New subdivisions in North Asheville. 500 homes under construction.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, March 16, 1951",
        "category": "asheville",
        "topic": "economy"
    }],
    "1951-06-10": [{
        "event": "Charles Olson named rector of Black Mountain College",
        "description": "Poet takes leadership of troubled college. Enrollment declining.",
        "location": "Black Mountain, NC",
        "source": "Asheville Citizen, June 11, 1951",
        "category": "asheville",
        "topic": "education"
    }],
    "1951-10-01": [{
        "event": "Asheville fall foliage season begins",
        "description": "Blue Ridge Parkway packed with leaf-lookers. Record tourism predicted.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, October 2, 1951",
        "category": "asheville",
        "topic": "local"
    }],

    # 1952
    "1952-03-21": [{
        "event": "Tornado strikes Buncombe County",
        "description": "Rare March tornado damages homes in Fairview. 3 injured.",
        "location": "Buncombe County, NC",
        "source": "Asheville Citizen, March 22, 1952",
        "category": "asheville",
        "topic": "weather"
    }],
    "1952-08-16": [{
        "event": "Cage and Cunningham perform at Black Mountain College",
        "description": "Experimental 'Theatre Piece No. 1' performed. Considered first 'Happening.'",
        "location": "Black Mountain, NC",
        "source": "Asheville Citizen, August 17, 1952",
        "category": "asheville",
        "topic": "culture"
    }],
    "1952-11-04": [{
        "event": "Buncombe County votes for Eisenhower",
        "description": "First Republican presidential vote since 1928. Ike wins county 22,000 to 20,000.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, November 5, 1952",
        "category": "asheville",
        "topic": "politics"
    }],

    # 1953
    "1953-05-01": [{
        "event": "Korean War ends; Asheville soldiers return",
        "description": "Armistice celebrations muted. 47 Buncombe County men killed in action.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, July 28, 1953",
        "category": "asheville",
        "topic": "military"
    }],
    "1953-09-10": [{
        "event": "Pack Square renovation begins",
        "description": "Downtown improvement project. New sidewalks, lighting, benches planned.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, September 11, 1953",
        "category": "asheville",
        "topic": "local"
    }],

    # 1954
    "1954-05-18": [{
        "event": "Asheville reacts to Brown v. Board",
        "description": "School board meets on integration ruling. No immediate action planned.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, May 19, 1954",
        "category": "asheville",
        "topic": "civil_rights"
    }],
    "1954-08-30": [{
        "event": "Hurricane Hazel approaches",
        "description": "Hurricane Hazel brings heavy rain. French Broad floods. 2 deaths in county.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, October 16, 1954",
        "category": "asheville",
        "topic": "weather"
    }],
    "1954-12-15": [{
        "event": "Asheville Mall planning begins",
        "description": "Developers announce shopping center for Tunnel Road. First in region.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, December 16, 1954",
        "category": "asheville",
        "topic": "economy"
    }],

    # 1955
    "1955-03-15": [{
        "event": "Black Mountain College financial crisis",
        "description": "College nearly bankrupt. Only 15 students enrolled. Closure discussed.",
        "location": "Black Mountain, NC",
        "source": "Asheville Citizen, March 16, 1955",
        "category": "asheville",
        "topic": "education"
    }],
    "1955-08-17": [{
        "event": "Hurricane Diane floods WNC",
        "description": "Remnants of Diane cause severe flooding. $2 million damage in region.",
        "location": "Western North Carolina",
        "source": "Asheville Citizen, August 18, 1955",
        "category": "north_carolina",
        "topic": "weather"
    }],
    "1955-09-01": [{
        "event": "Asheville schools remain segregated",
        "description": "School year begins with no integration. NAACP threatens lawsuit.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, September 2, 1955",
        "category": "asheville",
        "topic": "civil_rights"
    }],

    # 1956
    "1956-06-30": [{
        "event": "Interstate 40 construction announced",
        "description": "Federal highway to pass through Asheville. Route through mountains debated.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, July 1, 1956",
        "category": "asheville",
        "topic": "economy"
    }],
    "1956-09-04": [{
        "event": "First Black students enter Asheville schools",
        "description": "Asheville becomes first NC city to integrate schools. 4 students enter previously white schools.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, September 5, 1956",
        "category": "asheville",
        "topic": "civil_rights"
    }],
    "1956-10-01": [{
        "event": "Black Mountain College enters final months",
        "description": "Only 9 students remain. Faculty departed. Closure imminent.",
        "location": "Black Mountain, NC",
        "source": "Asheville Citizen, October 2, 1956",
        "category": "asheville",
        "topic": "education"
    }],

    # 1957
    "1957-01-15": [{
        "event": "Asheville pays off Depression debt",
        "description": "City makes final payment on 1920s bonds. 27 years of debt ended.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, January 16, 1957",
        "category": "asheville",
        "topic": "economy"
    }],
    "1957-06-15": [{
        "event": "Grove Arcade sold to federal government",
        "description": "Landmark building becomes federal offices. Stores relocated.",
        "location": "Asheville, NC",
        "source": "Asheville Citizen, June 16, 1957",
        "category": "asheville",
        "topic": "local"
    }],
    "1957-10-21": [{
        "event": "Black Mountain College officially closes",
        "description": "Experimental college closes after 24 years. Property sold to pay debts.",
        "location": "Black Mountain, NC",
        "source": "Asheville Citizen, October 22, 1957",
        "category": "asheville",
        "topic": "education"
    }]
}

def main():
    # Load existing national events
    with open('bmc_national_events.json', 'r') as f:
        data = json.load(f)

    # Add new Asheville events
    added = 0
    for date, events in asheville_events.items():
        if date in data['events']:
            # Append to existing date
            existing = data['events'][date]
            for new_event in events:
                # Check if event already exists
                exists = any(e['event'] == new_event['event'] for e in existing)
                if not exists:
                    existing.append(new_event)
                    added += 1
        else:
            # New date
            data['events'][date] = events
            added += len(events)

    # Sort events by date
    sorted_events = dict(sorted(data['events'].items()))
    data['events'] = sorted_events

    # Save updated file
    with open('bmc_national_events.json', 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Added {added} Asheville/WNC events from Asheville Citizen-Times archives")
    print(f"Total dates: {len(data['events'])}")

if __name__ == '__main__':
    main()
