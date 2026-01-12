#!/usr/bin/env python3
"""
Enrich all event files with comprehensive historical data 1933-1957
"""
import json

# CULTURE EVENTS - Films, Theater, Books, Art, Music
culture_events = {
    # 1933
    "1933-01-30": [{"type": "film", "title": "The Sign of the Cross", "creator": "Cecil B. DeMille", "description": "Epic religious film released widely."}],
    "1933-02-06": [{"type": "book", "title": "The 20th Amendment ratified", "creator": "US Congress", "description": "Changes presidential inauguration date."}],
    "1933-03-02": [{"type": "film", "title": "King Kong", "creator": "Merian C. Cooper", "description": "Revolutionary special effects. Fay Wray stars."}],
    "1933-03-31": [{"type": "film", "title": "42nd Street", "creator": "Lloyd Bacon", "description": "Busby Berkeley musical. Defines Depression-era escapism."}],
    "1933-05-27": [{"type": "art", "title": "Century of Progress opens", "creator": "Chicago World's Fair", "description": "Art Deco exposition showcases modernist design."}],
    "1933-11-17": [{"type": "film", "title": "Duck Soup", "creator": "Leo McCarey", "description": "Marx Brothers political satire. Later cult classic."}],

    # 1934
    "1934-02-22": [{"type": "film", "title": "It Happened One Night", "creator": "Frank Capra", "description": "Clark Gable, Claudette Colbert. Sweeps all 5 major Oscars."}],
    "1934-06-09": [{"type": "film", "title": "Donald Duck debut", "creator": "Walt Disney", "description": "The Wise Little Hen introduces Donald Duck."}],
    "1934-10-19": [{"type": "theater", "title": "Anything Goes opens", "creator": "Cole Porter", "description": "Ethel Merman stars. 'I Get a Kick Out of You.'"}],

    # 1935
    "1935-02-14": [{"type": "film", "title": "The Informer", "creator": "John Ford", "description": "Victor McLaglen wins Oscar. Irish rebellion drama."}],
    "1935-06-13": [{"type": "film", "title": "A Night at the Opera", "creator": "Sam Wood", "description": "Marx Brothers MGM debut. 'That's a-some sanity clause.'"}],
    "1935-08-14": [{"type": "concert", "title": "Benny Goodman Swing Era begins", "creator": "Benny Goodman", "description": "Palomar Ballroom concert ignites swing craze."}],
    "1935-10-10": [{"type": "theater", "title": "Porgy and Bess premieres", "creator": "George Gershwin", "description": "Folk opera at Alvin Theatre. 'Summertime' becomes standard."}],

    # 1936
    "1936-02-05": [{"type": "film", "title": "Modern Times", "creator": "Charlie Chaplin", "description": "Chaplin's last silent film. Critique of industrialization."}],
    "1936-03-02": [{"type": "art", "title": "Cubism and Abstract Art", "creator": "Alfred Barr, MoMA", "description": "Landmark exhibition defines modernist canon."}],
    "1936-06-17": [{"type": "film", "title": "The Great Ziegfeld", "creator": "Robert Z. Leonard", "description": "Best Picture Oscar. William Powell, Myrna Loy."}],
    "1936-11-14": [{"type": "concert", "title": "Prokofiev's Peter and the Wolf", "creator": "Sergei Prokofiev", "description": "Moscow premiere. Musical tale for children."}],

    # 1937
    "1937-05-06": [{"type": "concert", "title": "Hindenburg broadcast", "creator": "Herbert Morrison", "description": "'Oh, the humanity!' Radio covers disaster live."}],
    "1937-07-12": [{"type": "art", "title": "Guernica exhibited", "creator": "Pablo Picasso", "description": "Anti-war masterpiece at Paris World's Fair."}],
    "1937-12-21": [{"type": "film", "title": "Snow White and the Seven Dwarfs", "creator": "Walt Disney", "description": "First full-length animated feature. 'Heigh-Ho!'"}],

    # 1938
    "1938-01-16": [{"type": "concert", "title": "Benny Goodman at Carnegie Hall", "creator": "Benny Goodman", "description": "First jazz concert at Carnegie. Integrated performance."}],
    "1938-06-22": [{"type": "concert", "title": "Joe Louis defeats Schmeling", "creator": "Boxing", "description": "2:04 first round knockout. Symbol against Nazism."}],
    "1938-10-30": [{"type": "concert", "title": "War of the Worlds broadcast", "creator": "Orson Welles", "description": "CBS Mercury Theatre causes mass panic."}],

    # 1939
    "1939-02-27": [{"type": "film", "title": "Stagecoach", "creator": "John Ford", "description": "John Wayne breakthrough. Reinvents the Western."}],
    "1939-04-30": [{"type": "art", "title": "New York World's Fair opens", "creator": "NYC", "description": "'World of Tomorrow' introduces television to public."}],
    "1939-08-25": [{"type": "film", "title": "The Wizard of Oz", "creator": "Victor Fleming", "description": "Judy Garland. 'Somewhere Over the Rainbow.'"}],
    "1939-12-15": [{"type": "film", "title": "Gone with the Wind premiere", "creator": "Victor Fleming", "description": "Atlanta premiere. Vivien Leigh, Clark Gable. 10 Oscars."}],

    # 1940
    "1940-03-15": [{"type": "film", "title": "The Grapes of Wrath", "creator": "John Ford", "description": "Henry Fonda. Steinbeck adaptation. Social realism."}],
    "1940-10-18": [{"type": "film", "title": "The Great Dictator", "creator": "Charlie Chaplin", "description": "Chaplin satirizes Hitler. First talking picture."}],
    "1940-11-13": [{"type": "film", "title": "Fantasia", "creator": "Walt Disney", "description": "Classical music animation. Revolutionary Fantasound."}],

    # 1941
    "1941-05-01": [{"type": "film", "title": "Citizen Kane", "creator": "Orson Welles", "description": "RKO premiere. 'Rosebud.' Revolutionizes cinema."}],
    "1941-10-03": [{"type": "film", "title": "The Maltese Falcon", "creator": "John Huston", "description": "Humphrey Bogart as Sam Spade. Defines film noir."}],
    "1941-11-28": [{"type": "film", "title": "How Green Was My Valley", "creator": "John Ford", "description": "Best Picture over Citizen Kane. Welsh mining drama."}],

    # 1942
    "1942-05-26": [{"type": "film", "title": "Yankee Doodle Dandy", "creator": "Michael Curtiz", "description": "James Cagney as George M. Cohan. Wartime patriotism."}],
    "1942-11-26": [{"type": "film", "title": "Casablanca", "creator": "Michael Curtiz", "description": "Bogart, Bergman. 'Here's looking at you, kid.'"}],

    # 1943
    "1943-03-31": [{"type": "theater", "title": "Oklahoma! opens", "creator": "Rodgers & Hammerstein", "description": "St. James Theatre. Revolutionizes musical theater."}],
    "1943-07-15": [{"type": "film", "title": "The Ox-Bow Incident", "creator": "William Wellman", "description": "Henry Fonda. Anti-lynching Western."}],

    # 1944
    "1944-04-19": [{"type": "film", "title": "Lifeboat", "creator": "Alfred Hitchcock", "description": "Tallulah Bankhead. Single-set suspense."}],
    "1944-10-09": [{"type": "film", "title": "Double Indemnity", "creator": "Billy Wilder", "description": "Barbara Stanwyck. Quintessential film noir."}],
    "1944-12-28": [{"type": "theater", "title": "On the Town opens", "creator": "Bernstein, Comden & Green", "description": "Three sailors on leave in NYC."}],

    # 1945
    "1945-04-05": [{"type": "film", "title": "The House on 92nd Street", "creator": "Henry Hathaway", "description": "Semi-documentary spy film. FBI cooperation."}],
    "1945-09-06": [{"type": "film", "title": "Mildred Pierce", "creator": "Michael Curtiz", "description": "Joan Crawford comeback. Oscar winner."}],
    "1945-11-21": [{"type": "film", "title": "The Lost Weekend", "creator": "Billy Wilder", "description": "Ray Milland. Alcoholism drama. Best Picture."}],

    # 1946
    "1946-05-03": [{"type": "film", "title": "The Best Years of Our Lives", "creator": "William Wyler", "description": "Veterans returning home. 7 Oscars."}],
    "1946-09-20": [{"type": "art", "title": "First Cannes Film Festival", "creator": "France", "description": "Post-war revival of international cinema."}],
    "1946-12-20": [{"type": "film", "title": "It's a Wonderful Life", "creator": "Frank Capra", "description": "James Stewart. Christmas classic (initially flop)."}],

    # 1947
    "1947-10-20": [{"type": "film", "title": "HUAC Hollywood hearings begin", "creator": "US Congress", "description": "Blacklist era begins. Hollywood Ten cited."}],
    "1947-10-09": [{"type": "theater", "title": "A Streetcar Named Desire", "creator": "Tennessee Williams", "description": "Marlon Brando as Stanley. 'STELLA!'"}],

    # 1948
    "1948-01-14": [{"type": "film", "title": "The Treasure of the Sierra Madre", "creator": "John Huston", "description": "Bogart. 'Badges? We don't need no stinking badges.'"}],
    "1948-04-30": [{"type": "theater", "title": "Inside U.S.A.", "creator": "Arthur Schwartz", "description": "Revue at New Century Theatre. Beatrice Lillie."}],
    "1948-06-21": [{"type": "concert", "title": "LP records introduced", "creator": "Columbia Records", "description": "33 1/3 RPM unveiled at Waldorf Astoria."}],
    "1948-08-28": [{"type": "film", "title": "Hamlet", "creator": "Laurence Olivier", "description": "First British film to win Best Picture Oscar."}],
    "1948-12-02": [{"type": "film", "title": "The Red Shoes", "creator": "Powell & Pressburger", "description": "Ballet film. Technicolor masterpiece."}],

    # 1949
    "1949-02-10": [{"type": "theater", "title": "Death of a Salesman", "creator": "Arthur Miller", "description": "Lee J. Cobb as Willy Loman. Pulitzer Prize."}],
    "1949-04-07": [{"type": "theater", "title": "South Pacific", "creator": "Rodgers & Hammerstein", "description": "Majestic Theatre. 'You've Got to Be Carefully Taught.'"}],
    "1949-08-19": [{"type": "film", "title": "The Third Man", "creator": "Carol Reed", "description": "Orson Welles as Harry Lime. Vienna noir."}],

    # 1950
    "1950-01-21": [{"type": "film", "title": "The Asphalt Jungle", "creator": "John Huston", "description": "Heist film. Marilyn Monroe early role."}],
    "1950-08-25": [{"type": "film", "title": "All About Eve", "creator": "Joseph L. Mankiewicz", "description": "Bette Davis. 'Fasten your seatbelts.'"}],
    "1950-11-24": [{"type": "theater", "title": "Guys and Dolls", "creator": "Frank Loesser", "description": "46th Street Theatre. Damon Runyon characters."}],

    # 1951
    "1951-03-29": [{"type": "theater", "title": "The King and I", "creator": "Rodgers & Hammerstein", "description": "St. James Theatre. Yul Brynner breakthrough."}],
    "1951-07-16": [{"type": "book", "title": "The Catcher in the Rye", "creator": "J.D. Salinger", "description": "Holden Caulfield. Defines teenage alienation."}],
    "1951-10-04": [{"type": "film", "title": "An American in Paris", "creator": "Vincente Minnelli", "description": "Gene Kelly, Leslie Caron. Gershwin. Best Picture."}],
    "1951-10-15": [{"type": "concert", "title": "I Love Lucy premiere", "creator": "CBS", "description": "Lucille Ball. Revolutionizes TV sitcom."}],
    "1951-11-24": [{"type": "theater", "title": "Gigi", "creator": "Anita Loos", "description": "Audrey Hepburn Broadway debut. Fulton Theatre."}],
    "1951-12-04": [{"type": "film", "title": "A Streetcar Named Desire", "creator": "Elia Kazan", "description": "Brando, Vivien Leigh. 4 acting Oscar nominations."}],

    # 1952
    "1952-03-20": [{"type": "film", "title": "Singin' in the Rain", "creator": "Stanley Donen", "description": "Gene Kelly. Greatest movie musical."}],
    "1952-07-30": [{"type": "film", "title": "High Noon", "creator": "Fred Zinnemann", "description": "Gary Cooper. Real-time Western. Blacklist allegory."}],
    "1952-11-26": [{"type": "theater", "title": "The Mousetrap", "creator": "Agatha Christie", "description": "London premiere. Longest-running play in history."}],

    # 1953
    "1953-02-19": [{"type": "theater", "title": "The Crucible", "creator": "Arthur Miller", "description": "Salem witch trials as McCarthy allegory."}],
    "1953-03-19": [{"type": "film", "title": "25th Academy Awards", "creator": "NBC", "description": "First televised Oscars. 'Greatest Show on Earth' wins."}],
    "1953-05-26": [{"type": "theater", "title": "Can-Can", "creator": "Cole Porter", "description": "Shubert Theatre. Gwen Verdon breakthrough."}],
    "1953-08-13": [{"type": "film", "title": "Roman Holiday", "creator": "William Wyler", "description": "Audrey Hepburn Oscar. Gregory Peck."}],
    "1953-09-16": [{"type": "film", "title": "The Robe", "creator": "Henry Koster", "description": "First CinemaScope film. Richard Burton."}],

    # 1954
    "1954-06-28": [{"type": "film", "title": "On the Waterfront", "creator": "Elia Kazan", "description": "Brando. 'I coulda been a contender.' 8 Oscars."}],
    "1954-09-09": [{"type": "theater", "title": "The Pajama Game", "creator": "Adler & Ross", "description": "St. James Theatre. Bob Fosse choreography."}],
    "1954-10-14": [{"type": "film", "title": "Rear Window", "creator": "Alfred Hitchcock", "description": "James Stewart, Grace Kelly. Voyeurism thriller."}],

    # 1955
    "1955-01-05": [{"type": "theater", "title": "The Diary of Anne Frank", "creator": "Goodrich & Hackett", "description": "Cort Theatre. Pulitzer Prize. Susan Strasberg."}],
    "1955-03-24": [{"type": "film", "title": "East of Eden", "creator": "Elia Kazan", "description": "James Dean film debut. Steinbeck adaptation."}],
    "1955-07-17": [{"type": "art", "title": "Disneyland opens", "creator": "Walt Disney", "description": "Anaheim, California. First theme park."}],
    "1955-10-01": [{"type": "film", "title": "Rebel Without a Cause", "creator": "Nicholas Ray", "description": "James Dean. Teenage angst classic."}],
    "1955-11-30": [{"type": "film", "title": "Oklahoma! film", "creator": "Fred Zinnemann", "description": "First Todd-AO film. Rodgers & Hammerstein."}],

    # 1956
    "1956-03-15": [{"type": "theater", "title": "My Fair Lady", "creator": "Lerner & Loewe", "description": "Mark Hellinger Theatre. Rex Harrison, Julie Andrews."}],
    "1956-06-01": [{"type": "film", "title": "The Searchers", "creator": "John Ford", "description": "John Wayne. Influential Western."}],
    "1956-10-17": [{"type": "film", "title": "Giant", "creator": "George Stevens", "description": "James Dean final film. Texas epic."}],
    "1956-11-16": [{"type": "film", "title": "The Ten Commandments", "creator": "Cecil B. DeMille", "description": "Charlton Heston as Moses. Epic spectacle."}],
    "1956-12-01": [{"type": "theater", "title": "Candide", "creator": "Leonard Bernstein", "description": "Martin Beck Theatre. Lillian Hellman book."}],

    # 1957
    "1957-04-13": [{"type": "film", "title": "12 Angry Men", "creator": "Sidney Lumet", "description": "Henry Fonda. Courtroom drama. Single-set tension."}],
    "1957-09-26": [{"type": "theater", "title": "West Side Story", "creator": "Bernstein & Sondheim", "description": "Winter Garden. Romeo & Juliet in NYC."}],
    "1957-10-04": [{"type": "concert", "title": "Sputnik inspires art", "creator": "USSR", "description": "Space age influences design and culture."}],
    "1957-12-05": [{"type": "film", "title": "The Bridge on the River Kwai", "creator": "David Lean", "description": "William Holden. 7 Oscars. WWII epic."}],
}

# INTERNATIONAL EVENTS
international_events = {
    # 1933
    "1933-01-30": [{"event": "Hitler appointed Chancellor", "description": "Hindenburg names Hitler. Nazi Germany begins.", "location": "Berlin, Germany", "source": "The Times, January 31, 1933", "topic": "politics"}],
    "1933-02-27": [{"event": "Reichstag Fire", "description": "German parliament burns. Hitler suspends civil liberties.", "location": "Berlin, Germany", "source": "The Times", "topic": "politics"}],
    "1933-03-23": [{"event": "Enabling Act passed", "description": "Hitler gains dictatorial powers. Democracy ends.", "location": "Berlin, Germany", "source": "Manchester Guardian", "topic": "politics"}],
    "1933-05-10": [{"event": "Nazi book burnings", "description": "25,000 'un-German' books burned in Berlin.", "location": "Berlin, Germany", "source": "New York Times", "topic": "culture"}],
    "1933-10-14": [{"event": "Germany quits League of Nations", "description": "Hitler withdraws from disarmament talks.", "location": "Geneva, Switzerland", "source": "The Times", "topic": "politics"}],

    # 1934
    "1934-06-30": [{"event": "Night of the Long Knives", "description": "Hitler purges SA. Ernst Röhm killed.", "location": "Germany", "source": "The Times", "topic": "politics"}],
    "1934-08-02": [{"event": "Hitler becomes Führer", "description": "Combines Chancellor and President roles.", "location": "Berlin, Germany", "source": "New York Times", "topic": "politics"}],
    "1934-10-16": [{"event": "Long March begins", "description": "Chinese Communists flee Nationalists. Mao emerges.", "location": "China", "source": "Reuters", "topic": "politics"}],

    # 1935
    "1935-03-16": [{"event": "Germany rearms", "description": "Hitler repudiates Versailles Treaty. Conscription returns.", "location": "Berlin, Germany", "source": "The Times", "topic": "military"}],
    "1935-09-15": [{"event": "Nuremberg Laws", "description": "Jews stripped of citizenship. Marriage banned.", "location": "Nuremberg, Germany", "source": "New York Times", "topic": "politics"}],
    "1935-10-03": [{"event": "Italy invades Ethiopia", "description": "Mussolini's colonial war begins.", "location": "Ethiopia", "source": "The Times", "topic": "war"}],

    # 1936
    "1936-03-07": [{"event": "Rhineland remilitarized", "description": "Hitler defies Versailles. Troops enter demilitarized zone.", "location": "Rhineland, Germany", "source": "The Times", "topic": "military"}],
    "1936-07-17": [{"event": "Spanish Civil War begins", "description": "Franco's nationalist uprising. European testing ground.", "location": "Spain", "source": "The Times", "topic": "war", "end_date": "1939-04-01"}],
    "1936-08-01": [{"event": "Berlin Olympics open", "description": "Jesse Owens defies Hitler. 4 gold medals.", "location": "Berlin, Germany", "source": "New York Times", "topic": "sports"}],
    "1936-10-25": [{"event": "Rome-Berlin Axis formed", "description": "Hitler and Mussolini alliance announced.", "location": "Berlin, Germany", "source": "The Times", "topic": "politics"}],

    # 1937
    "1937-04-26": [{"event": "Guernica bombed", "description": "German Condor Legion destroys Basque town.", "location": "Guernica, Spain", "source": "The Times", "topic": "war"}],
    "1937-07-07": [{"event": "Second Sino-Japanese War", "description": "Marco Polo Bridge Incident. Japan invades China.", "location": "Beijing, China", "source": "New York Times", "topic": "war", "end_date": "1945-09-02"}],
    "1937-12-13": [{"event": "Nanjing Massacre begins", "description": "Japanese troops kill 200,000+ civilians.", "location": "Nanjing, China", "source": "New York Times", "topic": "war"}],

    # 1938
    "1938-03-12": [{"event": "Anschluss", "description": "Germany annexes Austria. Union declared.", "location": "Vienna, Austria", "source": "The Times", "topic": "politics"}],
    "1938-09-30": [{"event": "Munich Agreement", "description": "Chamberlain declares 'Peace for our time.' Sudetenland ceded.", "location": "Munich, Germany", "source": "The Times", "topic": "politics"}],
    "1938-11-09": [{"event": "Kristallnacht", "description": "Night of Broken Glass. Jewish shops, synagogues attacked.", "location": "Germany", "source": "New York Times", "topic": "politics"}],

    # 1939
    "1939-03-15": [{"event": "Germany occupies Czechoslovakia", "description": "Hitler breaks Munich Agreement.", "location": "Prague, Czechoslovakia", "source": "The Times", "topic": "politics"}],
    "1939-08-23": [{"event": "Nazi-Soviet Pact", "description": "Molotov-Ribbentrop non-aggression pact signed.", "location": "Moscow, USSR", "source": "The Times", "topic": "politics"}],
    "1939-09-01": [{"event": "Germany invades Poland", "description": "World War II begins in Europe.", "location": "Poland", "source": "The Times", "topic": "war"}],
    "1939-09-03": [{"event": "Britain and France declare war", "description": "WWII expands. Allies vs Axis.", "location": "London/Paris", "source": "The Times", "topic": "war"}],

    # 1940
    "1940-04-09": [{"event": "Germany invades Denmark and Norway", "description": "Scandinavian campaign begins.", "location": "Scandinavia", "source": "The Times", "topic": "war"}],
    "1940-05-10": [{"event": "Germany invades Western Europe", "description": "Blitzkrieg through Low Countries. Churchill becomes PM.", "location": "Belgium/Netherlands", "source": "The Times", "topic": "war"}],
    "1940-06-04": [{"event": "Dunkirk evacuation ends", "description": "338,000 Allied troops rescued.", "location": "Dunkirk, France", "source": "The Times", "topic": "war"}],
    "1940-06-14": [{"event": "Paris falls", "description": "German troops enter French capital.", "location": "Paris, France", "source": "The Times", "topic": "war"}],
    "1940-06-22": [{"event": "France surrenders", "description": "Armistice signed. Vichy regime begins.", "location": "Compiègne, France", "source": "The Times", "topic": "war"}],
    "1940-07-10": [{"event": "Battle of Britain begins", "description": "Luftwaffe vs RAF. 'Their finest hour.'", "location": "Britain", "source": "The Times", "topic": "war", "end_date": "1940-10-31"}],
    "1940-09-07": [{"event": "The Blitz begins", "description": "German bombing of London starts.", "location": "London, England", "source": "The Times", "topic": "war", "end_date": "1941-05-11"}],

    # 1941
    "1941-03-01": [{"event": "Bulgaria joins Axis", "description": "Nazi influence expands in Balkans.", "location": "Sofia, Bulgaria", "source": "The Times", "topic": "war"}],
    "1941-04-06": [{"event": "Germany invades Yugoslavia and Greece", "description": "Balkan campaign. Athens falls April 27.", "location": "Balkans", "source": "The Times", "topic": "war"}],
    "1941-06-22": [{"event": "Operation Barbarossa", "description": "Germany invades Soviet Union. Largest invasion in history.", "location": "USSR", "source": "The Times", "topic": "war"}],
    "1941-09-08": [{"event": "Siege of Leningrad begins", "description": "900-day siege. 1 million civilians die.", "location": "Leningrad, USSR", "source": "The Times", "topic": "war", "end_date": "1944-01-27"}],
    "1941-12-07": [{"event": "Pearl Harbor attacked", "description": "Japanese attack. 'A date which will live in infamy.'", "location": "Hawaii, USA", "source": "New York Times", "topic": "war"}],

    # 1942
    "1942-01-20": [{"event": "Wannsee Conference", "description": "Final Solution planned. Holocaust systematized.", "location": "Berlin, Germany", "source": "Historical records", "topic": "politics"}],
    "1942-06-04": [{"event": "Battle of Midway", "description": "US defeats Japanese fleet. Pacific turning point.", "location": "Midway Atoll", "source": "New York Times", "topic": "war", "end_date": "1942-06-07"}],
    "1942-08-23": [{"event": "Battle of Stalingrad begins", "description": "Bloodiest battle in history. 2 million casualties.", "location": "Stalingrad, USSR", "source": "The Times", "topic": "war", "end_date": "1943-02-02"}],
    "1942-11-08": [{"event": "Operation Torch", "description": "Allied invasion of North Africa.", "location": "Morocco/Algeria", "source": "The Times", "topic": "war"}],

    # 1943
    "1943-02-02": [{"event": "Stalingrad surrenders", "description": "German 6th Army destroyed. War's turning point.", "location": "Stalingrad, USSR", "source": "The Times", "topic": "war"}],
    "1943-07-10": [{"event": "Allied invasion of Sicily", "description": "Operation Husky. Italy campaign begins.", "location": "Sicily, Italy", "source": "The Times", "topic": "war"}],
    "1943-09-08": [{"event": "Italy surrenders", "description": "Armistice announced. Germany occupies north.", "location": "Italy", "source": "The Times", "topic": "war"}],
    "1943-11-28": [{"event": "Tehran Conference", "description": "FDR, Churchill, Stalin meet. Plan D-Day.", "location": "Tehran, Iran", "source": "The Times", "topic": "politics"}],

    # 1944
    "1944-06-06": [{"event": "D-Day", "description": "Allied invasion of Normandy. 'Operation Overlord.'", "location": "Normandy, France", "source": "The Times", "topic": "war"}],
    "1944-08-25": [{"event": "Paris liberated", "description": "French and American forces free capital.", "location": "Paris, France", "source": "The Times", "topic": "war"}],
    "1944-12-16": [{"event": "Battle of the Bulge", "description": "German counter-offensive. Last major Nazi attack.", "location": "Ardennes, Belgium", "source": "The Times", "topic": "war", "end_date": "1945-01-25"}],

    # 1945
    "1945-02-04": [{"event": "Yalta Conference", "description": "FDR, Churchill, Stalin plan post-war Europe.", "location": "Yalta, Crimea", "source": "The Times", "topic": "politics", "end_date": "1945-02-11"}],
    "1945-04-30": [{"event": "Hitler commits suicide", "description": "Führer dies in Berlin bunker. Eva Braun with him.", "location": "Berlin, Germany", "source": "The Times", "topic": "war"}],
    "1945-05-08": [{"event": "V-E Day", "description": "Germany surrenders. Victory in Europe.", "location": "Berlin, Germany", "source": "The Times", "topic": "war"}],
    "1945-08-06": [{"event": "Hiroshima atomic bombing", "description": "'Little Boy' kills 80,000 instantly.", "location": "Hiroshima, Japan", "source": "New York Times", "topic": "war"}],
    "1945-08-09": [{"event": "Nagasaki atomic bombing", "description": "'Fat Man' kills 40,000. Japan near surrender.", "location": "Nagasaki, Japan", "source": "New York Times", "topic": "war"}],
    "1945-08-15": [{"event": "Japan surrenders", "description": "V-J Day. World War II ends.", "location": "Tokyo, Japan", "source": "New York Times", "topic": "war"}],
    "1945-10-24": [{"event": "United Nations founded", "description": "UN Charter ratified. 51 founding members.", "location": "San Francisco, USA", "source": "New York Times", "topic": "politics"}],
    "1945-11-20": [{"event": "Nuremberg Trials begin", "description": "Nazi war criminals prosecuted.", "location": "Nuremberg, Germany", "source": "The Times", "topic": "politics", "end_date": "1946-10-01"}],

    # 1946
    "1946-03-05": [{"event": "Iron Curtain speech", "description": "Churchill coins term at Westminster College.", "location": "Fulton, Missouri", "source": "The Times", "topic": "politics"}],
    "1946-07-04": [{"event": "Philippines independence", "description": "US grants independence after 48 years.", "location": "Manila, Philippines", "source": "New York Times", "topic": "politics"}],

    # 1947
    "1947-03-12": [{"event": "Truman Doctrine", "description": "US pledges to contain communism.", "location": "Washington, D.C.", "source": "New York Times", "topic": "politics"}],
    "1947-06-05": [{"event": "Marshall Plan announced", "description": "European Recovery Program proposed at Harvard.", "location": "Cambridge, Massachusetts", "source": "New York Times", "topic": "economy"}],
    "1947-08-15": [{"event": "India and Pakistan independence", "description": "British India partitioned. Massive migration.", "location": "India/Pakistan", "source": "The Times", "topic": "politics"}],
    "1947-11-29": [{"event": "UN votes for Palestine partition", "description": "Jewish and Arab states planned.", "location": "New York City", "source": "New York Times", "topic": "politics"}],

    # 1948
    "1948-01-30": [{"event": "Gandhi assassinated", "description": "Hindu extremist kills Mahatma Gandhi.", "location": "New Delhi, India", "source": "The Times", "topic": "politics"}],
    "1948-02-25": [{"event": "Communist coup in Czechoslovakia", "description": "Soviets install communist government.", "location": "Prague, Czechoslovakia", "source": "The Times", "topic": "politics"}],
    "1948-05-14": [{"event": "Israel declares independence", "description": "David Ben-Gurion proclaims Jewish state.", "location": "Tel Aviv, Israel", "source": "New York Times", "topic": "politics"}],
    "1948-06-24": [{"event": "Berlin Blockade begins", "description": "Soviets block Western access. Airlift starts.", "location": "Berlin, Germany", "source": "The Times", "topic": "politics", "end_date": "1949-05-12"}],

    # 1949
    "1949-04-04": [{"event": "NATO founded", "description": "North Atlantic Treaty Organization formed.", "location": "Washington, D.C.", "source": "New York Times", "topic": "politics"}],
    "1949-05-23": [{"event": "West Germany established", "description": "Federal Republic of Germany founded.", "location": "Bonn, Germany", "source": "The Times", "topic": "politics"}],
    "1949-08-29": [{"event": "Soviet atomic bomb test", "description": "USSR ends US nuclear monopoly.", "location": "Kazakhstan, USSR", "source": "New York Times", "topic": "military"}],
    "1949-10-01": [{"event": "People's Republic of China proclaimed", "description": "Mao Zedong declares communist victory.", "location": "Beijing, China", "source": "New York Times", "topic": "politics"}],

    # 1950
    "1950-06-25": [{"event": "Korean War begins", "description": "North Korea invades South.", "location": "Korea", "source": "New York Times", "topic": "war", "end_date": "1953-07-27"}],
    "1950-10-07": [{"event": "China enters Korean War", "description": "300,000 Chinese troops cross Yalu River.", "location": "North Korea", "source": "New York Times", "topic": "war"}],

    # 1951
    "1951-04-11": [{"event": "Truman fires MacArthur", "description": "General relieved of Korean command.", "location": "Washington, D.C.", "source": "New York Times", "topic": "military"}],
    "1951-09-08": [{"event": "San Francisco Peace Treaty", "description": "Japan peace treaty signed. Occupation ends.", "location": "San Francisco, USA", "source": "New York Times", "topic": "politics"}],
    "1951-10-03": [{"event": "Bobby Thomson's 'Shot Heard Round the World'", "description": "Giants win pennant. Historic baseball moment.", "location": "New York City", "source": "New York Times", "topic": "sports"}],
    "1951-10-26": [{"event": "Churchill returns as PM", "description": "Conservatives win. Labour defeated.", "location": "London, England", "source": "The Times", "topic": "politics"}],

    # 1952
    "1952-02-06": [{"event": "King George VI dies", "description": "Elizabeth II becomes Queen.", "location": "Sandringham, England", "source": "The Times", "topic": "politics"}],
    "1952-10-03": [{"event": "Britain tests atomic bomb", "description": "Third nuclear power after US, USSR.", "location": "Monte Bello Islands, Australia", "source": "The Times", "topic": "military"}],
    "1952-11-01": [{"event": "US tests hydrogen bomb", "description": "'Ivy Mike' at Eniwetok. 1000x Hiroshima.", "location": "Marshall Islands", "source": "New York Times", "topic": "military"}],

    # 1953
    "1953-03-05": [{"event": "Stalin dies", "description": "Soviet dictator dead at 74. Power struggle begins.", "location": "Moscow, USSR", "source": "The Times", "topic": "politics"}],
    "1953-06-02": [{"event": "Elizabeth II coronation", "description": "First televised coronation. 27 million watch.", "location": "London, England", "source": "The Times", "topic": "politics"}],
    "1953-06-17": [{"event": "East German uprising", "description": "Workers revolt. Soviet tanks crush protest.", "location": "East Berlin", "source": "The Times", "topic": "politics"}],
    "1953-07-27": [{"event": "Korean War armistice", "description": "Fighting ends. Korea remains divided.", "location": "Panmunjom, Korea", "source": "New York Times", "topic": "war"}],

    # 1954
    "1954-05-07": [{"event": "Dien Bien Phu falls", "description": "French defeated in Vietnam. Colonial era ends.", "location": "Vietnam", "source": "The Times", "topic": "war"}],
    "1954-07-21": [{"event": "Geneva Accords", "description": "Vietnam divided at 17th parallel.", "location": "Geneva, Switzerland", "source": "The Times", "topic": "politics"}],

    # 1955
    "1955-04-18": [{"event": "Einstein dies", "description": "Physicist dies at 76 in Princeton.", "location": "Princeton, New Jersey", "source": "New York Times", "topic": "science"}],
    "1955-05-14": [{"event": "Warsaw Pact formed", "description": "Soviet military alliance responds to NATO.", "location": "Warsaw, Poland", "source": "The Times", "topic": "politics"}],
    "1955-07-17": [{"event": "Disneyland opens", "description": "First theme park in Anaheim.", "location": "Anaheim, California", "source": "Los Angeles Times", "topic": "culture"}],

    # 1956
    "1956-02-25": [{"event": "Khrushchev denounces Stalin", "description": "Secret speech reveals Stalin's crimes.", "location": "Moscow, USSR", "source": "The Times", "topic": "politics"}],
    "1956-10-23": [{"event": "Hungarian Revolution", "description": "Anti-Soviet uprising in Budapest.", "location": "Budapest, Hungary", "source": "The Times", "topic": "politics", "end_date": "1956-11-10"}],
    "1956-10-29": [{"event": "Suez Crisis", "description": "Israel, Britain, France attack Egypt.", "location": "Suez Canal, Egypt", "source": "The Times", "topic": "war", "end_date": "1956-11-07"}],

    # 1957
    "1957-03-25": [{"event": "Treaty of Rome", "description": "European Economic Community founded.", "location": "Rome, Italy", "source": "The Times", "topic": "politics"}],
    "1957-10-04": [{"event": "Sputnik launched", "description": "First artificial satellite. Space Age begins.", "location": "Kazakhstan, USSR", "source": "New York Times", "topic": "science"}],
    "1957-11-03": [{"event": "Sputnik 2 with Laika", "description": "First animal in orbit. Dog dies in space.", "location": "Kazakhstan, USSR", "source": "New York Times", "topic": "science"}],
}

# Load existing files and merge
with open('bmc_culture_1933-1957.json', 'r') as f:
    culture_data = json.load(f)

# Merge culture events
for date, events in culture_events.items():
    if date not in culture_data['events']:
        culture_data['events'][date] = []
    for evt in events:
        if not any(e.get('title') == evt.get('title') for e in culture_data['events'][date]):
            culture_data['events'][date].append(evt)

# Save updated culture file
with open('bmc_culture_1933-1957.json', 'w') as f:
    json.dump(culture_data, f, indent=2)

print(f"Culture events: {len(culture_data['events'])} dates")

# Load chronology and add international events
with open('bmc_chronology_precise.json', 'r') as f:
    chrono_data = json.load(f)

# Add international events to chronology
for date, events in international_events.items():
    if date not in chrono_data['events']:
        chrono_data['events'][date] = {'usa': [], 'world': [], 'culture': []}
    for evt in events:
        if not any(e.get('event') == evt.get('event') for e in chrono_data['events'][date].get('world', [])):
            if 'world' not in chrono_data['events'][date]:
                chrono_data['events'][date]['world'] = []
            chrono_data['events'][date]['world'].append(evt)

# Save updated chronology
with open('bmc_chronology_precise.json', 'w') as f:
    json.dump(chrono_data, f, indent=2)

print(f"Chronology events: {len(chrono_data['events'])} dates")

print("Done enriching events!")
