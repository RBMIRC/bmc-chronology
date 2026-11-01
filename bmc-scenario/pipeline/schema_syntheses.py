"""Schémas des synthèses (06) : personnages, années, mois, enseignements."""
from schema import DATE, E, L, PRECISION, S, SN, obj

REFS = L(S(), "identifiants des fiches utilisées (EV-…, SC-…, PE-…)")
CERT = E(["atteste", "probable", "deduit", "invente_pour_le_recit_interdit"],
         "« deduit » = inférence raisonnable depuis les fiches ; ne jamais inventer")

# Schéma allégé : l'API Claude refuse une grammaire trop grosse (trop de champs
# « null possible » et d'énumérations répétées). Chaîne vide = rien dans les fiches.
D = S("date ISO partielle, ou chaîne vide")
PERSONNE = obj(
    nom=S(), autres_noms=L(S()), dates_de_vie=S(),
    statut_bmc=S(),
    presence=L(obj(debut=D, fin=D, role=S(), refs=REFS), "chaque séjour au collège"),
    portrait_physique=S(),
    noyau_psychologique=S("ce qui fait agir cette personne, en quelques phrases"),
    blessures=S(), desirs=S(), peurs=S(),
    maniere_d_aimer=S(), rapport_au_pouvoir=S(),
    voix=obj(registre=S(), tics=S(), exemples_paraphrases=L(S(), "façons de dire, paraphrasées")),
    habitudes=L(S()), convictions=L(S()),
    arc_bmc=L(obj(date=D, moment=S(), etat_interieur=S(), refs=REFS),
              "étapes de sa vie au collège, dans l'ordre"),
    avant=L(obj(date=D, moment=S(), refs=REFS), "matière à flash-back"),
    apres=L(obj(date=D, moment=S(), refs=REFS), "matière à flash-forward"),
    relations_cles=L(obj(avec=S(), nature=S(), evolution=S(), refs=REFS)),
    contradictions_entre_sources=L(S()),
    situations_revelatrices=L(S(), "types de scènes où cette personne se révèle"),
    citations=REFS,
    questions_ouvertes=L(S(), "ce que les sources ne disent pas et qu'il faudrait chercher"),
)

ANNEE = obj(
    annee=S(),
    sessions=L(obj(nom=S(), debut=DATE, fin=DATE, description=S(), refs=REFS),
               "trimestres, sessions d'été, vacances"),
    recit=S("le chapitre de l'année, de façon dense et concrète"),
    effectifs=SN(), argent=SN(), lieux_principaux=L(S()),
    presents_cles=L(obj(nom=S(), role=S(), periode=SN(), refs=REFS)),
    arrivees=L(obj(nom=S(), date=DATE, refs=REFS)), departs=L(obj(nom=S(), date=DATE, refs=REFS)),
    crises=L(obj(titre=S(), date=DATE, resume=S(), refs=REFS)),
    fils=L(obj(titre=S(), description=S(), debut=DATE, fin=DATE, refs=REFS),
           "intrigues qui courent sur plusieurs mois"),
    climat_general=S("humeur collective, saisons, guerre, argent"),
    questions_ouvertes=L(S()),
)

MOIS = obj(
    mois=S(),
    session=SN("session en cours (trimestre, session d'été, vacances)"),
    saison_et_climat=S(),
    situation=S("où en est le collège ce mois-ci"),
    presents_probables=L(obj(nom=S(), certitude=CERT)),
    evenements=L(obj(date=DATE, precision=PRECISION, ce_qui_arrive=S(), certitude=CERT, refs=REFS)),
    quotidien=S("la vie ordinaire de ce mois : travaux, repas, musique, cours"),
    tensions=L(S()),
    scenes_possibles=L(obj(titre=S(), date=DATE, lieu=SN(), personnages=L(S()), deroule=S(),
                           certitude=CERT, refs=REFS)),
    ouvertures_temporelles=L(obj(sens=E(["flashback", "flashforward"]), depuis=S("qui, dans quel moment du mois"),
                                 vers_date=DATE, vers=S(), refs=REFS),
                             "flash-back et flash-forward qui s'ouvrent naturellement depuis ce mois"),
    motifs=L(S()),
    lacunes=SN("ce qu'on ignore de ce mois"),
)

ENSEIGNEMENT = obj(
    enseignant=S(),
    cours=L(obj(
        intitule=S(), periodes=L(S()), atteste=E(["oui", "non", "incertain"]),
        objectifs=S(), deroule_type_seance=SN(),
        exercices=L(obj(consigne=S(), materiaux=SN(), but=SN(), refs=REFS)),
        lectures_et_references=L(S()),
        propos_types=L(S(), "ce qu'il ou elle disait, paraphrasé"),
        critique_et_evaluation=SN(), reactions_etudiants=SN(), evolution=SN(), refs=REFS)),
    idees_enseignables=L(obj(idee=S(), en_classe=S(), atteste=E(["oui", "non", "incertain"]), refs=REFS),
                         "pensée de l'enseignant transposable en séance"),
)
