#!/usr/bin/env python3
"""
Generate precise chronological data for BMC archive.
Includes exact dates and date ranges for processes/events.
"""

import json
from datetime import datetime

OUTPUT_FILE = "../bmc_chronology_precise.json"

# Comprehensive chronological events with precise dates
EVENTS = {
    # ============ 1933 ============
    "1933-01-30": {
        "usa": [],
        "world": [
            {
                "event": "Hitler appointed Chancellor of Germany",
                "description": "President Hindenburg appoints Adolf Hitler as Chancellor, marking the beginning of Nazi control.",
                "location": "Berlin, Germany",
                "source": "The New York Times, January 31, 1933",
                "topic": "politics"
            }
        ],
        "culture": []
    },
    "1933-02-27": {
        "usa": [],
        "world": [
            {
                "event": "Reichstag Fire",
                "description": "German parliament building set ablaze. Hitler uses event to suspend civil liberties.",
                "location": "Berlin, Germany",
                "source": "The Times, February 28, 1933",
                "topic": "politics"
            }
        ],
        "culture": []
    },
    "1933-03-02": {
        "usa": [],
        "world": [],
        "culture": [
            {
                "type": "film",
                "title": "King Kong",
                "creator": "Merian C. Cooper, Ernest B. Schoedsack",
                "description": "Revolutionary special effects film premieres at Radio City Music Hall.",
                "location": "New York City"
            }
        ]
    },
    "1933-03-04": {
        "usa": [
            {
                "event": "FDR inaugurated as 32nd President",
                "description": "'The only thing we have to fear is fear itself.' New Deal era begins.",
                "location": "Washington, D.C.",
                "source": "The New York Times, March 5, 1933",
                "topic": "politics"
            }
        ],
        "world": [],
        "culture": []
    },
    "1933-03-09": {
        "usa": [
            {
                "event": "Emergency Banking Act passed",
                "description": "Congress gives FDR power to regulate banking. Banks reopen March 13 after 'bank holiday.'",
                "location": "Washington, D.C.",
                "source": "Congressional Record",
                "topic": "economy"
            }
        ],
        "world": [],
        "culture": []
    },
    "1933-03-23": {
        "usa": [],
        "world": [
            {
                "event": "Enabling Act gives Hitler dictatorial powers",
                "description": "Reichstag passes act allowing Hitler to enact laws without parliament. Democracy ends in Germany.",
                "location": "Berlin, Germany",
                "source": "The Manchester Guardian, March 24, 1933",
                "topic": "politics"
            }
        ],
        "culture": []
    },
    "1933-05-10": {
        "usa": [],
        "world": [
            {
                "event": "Nazi book burnings begin",
                "description": "Students burn 25,000 'un-German' books in Berlin's Opera Square. Works by Jewish, pacifist authors destroyed.",
                "location": "Berlin, Germany",
                "source": "The New York Times, May 11, 1933",
                "topic": "culture"
            }
        ],
        "culture": []
    },
    "1933-05-18": {
        "usa": [
            {
                "event": "Tennessee Valley Authority created",
                "description": "FDR signs TVA Act creating federal corporation for regional development through dams and electricity.",
                "location": "Tennessee Valley",
                "source": "Public Law 73-17",
                "topic": "economy"
            }
        ],
        "world": [],
        "culture": []
    },
    "1933-10-14": {
        "usa": [],
        "world": [
            {
                "event": "Germany withdraws from League of Nations",
                "description": "Hitler announces withdrawal from League and Disarmament Conference.",
                "location": "Geneva, Switzerland",
                "source": "League of Nations Archives",
                "topic": "politics"
            }
        ],
        "culture": []
    },
    "1933-12-05": {
        "usa": [
            {
                "event": "Prohibition ends",
                "description": "21st Amendment ratified, repealing Prohibition after 13 years. Utah is 36th state to ratify.",
                "location": "United States",
                "source": "The New York Times, December 6, 1933",
                "topic": "politics"
            }
        ],
        "world": [],
        "culture": []
    },
    "1933-12-06": {
        "usa": [],
        "world": [],
        "culture": [
            {
                "type": "film",
                "title": "Duck Soup",
                "creator": "Leo McCarey, Marx Brothers",
                "description": "Marx Brothers' anarchic political satire. Later considered their masterpiece.",
                "location": "United States"
            }
        ]
    },

    # ============ 1934 ============
    "1934-06-30": {
        "usa": [],
        "world": [
            {
                "event": "Night of the Long Knives",
                "description": "Hitler purges SA leadership. Ernst Röhm and at least 85 others killed. SS becomes dominant.",
                "location": "Germany",
                "source": "The Times, July 2, 1934",
                "topic": "politics",
                "end_date": "1934-07-02"
            }
        ],
        "culture": []
    },
    "1934-08-02": {
        "usa": [],
        "world": [
            {
                "event": "Hitler becomes Führer",
                "description": "Following Hindenburg's death, Hitler merges Chancellor and President offices.",
                "location": "Berlin, Germany",
                "source": "The New York Times, August 3, 1934",
                "topic": "politics"
            }
        ],
        "culture": []
    },
    "1934-11-21": {
        "usa": [],
        "world": [],
        "culture": [
            {
                "type": "theater",
                "title": "Anything Goes",
                "creator": "Cole Porter",
                "description": "Musical opens on Broadway. Ethel Merman stars. 'I Get a Kick Out of You.'",
                "location": "Alvin Theatre, New York"
            }
        ]
    },

    # ============ 1935 ============
    "1935-03-16": {
        "usa": [],
        "world": [
            {
                "event": "Germany reintroduces military conscription",
                "description": "Hitler announces compulsory military service, violating Treaty of Versailles.",
                "location": "Berlin, Germany",
                "source": "The Times, March 18, 1935",
                "topic": "war"
            }
        ],
        "culture": []
    },
    "1935-05-06": {
        "usa": [
            {
                "event": "Works Progress Administration created",
                "description": "FDR creates WPA by executive order. Will employ 8.5 million including artists and writers.",
                "location": "Washington, D.C.",
                "source": "Executive Order 7034",
                "topic": "economy"
            }
        ],
        "world": [],
        "culture": []
    },
    "1935-08-14": {
        "usa": [
            {
                "event": "Social Security Act signed",
                "description": "FDR signs act establishing old-age pensions, unemployment insurance, aid to dependent children.",
                "location": "Washington, D.C.",
                "source": "Public Law 74-271",
                "topic": "politics"
            }
        ],
        "world": [],
        "culture": []
    },
    "1935-08-21": {
        "usa": [],
        "world": [],
        "culture": [
            {
                "type": "concert",
                "title": "Benny Goodman launches Swing Era",
                "creator": "Benny Goodman",
                "description": "Palomar Ballroom concert ignites national swing dance craze.",
                "location": "Los Angeles, California"
            }
        ]
    },
    "1935-09-15": {
        "usa": [],
        "world": [
            {
                "event": "Nuremberg Laws enacted",
                "description": "Laws strip Jews of citizenship and forbid marriage between Jews and non-Jews.",
                "location": "Nuremberg, Germany",
                "source": "Reichsgesetzblatt I",
                "topic": "politics"
            }
        ],
        "culture": []
    },
    "1935-10-03": {
        "usa": [],
        "world": [
            {
                "event": "Italy invades Ethiopia",
                "description": "Mussolini's forces invade without declaration of war. League condemns but fails to stop.",
                "location": "Ethiopia",
                "source": "The Times, October 4, 1935",
                "topic": "war",
                "end_date": "1936-05-07"
            }
        ],
        "culture": []
    },
    "1935-10-10": {
        "usa": [],
        "world": [],
        "culture": [
            {
                "type": "theater",
                "title": "Porgy and Bess",
                "creator": "George Gershwin",
                "description": "'Folk opera' premieres. 'Summertime' becomes jazz standard.",
                "location": "Alvin Theatre, New York"
            }
        ]
    },

    # ============ 1936 ============
    "1936-03-02": {
        "usa": [],
        "world": [],
        "culture": [
            {
                "type": "art",
                "title": "Cubism and Abstract Art",
                "creator": "Alfred H. Barr Jr.",
                "description": "MoMA landmark exhibition defines modernist canon.",
                "location": "Museum of Modern Art, New York",
                "end_date": "1936-04-19"
            }
        ]
    },
    "1936-03-07": {
        "usa": [],
        "world": [
            {
                "event": "Germany remilitarizes the Rhineland",
                "description": "German troops march into demilitarized Rhineland, violating Versailles Treaty.",
                "location": "Rhineland, Germany",
                "source": "The Manchester Guardian, March 9, 1936",
                "topic": "war"
            }
        ],
        "culture": []
    },
    "1936-07-17": {
        "usa": [],
        "world": [
            {
                "event": "Spanish Civil War begins",
                "description": "Nationalist generals led by Franco revolt against Republic. War becomes WWII prelude.",
                "location": "Spain",
                "source": "The Times, July 20, 1936",
                "topic": "war",
                "end_date": "1939-04-01"
            }
        ],
        "culture": []
    },
    "1936-08-01": {
        "usa": [],
        "world": [
            {
                "event": "Berlin Olympics open",
                "description": "Hitler opens Summer Olympics. Jesse Owens wins 4 gold medals. First televised Olympics.",
                "location": "Berlin, Germany",
                "source": "The New York Times, August 2, 1936",
                "topic": "sports",
                "end_date": "1936-08-16"
            }
        ],
        "culture": []
    },
    "1936-11-03": {
        "usa": [
            {
                "event": "FDR wins landslide re-election",
                "description": "Roosevelt defeats Alf Landon 523-8, largest Electoral College victory since 1820.",
                "location": "United States",
                "source": "The New York Times, November 4, 1936",
                "topic": "politics"
            }
        ],
        "world": [],
        "culture": []
    },
    "1936-12-11": {
        "usa": [],
        "world": [
            {
                "event": "Edward VIII abdicates",
                "description": "King abdicates to marry American divorcée Wallis Simpson. Brother becomes George VI.",
                "location": "London, England",
                "source": "The Times, December 12, 1936",
                "topic": "politics"
            }
        ],
        "culture": []
    },

    # ============ 1937 ============
    "1937-04-26": {
        "usa": [],
        "world": [
            {
                "event": "Guernica bombed",
                "description": "German Luftwaffe bombs Guernica, killing hundreds. Picasso's painting immortalizes atrocity.",
                "location": "Guernica, Spain",
                "source": "The Times, April 28, 1937",
                "topic": "war"
            }
        ],
        "culture": []
    },
    "1937-05-06": {
        "usa": [],
        "world": [
            {
                "event": "Hindenburg disaster",
                "description": "German airship catches fire landing at Lakehurst. 36 killed. Ends passenger airship era.",
                "location": "Lakehurst, New Jersey",
                "source": "The New York Times, May 7, 1937",
                "topic": "science"
            }
        ],
        "culture": []
    },
    "1937-06-16": {
        "usa": [],
        "world": [],
        "culture": [
            {
                "type": "theater",
                "title": "The Cradle Will Rock",
                "creator": "Marc Blitzstein",
                "description": "Federal Theatre banned. Orson Welles stages legendary unauthorized performance.",
                "location": "Venice Theatre, New York"
            }
        ]
    },
    "1937-07-07": {
        "usa": [],
        "world": [
            {
                "event": "Second Sino-Japanese War begins",
                "description": "Marco Polo Bridge Incident near Beijing escalates into full-scale war.",
                "location": "China",
                "source": "The Times, July 9, 1937",
                "topic": "war",
                "end_date": "1945-09-02"
            }
        ],
        "culture": []
    },
    "1937-07-12": {
        "usa": [],
        "world": [],
        "culture": [
            {
                "type": "art",
                "title": "Guernica exhibited",
                "creator": "Pablo Picasso",
                "description": "Anti-war masterpiece shown at Spanish Republic pavilion, Paris World's Fair.",
                "location": "Paris, France"
            }
        ]
    },

    # ============ 1938 ============
    "1938-01-16": {
        "usa": [],
        "world": [],
        "culture": [
            {
                "type": "concert",
                "title": "Benny Goodman at Carnegie Hall",
                "creator": "Benny Goodman",
                "description": "First jazz concert at Carnegie Hall. Historic integrated performance.",
                "location": "Carnegie Hall, New York"
            }
        ]
    },
    "1938-02-04": {
        "usa": [],
        "world": [],
        "culture": [
            {
                "type": "theater",
                "title": "Our Town",
                "creator": "Thornton Wilder",
                "description": "Pulitzer Prize play. Innovative staging without sets.",
                "location": "Henry Miller's Theatre, New York"
            }
        ]
    },
    "1938-03-12": {
        "usa": [],
        "world": [
            {
                "event": "Anschluss: Germany annexes Austria",
                "description": "German troops march into Austria unopposed. Hitler announces union.",
                "location": "Austria",
                "source": "The Times, March 14, 1938",
                "topic": "war"
            }
        ],
        "culture": []
    },
    "1938-09-30": {
        "usa": [],
        "world": [
            {
                "event": "Munich Agreement signed",
                "description": "Britain, France agree to German annexation of Sudetenland. 'Peace for our time.'",
                "location": "Munich, Germany",
                "source": "The Times, October 1, 1938",
                "topic": "politics"
            }
        ],
        "culture": []
    },
    "1938-10-30": {
        "usa": [
            {
                "event": "War of the Worlds broadcast",
                "description": "Orson Welles' CBS radio adaptation causes panic as listeners believe Martians invading.",
                "location": "New York City",
                "source": "The New York Times, October 31, 1938",
                "topic": "culture"
            }
        ],
        "world": [],
        "culture": []
    },
    "1938-11-09": {
        "usa": [],
        "world": [
            {
                "event": "Kristallnacht",
                "description": "Nazi mobs attack Jewish homes, businesses, synagogues. 91 killed, 30,000 sent to camps.",
                "location": "Germany and Austria",
                "source": "The Manchester Guardian, November 11, 1938",
                "topic": "politics",
                "end_date": "1938-11-10"
            }
        ],
        "culture": []
    },

    # ============ 1939 ============
    "1939-03-28": {
        "usa": [],
        "world": [],
        "culture": [
            {
                "type": "theater",
                "title": "The Philadelphia Story",
                "creator": "Philip Barry",
                "description": "Katharine Hepburn stars. Play revives her career.",
                "location": "Shubert Theatre, New York"
            }
        ]
    },
    "1939-04-09": {
        "usa": [],
        "world": [],
        "culture": [
            {
                "type": "concert",
                "title": "Marian Anderson at Lincoln Memorial",
                "creator": "Marian Anderson",
                "description": "After DAR ban, contralto performs for 75,000 on Easter Sunday.",
                "location": "Lincoln Memorial, Washington D.C."
            }
        ]
    },
    "1939-04-30": {
        "usa": [
            {
                "event": "New York World's Fair opens",
                "description": "'World of Tomorrow' fair with technology exhibits. First public TV demonstration.",
                "location": "Flushing Meadows, New York",
                "source": "The New York Times, May 1, 1939",
                "topic": "culture",
                "end_date": "1940-10-27"
            }
        ],
        "world": [],
        "culture": []
    },
    "1939-08-17": {
        "usa": [],
        "world": [],
        "culture": [
            {
                "type": "film",
                "title": "The Wizard of Oz",
                "creator": "Victor Fleming",
                "description": "Judy Garland in MGM's Technicolor fantasy. 'Somewhere Over the Rainbow.'",
                "location": "United States"
            }
        ]
    },
    "1939-08-23": {
        "usa": [],
        "world": [
            {
                "event": "Nazi-Soviet Pact signed",
                "description": "Non-aggression pact with secret protocols dividing Eastern Europe.",
                "location": "Moscow, USSR",
                "source": "The Times, August 24, 1939",
                "topic": "politics"
            }
        ],
        "culture": []
    },
    "1939-09-01": {
        "usa": [],
        "world": [
            {
                "event": "Germany invades Poland - WWII begins",
                "description": "1.5 million German troops invade Poland. World War II begins in Europe.",
                "location": "Poland",
                "source": "The Times, September 2, 1939",
                "topic": "war"
            }
        ],
        "culture": []
    },
    "1939-09-03": {
        "usa": [],
        "world": [
            {
                "event": "Britain and France declare war on Germany",
                "description": "After Germany ignores ultimatum, Allies declare war. Second World War begins.",
                "location": "London/Paris",
                "source": "The Times, September 4, 1939",
                "topic": "war"
            }
        ],
        "culture": []
    },
    "1939-12-15": {
        "usa": [],
        "world": [],
        "culture": [
            {
                "type": "film",
                "title": "Gone with the Wind",
                "creator": "Victor Fleming",
                "description": "Civil War epic premieres in Atlanta. Vivien Leigh, Clark Gable.",
                "location": "Atlanta, Georgia"
            }
        ]
    },

    # ============ 1940 ============
    "1940-04-09": {
        "usa": [],
        "world": [
            {
                "event": "Germany invades Denmark and Norway",
                "description": "Denmark conquered in hours. Norway campaign lasts two months.",
                "location": "Scandinavia",
                "source": "The Times, April 10, 1940",
                "topic": "war",
                "end_date": "1940-06-10"
            }
        ],
        "culture": []
    },
    "1940-05-10": {
        "usa": [],
        "world": [
            {
                "event": "Germany invades Western Europe; Churchill becomes PM",
                "description": "Attack on Netherlands, Belgium, Luxembourg, France. Churchill replaces Chamberlain.",
                "location": "Western Europe",
                "source": "The Times, May 11, 1940",
                "topic": "war"
            }
        ],
        "culture": []
    },
    "1940-05-26": {
        "usa": [],
        "world": [
            {
                "event": "Dunkirk evacuation begins",
                "description": "Operation Dynamo evacuates 338,000 Allied soldiers from France over 9 days.",
                "location": "Dunkirk, France",
                "source": "The Times, June 5, 1940",
                "topic": "war",
                "end_date": "1940-06-04"
            }
        ],
        "culture": []
    },
    "1940-06-22": {
        "usa": [],
        "world": [
            {
                "event": "France surrenders to Germany",
                "description": "Armistice signed in same railway car where Germany surrendered in 1918.",
                "location": "Compiègne, France",
                "source": "The Times, June 24, 1940",
                "topic": "war"
            }
        ],
        "culture": []
    },
    "1940-07-10": {
        "usa": [],
        "world": [
            {
                "event": "Battle of Britain begins",
                "description": "Luftwaffe begins sustained bombing campaign. RAF defends against invasion.",
                "location": "United Kingdom",
                "source": "The Times, July 11, 1940",
                "topic": "war",
                "end_date": "1940-10-31"
            }
        ],
        "culture": []
    },
    "1940-09-16": {
        "usa": [
            {
                "event": "Selective Training and Service Act signed",
                "description": "First peacetime draft in U.S. history. 16 million men register.",
                "location": "Washington, D.C.",
                "source": "Public Law 76-783",
                "topic": "war"
            }
        ],
        "world": [],
        "culture": []
    },
    "1940-11-05": {
        "usa": [
            {
                "event": "FDR wins unprecedented third term",
                "description": "Roosevelt defeats Wendell Willkie, first president to win third term.",
                "location": "United States",
                "source": "The New York Times, November 6, 1940",
                "topic": "politics"
            }
        ],
        "world": [],
        "culture": []
    },

    # ============ 1941 ============
    "1941-01-23": {
        "usa": [],
        "world": [],
        "culture": [
            {
                "type": "concert",
                "title": "Duke Ellington at Carnegie Hall",
                "creator": "Duke Ellington",
                "description": "Premieres 'Black, Brown and Beige' - 45-minute tone poem.",
                "location": "Carnegie Hall, New York"
            }
        ]
    },
    "1941-03-11": {
        "usa": [
            {
                "event": "Lend-Lease Act signed",
                "description": "Allows U.S. to supply weapons to Britain and Allies. Ends American neutrality.",
                "location": "Washington, D.C.",
                "source": "Public Law 77-11",
                "topic": "war"
            }
        ],
        "world": [],
        "culture": []
    },
    "1941-05-01": {
        "usa": [],
        "world": [],
        "culture": [
            {
                "type": "film",
                "title": "Citizen Kane",
                "creator": "Orson Welles",
                "description": "Directorial debut revolutionizes cinema with deep focus and non-linear narrative.",
                "location": "United States"
            }
        ]
    },
    "1941-06-22": {
        "usa": [],
        "world": [
            {
                "event": "Germany invades Soviet Union",
                "description": "Operation Barbarossa: 3 million troops attack in largest military operation ever.",
                "location": "USSR",
                "source": "The Times, June 23, 1941",
                "topic": "war"
            }
        ],
        "culture": []
    },
    "1941-12-07": {
        "usa": [
            {
                "event": "Japan attacks Pearl Harbor",
                "description": "Japanese attack Pacific Fleet. 2,403 killed, 8 battleships damaged or sunk.",
                "location": "Pearl Harbor, Hawaii",
                "source": "The New York Times, December 8, 1941",
                "topic": "war"
            }
        ],
        "world": [],
        "culture": []
    },
    "1941-12-08": {
        "usa": [
            {
                "event": "United States declares war on Japan",
                "description": "FDR: 'a date which will live in infamy.' War declared with one dissent.",
                "location": "Washington, D.C.",
                "source": "Congressional Record",
                "topic": "war"
            }
        ],
        "world": [],
        "culture": []
    },
    "1941-12-11": {
        "usa": [],
        "world": [
            {
                "event": "Germany and Italy declare war on US",
                "description": "America now fully engaged in both theaters of World War II.",
                "location": "Berlin/Rome",
                "source": "The Times, December 12, 1941",
                "topic": "war"
            }
        ],
        "culture": []
    },

    # ============ 1942 ============
    "1942-02-19": {
        "usa": [
            {
                "event": "Executive Order 9066: Japanese internment",
                "description": "120,000 Japanese Americans, mostly citizens, forced into internment camps.",
                "location": "United States",
                "source": "Executive Order 9066",
                "topic": "politics"
            }
        ],
        "world": [],
        "culture": []
    },
    "1942-06-04": {
        "usa": [],
        "world": [
            {
                "event": "Battle of Midway",
                "description": "U.S. Navy defeats Japan, sinking 4 carriers. Pacific War turning point.",
                "location": "Midway Atoll",
                "source": "The New York Times, June 7, 1942",
                "topic": "war",
                "end_date": "1942-06-07"
            }
        ],
        "culture": []
    },
    "1942-08-07": {
        "usa": [],
        "world": [
            {
                "event": "Guadalcanal Campaign begins",
                "description": "Marines land in first major Allied offensive. Six-month battle follows.",
                "location": "Solomon Islands",
                "source": "The New York Times, August 8, 1942",
                "topic": "war",
                "end_date": "1943-02-09"
            }
        ],
        "culture": []
    },
    "1942-10-20": {
        "usa": [],
        "world": [],
        "culture": [
            {
                "type": "art",
                "title": "Art of This Century gallery opens",
                "creator": "Peggy Guggenheim",
                "description": "Frederick Kiesler-designed space showcases Surrealism and emerging Abstract Expressionists.",
                "location": "New York City"
            }
        ]
    },
    "1942-11-08": {
        "usa": [],
        "world": [
            {
                "event": "Operation Torch: Allied invasion of North Africa",
                "description": "Anglo-American forces land in Morocco and Algeria. First major US ground operation.",
                "location": "North Africa",
                "source": "The Times, November 9, 1942",
                "topic": "war"
            }
        ],
        "culture": []
    },
    "1942-11-26": {
        "usa": [],
        "world": [],
        "culture": [
            {
                "type": "film",
                "title": "Casablanca",
                "creator": "Michael Curtiz",
                "description": "Bogart and Bergman in wartime romance. 'Here's looking at you, kid.'",
                "location": "United States"
            }
        ]
    },

    # ============ 1943 ============
    "1943-02-02": {
        "usa": [],
        "world": [
            {
                "event": "German surrender at Stalingrad",
                "description": "6th Army surrenders after brutal urban combat. 91,000 captured. Major turning point.",
                "location": "Stalingrad, USSR",
                "source": "The Times, February 3, 1943",
                "topic": "war"
            }
        ],
        "culture": []
    },
    "1943-03-31": {
        "usa": [],
        "world": [],
        "culture": [
            {
                "type": "theater",
                "title": "Oklahoma!",
                "creator": "Rodgers and Hammerstein",
                "description": "Revolutionary musical integrates song, dance, story. 2,212 performances.",
                "location": "St. James Theatre, New York"
            }
        ]
    },
    "1943-07-10": {
        "usa": [],
        "world": [
            {
                "event": "Allied invasion of Sicily",
                "description": "Operation Husky: 160,000 troops land. Mussolini falls two weeks later.",
                "location": "Sicily, Italy",
                "source": "The Times, July 12, 1943",
                "topic": "war",
                "end_date": "1943-08-17"
            }
        ],
        "culture": []
    },
    "1943-09-08": {
        "usa": [],
        "world": [
            {
                "event": "Italy surrenders",
                "description": "Armistice signed. Germany immediately occupies much of Italy.",
                "location": "Italy",
                "source": "The Times, September 9, 1943",
                "topic": "war"
            }
        ],
        "culture": []
    },

    # ============ 1944 ============
    "1944-06-06": {
        "usa": [],
        "world": [
            {
                "event": "D-Day: Allied invasion of Normandy",
                "description": "Operation Overlord: 156,000 troops land on five beaches. Largest amphibious invasion ever.",
                "location": "Normandy, France",
                "source": "The Times, June 7, 1944",
                "topic": "war"
            }
        ],
        "culture": []
    },
    "1944-06-22": {
        "usa": [
            {
                "event": "GI Bill signed",
                "description": "Servicemen's Readjustment Act provides education, housing benefits to veterans.",
                "location": "Washington, D.C.",
                "source": "Public Law 78-346",
                "topic": "politics"
            }
        ],
        "world": [],
        "culture": []
    },
    "1944-07-20": {
        "usa": [],
        "world": [
            {
                "event": "Failed assassination attempt on Hitler",
                "description": "Stauffenberg's bomb fails. Thousands executed in reprisals.",
                "location": "Rastenburg, East Prussia",
                "source": "The Times, July 22, 1944",
                "topic": "war"
            }
        ],
        "culture": []
    },
    "1944-08-25": {
        "usa": [],
        "world": [
            {
                "event": "Liberation of Paris",
                "description": "French and American forces liberate Paris after 4 years. De Gaulle leads parade.",
                "location": "Paris, France",
                "source": "The Times, August 26, 1944",
                "topic": "war"
            }
        ],
        "culture": []
    },
    "1944-12-16": {
        "usa": [],
        "world": [
            {
                "event": "Battle of the Bulge begins",
                "description": "Germany's last major offensive. 200,000 troops attack through Ardennes.",
                "location": "Ardennes, Belgium",
                "source": "The Times, December 18, 1944",
                "topic": "war",
                "end_date": "1945-01-25"
            }
        ],
        "culture": []
    },
    "1944-12-26": {
        "usa": [],
        "world": [],
        "culture": [
            {
                "type": "theater",
                "title": "The Glass Menagerie",
                "creator": "Tennessee Williams",
                "description": "'Memory play' premieres. Laurette Taylor stars.",
                "location": "Civic Theatre, Chicago"
            }
        ]
    },

    # ============ 1945 ============
    "1945-02-04": {
        "usa": [],
        "world": [
            {
                "event": "Yalta Conference",
                "description": "FDR, Churchill, Stalin plan post-war Europe. UN, division of Germany agreed.",
                "location": "Yalta, Crimea",
                "source": "The Times, February 13, 1945",
                "topic": "politics",
                "end_date": "1945-02-11"
            }
        ],
        "culture": []
    },
    "1945-02-19": {
        "usa": [],
        "world": [
            {
                "event": "Battle of Iwo Jima",
                "description": "Marines invade. 36-day battle. Iconic flag-raising on Mount Suribachi.",
                "location": "Iwo Jima, Japan",
                "source": "The New York Times, February 20, 1945",
                "topic": "war",
                "end_date": "1945-03-26"
            }
        ],
        "culture": []
    },
    "1945-04-12": {
        "usa": [
            {
                "event": "President Roosevelt dies",
                "description": "FDR dies of cerebral hemorrhage. Truman sworn in as 33rd President.",
                "location": "Warm Springs, Georgia",
                "source": "The New York Times, April 13, 1945",
                "topic": "politics"
            }
        ],
        "world": [],
        "culture": []
    },
    "1945-04-19": {
        "usa": [],
        "world": [],
        "culture": [
            {
                "type": "theater",
                "title": "Carousel",
                "creator": "Rodgers and Hammerstein",
                "description": "Dark musical. 'You'll Never Walk Alone' becomes anthem.",
                "location": "Majestic Theatre, New York"
            }
        ]
    },
    "1945-04-30": {
        "usa": [],
        "world": [
            {
                "event": "Hitler commits suicide",
                "description": "Hitler kills himself in bunker as Soviets close in. Eva Braun dies with him.",
                "location": "Berlin, Germany",
                "source": "The Times, May 2, 1945",
                "topic": "war"
            }
        ],
        "culture": []
    },
    "1945-05-08": {
        "usa": [],
        "world": [
            {
                "event": "V-E Day: Germany surrenders",
                "description": "Germany signs unconditional surrender. Victory in Europe celebrated.",
                "location": "Berlin, Germany",
                "source": "The Times, May 9, 1945",
                "topic": "war"
            }
        ],
        "culture": []
    },
    "1945-07-16": {
        "usa": [
            {
                "event": "First atomic bomb tested",
                "description": "Trinity test. Oppenheimer: 'I am become Death, the destroyer of worlds.'",
                "location": "Alamogordo, New Mexico",
                "source": "Manhattan Engineer District Records",
                "topic": "science"
            }
        ],
        "world": [],
        "culture": []
    },
    "1945-08-06": {
        "usa": [],
        "world": [
            {
                "event": "Atomic bomb dropped on Hiroshima",
                "description": "'Enola Gay' drops uranium bomb. 80,000 killed instantly; 140,000 by year's end.",
                "location": "Hiroshima, Japan",
                "source": "The New York Times, August 7, 1945",
                "topic": "war"
            }
        ],
        "culture": []
    },
    "1945-08-09": {
        "usa": [],
        "world": [
            {
                "event": "Atomic bomb dropped on Nagasaki",
                "description": "Second bomb destroys Nagasaki. 40,000 killed. Japan begins surrender talks.",
                "location": "Nagasaki, Japan",
                "source": "The New York Times, August 10, 1945",
                "topic": "war"
            }
        ],
        "culture": []
    },
    "1945-08-15": {
        "usa": [],
        "world": [
            {
                "event": "V-J Day: Japan surrenders",
                "description": "Emperor Hirohito announces surrender. World War II ends after six years.",
                "location": "Tokyo, Japan",
                "source": "The Times, August 16, 1945",
                "topic": "war"
            }
        ],
        "culture": []
    },
    "1945-11-20": {
        "usa": [],
        "world": [
            {
                "event": "Nuremberg Trials begin",
                "description": "International tribunal tries 24 Nazi war criminals. Establishes legal precedents.",
                "location": "Nuremberg, Germany",
                "source": "The Times, November 21, 1945",
                "topic": "politics",
                "end_date": "1946-10-01"
            }
        ],
        "culture": []
    },

    # ============ 1946-1957 (abbreviated) ============
    "1946-03-05": {
        "usa": [],
        "world": [
            {
                "event": "Churchill's 'Iron Curtain' speech",
                "description": "'An iron curtain has descended across the Continent.' Cold War rhetoric begins.",
                "location": "Fulton, Missouri",
                "source": "The New York Times, March 6, 1946",
                "topic": "politics"
            }
        ],
        "culture": []
    },
    "1946-05-16": {
        "usa": [],
        "world": [],
        "culture": [
            {
                "type": "theater",
                "title": "Annie Get Your Gun",
                "creator": "Irving Berlin",
                "description": "Ethel Merman as Annie Oakley. 'There's No Business Like Show Business.'",
                "location": "Imperial Theatre, New York"
            }
        ]
    },
    "1947-03-12": {
        "usa": [
            {
                "event": "Truman Doctrine announced",
                "description": "Pledges support for countries resisting communism. $400M for Greece and Turkey.",
                "location": "Washington, D.C.",
                "source": "The New York Times, March 13, 1947",
                "topic": "politics"
            }
        ],
        "world": [],
        "culture": []
    },
    "1947-04-15": {
        "usa": [
            {
                "event": "Jackie Robinson breaks baseball color barrier",
                "description": "First Black player in MLB since 1880s debuts for Brooklyn Dodgers.",
                "location": "Brooklyn, New York",
                "source": "The New York Times, April 16, 1947",
                "topic": "sports"
            }
        ],
        "world": [],
        "culture": []
    },
    "1947-06-05": {
        "usa": [
            {
                "event": "Marshall Plan announced",
                "description": "Massive European recovery aid program proposed. $13 billion provided 1948-1952.",
                "location": "Cambridge, Massachusetts",
                "source": "The New York Times, June 6, 1947",
                "topic": "economy"
            }
        ],
        "world": [],
        "culture": []
    },
    "1947-12-03": {
        "usa": [],
        "world": [],
        "culture": [
            {
                "type": "theater",
                "title": "A Streetcar Named Desire",
                "creator": "Tennessee Williams",
                "description": "Brando as Stanley Kowalski. 'I have always depended on the kindness of strangers.'",
                "location": "Ethel Barrymore Theatre, New York"
            }
        ]
    },
    "1948-05-14": {
        "usa": [],
        "world": [
            {
                "event": "State of Israel proclaimed",
                "description": "Ben-Gurion declares independence. U.S. recognizes immediately. Arab-Israeli War begins.",
                "location": "Tel Aviv, Israel",
                "source": "The Times, May 15, 1948",
                "topic": "politics"
            }
        ],
        "culture": []
    },
    "1948-06-21": {
        "usa": [],
        "world": [],
        "culture": [
            {
                "type": "concert",
                "title": "LP records introduced",
                "creator": "Columbia Records",
                "description": "33 1/3 RPM unveiled at Waldorf Astoria. 10\" and 12\" formats revolutionize music.",
                "location": "Waldorf Astoria, New York"
            }
        ]
    },
    "1948-06-24": {
        "usa": [],
        "world": [
            {
                "event": "Berlin Blockade begins",
                "description": "Soviets block ground access. Allies begin airlift to supply 2.5 million residents.",
                "location": "Berlin, Germany",
                "source": "The Times, June 25, 1948",
                "topic": "war",
                "end_date": "1949-05-12"
            }
        ],
        "culture": []
    },
    "1949-02-10": {
        "usa": [],
        "world": [],
        "culture": [
            {
                "type": "theater",
                "title": "Death of a Salesman",
                "creator": "Arthur Miller",
                "description": "Pulitzer Prize. Cobb as Willy Loman. 'Attention must be paid.'",
                "location": "Morosco Theatre, New York"
            }
        ]
    },
    "1949-04-04": {
        "usa": [],
        "world": [
            {
                "event": "NATO founded",
                "description": "Twelve nations sign North Atlantic Treaty for collective defense.",
                "location": "Washington, D.C.",
                "source": "The New York Times, April 5, 1949",
                "topic": "politics"
            }
        ],
        "culture": []
    },
    "1949-10-01": {
        "usa": [],
        "world": [
            {
                "event": "People's Republic of China proclaimed",
                "description": "Mao declares Communist victory. Nationalists flee to Taiwan.",
                "location": "Beijing, China",
                "source": "The Times, October 3, 1949",
                "topic": "politics"
            }
        ],
        "culture": []
    },
    "1950-06-25": {
        "usa": [],
        "world": [
            {
                "event": "Korean War begins",
                "description": "North Korea invades South. UN intervenes. Cold War turns hot.",
                "location": "Korea",
                "source": "The New York Times, June 26, 1950",
                "topic": "war",
                "end_date": "1953-07-27"
            }
        ],
        "culture": []
    },
    "1952-08-29": {
        "usa": [],
        "world": [],
        "culture": [
            {
                "type": "concert",
                "title": "John Cage's 4'33\"",
                "creator": "John Cage",
                "description": "David Tudor premieres silent composition. Audience sounds become the music.",
                "location": "Woodstock, New York"
            }
        ]
    },
    "1953-07-27": {
        "usa": [],
        "world": [
            {
                "event": "Korean War armistice",
                "description": "Armistice ends fighting. Korea remains divided. 36,000 Americans died.",
                "location": "Panmunjom, Korea",
                "source": "The New York Times, July 28, 1953",
                "topic": "war"
            }
        ],
        "culture": []
    },
    "1954-05-17": {
        "usa": [
            {
                "event": "Brown v. Board of Education",
                "description": "Supreme Court: school segregation unconstitutional. 'Separate is inherently unequal.'",
                "location": "Washington, D.C.",
                "source": "The New York Times, May 18, 1954",
                "topic": "politics"
            }
        ],
        "world": [],
        "culture": []
    },
    "1955-12-01": {
        "usa": [
            {
                "event": "Rosa Parks arrested",
                "description": "Refuses to give up bus seat. Sparks Montgomery Bus Boycott led by MLK Jr.",
                "location": "Montgomery, Alabama",
                "source": "The New York Times, December 6, 1955",
                "topic": "politics"
            }
        ],
        "world": [],
        "culture": []
    },
    "1956-03-15": {
        "usa": [],
        "world": [],
        "culture": [
            {
                "type": "theater",
                "title": "My Fair Lady",
                "creator": "Lerner and Loewe",
                "description": "Rex Harrison, Julie Andrews. Record 2,717 performances.",
                "location": "Mark Hellinger Theatre, New York"
            }
        ]
    },
    "1957-09-04": {
        "usa": [
            {
                "event": "Little Rock school integration",
                "description": "Governor uses Guard to block Black students. Eisenhower sends federal troops.",
                "location": "Little Rock, Arkansas",
                "source": "The New York Times, September 5, 1957",
                "topic": "politics"
            }
        ],
        "world": [],
        "culture": []
    },
    "1957-09-26": {
        "usa": [],
        "world": [],
        "culture": [
            {
                "type": "theater",
                "title": "West Side Story",
                "creator": "Bernstein, Sondheim",
                "description": "Modern Romeo and Juliet. Jerome Robbins choreography.",
                "location": "Winter Garden Theatre, New York"
            }
        ]
    },
    "1957-10-04": {
        "usa": [],
        "world": [
            {
                "event": "Sputnik launched",
                "description": "First artificial satellite. Space race begins. Americans shocked.",
                "location": "Baikonur, Kazakhstan",
                "source": "The New York Times, October 5, 1957",
                "topic": "science"
            }
        ],
        "culture": []
    }
}


def main():
    print("=" * 70)
    print("GENERATING PRECISE CHRONOLOGY DATA")
    print("=" * 70)

    output = {
        "metadata": {
            "description": "Precise chronological data for BMC archive",
            "coverage": "1933-1957",
            "generated_at": datetime.now().isoformat()
        },
        "events": EVENTS
    }

    # Statistics
    total_usa = 0
    total_world = 0
    total_culture = 0
    events_with_duration = 0

    for date, data in EVENTS.items():
        total_usa += len(data.get("usa", []))
        total_world += len(data.get("world", []))
        total_culture += len(data.get("culture", []))

        for cat in ["usa", "world", "culture"]:
            for e in data.get(cat, []):
                if "end_date" in e:
                    events_with_duration += 1

    print(f"\nTotal events: {total_usa + total_world + total_culture}")
    print(f"  USA: {total_usa}")
    print(f"  International: {total_world}")
    print(f"  Culture: {total_culture}")
    print(f"  Events with duration: {events_with_duration}")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Output: {OUTPUT_FILE}")


if __name__ == '__main__':
    main()
