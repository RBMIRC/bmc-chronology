# Chronos 1/5 : asheville_events.json contre l'AAM audité (001)

Source : `DATA_BMC/Chronos/asheville_events.json` (extraction automatique du 2025-12-01, 377 documents, 1906 événements). Comparé à `programme/evenements.csv` (4 650 activités, extraction manuelle et audit phrase par phrase) et au texte OCR de chaque document.

## Résultat

| statut | événements | dont retrouvés dans le texte du document |
|---|---|---|
| confirmé | 1120 | 1098 (98 %) |
| absent de l'AAM | 331 | 305 (92 %) |
| confirmé par un autre document AAM | 172 | 167 (97 %) |
| confirmé (calendrier) | 107 | 95 (89 %) |
| document hors corpus | 105 | 95 (90 %) |
| date différente | 51 | 50 (98 %) |
| date illisible | 18 | 18 (100 %) |
| confirmé par Duberman | 2 | 1 (50 %) |

Vérification dans le texte : retrouvé 1829, indice faible 76, à relire 1.

## Lecture

- **Confirmé** : l'extraction automatique retrouve une activité AAM du même document à la même date.
- **Date différente** : même fait probable dans le même document, daté autrement. Ordre de confiance : la lecture manuelle (AAM) prime ; à relire seulement si Chronos est retrouvé dans le texte.
- **Absent de l'AAM** : pistes. L'audit AAM a relu toutes les phrases datées : un absent est soit un oubli, soit une règle écartée volontairement (administratif, horaires), soit une invention du modèle (alors non retrouvé dans le texte).

## Absents de l'AAM, datés au jour et retrouvés dans le texte (137) — à relire en priorité

- 1942-06-22 · 2017.40.019 · Start of Accelerated Program
- 1942-06-22 · 2017.40.020 · Beginning of the accelerated program with four quarters of eleven weeks each.
- 1943-08-17 · 2017.40.024 · Final decision to open the college for the new academic year
- 1943-08-12 · 2017.40.024 · Seminar on America ended
- 1943-09-01 · 2017.40.024 · Fundraising campaign status
- 1945-07-02 · 2017.40.035 · Start of the Second Art Institute Summer 1945
- 1945-09-08 · 2017.40.035 · End of the Second Art Institute Summer 1945
- 1946-08-27 · 2017.40.038 · Death of Bascomb Allen
- 1947-04-01 · 2017.40.039 · Peggy Bennett's visit to New York
- 1942-01-24 · 2017.40.054 · Bob Wunsch leaves for Fiske University
- 1942-03-03 · 2017.40.065.01a-b · Jack Kasik inducted into military service
- 1942-03-03 · 2017.40.065.01a-b · Ted Dreier's business trip
- 1942-03-04 · 2017.40.065.01a-b · Bob Wunsch's conference
- 1942-03-02 · 2017.40.065.02a-b · Faculty meeting
- 1942-03-03 · 2017.40.065.02a-b · Jack Kasik leaves for military service
- 1942-03-03 · 2017.40.065.02a-b · Ted Dreier's business trip
- 1942-03-04 · 2017.40.065.02a-b · Bob Wunsch's trip to Nashville
- 1942-03-30 · 2017.40.068.02 · Faculty meeting
- 1942-05-16 · 2017.40.068.02 · Play production
- 1942-04-28 · 2017.40.074 · Letter from CS Adams to Fred Mangold
- 1942-05-11 · 2017.40.074 · Josephine Duveneck joins Advisory Council
- 1942-06-22 · 2017.40.076a-f · Opening of the first Summer Quarter
- 1942-11-04 · 2017.40.079 · College Conference in Greensboro
- 1942-12-02 · 2017.40.085 · Lecture by Dr. Strauss
- 1942-12-10 · 2017.40.086 · Board of Fellows appoints Robert Orr
- 1943-01-01 · 2017.40.087a-c · War Department to call enlisted reserve corps students to active duty.
- 1943-03-13 · 2017.40.094.02a-b · Concert of trios
- 1943-03-21 · 2017.40.098 · Black Mountain College radio program
- 1943-04-13 · 2017.40.101a-c · Student meeting in the Lobby of North Lodge
- 1943-04-21 · 2017.40.102a-e · Talk by Frances deGraaff
- 1943-05-31 · 2017.40.109a-b · Regular weekly meeting of the Faculty and the Student Officers.
- 1943-06-14 · 2017.40.110a-c · Publication of the Black Mountain College Community Bulletin
- 1943-04-27 · 2017.40.110a-c · Oliver Freud arrives in America
- 1943-04-01 · 2017.40.110a-c · Start of financial campaign
- 1943-06-28 · 2017.40.112a-c · Arrival of American Seminar members
- 1943-07-19 · 2017.40.116a-d · C.K. Robinson spoke on 'Problems of the South'
- 1943-08-28 · 2017.40.122a-c · Community work report
- 1943-09-13 · 2017.40.123a-d · Faculty meeting
- 1943-09-13 · 2017.40.123a-d · Board of Fellows meeting
- 1943-09-13 · 2017.40.123a-d · Picnic and concert
- 1943-09-13 · 2017.40.123a-d · Paul Radin's return
- 1943-09-13 · 2017.40.123a-d · Fire loss report
- 1944-01-24 · 2017.40.127 · Editorial in the Asheville Times about the Southern Conference for Human Welfare
- 1944-01-28 · 2017.40.127 · Letter from Southern Conference for Human Welfare
- 1943-10-21 · 2017.40.129a-d · Student meeting in the Lobby of North Lodge
- 1943-10-07 · 2017.40.129a-d · Student decisions meeting
- 1943-11-03 · 2017.40.131a-c · North Carolina College Conference
- 1943-12-06 · 2017.40.136a-d · Faculty meeting
- 1944-01-11 · 2017.40.139a-b · Faculty meeting
- 1944-01-11 · 2017.40.139a-b · Community meeting
- 1944-01-12 · 2017.40.139a-b · Board of Fellows meeting
- 1944-01-13 · 2017.40.139a-b · Students' meeting
- 1944-01-17 · 2017.40.140a-c · Dillon Graham requests a performance at the Army Air Forces Redistribution Rest Camp.
- 1944-03-06 · 2017.40.146a-e · Interlude begins
- 1944-05-01 · 2017.40.155a-e · Construction and maintenance updates
- 1944-06-05 · 2017.40.157a-e · Construction Progress
- 1944-06-12 · 2017.40.158a-e · Resignation of Paul Radin
- 1944-07-01 · 2017.40.159a-e · Visit of Private Herbert Oppenheimer
- 1944-07-03 · 2017.40.159a-e · Completion of construction work on South Lodge
- 1944-07-22 · 2017.40.161a-d · Mrs. Freud to participate in the class work of the Art Institute.
- 1944-07-17 · 2017.40.161a-d · Faculty and Student Officers meeting decision.
- 1944-07-18 · 2017.40.161a-d · Board of Fellows meeting decision.
- 1944-07-27 · 2017.40.164a-e · Letter from Sergeant John M Stix
- 1944-08-11 · 2017.40.166.01a-e · Sergeant John Evarts writes from France.
- 1945-07-11 · 2017.40.303.01 · Art lecture by Dr Karl
- 1945-07-18 · 2017.40.304.01 · Illustrated lecture by Dr. Karl With
- 1945-07-28 · 2017.40.305.01 · Concert featuring works by J.S. Bach and J. Haydn
- 1945-08-15 · 2017.40.308.01 · First lecture by Robert Motherwell on 'Artist and Society'
- 1945-08-18 · 2017.40.308.01 · Concert featuring works by Hugo Kauder, Schubert, Ernest Bloch, and Mozart
- 1945-08-22 · 2017.40.309.01 · Lecture by Robert Motherwell
- 1941-07-26 · 2017.40.334 · End of the first session of Black Mountain College Work Camp
- 1946-07-01 · 2017.40.336 · School for American Craftsmen transferred to Alfred University
- 1945-07-01 · 2017.40.236.02 · Start of the Seminar on America for Foreign Scholars, Teachers and Artists
- 1945-08-12 · 2017.40.236.02 · End of the Seminar on America for Foreign Scholars, Teachers and Artists
- 1944-11-15 · 2017.40.171a-e · Theatrical Production of 'The Braggart Warrior'
- 1944-12-01 · 2017.40.171a-e · Mediaeval Mystery Plays
- 1944-10-02 · 2017.40.173a-c · Kenneth Kurtz's departure for Yale University.
- 1944-09-25 · 2017.40.173a-c · Letter from Gisela Kronenburg about her work in Chicago.
- 1944-09-16 · 2017.40.173a-c · Letter from Private Bob Marden about his work in England.
- 1944-09-20 · 2017.40.173a-c · Letter from Sergeant John M. Stix about the fall of Brest.
- … 57 autres dans le CSV

## Dates différentes (51)

- 2017.40.022 : Chronos May 29, 1943 « Death of Derek Bovingdon » / AAM 1943-04-11 « Memorial service for Lt Derek Bovingdon: the A Cappella group sings the Bach chorale "Es i » (retrouvé)
- 2017.40.052 : Chronos 1941-12-13 « Visit by Arthur Raper » / AAM 1941-12-14 « Arthur Raper, Southern sociologist, speaks to the College community (24-hour visit, arrive » (retrouvé)
- 2017.40.055 : Chronos 1942-01-25 « Dr Jalowetz travels to New York City » / AAM 1942-01-27 « Steuermann-Kolisch benefit concert at the home of Mrs Edward Norman (300 invitations); Yel » (retrouvé)
- 2017.40.070 : Chronos 1942-04-13 « Frances Kuntz won first prize in the costume plate contest and the highest award in the co » / AAM 1942-04-10 « The Highbrow Ladies judged best play of the 19th State Dramatic Festival; Frances Kuntz wi » (retrouvé)
- 2017.40.078 : Chronos 1942-10-10 « Bob Wunsch attends North Carolina Drama Directors’ Meeting » / AAM 1942-10-03 « Bob Wunsch at the North Carolina Drama Directors' Meeting » (retrouvé)
- 2017.40.079 : Chronos 1942-10-24 « John Evarts Farewell Concert » / AAM 1942-10-17 « Concert: Mozart Sonata in G major (Gretel and Edward Lowinsky); Rondo from the Haffner Ser » (retrouvé)
- 2017.40.081 : Chronos 1942-10 « Visit of Elmer Hall and Frances Benn Hall » / AAM 1942-11-02 « Arrivée d'Elmer Hall et de sa femme Frances Benn Hall pour quelques jours » (retrouvé)
- 2017.40.087a-c : Chronos 1942-12-31 « Appointment of Eric Bentley and Herbert Adolphus Miller to the faculty. » / AAM 1943-01-08 « Arrivée de Herbert A. Miller, qui enseignera deux cours au trimestre d'hiver (dont The Beg » (retrouvé)
- 2017.40.094.01a-b : Chronos 1943-03-13 « Concert of trios » / AAM 1943-02-27 « Concert with two compositions by Frederic Cohen: dance comedy Drums in Hackensack (Lowinsk » (retrouvé)
- 2017.40.096 : Chronos 1943-03-05 « Lecture by Frederick H Koch » / AAM 1943-03-06 « Actors of Ethan Frome give two scenes of Act III at the Drama Festival (Bob Wunsch chairma » (retrouvé)
- 2017.40.099 : Chronos 1943-03 « Bill McCleery's potential visit » / AAM 1943-05-03 « Bill McCleery (PM's Picture News) arrives for a week at Lake Eden » (retrouvé)
- 2017.40.102a-e : Chronos 1943-04-26 « Francis Foster's induction » / AAM 1943-04-21 « Francis Foster quitte Black Mountain pour son incorporation à Fort Snelling (Saint Paul, M » (retrouvé)
- 2017.40.120a-e : Chronos 1943-08-23 « Concert by Mrs Henry Leonard and Miss Radiana Pazmore » / AAM 1943-08-26 « Concert of duets by Bach, Mendelssohn, Schumann and Brahms: Mrs Henry Leonard (Lotte Leona » (retrouvé)
- 2017.40.122a-c : Chronos 1943-09-04 « Destruction by fire of the Service Building » / AAM 1943-08-30 « Incendie : le Service Building est détruit (étage effondré dans le rez-de-chaussée, arrièr » (indice faible)
- 2017.40.123a-d : Chronos 1943-09-13 « Appointment of Clark Foreman » / AAM 1943-10-01 « Arrivée de Clark Foreman, nommé enseignant, et de sa famille (appartement du Meadows Inn) » (retrouvé)
- 2017.40.124a-e : Chronos 1943-09-27 « Mathematics placement test for new students » / AAM 1943-09-28 « Old and new students visit classes; new students take a mathematics placement test in the  » (retrouvé)
- 2017.40.127 : Chronos 1944-01-30 « Concert by students and teachers » / AAM 1944-01-29 « Concert des étudiants et des enseignants : Vivaldi, double concerto en ré mineur (Trudi St » (retrouvé)
- 2017.40.133a-g : Chronos 1943-11-01 « Dr. F. J. Hansgirg announced a proposed gift to the College involving a process for extrac » / AAM 1943-11-11 « Le Dr F. J. Hansgirg annonce au Board of Fellows un projet de don : une petite compagnie p » (retrouvé)
- 2017.40.133a-g : Chronos 1943-11-16 « Bob Wunsch to attend a meeting of the Executive Committee of the North Carolina College Co » / AAM 1943-11-15 « Bob Wunsch leaves for Raleigh: open meeting of the North Carolina College Conference commi » (retrouvé)
- 2017.40.136a-d : Chronos 1943-12-06 « Board of Fellows meeting to discuss 1944 Summer Institutes » / AAM 1943-12-07 « Board of Fellows: plans for the 1944 Summer Institutes » (retrouvé)
- 2017.40.136a-d : Chronos 1943-12-06 « Josef Albers discussion on 'The Picture of the Month' » / AAM 1943-12-09 « Discussion on "The Picture of the Month" (Seeing Art) » (retrouvé)
- 2017.40.138a-g : Chronos 1943-12-24 « Death of Roman Maciejczyk in a bomber crash. » / AAM 1943-12-02 « Funérailles de Roman Maciejczyk, en présence d'un jeune pilote qui a accompagné le corps » (retrouvé)
- 2017.40.140a-c : Chronos 1944-01-17 « New students will visit classes and register for the Winter Quarter. » / AAM 1944-01-22 « New students register for the Winter Quarter after consulting their advisers » (retrouvé)
- 2017.40.149a-d : Chronos 1944-03-25 « Frederic Cohen's trip to NYC » / AAM 1944-04-01 « Frederic Cohen part pour New York voir des critiques et des rédacteurs au sujet du Summer  » (retrouvé)
- 2017.40.149a-d : Chronos 1944-03-27 « Record recital of Mozart’s opera 'Don Giovanni' » / AAM 1944-04-01 « Record recital of Mozart's Don Giovanni with drawings following the action; introduction a » (retrouvé)
- 2017.40.150a-g : Chronos 1944-04-29 « Performance of 'More Straw for the Scarecrow' » / AAM 1944-04-03 « Rehearsals begin for Betty Kelley's three-act fairy play More Straw for the Scarecrow (Car » (retrouvé)
- 2017.40.153a-d : Chronos 1944-05-09 « Second performance of the fairy play » / AAM 1944-04-29 « More Straw for the Scarecrow, first performance, Asheville Children's Theatre (music Barba » (retrouvé)
- 2017.40.157a-e : Chronos 1944-06-05 « Community Clean-Up Day » / AAM 1944-06-01 « Student elections: Mary Brett, Sam Brown and Ruth Miller elected Student Officers » (retrouvé)
- 2017.40.158a-e : Chronos 1944-06-10 « Report on Music and Art Institutes » / AAM 1944-07-08 « Series of ten Saturday evenings of chamber music from Bach to Schoenberg: Institute Quarte » (retrouvé)
- 2017.40.158a-e : Chronos 1944-06-12 « Departure of Josef Albers » / AAM 1944-06-14 « Josef Albers part pour Groton (Lowthorpe School) ; retour à Lake Eden le 16 juillet pour d » (retrouvé)
- 2017.40.166.01a-e : Chronos 1944-08-13 « Gwendolyn Currier resigns as student moderator. » / AAM 1944-08-16 « Student election: Charles Forberg elected moderator (succeeding Gwendolyn Currier); Marily » (retrouvé)
- 2017.40.167a-c : Chronos 1944-08-31 « Lecture by JB Neumann on 'From Rembrandt to Klee' » / AAM 1944-09-07 « "The Evolution of Modern Art" (3rd lecture), slides; afterwards a dance given by a company » (retrouvé)
- 2017.40.279 : Chronos 1943-11-07 « Performance of Paul Green's 'Quare Medicine' » / AAM 1942-11-07 « Paul Green, Quare Medicine (one-act comedy); scenery Bruno Piscitelli, Otis Levy, Bill Ber » (retrouvé)
- 2017.40.290 : Chronos 1942-10-24 « Farewell concert of music by John Evarts » / AAM 1942-10-17 « Concert: Mozart Sonata in G major (Gretel and Edward Lowinsky); Rondo from the Haffner Ser » (retrouvé)
- 2017.40.290 : Chronos 1942-10-31 « Program of piano music » / AAM 1942-10-17 « Concert: Mozart Sonata in G major (Gretel and Edward Lowinsky); Rondo from the Haffner Ser » (retrouvé)
- 2017.40.310.01 : Chronos 1945-08-24 « Concert by The Gordon String Quartet » / AAM 1945-08-21 « Gordon String Quartet (1): Haydn op. 33 no. 2, Piston Quartet no. 2, Beethoven op. 59 no.  » (retrouvé)
- 2017.40.311 : Chronos 1945-06-05 « Black Mountain College Music Institute Concert » / AAM 1945-07-05 « Music Institute concert: Italian songs — Caldara, Marcello, Carissimi, Handel… » (retrouvé)
- 2017.40.322 : Chronos March 22, 1946 « Spring concert featuring performances of classical music pieces. » / AAM 1947-03-22 « Spring concert: Hindemith Viola Sonata (Gretel and Edward Lowinsky); Hugo Wolf; Mark Fax,  » (retrouvé)
- 2017.40.171a-e : Chronos 1944-09-25 « Arrival of Alfred Kazin » / AAM 1944-09-22 « Alfred Kazin, nouveau visiting lecturer de littérature anglaise et américaine, arrive à La » (retrouvé)
- 2017.40.171a-e : Chronos 1944-09-25 « Sabbatical Leave for Erwin Straus » / AAM 1944-09-28 « Erwin Straus, en congé sabbatique accordé par le Board of Fellows, part pour Baltimore : F » (retrouvé)
- 2017.40.171a-e : Chronos 1944-09-25 « Sabbatical Leave for Kenneth Kurtz » / AAM 1944-09-18 « Programme de travail : derniers chargements d'ensilage le lundi, ensileuse rendue à l'orph » (retrouvé)
- 2017.40.175a-d : Chronos 1944-12-02 « Performance of 'An Almost Lonely Christmas' » / AAM 1944-10-19 « Rehearsals begin for Betty Kelley's three-act children's play An Almost Lonely Christmas ( » (retrouvé)
- 2017.40.180a-d : Chronos 1944-12-02 « Children's play 'An Almost Lonely Christmas' » / AAM 1944-11-19 « Dance rehearsals begin for the children's play An Almost Lonely Christmas (music written b » (retrouvé)
- 2017.40.188a-c : Chronos 1945-02-05 « Visit by Mr and Mrs Milton Rose » / AAM 1945-01-29 « Mr et Mrs Milton Rose (Winston-Salem), avocat de la Whitney Foundation, arrivent ; départ  » (retrouvé)
- 2017.40.191a-c : Chronos 1945-02-26 « Visit of Frederic Cohen » / AAM 1945-02-19 « Autres visiteurs de la semaine : Frederic Cohen (second institut d'été, avec la Music Inst » (retrouvé)
- 2017.40.191a-c : Chronos 1945-02-26 « Visit of Mary Gregory » / AAM 1945-02-21 « Mrs Mary Gregory, mère de Molly, arrive du Tennessee ; départ le jeudi pour Wenham (Massac » (retrouvé)
- 2017.40.191a-c : Chronos 1945-02-26 « Visit of Kenneth Kurtz » / AAM 1945-02-22 « Kenneth Kurtz arrive ; il part mardi pour Yale reprendre ses études de littérature » (retrouvé)
- 2017.40.197a-c : Chronos 1945-04-04 « Betty Kelley oral exam » / AAM 1945-04-11 « Betty Kelley's oral examinations for graduation in dramatics under Samuel Selden » (retrouvé)
- 2017.40.197a-c : Chronos 1945-04-07 « Performance of Tennessee Williams' 'Landscape with Figures' » / AAM 1945-04-14 « Les étudiants jouent « Landscape with Figures » de Tennessee Williams au festival » (retrouvé)
- 2017.40.208a-f : Chronos 1945-07-08 « The new music practice room was formally opened. » / AAM 1945-07-09 « Opening of the new music practice room: Edward Lowinsky and Josef Albers speak; Carol Bric » (retrouvé)
- 2017.40.213a-d : Chronos 1945-11-04 « Annual Meeting of the Faculty and election of Board of Fellows members. » / AAM 1945-11-02 « Advisory Council session with faculty, student officers and students, Theodore Dreier pres » (retrouvé)

## Documents hors du corpus AAM (52)

- 2017.40.001.01 · Black Mountain College Logo & Statement
- 2017.40.001.02 · Black Mountain College Logo & Statement
- 2017.40.003 · Black Mountain College Photo Booklet, 1938-1939
- 2017.40.031.01 · Black Mountain College Bulletin: Two Addresses by Ernst Krenek given at Summer Music Institute 1944, "Arnold Schoenberg 
- 2017.40.032 · Black Mountain College Bulletin: Arnold Schoenberg at Seventy by Ernst Krenek (Vol. 3, No. 1, November 1944)
- 2017.40.033 · Black Mountain College Bulletin: The Composer and the Interpreter by Ernst Krenek (Vol. 3, No. 2, December 1944)
- 2017.40.046 · Black Mountain College Bulletin: "Physics for Liberal Arts Students by Natasha Goldowski" (Vol. 7, No. 3, May 1949)
- 2017.40.220 · 1934 Audit "In the matter of Black Mountain College"
- 2017.40.221 · 1935 Audit "In the matter of Black Mountain College"
- 2017.40.222 · 1936 Audit "In the matter of Black Mountain College"
- 2017.40.223 · 1937 Audit "In the matter of Black Mountain College"
- 2017.40.224 · 1938 Audit "In the matter of Black Mountain College"
- 2017.40.225 · 1939 Audit "In the matter of Black Mountain College" November 16, 1939
- 2017.40.226 · 1940 Audit "In the matter of Black Mountain College"
- 2017.40.227 · 1941 Audit "In the matter of Black Mountain College"
- 2017.40.228 · 1942 Audit "In the matter of Black Mountain College"
- 2017.40.229 · 1943 Audit "In the matter of Black Mountain College"
- 2017.40.230 · Audit 1944 "In the matter of Black Mountain College"
- 2017.40.231.01 · 1945 Audit "In the matter of Black Mountain College"
- 2017.40.232 · 1946 Audit "In the matter of Black Mountain College"
- 2017.40.233 · 1947 Audit "In the matter of Black Mountain College"
- 2017.40.234 · 1948 Audit "In the matter of Black Mountain College"
- 2017.40.235 · Black Mountain College Bulletin 6: The Building Project and Work Program
- 2017.40.240 · "Concerning Art Instruction" in Black Mountain College Bulletin 2
- 2017.40.241 · "On the Civilization of the Two Americas" Black Mountain College Bulletin 4
- 2017.40.242 · "Work with Material" Black Mountain College Bulletin 5
- 2017.40.244 · Black Mountain College...AND BEYOND THE DURATION
- 2017.40.246a-i · Exhibit of the Evolution of Housing Plans of Black Mountain College
- 2017.40.248 · Subject: Cheers, Directions: To be yelled at top of lungs!
- 2017.40.249 · Black Mountain College Bulletin Vol. 1, No. 1, November 1942: Black Mountain College Offers 17 Wartime Scholarships
- 2017.40.250 · Invitation to Exhibition of Drama Design at Dalton School by the Students of Black Mountain College
- 2017.40.251 · Black Mountain College Constitution
- 2017.40.265 · New Studies Building
- 2017.40.301 · Palmer Memorial Institute presents A Musical Event of Unusual Interest Annual Spring Festival of Music
- 2017.40.331 · LAKE EDEN INN and COTTAGES 1939 SEASON-- FROM JUNE 5 to SEMPTEMBER 9
- 2017.40.332.02 · building project
- 2017.40.337 · Admission card Eduard Steuermann and Rudolf Kolisch Benefit for Black Mountain College
- 2017.40.338 · Invitation from the Black Mountain Association to meet Dr. Walter Gropius, Mr. Josef Albers, Dr. Erwin W. Straus, and Mr
- 2017.40.339 · “THESE ARTISTS HAVE CHOSEN TO TEACH AT BLACK MOUNTAIN COLLEGE”
- 2017.40.341 · Anni Albers, Alex Reed: Exhibition of necklaces, Willard Gallery May 5-May 24, 32 East 57 New York
- 2017.40.342 · The Black Mountain College Review June 1951 Vol.1 No.1
- 2017.40.344 · Converting the Impossible into the actual has always been an American tradition
- 2017.40.345 · Rollins College Report [Reprinted from the Bulletin of the American Association of University Professors, Vol. XIX, No. 
- 2017.40.350 · 'Josef Albers' at New Art Circle, J.B. Neumann Director 509 Madison Ave. N.Y. Mar. 9-30 Weekdays 10-5
- 2017.40.351 · "Josef Albers" by Ray Nash, Reprinted from PRINT, Vol. III, No. 4, Woodstock, Vermont
- 2017.40.353 · "Handweaving Today: Textile Work at Black Mountain College"
- 2017.40.354 · Black Mountain College Bulletin 2: Concerning Art Insrtuction
- 2017.40.358 · BLACK MOUNTAIN COLLEGE’“The Idea of Black Mountain College”
- 2017.40.363a-c · "The College That Built Itself: Black Mountain Points its program to the future" (Magazine excerpt)
- 2017.40.364.01 · Art As a Fourth "R": A New American College is Combatting the Idea that Only Painters Can Paint
- 2017.40.364.02 · Art As a Fourth "R": A New American College is Combatting the Idea that Only Painters Can Paint
- 2017.40.364.03 · Art As a Fourth "R": A New American College is Combatting the Idea that Only Painters Can Paint

## Couche du semainier

Couche « Chronos » du semainier : 215 entrées (`001_asheville_couche.csv`).
