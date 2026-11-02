// Langue de la page (FR / EN) : ?lang=en dans l'adresse, sinon le dernier choix, sinon le français.
// Contenu : dictionnaire de l'interface, noms des collections, règles de traduction des formules du barème et des
// activités reconstituées (traductions relues). Les titres et notes rédigés en français sont dans data_en.js
// (scripts/traduire_en.py : relus d'abord, sinon traduction automatique signalée).
(function () {
  let lang = new URLSearchParams(location.search).get("lang");
  try { if (!lang) lang = localStorage.getItem("bmc-lang"); if (lang) localStorage.setItem("bmc-lang", lang); } catch (e) {}
  window.LANG = lang === "en" ? "en" : "fr";
  window.LOC = window.LANG === "en" ? "en-US" : "fr-FR";
  if (window.LANG === "en") document.write('<script src="data_en.js"><\/script>');
})();

const UI_EN = {
  // en-tête
  "Semainier · Black Mountain College": "Weekly calendar · Black Mountain College",
  "d'après les fiches de l'Asheville Art Museum": "from the Asheville Art Museum records and other sources",
  "Semaine": "Week", "Grille": "Grid", "Présences": "Presence", "Liste": "List", "Mois": "Month",
  "Repères…": "Landmarks…", "Personne, cours, lieu…": "Person, course, place…", "déduction ≤": "deduced ≤",
  "Filtres : types d'activité, recherche, part déduite": "Filters: activity types, search, deduced share",
  "Retrouvées seulement": "Found in source only", "Duberman (1972)": "Duberman (1972)",
  "Témoignages, Silver, compléments": "Testimonies, Silver, supplements", "Autres livres et études (52)": "Other books and studies (52)",
  "Reconstitution (emploi du temps)": "Reconstruction (timetable)",
  " · version publique : références sans extraits": " · public version: references without excerpts",
  "Cours, ateliers": "Courses, workshops", "Réunions": "Meetings", "Concerts, théâtre, danse": "Concerts, theater, dance",
  "Conférences, radio": "Lectures, radio", "Vie de la communauté": "Community life", "Calendrier, examens": "Calendar, exams",
  // vue Semaine
  "◀ semaine": "◀ week", "semaine ▶": "week ▶", "hors période de cours attestée": "outside any attested term",
  "Contexte de la semaine": "Week context", "barres : faits attestés de la semaine · fond gris : semaine reconstituée · trait rouge : semaine affichée":
    "bars: attested facts of the week · grey: reconstructed week · red line: week shown",
  "tout": "all", "rien": "none", "sources relues seulement": "reviewed sources only",
  "documents du collège lus et relus, Duberman et Rumaker dépouillés": "college documents read and checked, Duberman and Rumaker fully indexed",
  "Datés au mois ou à la saison, sans jour précis": "Dated to the month or season, no exact day",
  "Chaque jour ou chaque semaine": "Every day or every week", "(récurrence attestée par un document)": "(recurrence attested by a document)",
  "Toute la semaine": "All week", "attesté": "attested", "attestés": "attested", "reconst.": "reconstr.",
  "cours reconstitués": "reconstructed courses", "cours attestés": "attested courses", "moy.": "avg.",
  "Lire les marques et la reconstitution": "How to read the marks and the reconstruction",
  "Autres livres et études cette semaine": "Other books and studies this week", "choisir": "choose", "titre": "title", "titres": "titles",
  "Analyse": "Analysis", "et barème": "and scoring",
  // fiche
  "fermer": "close", "Collection": "Collection", "Qui": "Who", "Lieu": "Place", "Note": "Note", "Part déduite": "Deduced share",
  "Récurrence": "Recurrence", "Affichage": "Display", "Couche": "Layer", "Cours du catalogue": "Catalog course",
  "Parts déduites": "Deduced shares", "Autres cours possibles": "Other possible courses", "Rattachement": "Attribution",
  "Année précédente": "Previous year", "Année suivante": "Following year", "Source": "Source", "Document source": "Source document",
  "Documents sources": "Source documents", "Notes de Duberman": "Duberman's notes", "Même jour (AAM)": "Same day (AAM)",
  "Autres versions": "Other versions", "Recoupement": "Cross-check", "Aussi dans les livres": "Also in books",
  "Aussi dans les livres (lecture automatique)": "Also in books (automatic reading)", "Inventaire": "Inventory", "Vue": "View",
  "Vérifier dans la source": "Check in the source", "ouvrir la fiche du musée": "open the museum record",
  "Original (français)": "Original (French)", "traduction automatique": "machine translation",
  "Version publique : la référence exacte est donnée ci-dessus ; les extraits des textes cités ne sont pas reproduits (droits des auteurs et des éditeurs).":
    "Public version: the exact reference is given above; excerpts of the cited texts are not reproduced (authors' and publishers' rights).",
  "retrouvé": "found", "indice faible": "weak clue", "à relire": "to be checked", "référence introuvable": "reference not found", "sans source": "no source",
  // panneau
  "Période": "Term", "État de la semaine (audit)": "State of the week (audit)", "Semaine reconstituée": "Reconstructed week",
  "Documents datés de ces jours": "Documents dated these days", "Autres sources des activités affichées": "Other sources of the activities shown",
  "Personnes": "People", "Lire la biographie sur bmcyearbook.org": "Read the biography on bmcyearbook.org",
  "Arrivées et départs cette semaine selon le BMC Yearbook": "Arrivals and departures this week according to the BMC Yearbook",
  "afficher": "show", "notice en ligne": "online entry", "notice": "entry",
  // types, statuts, vérification
  "cours": "course", "atelier": "workshop", "reunion": "meeting", "concert": "concert", "theatre": "theater", "danse": "dance", "conference": "lecture",
  "radio": "radio", "social": "social", "travail": "work", "expo": "exhibition", "visite": "visit", "sortie": "outing", "autre": "other", "calendrier": "calendar", "examen": "exam",
  "lettre": "letter", "proces_verbal": "minutes", "publication": "publication", "document": "document", "journal": "diary", "telegramme": "telegram",
  "les témoins de l'entrée (noms, mots du titre, date) sont réunis dans un même passage du texte cité": "the entry's clues (names, title words, date) are found together in one passage of the cited text",
  "un nom ou quelques mots seulement : à relire dans la source": "only a name or a few words: check in the source",
  "le texte cité est ouvert mais rien n'y est retrouvé automatiquement (traduction, paraphrase, OCR) : à relire": "the cited text is open but nothing is found automatically (translation, paraphrase, OCR): to be checked",
  "la référence citée n'existe pas dans les textes du dépôt": "the cited reference is not among the texts of the repository", "aucune source indiquée": "no source given",
  "Extrait du texte cité": "Excerpt of the cited text", "texte de la source": "text of the source", "Duberman, texte corrigé": "Duberman, corrected text",
  "livre, page citée": "book, cited page", "document cité par le gabarit": "document cited by the template", "OCR de la fiche du musée": "OCR of the museum record",
  "surligné : ce qui a été retrouvé.": "highlighted: what was found.", "source primaire citée": "primary source cited",
  "dépouillement manuel du texte corrigé": "manual indexing of the corrected text", "extraction automatique de décembre 2025, à relire": "automatic extraction of December 2025, to be checked",
  "phrase datée tirée automatiquement des textes des PDF (novembre 2026), à relire": "dated sentence drawn automatically from the PDF texts (November 2026), to be checked",
  "date dans la source": "date in the source", "confirmé (Duberman ou AAM)": "confirmed (Duberman or AAM)", "témoignage seul": "single testimony",
  "Années reconstituées (spéculatif)": "Reconstructed years (speculative)", "Semaines les plus documentées": "Best-documented weeks",
  "Débuts de trimestre et sessions": "Starts of terms and sessions", "semaines": "weeks", "activités": "activities",
  "Français / English": "Français / English", "◀ doc.": "◀ doc.", "doc. ▶": "doc. ▶",
  "Semaine documentée précédente": "Previous documented week", "Semaine documentée suivante": "Next documented week",
  "Part de déduction maximale affichée": "Maximum deduced share shown",
  "Les 7 jours de la semaine ; les options choisissent ce qui apparaît dans chaque jour": "The 7 days of the week; options choose what appears on each day",
  "Grille horaire (lisible surtout pour les semaines à horaire attesté)": "Hourly grid (most readable for weeks with an attested timetable)",
};
const t = s => (window.LANG === "en" && UI_EN[s] !== undefined) ? UI_EN[s] : s;

// noms des collections (même ordre que COLLECTIONS dans index.html) : [nom, nom court, description]
const COL_EN = {
  bulletins: ["Community bulletins", "Bulletin", "the college's weekly Community Bulletins, read and checked (AAM)"],
  catalogues: ["Catalogs and announcements", "Catalog", "annual catalogs, course and session announcements (AAM)"],
  newsletters: ["Newsletters", "Newsletter", "newsletters and bulletins sent to friends of the college (AAM)"],
  programmes: ["Concert and performance programs", "Program", "programs, posters and invitations (AAM)"],
  cours: ["Courses with attested schedule", "Course", "courses placed from a timetable or a dated bulletin (AAM)"],
  musee_auto: ["Museum records, automatic reading", "Museum (auto.)", "supplements drawn automatically from the 377 museum records, cross-checked with the reviewed reading"],
  harris: ["Mary Emma Harris interviews", "Harris interview", "165 interviews of the Black Mountain College Project: facts drawn automatically, checked against the transcripts"],
  rumaker: ["Rumaker, Black Mountain Days (2003)", "Rumaker", "a student's memoir (1952-1956), fully indexed and checked"],
  duberman: ["Duberman, Black Mountain (1972)", "Duberman", "Martin Duberman's history of the college, fully indexed and checked (935 facts)"],
  duberman_auto: ["Duberman (1972), automatic reading", "Duberman (auto.)", "supplements from an earlier automatic reading of the book, cross-checked"],
  silver: ["Silver, The Farm at Black Mountain College (2024)", "Silver (farm)", "history of the college farm, automatic reading cross-checked"],
  livres: ["Other books and studies", "", "automatic, unreviewed reading of 52 books (biographies, exhibition catalogs, studies); choose title by title"],
  spec_cours: ["Reconstructed timetable", "Reconstructed", "term courses placed from catalogs, bulletins, course lists, student records and testimonies"],
  spec_vie: ["Reconstructed community life", "Reconstructed", "meals, work, meetings and evenings of the term template"],
};
const GROUPES_EN = { "Documents du collège (Asheville Art Museum)": "College documents (Asheville Art Museum)", "Témoignages": "Testimonies",
  "Histoires et études": "Histories and studies", "Reconstitution (analyse croisée des documents)": "Reconstruction (cross-analysis of documents)",
  "Précision de la date": "Date precision" };

// formules du barème et précisions des activités reconstituées : règles (ordre = priorité)
const REGLES_EN = [
  [/^présence cette semaine-là déduite d'un rythme régulier \(hebdomadaire, quotidien, cours de toute l'année\)/, "presence that week deduced from a regular rhythm (weekly, daily, year-long course)"],
  [/^jour choisi par moi/, "day chosen by me"],
  [/^heure choisie par moi dans un créneau attesté \(matin, après-midi de cours, après le dîner, samedi soir\)/, "time chosen by me within an attested time slot (morning, afternoon classes, after dinner, Saturday evening)"],
  [/^heure choisie par moi sans source/, "time chosen by me without a source"],
  [/^cours ou activité attesté pour l'année même/, "course or activity attested for the same year"],
  [/^extraction automatique par modèle de langage, non relue/, "automatic extraction by a language model, unreviewed"],
  [/^extraction automatique \(Chronos, décembre 2025\), non relue/, "automatic extraction (December 2025), unreviewed"],
  [/^extraction automatique \(GPT-4o Vision sur le scan, décembre 2025\), non relue/, "automatic extraction (GPT-4o Vision on the scan, December 2025), unreviewed"],
  [/^extraction automatique \(Chronos 2\), citation retrouvée dans le texte corrigé de Duberman/, "automatic extraction, quotation found in the corrected text of Duberman"],
  [/^volume horaire supposé \(non donné pour ce cours\)/, "number of hours assumed (not given for this course)"],
  [/^enseignant nommé pour ce cours dans le catalogue de l'année/, "teacher named for this course in the year's catalog"],
  [/^structure \(heures, semestres\) ou usage pris dans une année voisine/, "structure (hours, terms) or practice taken from a neighboring year"],
  [/^enseignant rattaché par sa discipline et nommé pour ce cours \(ou son équivalent\) dans une année voisine/, "teacher attributed by subject and named for this course (or its equivalent) in a neighboring year"],
  [/^enseignant rattaché par sa discipline : seul enseignant de cette matière au catalogue/, "teacher attributed by subject: the only teacher of the subject in the catalog"],
  [/^enseignant rattaché par élimination entre collègues de la même discipline/, "teacher attributed by elimination among colleagues in the same subject"],
  [/^enseignant inconnu ou rattaché par simple compétence/, "teacher unknown or attributed by competence alone"],
  [/^enseignant rattaché d'après Duberman \(texte corrigé\), pas d'après un document de l'année/, "teacher attributed from Duberman (corrected text), not from a document of the year"],
  [/^enseignant ou rattachement déduit \(pas écrit dans ce document\)/, "teacher or attribution deduced (not written in this document)"],
  [/^témoignage direct \(souvenir publié, souvent tardif\)/, "direct testimony (published memory, often late)"],
  [/^témoignage : mémoires écrits près de cinquante ans après/, "testimony: memoir written nearly fifty years later"],
  [/^témoignage oral, recueilli (-?\d+) ans après/, "oral testimony, recorded $1 years later"],
  [/^témoignage oral$/, "oral testimony"],
  [/^séance projetée sur chaque date d'après un horaire que la source donne comme régulier/, "session projected on each date from a schedule the source gives as regular"],
  [/^séance projetée sur chaque date/, "session projected on each date"],
  [/^régularité déduite par moi/, "regularity deduced by me"],
  [/^titre : chance (\S+) que ce soit bien ce cours ce trimestre-là \(part du titre (\d+) %\)/, "title: a $1 chance that this is the course given that term (title share $2%)"],
  [/^liste de cours de l'année précédente : celle de l'année n'est pas lisible dans le corpus/, "course list of the previous year: the year's own list is not legible in the corpus"],
  [/^liste de cours donnée pour d'autres trimestres de l'année, reconduite pour celui-ci/, "course list given for other terms of the year, carried over to this one"],
  [/^transposé d'une période éloignée ou d'un autre campus/, "carried over from a distant period or another campus"],
  [/^cours suivi ce trimestre-là d'après les fiches d'étudiants \(BMC Yearbook, bmcyearbook\.org\)/, "course taken that term according to student records (BMC Yearbook, bmcyearbook.org)"],
  [/^attesté tel quel dans la source \(meilleure des sources fusionnées\)/, "attested as is in the source (best of the merged sources)"],
  [/^attesté tel quel dans la source/, "attested as is in the source"],
  [/^jour calculé à partir de la date du document \(« mardi », « hier »…\)/, "day computed from the document's date (\"Tuesday\", \"yesterday\"…)"],
  [/^jour calculé d'après une autre date du livre/, "day computed from another date in the book"],
  [/^date « ?(\w[\w ]*?) »? seulement/, (m, x) => `date to the ${({ annee: "year", mois: "month", saison: "season", session: "session", periode: "period", plage: "range", inconnue: "unknown", annee_scolaire: "school year", "annee scolaire": "school year", ete: "summer", "plage annees": "range of years" })[x.trim()] || x} only`],
  [/^date au (\w[\w ]*?) seulement/, (m, x) => `date to the ${({ annee: "year", mois: "month", saison: "season", "annee scolaire": "school year", "plage annees": "range of years" })[x.trim()] || x} only`],
  [/^date (\w+) seulement/, (m, x) => `date to the ${({ annee: "year", mois: "month", saison: "season", session: "session", periode: "period", inconnue: "unknown", ete: "summer" })[x] || x} only`],
  [/^date à la semaine/, "date to the week"], [/^date donnée telle quelle par Duberman/, "date given as is by Duberman"],
  [/^date approximative ou incomplète dans le livre/, "approximate or incomplete date in the book"],
  [/^date approximative ou incomplète dans la source/, "approximate or incomplete date in the source"],
  [/^date tirée du cadre du passage, pas du fait/, "date taken from the passage's context, not from the fact"],
  [/^date relative résolue sur une date du livre moins précise/, "relative date resolved on a less precise date of the book"],
  [/^date corrigée \(incohérence du livre\)/, "date corrected (inconsistency in the book)"],
  [/^date corrigée contre celle du musée ou du document/, "date corrected against the museum's or the document's"],
  [/^plage de (\d+) jours/, "range of $1 days"],
  [/^activité occasionnelle, mensuelle ou « à la demande » : rien ne dit qu'elle tombe cette semaine/, "occasional, monthly, or “on request” activity: nothing says it falls this week"],
  [/^élément supposé par moi \(heure, fin de période…\)/, "element assumed by me (hour, end of period…)"],
  [/^élément supposé \(date, durée ou participant\)/, "element assumed (date, duration or participant)"],
  [/^annoncé à l'avance : réalisation non attestée/, "announced in advance: actual event not attested"],
  [/^annoncé ou prévu, réalisation non attestée/, "announced or planned, actual event not attested"],
  [/^domaine annoncé à l'avance \(« fields represented will be… »\) : cours réel non attesté/, "field announced in advance (“fields represented will be…”): actual course not attested"],
  [/^récurrence ou période déduite/, "recurrence or period deduced"],
  [/^présence de l'enseignant pendant tout le trimestre non attestée/, "the teacher's presence throughout the term not attested"],
  [/^non retenu par l'audit manuel du même document : oubli, règle écartée ou date mal résolue — à relire/, "not kept by the manual audit of the same document: omission, rule set aside or date misread — to be checked"],
  [/^témoins non réunis dans les pages citées : indice faible/, "clues not found together in the cited pages: weak clue"],
  [/^témoins non réunis dans les pages citées : à relire/, "clues not found together in the cited pages: to be checked"],
  [/^témoins non réunis dans le texte du document : indice faible/, "clues not found together in the document's text: weak clue"],
  [/^témoins non réunis dans le texte du document : à relire/, "clues not found together in the document's text: to be checked"],
  [/^équivalence de titre avec une année voisine probable mais non certaine/, "title equivalence with a neighboring year probable but not certain"],
  [/^ouï-dire/, "hearsay"], [/^confiance « medium » selon l'extraction/, "\"medium\" confidence according to the extraction"],
  [/^fait contesté entre les sources/, "fact disputed between sources"], [/^interprétation de l'auteur du livre/, "interpretation by the book's author"],
  [/^hypothèse de l'auteur/, "author's hypothesis"], [/^lecture corrigée d'une coquille de la source/, "reading corrected for a typo in the source"],
  [/^le catalogue 1936-38 le dit offert « last year » \(1935-36\)/, "the 1936-38 catalog says it was offered “last year” (1935-36)"],
  [/^statut : annonce reportée\/annulée\/remplacée selon une source \(voir note\)/, "status: announcement postponed/cancelled/replaced according to a source (see note)"],
  [/^citation introuvable dans la transcription/, "quotation not found in the transcript"], [/^citation en partie dans la transcription/, "quotation partly in the transcript"],
  [/^citation vide dans la transcription/, "empty quotation in the transcript"], [/^« day » au 1er janvier traité comme une année/, "\"day\" on 1 January treated as a year"],
  [/^étude publiée après coup \(source secondaire\)/, "study published later (secondary source)"],
  [/^témoignage écrit après coup \(mémoires, souvenirs\)/, "testimony written later (memoirs)"],
  [/^fait tiré automatiquement de la phrase, non relu/, "fact drawn automatically from the sentence, unreviewed"],
  [/^date « (\w+) » seulement/, "date to the $1 only"],
  [/^(\d{4}-\d{2}), (automne|hiver|printemps|été|période)(.*)$/, (m, a, x, r) => `${a}, ${({ automne: "fall", hiver: "winter", printemps: "spring", "été": "summer", "période": "period" })[x]}${r}`],
  // affichage
  [/^aucune heure dans la source : affiché en journée entière/, "no time in the source: shown as all-day"],
  [/^fin non attestée : durée d'1 h affichée par défaut/, "end not attested: 1-hour duration shown by default"],
  [/^reconstitution : jour et heure proposés \(voir la part déduite\)/, "reconstruction: day and hour proposed (see the deduced share)"],
  [/^« (soir|après-midi|matin) » dans la source : placé (.+) à titre indicatif/, (m, a, b) => `"${({ soir: "evening", "après-midi": "afternoon", matin: "morning" })[a]}" in the source: placed ${b} as an indication`],
  [/^plage de dates dans le livre : affiché du (\S+) au (\S+)/, "date range in the book: shown from $1 to $2"],
  [/^date « ([\w_]+) »(?: dans le scénario)? : listé dans le panneau, pas dans la grille/, (m, x) => `date to the ${({ annee: "year", mois: "month", saison: "season", session: "session", periode: "period", plage: "range", inconnue: "unknown", annee_scolaire: "school year", semaine: "week", ete: "summer" })[x] || x}: listed in the panel, not in the grid`],
  [/^date (?:au |à la |à l'|sur une |sur )?(mois|saison|année scolaire|année|plage de dates|plusieurs années) dans le livre : listé dans le panneau, pas dans la grille/, (m, x) => `date to the ${({ mois: "month", saison: "season", "année": "year", "année scolaire": "school year", "plage de dates": "date range", "plusieurs années": "several years" })[x]} in the book: listed in the panel, not in the grid`],
  [/^date « ([\w_]+) » : listé dans le panneau, pas dans la grille/, "date to the $1: listed in the panel, not in the grid"],
  // activités reconstituées : semaines, précisions
  [/^Semaine de cours, (\d{4}-\d{2}), (automne|hiver|printemps|été)(?: \(([\d\/]+) – ([\d\/]+)\))? \((.+)\)$/, (m, a, s, d1, d2, c) =>
    `Teaching week, ${a}, ${({ automne: "fall", hiver: "winter", printemps: "spring", "été": "summer" })[s]}${d1 ? ` (${d1} – ${d2})` : ""} (${trCal(c)})`],
  [/^Semaine de la Summer Session (\d{4})$/, "Summer Session $1 week"],
  [/^(.+?) — leçons individuelles$/, "$1 — individual lessons"], [/^(.+?) — débutants$/, "$1 — beginners"], [/^(.+?) — avancé$/, "$1 — advanced"],
  [/^(.+?) — pour les nouveaux venus$/, "$1 — for newcomers"], [/^(.+?) — pour toute la communauté$/, "$1 — for the whole community"],
  [/^(.+?) — répétitions et productions$/, "$1 — rehearsals and productions"],
  [/^(.+?) — atelier ; enseignant à nommer — laboratoire$/, "$1 — workshop; teacher to be named — laboratory"],
  [/^(.+?) — atelier ; domaine de l'été 1954 — laboratoire$/, "$1 — workshop; field of summer 1954 — laboratory"],
  [/^(.+?) — laboratoire$/, "$1 — laboratory"], [/^(.+?) — séjours de deux semaines$/, "$1 — two-week stays"],
  [/^(.+?) — réunies? comme en 1936-38$/, "$1 — combined as in 1936-38"], [/^(.+?) — réunis en un cours comme en 1936-38$/, "$1 — combined into one course as in 1936-38"],
  [/^(.+?) — un seul cours,? (?:comme )?en 1936-38$/, "$1 — a single course in 1936-38"],
  [/^(.+?) : possible cette semaine(?: \(environ une chance sur quatre\))?$/, (m, x) => `${trAct(x)}: possible this week`],
  [/^(.+?) : possible$/, (m, x) => `${trAct(x)}: possible`],
];
const CAL_EN = [[/^calendrier du premier catalogue$/, "calendar of the first catalog"], [/^calendrier spéculatif : dates de 1933-34 transposées$/, "speculative calendar: 1933-34 dates transposed"],
  [/^calendrier imprimé dans les catalogues (.+)$/, "calendar printed in the $1 catalogs"], [/^calendrier du catalogue (.+)$/, "calendar of the $1 catalog"],
  [/^calendrier annoncé dans le catalogue (.+)$/, "calendar announced in the $1 catalog"], [/^calendrier du Bulletin (.+)$/, "calendar of the $1 Bulletin"],
  [/^calendrier de (.+)$/, "calendar of $1"], [/^calendrier imprimé en (.+)$/, "calendar printed in $1"],
  [/^calendrier des trimestres (.+) : annonces et bulletins$/, "term calendar $1: announcements and bulletins"],
  [/^calendrier révisé de 1941-42 : lettres d'octobre 1941 et bulletins de 1942$/, "revised 1941-42 calendar: October 1941 letters and 1942 bulletins"],
  [/^trimestres de onze semaines, (.+)$/, "eleven-week quarters, $1"]];
const MOIS_FR_EN = { "janvier": "January", "février": "February", "mars": "March", "avril": "April", "mai": "May", "juin": "June", "juillet": "July", "août": "August", "septembre": "September", "octobre": "October", "novembre": "November", "décembre": "December" };
function trCal(c) { for (const [r, v] of CAL_EN) if (r.test(c)) return c.replace(r, v).replace(/\b(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\b/g, m => MOIS_FR_EN[m]).replace(/ ; vacances de Noël supposées/, "; Christmas holidays assumed"); return c; }
// activités reconstituées les plus courantes (traductions relues)
const ACT_EN = {
  "Déjeuner en commun": "Communal lunch", "Dîner en commun": "Communal dinner", "Petit déjeuner en commun": "Communal breakfast",
  "Dîner du dimanche": "Sunday dinner", "Petit déjeuner du dimanche": "Sunday breakfast", "Souper du dimanche": "Sunday supper",
  "Souper froid du dimanche": "Cold Sunday supper", "Petit déjeuner en commun (servi par des volontaires)": "Communal breakfast (served by volunteers)",
  "Petit déjeuner en commun (service assuré à tour de rôle par les membres du collège)": "Communal breakfast (served in turn by college members)",
  "Petit déjeuner du dimanche (plus tard qu'en semaine)": "Sunday breakfast (later than on weekdays)", "Dîner du dimanche à 13 h": "Sunday dinner at 1 p.m.",
  "Répétition de la pièce en cours": "Rehearsal of the current play", "Répétition de la pièce en cours (pièce non identifiée)": "Rehearsal of the current play (play not identified)",
  "Demi-heure de danse après le dîner": "Half-hour of dancing after dinner", "Demi-heure de danse informelle après le dîner": "Half-hour of informal dancing after dinner",
  "Au-dehors : jeux, coupe du bois, routes, marche sur les sentiers de la montagne, piscine, tennis": "Outdoors: games, wood-cutting, roads, mountain trail walks, swimming pool, tennis",
  "Au-dehors : tennis, terrain de sport, gymnase, piscine, ferme, coupe du bois pour les cheminées, réparation des routes": "Outdoors: tennis, playing field, gym, swimming pool, farm, cutting wood for the fireplaces, road repair",
  "Programme de travail : ferme surtout, construction, entretien, réparations (équipes)": "Work program: mostly farm, construction, maintenance, repairs (crews)",
  "Concert du samedi soir": "Saturday evening concert", "Réunion générale de toute la communauté": "General meeting of the whole community",
  "Causerie d'un visiteur": "Talk by a visitor", "Chantier du Studies Building et des logements de Lake Eden (équipes de volontaires)": "Building site of the Studies Building and Lake Eden housing (volunteer crews)",
  "Autres travaux de l'après-midi : ferme, bois, bibliothèque, imprimerie, scène ; plein air": "Other afternoon work: farm, wood, library, print shop, stage; outdoors",
  "Programme de travail (ferme, entretien, construction)": "Work program (farm, maintenance, construction)",
  "Plein air : tennis, gymnase, terrain de sport, coupe du bois pour les cheminées, ferme, réparation des routes": "Outdoors: tennis, gym, playing field, cutting wood for the fireplaces, farm, road repair",
  "Au-dehors jusqu'à la reprise des cours à 16 h : sports, ferme, coupe du bois, routes (équipes de volontaires)": "Outdoors until classes resume at 4 p.m.: sports, farm, wood-cutting, roads (volunteer crews)",
  "Travail et plein air jusqu'à 16 h : bibliothèque, reliure, imprimerie, ferme, routes, travaux à Lake Eden": "Work and outdoors until 4 p.m.: library, bookbinding, print shop, farm, roads, work at Lake Eden",
  "Travail et plein air jusqu'à la reprise des cours à 16 h : bibliothèque, reliure, imprimerie, ferme, coupe du bois, routes, aménagement de Lake Eden": "Work and outdoors until classes resume at 4 p.m.: library, bookbinding, print shop, farm, wood-cutting, roads, Lake Eden improvements",
  "Work Camp et programme de travail d'été : construction, ferme, réparations, aménagements (étudiants de la Summer School et campeurs)": "Work Camp and summer work program: construction, farm, repairs, improvements (Summer School students and campers)",
  "Community Work Program (ferme, bois, ménage, chaudières, transport)": "Community Work Program (farm, wood, housekeeping, furnaces, transport)",
  "Community Work Program (ferme, bois, chaudières, ménage, transport)": "Community Work Program (farm, wood, furnaces, housekeeping, transport)",
  "Community Work Program : ferme, bois, mica, charbon, construction (équipes)": "Community Work Program: farm, wood, mica, coal, construction (crews)",
  "Programme de travail (ferme, bois, construction des logements fédéraux, ménage)": "Work program (farm, wood, building of the federal housing, housekeeping)",
  "Programme de travail : un après-midi de travail, 8 à 12 heures par semaine (jour non donné)": "Work program: one afternoon of work, 8 to 12 hours a week (day not given)",
  "Thé": "Tea", "Résumé et commentaire des nouvelles de la semaine": "Summary and commentary of the week's news",
  "Bal semi-habillé du samedi soir": "Saturday evening semiformal dance", "Bal semi-habillé du samedi soir, après le concert ou le programme": "Saturday evening semiformal dance, after the concert or program",
  "Bal du samedi soir": "Saturday evening dance", "Danse après le concert": "Dancing after the concert",
  "Réunion de la faculté": "Faculty meeting", "Réunion hebdomadaire de la faculté": "Weekly faculty meeting",
  "Réunion de la faculté (avec les officiers étudiants une semaine sur deux)": "Faculty meeting (with the student officers every other week)",
  "Réunion de la faculté et des officiers étudiants": "Meeting of the faculty and student officers", "Réunion hebdomadaire des étudiants": "Weekly student meeting",
  "Réunion hebdomadaire du Board of Fellows avec le comité des trois officiers étudiants": "Weekly Board of Fellows meeting with the committee of the three student officers",
  "Réunion hebdomadaire du Board of Fellows avec les autres officiers étudiants": "Weekly Board of Fellows meeting with the other student officers",
  "Réunion hebdomadaire du Board of Fellows avec les officiers étudiants": "Weekly Board of Fellows meeting with the student officers",
  "Émission radio du collège": "College radio broadcast", "Programme radio de Black Mountain College sur WWNC": "Black Mountain College radio program on WWNC",
  "Cours d'écriture de Charles Olson (un soir par semaine)": "Charles Olson's writing class (one evening a week)", "Cours du soir de Robert Creeley": "Robert Creeley's evening class",
  "Séminaire collectif de philosophie (quatre enseignants ou plus à chaque séance)": "Joint philosophy seminar (four or more teachers at each session)",
  "Séminaire collectif de littérature anglaise et d'histoire (quatre enseignants ou plus)": "Joint seminar in English literature and history (four or more teachers)",
  "Chant pour toute la communauté": "Singing for the whole community", "Discussion de l'actualité (« discussion of contemporary events »)": "Discussion of current events (\"discussion of contemporary events\")",
  "Répétitions de la compagnie Cunningham": "Cunningham company rehearsals", "Répétitions de la compagnie Cunningham (soir)": "Cunningham company rehearsals (evening)",
  "Conférence publique hebdomadaire d'un membre de la communauté sur un sujet d'actualité": "Weekly public lecture by a community member on a current topic",
  "Programme musical informel du dimanche soir chez les Lowinsky": "Informal Sunday evening music at the Lowinskys'",
  "« The World Today » : actualité nationale et mondiale, ouvert à tous": "\"The World Today\": national and world news, open to all",
  "Portes ouvertes chez Karl et Elizabeth Niebyl (discussions)": "Open house at Karl and Elizabeth Niebyl's (discussions)",
  "Entretien du college par tous et « Community Projects » volontaires (construction, ferme…) ; jour non donné": "Upkeep of the college by everyone and voluntary \"Community Projects\" (construction, farm…); day not given",
  "Community Meeting : possible cette semaine (jour non donné)": "Community Meeting: possible this week (day not given)",
  "Première semaine : chaque étudiant choisit un conseiller parmi les enseignants": "First week: each student chooses an adviser among the teachers",
  "Première semaine : chaque nouvel étudiant choisit un conseiller": "First week: each new student chooses an adviser",
  "Concert du samedi soir : possible": "Saturday evening concert: possible", "Réunion générale de toute la communauté : possible cette semaine": "General meeting of the whole community: possible this week",
  "Réunion de toute la communauté": "Meeting of the whole community", "Soirée dansante du samedi": "Saturday dance evening", "Programme musical (gens du collège ou invités)": "Music program (college people or guests)",
  "Réunion d'affaires mensuelle de la faculté avec les officiers étudiants": "Monthly faculty business meeting with the student officers",
  "Réunion d'affaires mensuelle de la faculté, avec les officiers étudiants": "Monthly faculty business meeting, with the student officers",
  "Board of Fellows avec les officiers étudiants": "Board of Fellows with the student officers", "Émission radio du vendredi après-midi": "Friday afternoon radio broadcast",
  "Conférence du mercredi soir (visiteur ou membre de la faculté)": "Wednesday evening lecture (visitor or faculty member)", "Conférence du jeudi soir (visiteur ou membre de la faculté)": "Thursday evening lecture (visitor or faculty member)",
  "Conférence du mercredi soir": "Wednesday evening lecture", "Réunion des étudiants": "Student meeting", "Hygiène : séminaire ou entretien avec le Professor of Hygiene": "Hygiene: seminar or conference with the Professor of Hygiene",
  "Hygiène : séminaire ou entretien avec le Professor of Hygiene (« through seminar and conference rather than by lecture »)": "Hygiene: seminar or conference with the Professor of Hygiene (\"through seminar and conference rather than by lecture\")",
  "Concert ou programme du samedi soir": "Saturday evening concert or program", "Projection de film (16 mm)": "Film screening (16 mm)",
  "Concert ou programme de danse du samedi soir": "Saturday evening concert or dance program", "General Art Class pour toute la communauté": "General Art Class for the whole community",
  "Réunion de la communauté": "Community meeting", "Conférence ou forum du soir": "Evening lecture or forum",
  "Revue mensuelle de tous les travaux d'étudiants par le corps enseignant": "Monthly review of all student work by the faculty",
  "Concert, disques commentés ou programme du samedi soir": "Saturday evening concert, commented records or program", "Réunion de la faculté : possible": "Faculty meeting: possible",
  "Art class pour toute la communauté (thèmes de forme, critique des expositions et des tissages) : réunion occasionnelle": "Art class for the whole community (themes of form, critique of exhibitions and weavings): occasional meeting",
  "General art class pour toute la communauté (formes, matériaux, critique des expositions et des tissages)": "General art class for the whole community (forms, materials, critique of exhibitions and weavings)",
  "Concert, formel ou informel": "Concert, formal or informal", "Disques et exposition du dimanche soir dans la salle d'art": "Sunday evening records and exhibition in the art room",
  "Groupe de lecture de pièces": "Play-reading group", "Thé du mercredi": "Wednesday tea", "Café et exposition de travaux d'étudiants du dimanche soir": "Sunday evening coffee and exhibition of student work",
  "Spectacle de la compagnie Cunningham pour la communauté": "Cunningham company performance for the community",
  "Concert du quatuor à cordes en résidence (musique de chambre contemporaine)": "Concert by the resident string quartet (contemporary chamber music)",
  "Semaine du Summer Quarter 1954 (fin)": "Summer Quarter 1954 week (end)",
};
function trAct(s) { return ACT_EN[s] || s; }
// traduction d'un texte de données : relue (data_en.js, ACT_EN, règles) d'abord, puis automatique ; {t, auto}
function tr(s) {
  if (window.LANG !== "en" || !s) return { t: s, auto: false };
  const E = window.BMC_EN || { revu: {}, auto: {} };
  if (E.revu[s]) return { t: E.revu[s], auto: false };
  if (ACT_EN[s]) return { t: ACT_EN[s], auto: false };
  for (const [r, v] of REGLES_EN) if (r.test(s)) return { t: s.replace(r, v), auto: false };
  if (E.auto[s]) return { t: E.auto[s], auto: true };
  return { t: s, auto: false };
}
const tx = s => tr(s).t;
// motifs de la part déduite : chaque formule « … (+N) » traduite séparément
function trMotifs(m) {
  if (window.LANG !== "en" || !m) return m;
  return m.split(" ; ").map(x => { const k = x.match(/^(.*?)(\s*\(\+?-?\d+\).*)?$/); return tx(k[1].trim()) + (k[2] || ""); }).join(" ; ");
}

// colonne de contexte : titres et légendes (le contenu des synthèses reste en français)
const HTML_EN = [
  [/<h2>Période<\/h2>/g, "<h2>Term</h2>"], [/<h2>État de la semaine \(audit\)<\/h2>/g, "<h2>State of the week (audit)</h2>"],
  [/<h2>Semaine reconstituée<\/h2>/g, "<h2>Reconstructed week</h2>"], [/<h2>Documents datés de ces jours<\/h2>/g, "<h2>Documents dated these days</h2>"],
  [/<h2>Autres sources des activités affichées<\/h2>/g, "<h2>Other sources of the activities shown</h2>"], [/<h2>Lecture<\/h2>/g, "<h2>Reading guide</h2>"],
  [/<h2>(\d+) activités? sur ces dates/g, "<h2>$1 activities on these dates"],
  [/<h2>Arrivées et départs cette semaine selon le BMC Yearbook/g, "<h2>Arrivals and departures this week according to the BMC Yearbook"],
  [/<h2>Duberman \(1972\) : (\d+) faits? datés de façon imprécise/g, "<h2>Duberman (1972): $1 facts with an imprecise date"],
  [/<h2>Témoignages, Silver, compléments : (\d+) faits? datés au mois ou plus/g, "<h2>Testimonies, Silver, supplements: $1 facts dated to the month or broader"],
  [/<h2>Autres livres et études : (\d+) faits? datés de façon imprécise/g, "<h2>Other books and studies: $1 facts with an imprecise date"],
  [/<h2>Chronique de ([^(<]+) \(d'après les livres\)/g, "<h2>Chronicle of $1 (from the books, in French)"],
  [/<h2>Conflits en (\d+) selon les livres/g, "<h2>Conflicts in $1 according to the books"], [/<h2>Cours de ([\d-]+) selon les livres et études/g, "<h2>Courses of $1 according to books and studies"],
  [/<h2>Cours offerts en ([\d-]+) \(catalogues, bulletins\)/g, "<h2>Courses offered in $1 (catalogs, bulletins)"],
  [/<h2>Cours suivis \(([^)]*)\) selon les fiches d'étudiants/g, "<h2>Courses taken ($1) according to student records"],
  [/<h2>Vie quotidienne ([\d-]+) selon les livres/g, "<h2>Daily life $1 according to the books"], [/<h2>Œuvres liées à BMC en (\d+) selon les livres/g, "<h2>Works related to BMC in $1 according to the books"],
  [/Synthèse rédigée par un modèle de langage à partir des fiches de lecture des livres et études, non relue : à lire avec ses références\./g, "Synthesis written in French by a language model from reading notes on the books and studies, unreviewed: read with its references."],
  [/Dates des notices du site : pour moitié le premier ou le dernier jour d'une période de cours attestée \(70 % à une semaine près\), pas forcément le jour réel du voyage\./g, "Dates of the site's entries: half are the first or last day of an attested teaching period (70 % within a week), not necessarily the actual travel day."],
  [/Datés au mois, à la saison ou à l'année dans le livre : la période couvre ces jours, l'événement n'est pas placé dans la grille\./g, "Dated to the month, season or year in the book: the period covers these days; the event is not placed in the grid."],
  [/Fiches « cours » extraites automatiquement des livres ; référence cliquable pour la source et sa vérification\./g, "\"Course\" records drawn automatically from the books; click a reference for the source and its verification."],
  [/Couleur = famille d'activité\./g, "Color = type of activity."], [/✓ = nommé ce mois-ci dans l'AAM ou Duberman/g, "✓ = named this month in the AAM or Duberman"],
  [/BMC Yearbook \(bmcyearbook\.org\) : cours déclarés par les fiches de/g, "BMC Yearbook (bmcyearbook.org): courses declared in the records of"],
  [/>afficher</g, ">show<"], [/ attesté tel quel dans la source/g, " attested as is in the source"],
  [/semaine : /g, "week: "], [/remplissage /g, "coverage "], [/reconstituée \((\d+) jours?\)/g, "reconstructed ($1 days)"],
];
function traduireHtml(h) { for (const [r, v] of HTML_EN) h = h.replace(r, v); return h; }

// Anglais : pas d'espace avant « : », « ; » ni « % » (typographie française des gabarits), où que le texte soit affiché.
if (window.LANG === "en") {
  const corrige = n => { const v = n.nodeValue, w = v.replace(/[ \u00a0\u202f]+([:;!?])(?=\s|$)/g, "$1").replace(/(\d)[ \u00a0\u202f]%/g, "$1%"); if (w !== v) n.nodeValue = w; };
  const parcourt = r => { if (r.nodeType === 3) return corrige(r); const w = document.createTreeWalker(r, NodeFilter.SHOW_TEXT); while (w.nextNode()) corrige(w.currentNode); };
  document.addEventListener("DOMContentLoaded", () => {
    parcourt(document.body);
    new MutationObserver(L => L.forEach(m => m.type === "characterData" ? corrige(m.target) : m.addedNodes.forEach(parcourt)))
      .observe(document.body, { childList: true, subtree: true, characterData: true });
  });
}

// Références des sources (entretiens, renvois Chronos, livres) : seules nos parties françaises sont traduites.
const L = (fr, en) => window.LANG === "en" ? en : fr;
function trSrc(s) {
  if (window.LANG !== "en" || !s) return s || "";
  return s.replace(/^Entretien de (.+?) avec (.+?), /, "Interview with $1 by $2, ")
    .replace(/ — transcription /, " — transcript ").replace(/, d'après Chronos /, ", from Chronos ")
    .replace(/\(1972 ; Anchor 1973\)/, "(1972; Anchor 1973)")
    .replace(/^Albers, voyages Amérique latine/, "Albers, Latin American travels").replace(/^Albers noir et blanc/, "Albers, black and white")
    .replace(/^Albers, miniatures précolombiennes/, "Albers, pre-Columbian miniatures").replace(/, écrits\b/, ", writings")
    .replace(/^W\. de Kooning dessins/, "W. de Kooning, drawings").replace(/^thèse UMD/, "UMD dissertation")
    .replace(/^article art\/démocratie/, "article on art and democracy");
}
