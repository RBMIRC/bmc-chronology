"""Schéma de l'extraction par morceau (JSON Schema, sorties structurées).

Tout champ est requis ; « null » ou liste vide quand le texte ne dit rien.
Le contenu est rédigé en français ; les noms propres restent tels quels.
"""


def S(desc=None):
    return {"type": "string", **({"description": desc} if desc else {})}


def SN(desc=None):
    return {"type": ["string", "null"], **({"description": desc} if desc else {})}


def L(item, desc=None):
    return {"type": "array", "items": item, **({"description": desc} if desc else {})}


def E(valeurs, desc=None):
    return {"type": "string", "enum": valeurs, **({"description": desc} if desc else {})}


def obj(**champs):
    return {"type": "object", "properties": champs, "required": list(champs),
            "additionalProperties": False}


PAGES = L(S(), "folios tirés des repères [p. …] du texte")
DATE = SN("date ISO partielle : AAAA, AAAA-MM ou AAAA-MM-JJ ; null si inconnue")
PRECISION = E(["jour", "semaine", "mois", "saison", "session", "annee", "periode", "inconnue"],
              "précision réelle de la date (ne pas inventer un jour)")
EPOQUE = E(["avant_1933", "1933_1957", "apres_1957"],
           "avant l'ouverture du collège, pendant sa vie, après sa fermeture")
CERTITUDE = E(["atteste", "temoignage_direct", "oui_dire", "interpretation_auteur", "conteste", "hypothese"],
              "statut de l'information dans la source")

SCHEMA = obj(
    resume=S("deux ou trois phrases : ce que ce passage apporte au récit"),
    pertinence=E(["centrale", "utile", "marginale", "nulle"]),
    cadre_temporel=obj(
        debut=DATE, fin=DATE,
        justification=S("d'où vient ce cadre : date explicite, contexte du livre, présence connue des personnes")),
    evenements=L(obj(
        titre=S(), date=DATE, date_fin=DATE, precision=PRECISION, epoque=EPOQUE,
        lieu=SN(), personnes=L(S()),
        description=S("ce qui s'est passé, avec les détails"),
        details_concrets=SN("chiffres, objets, météo, heure, gestes, sommes d'argent"),
        consequences=SN(), certitude=CERTITUDE, pages=PAGES)),
    personnes=L(obj(
        nom=S("nom complet tel qu'usuel (ex. « Josef Albers »)"), autres_noms=L(S()),
        statut_bmc=E(["fondateur", "enseignant", "etudiant", "enseignant_ete", "invite", "personnel",
                      "famille", "voisin", "exterieur"]),
        presence_bmc=SN("périodes de présence au collège si dites"),
        apparence=SN(), temperament=SN(),
        psychologie=SN("blessures, peurs, désirs, besoins, façon d'aimer ou de dominer"),
        manieres_et_voix=SN("façon de parler, accent, tics, gestes, humour"),
        habitudes=SN(), convictions=SN(), contradictions=SN(),
        avant_bmc=SN("ce qui précède son arrivée (matière à flash-back)"),
        apres_bmc=SN("ce qui suit son départ ou la fermeture (matière à flash-forward)"),
        certitude=CERTITUDE, pages=PAGES)),
    relations=L(obj(
        personne_a=S(), personne_b=S(),
        nature=E(["amour", "mariage", "amitie", "mentorat", "admiration", "rivalite", "conflit",
                  "collaboration", "famille", "rejet", "autre"]),
        periode=SN(), description=S(), evolution=SN(), pages=PAGES)),
    cours=L(obj(
        enseignant=S(), intitule=S(), periode=SN(),
        atteste_a_bmc=E(["oui", "non", "incertain"], "ce cours a-t-il eu lieu au collège ?"),
        objectifs=SN(), exercices=L(S(), "consignes exactes, une par entrée"),
        materiaux=SN(), deroule_seance=SN(),
        propos_de_l_enseignant=SN("ce qu'il disait en classe, paraphrasé"),
        reactions_etudiants=SN(), pages=PAGES)),
    idees=L(obj(
        auteur=S(), idee=S("l'idée en une phrase"), developpement=S(),
        exemple=SN("exemple, cas, image qui la rend sensible"),
        en_classe=SN("comment elle pourrait se dire ou s'exercer devant des étudiants, paraphrasé"),
        lien_bmc=SN(), atteste_a_bmc=E(["oui", "non", "incertain"]), pages=PAGES)),
    lieux=L(obj(
        nom=S(), periode=SN(), description_physique=SN(), usages=SN(),
        ambiance=SN("lumière, sons, odeurs, température, saisons"), pages=PAGES)),
    quotidien=L(obj(
        theme=E(["repas", "travail_et_corvees", "ferme", "construction", "argent", "logement",
                 "reunions_et_gouvernance", "fetes_et_danses", "musique", "theatre", "sexualite_et_couples",
                 "enfants", "sante", "climat_et_saisons", "nature", "ville_et_voisins",
                 "race_et_segregation", "politique_et_guerre", "transport", "courrier_et_visiteurs",
                 "alcool_et_drogues", "autre"]),
        periode=SN(), description=S(), pages=PAGES)),
    scenes=L(obj(
        titre=S(), date=DATE, precision=PRECISION, lieu=SN(), personnages=L(S()),
        deroule=S("la scène pas à pas"),
        paroles_rapportees=SN("échanges rapportés, paraphrasés en français"),
        atmosphere=SN("sensations, lumière, bruit, climat émotionnel"),
        enjeu_dramatique=SN(), certitude=CERTITUDE, pages=PAGES)),
    citations=L(obj(
        locuteur=S(), texte_original=S("25 mots au plus, dans la langue de la source"),
        traduction_fr=S(), contexte=SN(), date=DATE, pages=PAGES)),
    oeuvres=L(obj(
        titre=S(), auteur=S(), date=DATE, technique=SN(), description=SN(), lien_bmc=SN(), pages=PAGES)),
    conflits=L(obj(
        titre=S(), periode=SN(), camps=S(), enjeu=S(), deroule=S(), issue=SN(), pages=PAGES)),
    echos=L(obj(
        moment_present=S("le moment raconté (qui, quand)"),
        moment_relie=S("le moment antérieur ou postérieur auquel le texte le relie"),
        sens=E(["flashback", "flashforward", "motif"]),
        explication=S(), pages=PAGES), "liens que le texte établit entre deux époques"),
    motifs=L(S(), "images, objets, gestes ou thèmes récurrents utiles au récit"),
)

CATEGORIES = ["evenements", "personnes", "relations", "cours", "idees", "lieux", "quotidien",
              "scenes", "citations", "oeuvres", "conflits", "echos"]
