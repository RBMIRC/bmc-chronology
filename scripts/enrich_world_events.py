#!/usr/bin/env python3
"""
Enrich world events data with more details.
Add descriptions, topics, locations, and sources.
"""

import json
from datetime import datetime

ARCHIVE_FILE = "../bmc_complete_archive.json"
OUTPUT_FILE = "../bmc_complete_archive.json"

# Major historical events 1933-1957 with details
HISTORICAL_EVENTS = {
    # 1933
    "1933-01-30": [
        {
            "event": "Hitler appointed Chancellor of Germany",
            "category": "world",
            "topic": "politics",
            "location": "Berlin, Germany",
            "description": "President Hindenburg appoints Adolf Hitler as Chancellor, marking the beginning of Nazi control over Germany. The Weimar Republic effectively ends.",
            "source": "The New York Times, January 31, 1933"
        }
    ],
    "1933-02-27": [
        {
            "event": "Reichstag Fire",
            "category": "world",
            "topic": "politics",
            "location": "Berlin, Germany",
            "description": "The German parliament building is set ablaze. Hitler uses the event to consolidate power, suspending civil liberties the next day.",
            "source": "The Times, February 28, 1933"
        }
    ],
    "1933-03-04": [
        {
            "event": "FDR inaugurated as 32nd President",
            "category": "usa",
            "topic": "politics",
            "location": "Washington, D.C.",
            "description": "Franklin D. Roosevelt delivers his first inaugural address: 'The only thing we have to fear is fear itself.' Begins the New Deal era.",
            "source": "The New York Times, March 5, 1933"
        }
    ],
    "1933-03-09": [
        {
            "event": "Emergency Banking Act passed",
            "category": "usa",
            "topic": "economy",
            "location": "Washington, D.C.",
            "description": "Congress passes the Emergency Banking Act, giving FDR power to regulate banking. Banks reopen March 13 after the 'bank holiday.'",
            "source": "Congressional Record, March 9, 1933"
        }
    ],
    "1933-03-23": [
        {
            "event": "Enabling Act gives Hitler dictatorial powers",
            "category": "world",
            "topic": "politics",
            "location": "Berlin, Germany",
            "description": "The Reichstag passes the Enabling Act, allowing Hitler to enact laws without parliamentary consent. Democracy in Germany ends.",
            "source": "The Manchester Guardian, March 24, 1933"
        }
    ],
    "1933-05-10": [
        {
            "event": "Nazi book burnings begin",
            "category": "world",
            "topic": "culture",
            "location": "Berlin, Germany",
            "description": "German students burn 25,000 'un-German' books in Berlin's Opera Square. Works by Jewish, pacifist, and socialist authors destroyed.",
            "source": "The New York Times, May 11, 1933"
        }
    ],
    "1933-05-18": [
        {
            "event": "Tennessee Valley Authority created",
            "category": "usa",
            "topic": "economy",
            "location": "Tennessee Valley",
            "description": "FDR signs the TVA Act, creating a federal corporation to develop the Tennessee Valley region through dams, electricity, and flood control.",
            "source": "Public Law 73-17, May 18, 1933"
        }
    ],
    "1933-06-16": [
        {
            "event": "National Industrial Recovery Act signed",
            "category": "usa",
            "topic": "economy",
            "location": "Washington, D.C.",
            "description": "NIRA creates the Public Works Administration and establishes industry codes. Part of FDR's 'First Hundred Days' of New Deal legislation.",
            "source": "Public Law 73-67, June 16, 1933"
        }
    ],
    "1933-10-14": [
        {
            "event": "Germany withdraws from League of Nations",
            "category": "world",
            "topic": "politics",
            "location": "Geneva, Switzerland",
            "description": "Hitler announces Germany's withdrawal from the League of Nations and the Disarmament Conference, signaling aggressive foreign policy.",
            "source": "League of Nations Archives, October 1933"
        }
    ],
    "1933-12-05": [
        {
            "event": "Prohibition ends in the United States",
            "category": "usa",
            "topic": "politics",
            "location": "United States",
            "description": "The 21st Amendment is ratified, repealing Prohibition after 13 years. Utah becomes the 36th state to ratify.",
            "source": "The New York Times, December 6, 1933"
        }
    ],

    # 1934
    "1934-06-30": [
        {
            "event": "Night of the Long Knives",
            "category": "world",
            "topic": "politics",
            "location": "Germany",
            "description": "Hitler purges the SA leadership. Ernst Röhm and at least 85 others killed. The SS becomes the dominant Nazi paramilitary force.",
            "source": "The Times, July 2, 1934"
        }
    ],
    "1934-08-02": [
        {
            "event": "Hitler becomes Führer",
            "category": "world",
            "topic": "politics",
            "location": "Berlin, Germany",
            "description": "Following Hindenburg's death, Hitler merges the offices of Chancellor and President, becoming 'Führer und Reichskanzler.'",
            "source": "The New York Times, August 3, 1934"
        }
    ],

    # 1935
    "1935-03-16": [
        {
            "event": "Germany reintroduces military conscription",
            "category": "world",
            "topic": "war",
            "location": "Berlin, Germany",
            "description": "Hitler announces the reintroduction of compulsory military service, violating the Treaty of Versailles. Wehrmacht expansion begins.",
            "source": "The Times, March 18, 1935"
        }
    ],
    "1935-05-06": [
        {
            "event": "Works Progress Administration created",
            "category": "usa",
            "topic": "economy",
            "location": "Washington, D.C.",
            "description": "FDR creates the WPA by executive order. It will employ 8.5 million Americans, including artists, writers, and musicians.",
            "source": "Executive Order 7034, May 6, 1935"
        }
    ],
    "1935-08-14": [
        {
            "event": "Social Security Act signed",
            "category": "usa",
            "topic": "politics",
            "location": "Washington, D.C.",
            "description": "FDR signs the Social Security Act, establishing old-age pensions, unemployment insurance, and aid to dependent children.",
            "source": "Public Law 74-271, August 14, 1935"
        }
    ],
    "1935-09-15": [
        {
            "event": "Nuremberg Laws enacted",
            "category": "world",
            "topic": "politics",
            "location": "Nuremberg, Germany",
            "description": "Nazi Germany passes laws stripping Jews of citizenship and forbidding marriage between Jews and non-Jews. Legal persecution begins.",
            "source": "Reichsgesetzblatt I, 1935"
        }
    ],
    "1935-10-03": [
        {
            "event": "Italy invades Ethiopia",
            "category": "world",
            "topic": "war",
            "location": "Ethiopia",
            "description": "Mussolini's forces invade Ethiopia without declaration of war. League of Nations condemns but fails to stop the aggression.",
            "source": "The Times, October 4, 1935"
        }
    ],

    # 1936
    "1936-03-07": [
        {
            "event": "Germany remilitarizes the Rhineland",
            "category": "world",
            "topic": "war",
            "location": "Rhineland, Germany",
            "description": "German troops march into the demilitarized Rhineland, violating the Treaty of Versailles. France and Britain do not respond.",
            "source": "The Manchester Guardian, March 9, 1936"
        }
    ],
    "1936-07-17": [
        {
            "event": "Spanish Civil War begins",
            "category": "world",
            "topic": "war",
            "location": "Spain",
            "description": "Nationalist generals led by Franco revolt against the Republican government. The war becomes a prelude to World War II.",
            "source": "The Times, July 20, 1936"
        }
    ],
    "1936-08-01": [
        {
            "event": "Berlin Olympics open",
            "category": "world",
            "topic": "sports",
            "location": "Berlin, Germany",
            "description": "Hitler opens the Summer Olympics. Jesse Owens wins 4 gold medals, challenging Nazi racial ideology. First televised Olympics.",
            "source": "The New York Times, August 2, 1936"
        }
    ],
    "1936-11-03": [
        {
            "event": "FDR wins landslide re-election",
            "category": "usa",
            "topic": "politics",
            "location": "United States",
            "description": "Roosevelt defeats Alf Landon in the largest Electoral College victory since 1820 (523-8). Democrats dominate Congress.",
            "source": "The New York Times, November 4, 1936"
        }
    ],
    "1936-12-11": [
        {
            "event": "Edward VIII abdicates",
            "category": "world",
            "topic": "politics",
            "location": "London, England",
            "description": "King Edward VIII abdicates to marry American divorcée Wallis Simpson. His brother becomes George VI.",
            "source": "The Times, December 12, 1936"
        }
    ],

    # 1937
    "1937-04-26": [
        {
            "event": "Guernica bombed",
            "category": "world",
            "topic": "war",
            "location": "Guernica, Spain",
            "description": "German Luftwaffe bombs Guernica, killing hundreds of civilians. Picasso's famous painting immortalizes the atrocity.",
            "source": "The Times, April 28, 1937"
        }
    ],
    "1937-05-06": [
        {
            "event": "Hindenburg disaster",
            "category": "world",
            "topic": "science",
            "location": "Lakehurst, New Jersey",
            "description": "The German airship Hindenburg catches fire while landing, killing 36. The disaster ends the era of passenger airships.",
            "source": "The New York Times, May 7, 1937"
        }
    ],
    "1937-07-07": [
        {
            "event": "Second Sino-Japanese War begins",
            "category": "world",
            "topic": "war",
            "location": "Marco Polo Bridge, China",
            "description": "A skirmish at the Marco Polo Bridge near Beijing escalates into full-scale war between Japan and China.",
            "source": "The Times, July 9, 1937"
        }
    ],
    "1937-12-12": [
        {
            "event": "USS Panay incident",
            "category": "usa",
            "topic": "war",
            "location": "Yangtze River, China",
            "description": "Japanese aircraft sink the USS Panay on the Yangtze River, killing three Americans. Japan apologizes and pays indemnity.",
            "source": "The New York Times, December 13, 1937"
        }
    ],

    # 1938
    "1938-03-12": [
        {
            "event": "Anschluss: Germany annexes Austria",
            "category": "world",
            "topic": "war",
            "location": "Austria",
            "description": "German troops march into Austria unopposed. Hitler announces the union of Austria and Germany before cheering crowds.",
            "source": "The Times, March 14, 1938"
        }
    ],
    "1938-09-30": [
        {
            "event": "Munich Agreement signed",
            "category": "world",
            "topic": "politics",
            "location": "Munich, Germany",
            "description": "Britain, France, Italy, and Germany agree to German annexation of Czechoslovakia's Sudetenland. Chamberlain declares 'peace for our time.'",
            "source": "The Times, October 1, 1938"
        }
    ],
    "1938-10-30": [
        {
            "event": "War of the Worlds broadcast",
            "category": "usa",
            "topic": "culture",
            "location": "New York City",
            "description": "Orson Welles' CBS radio adaptation of H.G. Wells' novel causes widespread panic as listeners believe Martians are invading.",
            "source": "The New York Times, October 31, 1938"
        }
    ],
    "1938-11-09": [
        {
            "event": "Kristallnacht",
            "category": "world",
            "topic": "politics",
            "location": "Germany and Austria",
            "description": "Nazi mobs attack Jewish homes, businesses, and synagogues across Germany and Austria. 91 killed, 30,000 sent to camps.",
            "source": "The Manchester Guardian, November 11, 1938"
        }
    ],

    # 1939
    "1939-04-30": [
        {
            "event": "New York World's Fair opens",
            "category": "usa",
            "topic": "culture",
            "location": "Flushing Meadows, New York",
            "description": "The 'World of Tomorrow' fair opens with exhibits on technology and democracy. First public demonstration of television.",
            "source": "The New York Times, May 1, 1939"
        }
    ],
    "1939-08-23": [
        {
            "event": "Nazi-Soviet Pact signed",
            "category": "world",
            "topic": "politics",
            "location": "Moscow, USSR",
            "description": "Germany and the Soviet Union sign a non-aggression pact with secret protocols dividing Eastern Europe between them.",
            "source": "The Times, August 24, 1939"
        }
    ],
    "1939-09-01": [
        {
            "event": "Germany invades Poland",
            "category": "world",
            "topic": "war",
            "location": "Poland",
            "description": "1.5 million German troops invade Poland without declaration of war. World War II begins in Europe.",
            "source": "The Times, September 2, 1939"
        }
    ],
    "1939-09-03": [
        {
            "event": "Britain and France declare war on Germany",
            "category": "world",
            "topic": "war",
            "location": "London/Paris",
            "description": "After Germany ignores ultimatum to withdraw from Poland, Britain and France declare war. The Second World War is underway.",
            "source": "The Times, September 4, 1939"
        }
    ],

    # 1940
    "1940-04-09": [
        {
            "event": "Germany invades Denmark and Norway",
            "category": "world",
            "topic": "war",
            "location": "Scandinavia",
            "description": "Germany launches surprise invasions of Denmark (conquered in hours) and Norway (conquered in two months).",
            "source": "The Times, April 10, 1940"
        }
    ],
    "1940-05-10": [
        {
            "event": "Germany invades Western Europe; Churchill becomes PM",
            "category": "world",
            "topic": "war",
            "location": "Western Europe",
            "description": "Germany attacks the Netherlands, Belgium, Luxembourg, and France. Winston Churchill replaces Chamberlain as Prime Minister.",
            "source": "The Times, May 11, 1940"
        }
    ],
    "1940-05-26": [
        {
            "event": "Dunkirk evacuation begins",
            "category": "world",
            "topic": "war",
            "location": "Dunkirk, France",
            "description": "Operation Dynamo begins. Over 9 days, 338,000 Allied soldiers are evacuated from France by military and civilian vessels.",
            "source": "The Times, June 5, 1940"
        }
    ],
    "1940-06-22": [
        {
            "event": "France surrenders to Germany",
            "category": "world",
            "topic": "war",
            "location": "Compiègne, France",
            "description": "France signs armistice with Germany in the same railway car where Germany surrendered in 1918. Vichy France established.",
            "source": "The Times, June 24, 1940"
        }
    ],
    "1940-07-10": [
        {
            "event": "Battle of Britain begins",
            "category": "world",
            "topic": "war",
            "location": "United Kingdom",
            "description": "The Luftwaffe begins sustained bombing campaign against Britain. RAF pilots defend against invasion attempt.",
            "source": "The Times, July 11, 1940"
        }
    ],
    "1940-09-16": [
        {
            "event": "Selective Training and Service Act signed",
            "category": "usa",
            "topic": "war",
            "location": "Washington, D.C.",
            "description": "FDR signs the first peacetime draft in U.S. history. 16 million men register; 10 million will eventually serve.",
            "source": "Public Law 76-783, September 16, 1940"
        }
    ],
    "1940-11-05": [
        {
            "event": "FDR wins unprecedented third term",
            "category": "usa",
            "topic": "politics",
            "location": "United States",
            "description": "Roosevelt defeats Wendell Willkie, becoming the only president to win a third term. Electoral vote: 449-82.",
            "source": "The New York Times, November 6, 1940"
        }
    ],

    # 1941
    "1941-03-11": [
        {
            "event": "Lend-Lease Act signed",
            "category": "usa",
            "topic": "war",
            "location": "Washington, D.C.",
            "description": "FDR signs the Lend-Lease Act, allowing U.S. to supply weapons to Britain and other Allies. Ends American neutrality.",
            "source": "Public Law 77-11, March 11, 1941"
        }
    ],
    "1941-06-22": [
        {
            "event": "Germany invades Soviet Union",
            "category": "world",
            "topic": "war",
            "location": "USSR",
            "description": "Operation Barbarossa begins. 3 million German troops attack the Soviet Union in the largest military operation in history.",
            "source": "The Times, June 23, 1941"
        }
    ],
    "1941-08-14": [
        {
            "event": "Atlantic Charter announced",
            "category": "world",
            "topic": "politics",
            "location": "Atlantic Ocean",
            "description": "FDR and Churchill issue joint declaration of war aims aboard ships off Newfoundland. Basis for the United Nations.",
            "source": "The New York Times, August 15, 1941"
        }
    ],
    "1941-12-07": [
        {
            "event": "Japan attacks Pearl Harbor",
            "category": "usa",
            "topic": "war",
            "location": "Pearl Harbor, Hawaii",
            "description": "Japanese aircraft attack the U.S. Pacific Fleet at Pearl Harbor. 2,403 Americans killed, 8 battleships damaged or sunk.",
            "source": "The New York Times, December 8, 1941"
        }
    ],
    "1941-12-08": [
        {
            "event": "United States declares war on Japan",
            "category": "usa",
            "topic": "war",
            "location": "Washington, D.C.",
            "description": "FDR addresses Congress: 'a date which will live in infamy.' War declared with only one dissenting vote (Jeannette Rankin).",
            "source": "Congressional Record, December 8, 1941"
        }
    ],
    "1941-12-11": [
        {
            "event": "Germany and Italy declare war on US",
            "category": "world",
            "topic": "war",
            "location": "Berlin/Rome",
            "description": "Germany and Italy declare war on the United States. America is now fully engaged in both theaters of World War II.",
            "source": "The Times, December 12, 1941"
        }
    ],

    # 1942
    "1942-02-19": [
        {
            "event": "Executive Order 9066: Japanese American internment",
            "category": "usa",
            "topic": "politics",
            "location": "United States",
            "description": "FDR authorizes the internment of Japanese Americans. 120,000 people, most U.S. citizens, forced into camps.",
            "source": "Executive Order 9066, February 19, 1942"
        }
    ],
    "1942-06-04": [
        {
            "event": "Battle of Midway",
            "category": "world",
            "topic": "war",
            "location": "Midway Atoll, Pacific",
            "description": "U.S. Navy defeats Japanese fleet, sinking 4 aircraft carriers. Turning point of the Pacific War.",
            "source": "The New York Times, June 7, 1942"
        }
    ],
    "1942-08-07": [
        {
            "event": "Guadalcanal Campaign begins",
            "category": "world",
            "topic": "war",
            "location": "Solomon Islands",
            "description": "U.S. Marines land on Guadalcanal in the first major Allied offensive in the Pacific. Six-month battle follows.",
            "source": "The New York Times, August 8, 1942"
        }
    ],
    "1942-11-08": [
        {
            "event": "Operation Torch: Allied invasion of North Africa",
            "category": "world",
            "topic": "war",
            "location": "Morocco and Algeria",
            "description": "Anglo-American forces land in French North Africa. First major U.S. ground operation against Axis forces.",
            "source": "The Times, November 9, 1942"
        }
    ],

    # 1943
    "1943-02-02": [
        {
            "event": "German surrender at Stalingrad",
            "category": "world",
            "topic": "war",
            "location": "Stalingrad, USSR",
            "description": "German 6th Army surrenders after months of brutal urban combat. 91,000 captured. Major turning point on Eastern Front.",
            "source": "The Times, February 3, 1943"
        }
    ],
    "1943-07-10": [
        {
            "event": "Allied invasion of Sicily",
            "category": "world",
            "topic": "war",
            "location": "Sicily, Italy",
            "description": "Operation Husky begins. 160,000 Allied troops land in Sicily. Mussolini falls from power two weeks later.",
            "source": "The Times, July 12, 1943"
        }
    ],
    "1943-09-08": [
        {
            "event": "Italy surrenders",
            "category": "world",
            "topic": "war",
            "location": "Italy",
            "description": "Italy signs armistice with Allies. Germany immediately occupies much of Italy. Long Italian campaign begins.",
            "source": "The Times, September 9, 1943"
        }
    ],
    "1943-11-28": [
        {
            "event": "Tehran Conference begins",
            "category": "world",
            "topic": "politics",
            "location": "Tehran, Iran",
            "description": "FDR, Churchill, and Stalin meet for the first time. They agree on D-Day invasion and Soviet entry into Pacific war.",
            "source": "The Times, December 7, 1943"
        }
    ],

    # 1944
    "1944-06-06": [
        {
            "event": "D-Day: Allied invasion of Normandy",
            "category": "world",
            "topic": "war",
            "location": "Normandy, France",
            "description": "Operation Overlord begins. 156,000 Allied troops land on five beaches in the largest amphibious invasion in history.",
            "source": "The Times, June 7, 1944"
        }
    ],
    "1944-06-22": [
        {
            "event": "GI Bill signed",
            "category": "usa",
            "topic": "politics",
            "location": "Washington, D.C.",
            "description": "FDR signs the Servicemen's Readjustment Act, providing education, housing, and employment benefits to veterans.",
            "source": "Public Law 78-346, June 22, 1944"
        }
    ],
    "1944-07-20": [
        {
            "event": "Failed assassination attempt on Hitler",
            "category": "world",
            "topic": "war",
            "location": "Rastenburg, East Prussia",
            "description": "Colonel Claus von Stauffenberg's bomb fails to kill Hitler. Thousands executed in reprisals against conspirators.",
            "source": "The Times, July 22, 1944"
        }
    ],
    "1944-08-25": [
        {
            "event": "Liberation of Paris",
            "category": "world",
            "topic": "war",
            "location": "Paris, France",
            "description": "French and American forces liberate Paris after four years of German occupation. De Gaulle leads victory parade.",
            "source": "The Times, August 26, 1944"
        }
    ],
    "1944-11-07": [
        {
            "event": "FDR wins fourth term",
            "category": "usa",
            "topic": "politics",
            "location": "United States",
            "description": "Roosevelt defeats Thomas Dewey, becoming the only president elected four times. Electoral vote: 432-99.",
            "source": "The New York Times, November 8, 1944"
        }
    ],
    "1944-12-16": [
        {
            "event": "Battle of the Bulge begins",
            "category": "world",
            "topic": "war",
            "location": "Ardennes, Belgium",
            "description": "Germany launches last major offensive in the West. 200,000 German troops attack through the Ardennes. Defeated by January.",
            "source": "The Times, December 18, 1944"
        }
    ],

    # 1945
    "1945-02-04": [
        {
            "event": "Yalta Conference begins",
            "category": "world",
            "topic": "politics",
            "location": "Yalta, Crimea",
            "description": "FDR, Churchill, and Stalin meet to plan post-war Europe. Agreements on UN, division of Germany, and Soviet sphere.",
            "source": "The Times, February 13, 1945"
        }
    ],
    "1945-02-19": [
        {
            "event": "Battle of Iwo Jima begins",
            "category": "world",
            "topic": "war",
            "location": "Iwo Jima, Japan",
            "description": "U.S. Marines invade Iwo Jima. 36-day battle for strategic airfields. Iconic flag-raising on Mount Suribachi.",
            "source": "The New York Times, February 20, 1945"
        }
    ],
    "1945-04-12": [
        {
            "event": "President Roosevelt dies",
            "category": "usa",
            "topic": "politics",
            "location": "Warm Springs, Georgia",
            "description": "FDR dies of cerebral hemorrhage after 12 years as president. Harry Truman sworn in as 33rd President.",
            "source": "The New York Times, April 13, 1945"
        }
    ],
    "1945-04-25": [
        {
            "event": "United Nations founding conference opens",
            "category": "world",
            "topic": "politics",
            "location": "San Francisco, California",
            "description": "Delegates from 50 nations meet to draft the UN Charter. Organization formally established October 24, 1945.",
            "source": "The New York Times, April 26, 1945"
        }
    ],
    "1945-04-30": [
        {
            "event": "Hitler commits suicide",
            "category": "world",
            "topic": "war",
            "location": "Berlin, Germany",
            "description": "Adolf Hitler kills himself in his bunker as Soviet forces close in on Berlin. Eva Braun dies with him.",
            "source": "The Times, May 2, 1945"
        }
    ],
    "1945-05-08": [
        {
            "event": "V-E Day: Germany surrenders",
            "category": "world",
            "topic": "war",
            "location": "Berlin, Germany",
            "description": "Germany signs unconditional surrender. Victory in Europe Day celebrated across Allied nations. War in Europe ends.",
            "source": "The Times, May 9, 1945"
        }
    ],
    "1945-07-16": [
        {
            "event": "First atomic bomb tested",
            "category": "usa",
            "topic": "science",
            "location": "Alamogordo, New Mexico",
            "description": "The Trinity test successfully detonates the first nuclear weapon. J. Robert Oppenheimer recalls Hindu scripture: 'I am become Death.'",
            "source": "Manhattan Engineer District Records"
        }
    ],
    "1945-08-06": [
        {
            "event": "Atomic bomb dropped on Hiroshima",
            "category": "world",
            "topic": "war",
            "location": "Hiroshima, Japan",
            "description": "B-29 'Enola Gay' drops uranium bomb on Hiroshima. 80,000 killed instantly; total deaths reach 140,000 by year's end.",
            "source": "The New York Times, August 7, 1945"
        }
    ],
    "1945-08-09": [
        {
            "event": "Atomic bomb dropped on Nagasaki",
            "category": "world",
            "topic": "war",
            "location": "Nagasaki, Japan",
            "description": "Second atomic bomb destroys Nagasaki. 40,000 killed instantly. Japan begins surrender negotiations.",
            "source": "The New York Times, August 10, 1945"
        }
    ],
    "1945-08-15": [
        {
            "event": "V-J Day: Japan surrenders",
            "category": "world",
            "topic": "war",
            "location": "Tokyo, Japan",
            "description": "Emperor Hirohito announces Japan's surrender in radio broadcast. World War II ends after six years.",
            "source": "The Times, August 16, 1945"
        }
    ],
    "1945-11-20": [
        {
            "event": "Nuremberg Trials begin",
            "category": "world",
            "topic": "politics",
            "location": "Nuremberg, Germany",
            "description": "International Military Tribunal begins trying 24 major Nazi war criminals. Establishes precedents for international law.",
            "source": "The Times, November 21, 1945"
        }
    ],

    # 1946
    "1946-02-24": [
        {
            "event": "Perón elected President of Argentina",
            "category": "world",
            "topic": "politics",
            "location": "Argentina",
            "description": "Juan Perón wins presidential election with 56% of vote. Begins era of Peronism in Argentine politics.",
            "source": "The Times, February 26, 1946"
        }
    ],
    "1946-03-05": [
        {
            "event": "Churchill's 'Iron Curtain' speech",
            "category": "world",
            "topic": "politics",
            "location": "Fulton, Missouri",
            "description": "Churchill warns that 'an iron curtain has descended across the Continent.' Speech marks start of Cold War rhetoric.",
            "source": "The New York Times, March 6, 1946"
        }
    ],
    "1946-07-01": [
        {
            "event": "Bikini Atoll atomic tests begin",
            "category": "usa",
            "topic": "science",
            "location": "Bikini Atoll, Marshall Islands",
            "description": "Operation Crossroads tests atomic bombs on naval vessels. Residents of Bikini permanently displaced.",
            "source": "The New York Times, July 2, 1946"
        }
    ],

    # 1947
    "1947-03-12": [
        {
            "event": "Truman Doctrine announced",
            "category": "usa",
            "topic": "politics",
            "location": "Washington, D.C.",
            "description": "Truman pledges U.S. support for countries resisting communism. Requests $400 million for Greece and Turkey.",
            "source": "The New York Times, March 13, 1947"
        }
    ],
    "1947-04-15": [
        {
            "event": "Jackie Robinson breaks baseball color barrier",
            "category": "usa",
            "topic": "sports",
            "location": "Brooklyn, New York",
            "description": "Jackie Robinson debuts for Brooklyn Dodgers, becoming first Black player in Major League Baseball since 1880s.",
            "source": "The New York Times, April 16, 1947"
        }
    ],
    "1947-06-05": [
        {
            "event": "Marshall Plan announced",
            "category": "usa",
            "topic": "economy",
            "location": "Cambridge, Massachusetts",
            "description": "Secretary of State George Marshall proposes massive aid program for European recovery. $13 billion provided 1948-1952.",
            "source": "The New York Times, June 6, 1947"
        }
    ],
    "1947-08-15": [
        {
            "event": "India and Pakistan gain independence",
            "category": "world",
            "topic": "politics",
            "location": "South Asia",
            "description": "British rule ends in India. Partition creates Muslim Pakistan and Hindu-majority India. Massive population transfers and violence.",
            "source": "The Times, August 16, 1947"
        }
    ],
    "1947-10-14": [
        {
            "event": "Chuck Yeager breaks sound barrier",
            "category": "usa",
            "topic": "science",
            "location": "Muroc, California",
            "description": "Captain Chuck Yeager flies Bell X-1 rocket plane faster than sound over Mojave Desert. Mach 1.06 achieved.",
            "source": "The New York Times (delayed release)"
        }
    ],
    "1947-11-29": [
        {
            "event": "UN votes to partition Palestine",
            "category": "world",
            "topic": "politics",
            "location": "New York City",
            "description": "UN General Assembly votes 33-13 to partition Palestine into Jewish and Arab states. Arabs reject the plan.",
            "source": "The New York Times, November 30, 1947"
        }
    ],

    # 1948
    "1948-02-25": [
        {
            "event": "Communist coup in Czechoslovakia",
            "category": "world",
            "topic": "politics",
            "location": "Prague, Czechoslovakia",
            "description": "Communists seize power in Czechoslovakia with Soviet backing. Last democracy in Eastern Europe falls.",
            "source": "The Times, February 26, 1948"
        }
    ],
    "1948-04-03": [
        {
            "event": "Marshall Plan enacted",
            "category": "usa",
            "topic": "economy",
            "location": "Washington, D.C.",
            "description": "Truman signs the Economic Cooperation Act. European Recovery Program begins distributing billions in aid.",
            "source": "Public Law 80-472, April 3, 1948"
        }
    ],
    "1948-05-14": [
        {
            "event": "State of Israel proclaimed",
            "category": "world",
            "topic": "politics",
            "location": "Tel Aviv, Israel",
            "description": "David Ben-Gurion declares Israeli independence. U.S. recognizes Israel within minutes. Arab-Israeli War begins.",
            "source": "The Times, May 15, 1948"
        }
    ],
    "1948-06-24": [
        {
            "event": "Berlin Blockade begins",
            "category": "world",
            "topic": "war",
            "location": "Berlin, Germany",
            "description": "Soviets block all ground access to West Berlin. Western Allies begin Berlin Airlift to supply 2.5 million residents.",
            "source": "The Times, June 25, 1948"
        }
    ],
    "1948-11-02": [
        {
            "event": "Truman wins upset election",
            "category": "usa",
            "topic": "politics",
            "location": "United States",
            "description": "Truman defeats Dewey despite polls and predictions. Chicago Tribune prints infamous 'Dewey Defeats Truman' headline.",
            "source": "The New York Times, November 3, 1948"
        }
    ],
    "1948-12-10": [
        {
            "event": "Universal Declaration of Human Rights adopted",
            "category": "world",
            "topic": "politics",
            "location": "Paris, France",
            "description": "UN General Assembly adopts declaration drafted by committee chaired by Eleanor Roosevelt. Sets global human rights standard.",
            "source": "UN Archives, December 10, 1948"
        }
    ],

    # 1949
    "1949-04-04": [
        {
            "event": "NATO founded",
            "category": "world",
            "topic": "politics",
            "location": "Washington, D.C.",
            "description": "Twelve nations sign North Atlantic Treaty. Collective defense alliance against Soviet threat established.",
            "source": "The New York Times, April 5, 1949"
        }
    ],
    "1949-05-12": [
        {
            "event": "Berlin Blockade ends",
            "category": "world",
            "topic": "politics",
            "location": "Berlin, Germany",
            "description": "Soviets lift Berlin blockade after 318 days. Western Allies flew 277,000 flights delivering 2.3 million tons of supplies.",
            "source": "The Times, May 13, 1949"
        }
    ],
    "1949-08-29": [
        {
            "event": "Soviet Union tests first atomic bomb",
            "category": "world",
            "topic": "science",
            "location": "Kazakhstan, USSR",
            "description": "USSR detonates first nuclear weapon, ending American atomic monopoly. Nuclear arms race begins.",
            "source": "The New York Times, September 23, 1949"
        }
    ],
    "1949-10-01": [
        {
            "event": "People's Republic of China proclaimed",
            "category": "world",
            "topic": "politics",
            "location": "Beijing, China",
            "description": "Mao Zedong proclaims Communist victory. Nationalists flee to Taiwan. 'China has stood up.'",
            "source": "The Times, October 3, 1949"
        }
    ],

    # 1950
    "1950-02-09": [
        {
            "event": "McCarthy's Wheeling speech",
            "category": "usa",
            "topic": "politics",
            "location": "Wheeling, West Virginia",
            "description": "Senator Joseph McCarthy claims to have list of Communists in State Department. McCarthyism era begins.",
            "source": "The New York Times, February 10, 1950"
        }
    ],
    "1950-06-25": [
        {
            "event": "Korean War begins",
            "category": "world",
            "topic": "war",
            "location": "Korea",
            "description": "North Korean forces invade South Korea. UN (led by U.S.) intervenes. Cold War turns hot in Asia.",
            "source": "The New York Times, June 26, 1950"
        }
    ],
    "1950-09-15": [
        {
            "event": "Inchon landing",
            "category": "world",
            "topic": "war",
            "location": "Inchon, Korea",
            "description": "MacArthur's amphibious assault at Inchon cuts North Korean supply lines. UN forces push north to Chinese border.",
            "source": "The New York Times, September 16, 1950"
        }
    ],
    "1950-11-26": [
        {
            "event": "Chinese forces enter Korean War",
            "category": "world",
            "topic": "war",
            "location": "North Korea",
            "description": "300,000 Chinese 'volunteers' attack UN forces near Yalu River. Longest retreat in U.S. military history follows.",
            "source": "The New York Times, November 28, 1950"
        }
    ],

    # 1951
    "1951-04-11": [
        {
            "event": "Truman fires MacArthur",
            "category": "usa",
            "topic": "politics",
            "location": "Washington, D.C.",
            "description": "Truman relieves General MacArthur of command for insubordination. Constitutional crisis over civilian control of military.",
            "source": "The New York Times, April 12, 1951"
        }
    ],
    "1951-09-08": [
        {
            "event": "San Francisco Peace Treaty signed",
            "category": "world",
            "topic": "politics",
            "location": "San Francisco, California",
            "description": "Japan signs peace treaty with 48 nations, ending World War II occupation. Japan regains sovereignty in 1952.",
            "source": "The New York Times, September 9, 1951"
        }
    ],

    # 1952
    "1952-02-06": [
        {
            "event": "Elizabeth II becomes Queen",
            "category": "world",
            "topic": "politics",
            "location": "Kenya/London",
            "description": "George VI dies. Princess Elizabeth, in Kenya, becomes Queen Elizabeth II at age 25.",
            "source": "The Times, February 7, 1952"
        }
    ],
    "1952-11-01": [
        {
            "event": "First hydrogen bomb tested",
            "category": "usa",
            "topic": "science",
            "location": "Enewetak Atoll, Pacific",
            "description": "U.S. detonates 'Mike,' first thermonuclear device. 10.4 megatons - 500 times Hiroshima. Island of Elugelab vaporized.",
            "source": "The New York Times (delayed release)"
        }
    ],
    "1952-11-04": [
        {
            "event": "Eisenhower elected President",
            "category": "usa",
            "topic": "politics",
            "location": "United States",
            "description": "Dwight D. Eisenhower defeats Adlai Stevenson. First Republican president in 20 years. Electoral vote: 442-89.",
            "source": "The New York Times, November 5, 1952"
        }
    ],

    # 1953
    "1953-03-05": [
        {
            "event": "Stalin dies",
            "category": "world",
            "topic": "politics",
            "location": "Moscow, USSR",
            "description": "Joseph Stalin dies after 29 years ruling the Soviet Union. Power struggle follows. Khrushchev eventually emerges as leader.",
            "source": "The Times, March 6, 1953"
        }
    ],
    "1953-06-02": [
        {
            "event": "Coronation of Elizabeth II",
            "category": "world",
            "topic": "politics",
            "location": "London, England",
            "description": "Queen Elizabeth II crowned at Westminster Abbey. First televised coronation watched by 27 million in Britain.",
            "source": "The Times, June 3, 1953"
        }
    ],
    "1953-06-19": [
        {
            "event": "Rosenbergs executed",
            "category": "usa",
            "topic": "politics",
            "location": "Ossining, New York",
            "description": "Julius and Ethel Rosenberg executed for atomic espionage. Only American civilians executed for espionage during Cold War.",
            "source": "The New York Times, June 20, 1953"
        }
    ],
    "1953-07-27": [
        {
            "event": "Korean War armistice signed",
            "category": "world",
            "topic": "war",
            "location": "Panmunjom, Korea",
            "description": "Armistice ends three years of fighting. Korea remains divided at 38th parallel. 36,000 Americans died; millions of Koreans.",
            "source": "The New York Times, July 28, 1953"
        }
    ],
    "1953-08-19": [
        {
            "event": "CIA coup in Iran",
            "category": "world",
            "topic": "politics",
            "location": "Tehran, Iran",
            "description": "CIA-backed coup overthrows Prime Minister Mosaddegh. Shah restored to power. Consequences reverberate for decades.",
            "source": "The Times, August 20, 1953"
        }
    ],

    # 1954
    "1954-04-22": [
        {
            "event": "Army-McCarthy hearings begin",
            "category": "usa",
            "topic": "politics",
            "location": "Washington, D.C.",
            "description": "Televised hearings expose McCarthy's tactics to millions. 'Have you no sense of decency?' asks Joseph Welch.",
            "source": "The New York Times, April 23, 1954"
        }
    ],
    "1954-05-07": [
        {
            "event": "French defeat at Dien Bien Phu",
            "category": "world",
            "topic": "war",
            "location": "Dien Bien Phu, Vietnam",
            "description": "Viet Minh forces overwhelm French garrison after 57-day siege. French colonial rule in Indochina ends.",
            "source": "The Times, May 8, 1954"
        }
    ],
    "1954-05-17": [
        {
            "event": "Brown v. Board of Education decision",
            "category": "usa",
            "topic": "politics",
            "location": "Washington, D.C.",
            "description": "Supreme Court unanimously rules school segregation unconstitutional. 'Separate educational facilities are inherently unequal.'",
            "source": "The New York Times, May 18, 1954"
        }
    ],
    "1954-07-21": [
        {
            "event": "Geneva Accords divide Vietnam",
            "category": "world",
            "topic": "politics",
            "location": "Geneva, Switzerland",
            "description": "Conference divides Vietnam at 17th parallel pending elections. U.S. does not sign. Seeds of future war planted.",
            "source": "The Times, July 22, 1954"
        }
    ],
    "1954-12-02": [
        {
            "event": "Senate censures McCarthy",
            "category": "usa",
            "topic": "politics",
            "location": "Washington, D.C.",
            "description": "Senate votes 67-22 to condemn Senator McCarthy. His influence collapses. Dies in 1957 of alcoholism-related illness.",
            "source": "The New York Times, December 3, 1954"
        }
    ],

    # 1955
    "1955-04-18": [
        {
            "event": "Einstein dies",
            "category": "world",
            "topic": "science",
            "location": "Princeton, New Jersey",
            "description": "Albert Einstein dies at 76. Greatest physicist since Newton. His brain preserved for study.",
            "source": "The New York Times, April 19, 1955"
        }
    ],
    "1955-05-14": [
        {
            "event": "Warsaw Pact signed",
            "category": "world",
            "topic": "politics",
            "location": "Warsaw, Poland",
            "description": "Soviet Union and seven Eastern European nations sign military alliance in response to NATO.",
            "source": "The Times, May 16, 1955"
        }
    ],
    "1955-07-17": [
        {
            "event": "Disneyland opens",
            "category": "usa",
            "topic": "culture",
            "location": "Anaheim, California",
            "description": "Walt Disney's theme park opens in Anaheim. Revolutionary entertainment concept attracts millions annually.",
            "source": "The Los Angeles Times, July 18, 1955"
        }
    ],
    "1955-12-01": [
        {
            "event": "Rosa Parks arrested in Montgomery",
            "category": "usa",
            "topic": "politics",
            "location": "Montgomery, Alabama",
            "description": "Rosa Parks refuses to give up bus seat to white passenger. Arrest sparks Montgomery Bus Boycott led by Martin Luther King Jr.",
            "source": "The New York Times, December 6, 1955"
        }
    ],

    # 1956
    "1956-02-25": [
        {
            "event": "Khrushchev's 'Secret Speech'",
            "category": "world",
            "topic": "politics",
            "location": "Moscow, USSR",
            "description": "Khrushchev denounces Stalin's crimes at 20th Party Congress. De-Stalinization begins. Text leaks to West.",
            "source": "The New York Times, June 1956"
        }
    ],
    "1956-06-29": [
        {
            "event": "Interstate Highway Act signed",
            "category": "usa",
            "topic": "economy",
            "location": "Washington, D.C.",
            "description": "Eisenhower signs Federal Aid Highway Act. 41,000-mile Interstate system transforms American transportation and geography.",
            "source": "Public Law 84-627, June 29, 1956"
        }
    ],
    "1956-10-23": [
        {
            "event": "Hungarian Revolution begins",
            "category": "world",
            "topic": "politics",
            "location": "Budapest, Hungary",
            "description": "Hungarians revolt against Soviet-imposed government. Initial success. Soviet tanks crush uprising November 4.",
            "source": "The Times, October 24, 1956"
        }
    ],
    "1956-10-29": [
        {
            "event": "Suez Crisis begins",
            "category": "world",
            "topic": "war",
            "location": "Egypt",
            "description": "Israel invades Sinai; Britain and France bomb Egypt after Nasser nationalizes canal. U.S. pressure forces withdrawal.",
            "source": "The Times, October 30, 1956"
        }
    ],
    "1956-11-06": [
        {
            "event": "Eisenhower re-elected",
            "category": "usa",
            "topic": "politics",
            "location": "United States",
            "description": "Eisenhower defeats Stevenson again despite heart attack and Suez/Hungary crises. Electoral vote: 457-73.",
            "source": "The New York Times, November 7, 1956"
        }
    ],

    # 1957
    "1957-01-10": [
        {
            "event": "Eisenhower Doctrine announced",
            "category": "usa",
            "topic": "politics",
            "location": "Washington, D.C.",
            "description": "Eisenhower pledges U.S. military and economic aid to Middle Eastern countries resisting Communist aggression.",
            "source": "The New York Times, January 11, 1957"
        }
    ],
    "1957-03-25": [
        {
            "event": "Treaty of Rome signed",
            "category": "world",
            "topic": "economy",
            "location": "Rome, Italy",
            "description": "Six nations sign treaties establishing European Economic Community. Foundation of European Union.",
            "source": "The Times, March 26, 1957"
        }
    ],
    "1957-09-04": [
        {
            "event": "Little Rock school integration crisis",
            "category": "usa",
            "topic": "politics",
            "location": "Little Rock, Arkansas",
            "description": "Governor Faubus uses National Guard to block Black students from Central High. Eisenhower sends federal troops.",
            "source": "The New York Times, September 5, 1957"
        }
    ],
    "1957-10-04": [
        {
            "event": "Sputnik launched",
            "category": "world",
            "topic": "science",
            "location": "Baikonur, Kazakhstan",
            "description": "Soviet Union launches first artificial satellite. 'Sputnik crisis' triggers space race. Americans shocked.",
            "source": "The New York Times, October 5, 1957"
        }
    ],
}


def main():
    print("=" * 70)
    print("ENRICHING WORLD EVENTS DATA")
    print("=" * 70)

    # Load archive
    print("\nLoading archive...")
    with open(ARCHIVE_FILE, 'r', encoding='utf-8') as f:
        archive = json.load(f)

    if 'daily_calendar' not in archive:
        archive['daily_calendar'] = {}

    # Add enriched events
    added = 0
    updated = 0

    print("\nAdding historical events...")
    for date_key, events in HISTORICAL_EVENTS.items():
        year = date_key[:4]

        # Ensure year structure exists
        if year not in archive['daily_calendar']:
            archive['daily_calendar'][year] = {}

        if date_key not in archive['daily_calendar'][year]:
            archive['daily_calendar'][year][date_key] = {
                'bmc_events': [],
                'world_events': []
            }

        # Ensure world_events exists
        if 'world_events' not in archive['daily_calendar'][year][date_key]:
            archive['daily_calendar'][year][date_key]['world_events'] = []

        # Check if event already exists (by event title)
        existing_titles = {e.get('event', '').lower() for e in archive['daily_calendar'][year][date_key]['world_events']}

        for event in events:
            if event['event'].lower() not in existing_titles:
                archive['daily_calendar'][year][date_key]['world_events'].append(event)
                added += 1
            else:
                # Update existing event with more details
                for existing in archive['daily_calendar'][year][date_key]['world_events']:
                    if existing.get('event', '').lower() == event['event'].lower():
                        existing.update(event)
                        updated += 1
                        break

    print(f"  Events added: {added}")
    print(f"  Events updated: {updated}")

    # Update metadata
    archive['metadata'] = archive.get('metadata', {})
    archive['metadata']['world_events_enriched'] = {
        'enriched_at': datetime.now().isoformat(),
        'events_added': added,
        'events_updated': updated,
        'coverage': '1933-1957'
    }

    # Save updated archive
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(archive, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Archive updated: {OUTPUT_FILE}")

    # Statistics
    total_world = 0
    total_usa = 0
    by_year = {}

    for year, dates in archive.get('daily_calendar', {}).items():
        for date_key, day_data in dates.items():
            for event in day_data.get('world_events', []):
                if event.get('category') == 'usa':
                    total_usa += 1
                else:
                    total_world += 1
                by_year[year] = by_year.get(year, 0) + 1

    print(f"\nTotal events: {total_usa + total_world}")
    print(f"  USA: {total_usa}")
    print(f"  International: {total_world}")


if __name__ == '__main__':
    main()
