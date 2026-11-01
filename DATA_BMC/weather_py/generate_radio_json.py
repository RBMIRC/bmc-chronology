#!/usr/bin/env python3
"""
Generate BMC Radio JSON with daily song probabilities
Structure similar to weather archive
"""

import json
import random
from datetime import date, timedelta
from collections import defaultdict
import math

# Song database with estimated chart periods
# Format: (title, artist, genre, peak_month (1-12), peak_position (1-100), duration_months)

SONGS_DATABASE = [
    # 1933
    (1933, "Stormy Weather", "Ethel Waters", "Jazz", 6, 1, 5),
    (1933, "Sophisticated Lady", "Duke Ellington", "Jazz", 4, 2, 4),
    (1933, "Gold Digger's Song", "Dick Powell", "Pop", 9, 3, 3),
    (1933, "Shadow Waltz", "Bing Crosby", "Pop", 7, 4, 4),
    (1933, "The Last Round-Up", "George Olsen", "Country", 10, 1, 6),
    (1933, "Lazybones", "Ted Lewis", "Jazz", 5, 8, 3),
    (1933, "Night & Day", "Eddy Duchin", "Pop", 3, 6, 4),
    (1933, "Easter Parade", "Leo Reisman", "Pop", 4, 10, 3),
    (1933, "April in Paris", "Henry King", "Jazz", 4, 15, 3),
    (1933, "Who's Afraid of the Big Bad Wolf?", "Don Bestor", "Novelty", 11, 5, 4),

    # 1934
    (1934, "June In January", "Bing Crosby", "Pop", 1, 1, 5),
    (1934, "Stars Fell on Alabama", "Jack Teagarden", "Jazz", 8, 5, 4),
    (1934, "The Continental", "Leo Reisman", "Pop", 10, 3, 4),
    (1934, "Cocktails for Two", "Duke Ellington", "Jazz", 6, 8, 3),
    (1934, "Isle of Capri", "Ray Noble", "Pop", 12, 2, 5),
    (1934, "Blue Moon", "Glen Gray", "Pop", 9, 6, 4),
    (1934, "I Only Have Eyes for You", "Ben Selvin", "Pop", 7, 4, 4),

    # 1935
    (1935, "Cheek to Cheek", "Fred Astaire", "Pop", 9, 1, 5),
    (1935, "Red Sails in the Sunset", "Bing Crosby", "Pop", 10, 3, 4),
    (1935, "I'm in the Mood for Love", "Little Jack Little", "Pop", 7, 5, 4),
    (1935, "Begin the Beguine", "Xavier Cugat", "Latin", 11, 8, 4),
    (1935, "Lullaby of Broadway", "Dorsey Brothers", "Swing", 5, 4, 3),
    (1935, "These Foolish Things", "Benny Goodman", "Swing", 6, 6, 4),

    # 1936
    (1936, "Pennies From Heaven", "Bing Crosby", "Pop", 11, 1, 6),
    (1936, "The Way You Look Tonight", "Fred Astaire", "Pop", 10, 2, 5),
    (1936, "I've Got You Under My Skin", "Cole Porter", "Jazz", 8, 5, 4),
    (1936, "Goody Goody", "Benny Goodman", "Swing", 3, 4, 4),
    (1936, "Is It True What They Say About Dixie?", "Rudy Vallee", "Pop", 5, 6, 3),

    # 1937
    (1937, "Once In A While", "Tommy Dorsey", "Swing", 11, 1, 5),
    (1937, "Boo-Hoo", "Guy Lombardo", "Pop", 3, 3, 4),
    (1937, "September in the Rain", "Guy Lombardo", "Pop", 9, 4, 4),
    (1937, "They Can't Take That Away from Me", "Fred Astaire", "Pop", 5, 5, 4),
    (1937, "A Foggy Day", "Fred Astaire", "Pop", 11, 6, 3),
    (1937, "In the Still of the Night", "Tommy Dorsey", "Swing", 8, 7, 4),

    # 1938
    (1938, "My Reverie", "Larry Clinton", "Swing", 10, 1, 5),
    (1938, "Begin The Beguine", "Artie Shaw", "Swing", 9, 2, 6),
    (1938, "A-Tisket A-Tasket", "Ella Fitzgerald", "Swing", 6, 1, 5),
    (1938, "Thanks for the Memory", "Bob Hope", "Pop", 3, 5, 4),
    (1938, "I've Got a Pocketful of Dreams", "Bing Crosby", "Pop", 8, 4, 4),
    (1938, "Jeepers Creepers", "Al Donohue", "Pop", 11, 6, 3),

    # 1939
    (1939, "Deep Purple", "Larry Clinton", "Swing", 4, 1, 5),
    (1939, "Over The Rainbow", "Judy Garland", "Pop", 8, 1, 6),
    (1939, "Beer Barrel Polka", "Will Glahe", "Polka", 6, 3, 4),
    (1939, "Moonlight Serenade", "Glenn Miller", "Swing", 5, 2, 6),
    (1939, "In the Mood", "Glenn Miller", "Swing", 11, 1, 8),
    (1939, "South of the Border", "Shep Fields", "Pop", 10, 5, 4),
    (1939, "Wishing", "Glenn Miller", "Swing", 7, 6, 4),

    # 1940
    (1940, "In the Mood", "Glenn Miller", "Swing", 1, 1, 6),
    (1940, "Frenesi", "Artie Shaw", "Swing", 9, 2, 5),
    (1940, "I'll Never Smile Again", "Tommy Dorsey & Frank Sinatra", "Swing", 7, 1, 6),
    (1940, "When You Wish Upon a Star", "Cliff Edwards", "Pop", 3, 4, 5),
    (1940, "Only Forever", "Bing Crosby", "Pop", 10, 5, 4),
    (1940, "Tuxedo Junction", "Glenn Miller", "Swing", 3, 3, 5),
    (1940, "Pennsylvania 6-5000", "Glenn Miller", "Swing", 5, 6, 4),
    (1940, "Blueberry Hill", "Glenn Miller", "Swing", 11, 8, 4),
    (1940, "You Are My Sunshine", "Jimmie Davis", "Country", 8, 4, 6),
    (1940, "Imagination", "Glenn Miller", "Swing", 6, 10, 4),
    (1940, "Ko Ko", "Duke Ellington", "Jazz", 4, 15, 3),
    (1940, "Stardust", "Tommy Dorsey", "Swing", 9, 12, 4),
    (1940, "Mule Skinner Blues", "Bill Monroe", "Bluegrass", 2, 20, 4),

    # 1941
    (1941, "Chattanooga Choo Choo", "Glenn Miller", "Swing", 12, 1, 6),
    (1941, "I Don't Want to Set the World on Fire", "The Ink Spots", "R&B", 8, 4, 5),
    (1941, "Amapola", "Jimmy Dorsey", "Swing", 3, 2, 5),
    (1941, "Daddy", "Sammy Kaye", "Pop", 4, 5, 4),
    (1941, "Blues in the Night", "Woody Herman", "Jazz", 12, 3, 5),
    (1941, "Green Eyes", "Jimmy Dorsey", "Swing", 7, 6, 4),
    (1941, "Take the 'A' Train", "Duke Ellington", "Jazz", 2, 1, 6),
    (1941, "This Love of Mine", "Tommy Dorsey & Frank Sinatra", "Swing", 9, 8, 4),

    # 1942
    (1942, "White Christmas", "Bing Crosby", "Pop", 10, 1, 8),
    (1942, "Sleepy Lagoon", "Harry James", "Swing", 7, 2, 5),
    (1942, "A String of Pearls", "Glenn Miller", "Swing", 2, 3, 5),
    (1942, "Moonlight Cocktail", "Glenn Miller", "Swing", 3, 4, 4),
    (1942, "Tangerine", "Jimmy Dorsey", "Swing", 5, 5, 4),
    (1942, "Don't Sit Under the Apple Tree", "Glenn Miller", "Swing", 6, 6, 4),
    (1942, "I've Got a Gal in Kalamazoo", "Glenn Miller", "Swing", 9, 7, 4),
    (1942, "At Last", "Glenn Miller", "Swing", 4, 8, 5),

    # 1943
    (1943, "I've Heard That Song Before", "Harry James", "Swing", 2, 1, 5),
    (1943, "Paper Doll", "The Mills Brothers", "R&B", 8, 1, 7),
    (1943, "You'll Never Know", "Dick Haymes", "Pop", 6, 2, 5),
    (1943, "That Old Black Magic", "Glenn Miller", "Swing", 3, 4, 4),
    (1943, "Pistol Packin' Mama", "Al Dexter", "Country", 10, 1, 6),
    (1943, "As Time Goes By", "Dooley Wilson", "Pop", 4, 5, 5),
    (1943, "Don't Get Around Much Anymore", "Duke Ellington", "Jazz", 5, 6, 4),

    # 1944
    (1944, "I'll Be Seeing You", "Bing Crosby", "Pop", 5, 1, 6),
    (1944, "Swinging on a Star", "Bing Crosby", "Pop", 7, 1, 5),
    (1944, "Long Ago And Far Away", "Jo Stafford", "Pop", 8, 3, 4),
    (1944, "The Trolley Song", "Judy Garland", "Pop", 11, 2, 5),
    (1944, "Shoo-Shoo Baby", "The Andrews Sisters", "Swing", 2, 4, 4),
    (1944, "Don't Fence Me In", "Bing Crosby", "Pop", 12, 1, 6),
    (1944, "I Love You", "Bing Crosby", "Pop", 9, 5, 4),

    # 1945
    (1945, "Sentimental Journey", "Les Brown & Doris Day", "Swing", 3, 1, 6),
    (1945, "Rum & Coca-Cola", "The Andrews Sisters", "Pop", 2, 2, 5),
    (1945, "Till The End of Time", "Perry Como", "Pop", 9, 1, 5),
    (1945, "On the Atchison Topeka", "Johnny Mercer", "Pop", 7, 3, 4),
    (1945, "It's Been a Long Long Time", "Harry James", "Swing", 11, 2, 5),
    (1945, "Accentuate the Positive", "Johnny Mercer", "Pop", 1, 4, 4),
    (1945, "Caledonia", "Louis Jordan", "R&B", 6, 5, 4),
    (1945, "I'm Beginning to See The Light", "Duke Ellington", "Jazz", 4, 6, 4),
    (1945, "Dream", "The Pied Pipers", "Pop", 5, 8, 4),
    (1945, "Nancy With The Laughing Face", "Frank Sinatra", "Pop", 10, 10, 4),

    # 1946
    (1946, "Prisoner of Love", "Perry Como", "Pop", 5, 1, 5),
    (1946, "To Each His Own", "Eddy Howard", "Pop", 8, 1, 6),
    (1946, "The Gypsy", "The Ink Spots", "R&B", 6, 2, 5),
    (1946, "Five Minutes More", "Frank Sinatra", "Pop", 9, 3, 4),
    (1946, "Ole Buttermilk Sky", "Kay Kyser", "Pop", 10, 4, 4),
    (1946, "Choo Choo Ch'Boogie", "Louis Jordan", "R&B", 7, 1, 5),
    (1946, "Route 66", "Nat King Cole", "Jazz", 4, 5, 5),
    (1946, "Personality", "Johnny Mercer", "Pop", 3, 6, 4),

    # 1947
    (1947, "Near You", "Francis Craig", "Pop", 9, 1, 7),
    (1947, "Peg O' My Heart", "Harmonicats", "Pop", 6, 2, 5),
    (1947, "Heartaches", "Ted Weems", "Pop", 4, 3, 5),
    (1947, "Mam'selle", "Art Lund", "Pop", 5, 5, 4),
    (1947, "Ballerina", "Vaughn Monroe", "Pop", 10, 4, 4),
    (1947, "Smoke Smoke Smoke", "Tex Williams", "Country", 7, 1, 5),
    (1947, "Move It On Over", "Hank Williams", "Country", 8, 8, 4),

    # 1948
    (1948, "Buttons & Bows", "Dinah Shore", "Pop", 10, 1, 6),
    (1948, "Nature Boy", "Nat King Cole", "Jazz", 4, 1, 6),
    (1948, "Twelfth Street Rag", "Pee Wee Hunt", "Jazz", 9, 3, 5),
    (1948, "Manana", "Peggy Lee", "Pop", 3, 2, 5),
    (1948, "Now Is the Hour", "Bing Crosby", "Pop", 2, 5, 4),
    (1948, "It's Magic", "Doris Day", "Pop", 6, 4, 5),
    (1948, "Good Rockin' Tonight", "Wynonie Harris", "R&B", 7, 8, 4),
    (1948, "My Happiness", "Ella Fitzgerald", "Jazz", 5, 6, 4),
    (1948, "Bouquet of Roses", "Eddy Arnold", "Country", 6, 7, 5),
    (1948, "Tennessee Waltz", "Pee Wee King", "Country", 12, 10, 4),
    (1948, "Boogie Chillun", "John Lee Hooker", "Blues", 1, 15, 3),

    # 1949
    (1949, "Riders in the Sky", "Vaughn Monroe", "Pop", 5, 1, 5),
    (1949, "That Lucky Old Sun", "Frankie Laine", "Pop", 9, 2, 5),
    (1949, "Some Enchanted Evening", "Perry Como", "Pop", 6, 3, 5),
    (1949, "Baby It's Cold Outside", "Dinah Shore", "Pop", 12, 4, 4),
    (1949, "Cruising Down the River", "Russ Morgan", "Pop", 4, 5, 4),
    (1949, "Lovesick Blues", "Hank Williams", "Country", 3, 1, 6),
    (1949, "I'm So Lonesome I Could Cry", "Hank Williams", "Country", 11, 6, 5),
    (1949, "The Fat Man", "Fats Domino", "R&B", 12, 10, 4),

    # 1950
    (1950, "Mona Lisa", "Nat King Cole", "Pop", 7, 1, 7),
    (1950, "Third Man Theme", "Anton Karas", "Pop", 4, 2, 5),
    (1950, "Tennessee Waltz", "Patti Page", "Pop", 12, 1, 8),
    (1950, "Music! Music! Music!", "Teresa Brewer", "Pop", 2, 3, 5),
    (1950, "Goodnight Irene", "The Weavers", "Folk", 8, 1, 6),
    (1950, "Bewitched", "Doris Day", "Pop", 5, 5, 4),
    (1950, "Rag Mop", "The Ames Brothers", "Pop", 3, 4, 4),
    (1950, "Chattanoogie Shoe-Shine Boy", "Red Foley", "Country", 2, 6, 4),
    (1950, "Foggy Mountain Breakdown", "Flatt & Scruggs", "Bluegrass", 6, 15, 4),
    (1950, "I'm Movin' On", "Hank Snow", "Country", 9, 8, 5),
    (1950, "Rollin' Stone", "Muddy Waters", "Blues", 5, 20, 3),

    # 1951
    (1951, "Too Young", "Nat King Cole", "Pop", 6, 1, 6),
    (1951, "Because of You", "Tony Bennett", "Pop", 9, 1, 6),
    (1951, "How High the Moon", "Les Paul & Mary Ford", "Pop", 4, 2, 5),
    (1951, "Come On-a My House", "Rosemary Clooney", "Pop", 7, 3, 5),
    (1951, "Be My Love", "Mario Lanza", "Pop", 2, 4, 4),
    (1951, "Cold Cold Heart", "Tony Bennett", "Pop", 11, 5, 5),
    (1951, "Hey Good Lookin'", "Hank Williams", "Country", 8, 6, 5),
    (1951, "Rocket 88", "Jackie Brenston", "R&B", 5, 8, 4),
    (1951, "Sixty Minute Man", "The Dominoes", "R&B", 6, 10, 4),

    # 1952
    (1952, "You Belong to Me", "Jo Stafford", "Pop", 9, 1, 6),
    (1952, "Blue Tango", "Leroy Anderson", "Pop", 5, 2, 5),
    (1952, "Wheel of Fortune", "Kay Starr", "Pop", 3, 3, 5),
    (1952, "Cry", "Johnnie Ray", "Pop", 2, 4, 5),
    (1952, "I Saw Mommy Kissing Santa Claus", "Jimmy Boyd", "Novelty", 12, 5, 3),
    (1952, "Lawdy Miss Clawdy", "Lloyd Price", "R&B", 6, 8, 4),
    (1952, "Jambalaya", "Hank Williams", "Country", 8, 1, 6),
    (1952, "Your Cheatin' Heart", "Hank Williams", "Country", 11, 6, 5),

    # 1953
    (1953, "Vaya Con Dios", "Les Paul & Mary Ford", "Pop", 8, 1, 6),
    (1953, "Song from Moulin Rouge", "Percy Faith", "Pop", 5, 2, 5),
    (1953, "Rags to Riches", "Tony Bennett", "Pop", 10, 3, 5),
    (1953, "That's Amore", "Dean Martin", "Pop", 11, 4, 5),
    (1953, "Crying in the Chapel", "The Orioles", "R&B", 7, 5, 4),
    (1953, "Shake Rattle & Roll", "Big Joe Turner", "R&B", 6, 8, 4),
    (1953, "Money Honey", "The Drifters", "R&B", 9, 10, 4),
    (1953, "Kaw-Liga", "Hank Williams", "Country", 3, 6, 5),

    # 1954
    (1954, "Sh-Boom", "The Crew-Cuts", "Pop", 7, 1, 5),
    (1954, "Little Things Mean a Lot", "Kitty Kallen", "Pop", 6, 2, 5),
    (1954, "Hey There", "Rosemary Clooney", "Pop", 9, 3, 5),
    (1954, "I Need You Now", "Eddie Fisher", "Pop", 10, 4, 4),
    (1954, "Earth Angel", "The Penguins", "Doo-wop", 12, 5, 5),
    (1954, "That's All Right", "Elvis Presley", "Rock", 8, 10, 4),
    (1954, "Blue Moon of Kentucky", "Elvis Presley", "Rock", 9, 12, 4),
    (1954, "Sh-Boom", "The Chords", "R&B", 7, 8, 4),

    # 1955
    (1955, "Rock Around the Clock", "Bill Haley", "Rock", 7, 1, 7),
    (1955, "Sixteen Tons", "Tennessee Ernie Ford", "Country", 11, 1, 6),
    (1955, "Cherry Pink", "Perez Prado", "Latin", 4, 2, 5),
    (1955, "Only You", "The Platters", "Doo-wop", 10, 3, 6),
    (1955, "Love is a Many Splendoured Thing", "Four Aces", "Pop", 9, 4, 5),
    (1955, "Unchained Melody", "Al Hibbler", "Pop", 5, 5, 5),
    (1955, "Tutti Frutti", "Little Richard", "Rock", 12, 6, 5),
    (1955, "Learnin' the Blues", "Frank Sinatra", "Pop", 6, 7, 4),
    (1955, "Maybellene", "Chuck Berry", "Rock", 8, 8, 5),
    (1955, "Ain't That a Shame", "Fats Domino", "Rock", 7, 9, 5),
    (1955, "Bo Diddley", "Bo Diddley", "Rock", 5, 12, 4),
    (1955, "Mystery Train", "Elvis Presley", "Rock", 10, 15, 4),
    (1955, "Cry Me a River", "Julie London", "Jazz", 11, 10, 4),

    # 1956
    (1956, "Heartbreak Hotel", "Elvis Presley", "Rock", 4, 1, 6),
    (1956, "Don't Be Cruel", "Elvis Presley", "Rock", 8, 1, 7),
    (1956, "Hound Dog", "Elvis Presley", "Rock", 8, 1, 6),
    (1956, "Love Me Tender", "Elvis Presley", "Rock", 11, 1, 5),
    (1956, "The Wayward Wind", "Gogi Grant", "Pop", 6, 2, 5),
    (1956, "My Prayer", "The Platters", "Doo-wop", 9, 3, 5),
    (1956, "The Great Pretender", "The Platters", "Doo-wop", 2, 4, 5),
    (1956, "Blue Suede Shoes", "Carl Perkins", "Rock", 3, 5, 5),
    (1956, "I Walk the Line", "Johnny Cash", "Country", 8, 6, 6),
    (1956, "Long Tall Sally", "Little Richard", "Rock", 5, 7, 4),
    (1956, "Blueberry Hill", "Fats Domino", "Rock", 10, 8, 5),
    (1956, "Be-Bop-A-Lula", "Gene Vincent", "Rock", 7, 9, 4),
    (1956, "Why Do Fools Fall in Love", "Frankie Lymon", "Doo-wop", 3, 10, 5),
    (1956, "Roll Over Beethoven", "Chuck Berry", "Rock", 6, 12, 4),

    # 1957
    (1957, "All Shook Up", "Elvis Presley", "Rock", 4, 1, 6),
    (1957, "Jailhouse Rock", "Elvis Presley", "Rock", 10, 1, 6),
    (1957, "Love Letters in the Sand", "Pat Boone", "Pop", 6, 2, 6),
    (1957, "Tammy", "Debbie Reynolds", "Pop", 8, 3, 5),
    (1957, "Young Love", "Tab Hunter", "Pop", 2, 4, 5),
    (1957, "Bye Bye Love", "The Everly Brothers", "Rock", 6, 5, 5),
    (1957, "Wake Up Little Susie", "The Everly Brothers", "Rock", 10, 6, 5),
    (1957, "That'll Be the Day", "Buddy Holly", "Rock", 9, 7, 5),
    (1957, "Peggy Sue", "Buddy Holly", "Rock", 11, 8, 5),
    (1957, "Diana", "Paul Anka", "Pop", 8, 9, 5),
    (1957, "Whole Lotta Shakin'", "Jerry Lee Lewis", "Rock", 7, 10, 5),
    (1957, "Great Balls of Fire", "Jerry Lee Lewis", "Rock", 12, 11, 5),
    (1957, "School Day", "Chuck Berry", "Rock", 5, 12, 4),
    (1957, "Lucille", "Little Richard", "Rock", 4, 15, 4),
    (1957, "Party Doll", "Buddy Knox", "Rock", 3, 18, 4),
]

# Regional/Local songs (WWNC Asheville, country, bluegrass)
REGIONAL_SONGS = [
    # Continuous regional favorites
    (1933, 1957, "Amazing Grace", "Traditional", "Gospel", 0.3),
    (1933, 1957, "Wildwood Flower", "Carter Family", "Folk", 0.25),
    (1933, 1957, "Keep on the Sunny Side", "Carter Family", "Folk", 0.2),
    (1935, 1957, "Great Speckled Bird", "Roy Acuff", "Country", 0.3),
    (1939, 1957, "Wabash Cannonball", "Roy Acuff", "Country", 0.25),
    (1940, 1957, "You Are My Sunshine", "Jimmie Davis", "Country", 0.35),
    (1940, 1950, "Mule Skinner Blues", "Bill Monroe", "Bluegrass", 0.25),
    (1941, 1957, "Walking the Floor Over You", "Ernest Tubb", "Country", 0.25),
    (1945, 1955, "Tramp on the Street", "Wilma Lee Cooper", "Bluegrass", 0.2),
    (1946, 1957, "Blue Moon of Kentucky", "Bill Monroe", "Bluegrass", 0.3),
    (1947, 1957, "Molly and Tenbrooks", "Bill Monroe", "Bluegrass", 0.25),
    (1949, 1957, "Foggy Mountain Breakdown", "Flatt & Scruggs", "Bluegrass", 0.35),
    (1949, 1957, "I'm So Lonesome I Could Cry", "Hank Williams", "Country", 0.3),
    (1951, 1957, "Cold Cold Heart", "Hank Williams", "Country", 0.3),
    (1952, 1957, "Jambalaya", "Hank Williams", "Country", 0.3),
    (1954, 1957, "I Don't Care", "Webb Pierce", "Country", 0.25),
    (1955, 1957, "Crazy Arms", "Ray Price", "Country", 0.25),
    (1956, 1957, "I Walk the Line", "Johnny Cash", "Country", 0.35),
]


def calculate_probability(peak_position, months_from_peak, duration_months):
    """Calculate probability based on chart position and time from peak"""
    # Base probability from chart position (1st = 0.9, 100th = 0.1)
    base_prob = max(0.1, 0.9 - (peak_position - 1) * 0.008)

    # Decay based on months from peak (Gaussian-like)
    half_duration = duration_months / 2
    if abs(months_from_peak) <= half_duration:
        time_factor = 1.0
    else:
        decay = abs(months_from_peak) - half_duration
        time_factor = max(0.1, math.exp(-decay * 0.5))

    return round(base_prob * time_factor, 2)


def get_songs_for_date(year, month, day, songs_db, regional):
    """Get list of songs with probabilities for a specific date"""
    songs = []

    # National hits
    for song in songs_db:
        s_year, title, artist, genre, peak_month, peak_pos, duration = song

        if s_year == year:
            months_from_peak = month - peak_month
            prob = calculate_probability(peak_pos, months_from_peak, duration)
            if prob >= 0.15:  # Only include if reasonable probability
                songs.append({
                    "title": title,
                    "artist": artist,
                    "genre": genre,
                    "probability": prob
                })
        # Also include hits from previous year still charting
        elif s_year == year - 1 and month <= 3:
            months_from_peak = month + (12 - peak_month)
            prob = calculate_probability(peak_pos, months_from_peak, duration)
            if prob >= 0.15:
                songs.append({
                    "title": title,
                    "artist": artist,
                    "genre": genre,
                    "probability": prob
                })

    # Regional favorites
    for reg in regional:
        start_year, end_year, title, artist, genre, base_prob = reg
        if start_year <= year <= end_year:
            # Regional songs have consistent probability with slight variation
            prob = round(base_prob + random.uniform(-0.05, 0.05), 2)
            songs.append({
                "title": title,
                "artist": artist,
                "genre": genre,
                "probability": max(0.1, min(0.5, prob)),
                "source": "WWNC_Asheville"
            })

    # Sort by probability
    songs.sort(key=lambda x: x["probability"], reverse=True)

    return songs[:15]  # Top 15 most likely songs


def generate_radio_archive():
    """Generate the full JSON archive"""

    archive = {
        "bmc_radio_archive": {
            "metadata": {
                "location": "Black Mountain, North Carolina",
                "coordinates": {"lat": 35.6179, "lon": -82.3968},
                "period": "1933-1957",
                "description": "Estimated radio playlist probabilities for Black Mountain College area",
                "sources": [
                    "Billboard Charts",
                    "Your Hit Parade",
                    "WWNC Asheville",
                    "Grand Ole Opry"
                ],
                "note": "Probabilities are estimates based on chart positions and regional music trends"
            },
            "years": {}
        }
    }

    # Set seed for reproducibility
    random.seed(1933)

    start_date = date(1933, 9, 1)  # BMC opened September 1933
    end_date = date(1957, 10, 31)  # BMC closed October 1957

    current_date = start_date
    total_days = 0

    while current_date <= end_date:
        year = str(current_date.year)
        month = f"{current_date.month:02d}"
        day = f"{current_date.day:02d}"

        # Initialize year/month structure
        if year not in archive["bmc_radio_archive"]["years"]:
            archive["bmc_radio_archive"]["years"][year] = {"months": {}}
        if month not in archive["bmc_radio_archive"]["years"][year]["months"]:
            archive["bmc_radio_archive"]["years"][year]["months"][month] = {"days": {}}

        # Get songs for this date
        songs = get_songs_for_date(
            current_date.year,
            current_date.month,
            current_date.day,
            SONGS_DATABASE,
            REGIONAL_SONGS
        )

        archive["bmc_radio_archive"]["years"][year]["months"][month]["days"][day] = {
            "songs": songs
        }

        current_date += timedelta(days=1)
        total_days += 1

    # Add statistics
    archive["bmc_radio_archive"]["statistics"] = {
        "total_days": total_days,
        "unique_songs": len(SONGS_DATABASE) + len(REGIONAL_SONGS),
        "genres": list(set([s[3] for s in SONGS_DATABASE] + [r[4] for r in REGIONAL_SONGS]))
    }

    return archive


if __name__ == "__main__":
    print("Generating BMC Radio Archive JSON...")
    archive = generate_radio_archive()

    output_path = "/Users/sylvain/Documents/METEO BMC/bmc_radio_archive_1933-1957.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(archive, f, indent=2, ensure_ascii=False)

    print(f"Archive saved to: {output_path}")
    print(f"Total days: {archive['bmc_radio_archive']['statistics']['total_days']}")
    print(f"Unique songs: {archive['bmc_radio_archive']['statistics']['unique_songs']}")
