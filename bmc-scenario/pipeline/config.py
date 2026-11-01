"""Réglages communs du pipeline « scénario BMC 1933-1957 à l'échelle 1 »."""
from pathlib import Path

SOURCES = Path("/Users/sylvain/Downloads/BMC exo theory BOOKS")
RACINE = Path(__file__).resolve().parent.parent

TEXTE = RACINE / "texte"            # 02 : une page par ligne, NNN.jsonl.gz
MORCEAUX = RACINE / "morceaux"      # 03 : morceaux.jsonl (un morceau = ~6 k tokens)
EXTRACTIONS = RACINE / "extractions"  # 04 : un JSON par morceau
FUSION = RACINE / "fusion"          # 05 : fiches fusionnées
SYNTHESES = RACINE / "syntheses"    # 06 : dossiers personnes, mois, cours
SORTIE = RACINE / "sortie"          # 07 : le JSON final
ETAT = RACINE / "etat"              # journaux, lots, coûts
REFERENTIEL = RACINE / "referentiel"  # noms canoniques, calendrier des sessions

INVENTAIRE = RACINE / "sources.csv"

# Taille des morceaux envoyés au modèle. Plus court = extraction plus dense.
MORCEAU_CARACTERES = 22_000   # ≈ 5,5 k tokens
CHEVAUCHEMENT_CARACTERES = 1_200

# Rôle de chaque source dans le récit. Le premier motif (sous-chaîne du nom de
# fichier, en minuscules) qui correspond l'emporte.
#   histoire     : histoire du collège (faits, dates, institutions)
#   temoignage   : mémoires, récits d'anciens (scènes, psychologie, quotidien)
#   biographie   : vie d'un membre (avant / pendant / après BMC)
#   enseignement : ce qui s'enseignait et comment (exercices, méthode)
#   ecrits       : pensée d'un membre (matière d'un cours possible, voix)
#   catalogue    : œuvres, notices, chronologies d'exposition
#   contexte     : époque, Bauhaus, monde de l'art autour
CLASSEMENT = [
    ("black mountain; an exploration in community", "histoire", "A", "Duberman 1972"),
    ("starting at zero", "histoire", "A", "Harris 2005"),
    ("leap before you look", "histoire", "A", "Molesworth 2015"),
    ("the experimenters", "histoire", "A", "Díaz 2014"),
    ("visions and vanities", "biographie", "A", "Chaddock 2002 (Rice)"),
    ("sprouted seeds", "temoignage", "A", "Lane 1990"),
    ("black mountain days", "temoignage", "A", "Rumaker 2003"),
    ("the black mountain book", "temoignage", "A", "Dawson 1970"),
    ("palpable elysium", "temoignage", "A", "Williams 2002"),
    ("boston_globe", "histoire", "A", "Boston Globe"),
    ("black_mountain_college_art_democratie", "histoire", "A", "article art/démocratie"),
    ("burns_jbmcs", "histoire", "A", "Burns, JBMCS vol. 11"),
    ("living with the land", "histoire", "A", "BMCM+AC, Living with the land"),
    ("hazel larsen archer", "histoire", "A", "BMCM+AC, Hazel Larsen Archer"),
    ("the last few days", "histoire", "A", "BMCM+AC, The Last Few Days"),
    ("daily hatch", "biographie", "A", "The Daily Hatch"),
    ("umi-umd", "histoire", "A", "thèse UMD"),
    ("bb659229", "histoire", "A", "article (sans titre)"),
    ("nathan rosen", "biographie", "B", "Wikipedia, Nathan Rosen"),
    ("ruth asawa", "biographie", "A", "Troeller 2025 (Asawa)"),
    ("generous vision", "biographie", "A", "Curtis 2017 (Elaine de Kooning)"),
    ("elaine and bill", "biographie", "A", "Hall 1993 (de Kooning)"),
    ("susan weil_ full circle", "biographie", "A", "Stein (Susan Weil)"),
    ("the bauhaus group", "doublon", "-", "doublon EPUB de The Bauhaus Group (058, PDF folioté)"),
    ("isbn_2900300169842", "biographie", "A", "Weber 2009, The Bauhaus Group"),
    ("to open eyes", "enseignement", "A", "Horowitz & Danilowitz 2009"),
    ("interacting with color", "enseignement", "A", "Horstman 2024"),
    ("on designing", "ecrits", "A", "Anni Albers 1961"),
    ("on weaving", "ecrits", "A", "Anni Albers 1965/2017"),
    ("des carrés", "enseignement", "C", "Albers jeunesse"),
    ("gestalt therapy_ excitement", "ecrits", "A", "Perls, Hefferline, Goodman 1951"),
    ("the gestalt therapy book", "doublon", "-", "doublon de Gestalt Therapy (1951)"),
    ("growing up absurd", "ecrits", "A", "Goodman 1960"),
    ("structure of literature", "ecrits", "B", "Goodman 1954"),
    ("people or personnel", "ecrits", "B", "Goodman 1965"),
    ("making do", "ecrits", "B", "Goodman 1963"),
    ("paul goodman reader", "ecrits", "A", "Goodman Reader 2011"),
    ("spirit of abstract expressionism", "ecrits", "A", "E. de Kooning, écrits"),
    ("works, writings and interviews", "ecrits", "A", "Rauschenberg, écrits"),
    ("works, writings, interviews", "ecrits", "A", "W. de Kooning, écrits"),
    ("rauschenberg and surrealism", "contexte", "B", "Parkinson 2023"),
    ("viajes por latinoam", "catalogue", "B", "Albers, voyages Amérique latine"),
    ("anni albers _ prints and drawings", "catalogue", "C", "Anni Albers, gravures"),
    ("woven and graphic art", "catalogue", "B", "Anni Albers 1985"),
    ("in black and white", "catalogue", "B", "Albers noir et blanc"),
    ("drawings of josef albers", "catalogue", "B", "Weber 1984"),
    ("pre-columbian mexican", "catalogue", "C", "Albers, miniatures précolombiennes"),
    ("albers collection of pre-columbian", "catalogue", "C", "Taube 1988"),
    ("white and black paintings", "catalogue", "B", "Rauschenberg 1949-1952"),
    ("werke 1950-1980", "catalogue", "B", "Rauschenberg Berlin 1980"),
    ("photographs, 1949-1962", "catalogue", "B", "Rauschenberg photographies"),
    ("drawings, 1958-1968", "catalogue", "C", "Rauschenberg dessins"),
    ("graphic art", "catalogue", "C", "Rauschenberg ICA 1970"),
    ("singular forms", "contexte", "C", "Guggenheim 2004"),
    ("illuminations _ bookworks", "catalogue", "C", "Susan Weil, livres"),
    ("artist's hand", "catalogue", "C", "W. de Kooning dessins"),
    ("de kooning 1904 - 1997", "biographie", "B", "Hess (W. de Kooning)"),
    ("ibauhaus", "contexte", "C", "Weber 2020"),
]

# Sources de fiction : leurs personnages ne sont jamais fondus avec des personnes réelles.
FICTION = {"059": "Goodman, Making Do (roman, 1963)"}

# Consignes propres à chaque rôle, injectées dans le prompt d'extraction.
CONSIGNE_ROLE = {
    "histoire": "Livre d'histoire du collège : privilégie les faits datés, les décisions, les arrivées et départs, les crises, les chiffres (effectifs, argent), mais aussi chaque détail concret ou humain.",
    "temoignage": "Témoignage d'un ancien : privilégie les scènes vécues, les dialogues rapportés, la psychologie des gens, les sensations, le quotidien, les rumeurs (marquées comme telles).",
    "biographie": "Biographie : distingue bien la vie AVANT le collège, PENDANT, et APRÈS (matière à flash-back et flash-forward). Garde la psychologie, les relations, les blessures, les habitudes.",
    "enseignement": "Pédagogie : reconstruis les cours (exercices exacts, matériaux, consignes, déroulé d'une séance, ce que disait l'enseignant, réactions des étudiants).",
    "ecrits": "Écrits d'un membre : extrais les idées comme la matière d'un cours ou d'une conversation qu'il aurait pu tenir au collège (idée, explication, exemple, formulation dans sa voix). Marque atteste_a_bmc=false si rien ne dit qu'il l'a enseigné là.",
    "catalogue": "Catalogue : extrais les œuvres (titre, date, technique, dimensions si utiles, lieu de fabrication) et tout fait biographique ou chronologique ; ignore les listes de prêteurs et les crédits.",
    "contexte": "Contexte : ne garde que ce qui touche le collège, ses membres ou l'époque 1920-1990 vue depuis eux.",
}
