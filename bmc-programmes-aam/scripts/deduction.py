"""Part de déduction (en %) d'une entrée par rapport à ses sources, avec motifs.
0 % = l'information figure telle quelle dans le document cité.
Chaque règle ajoute un pourcentage ; total plafonné à 90 %."""
import re

REGLES = [
    # (motif, points, motif regex sur la note et les champs)
    ("élément supposé par moi (heure, fin de période…)", 15,
     r"supposée?s?\b|présumée?"),
    ("enseignant ou rattachement déduit (pas écrit dans ce document)", 15,
     r"enseignant(e)?s? (probables?|déduite?s?|d.après)|attribution|déduite? de la liste|d.après la liste|programme probable"),
    ("récurrence ou période déduite", 10,
     r"récurrence déduite|période déduite|dates de début déduites|heure déduite|grille déduite|déduit des bulletins"),
    ("date approximative ou incomplète dans la source", 25,
     r"approximati|date exacte (non|inconnue)|non précisée|date incertaine|\bincertain|on or about|sans année|date non donnée|date de la représentation non"),
    ("annoncé à l'avance : réalisation non attestée", 15,
     r"provisoire|\bprévue?s?\b|proposée?\b|proposition|\bannoncée?s?\b|recommandé|tentative|à venir|planned"),
    ("date corrigée contre celle du musée ou du document", 20,
     r"le musée (indique|date)|par le musée|daté « c|1939-1940. par le musée"),
    ("lecture corrigée d'une coquille de la source", 10,
     r"texte :|imprimée? «|\blue? «|\bocr\b|\blire |heure lue|le texte (dit|donne|imprime)|bulletin : «|misprint|par coquille"),
]
STATUT = r"reporté|annulé|relâche|remplacé"

def evaluer(kind, date_tok, note, extra=""):
    pts, motifs = 0, []
    if kind == "E":
        if date_tok.startswith("R:"):
            if re.search(r"grille|régulière|chaque|hebdomadaire|weekly|regular|horaire quotidien|deux fois par semaine", note.lower()):
                pts += 10; motifs.append("séance projetée sur chaque date d'après un horaire que la source donne comme régulier (+10)")
            else:
                pts += 20; motifs.append("séance projetée sur chaque date ; régularité déduite par moi (+20)")
        elif re.fullmatch(r"[+-](lun|mar|mer|jeu|ven|sam|dim|\d+)", date_tok.strip()) and date_tok.strip() != "0":
            pts += 5; motifs.append("jour calculé à partir de la date du document (« mardi », « hier »…) (+5)")
    txt = (note + " " + extra).lower()
    for motif, p, rx in REGLES:
        if re.search(rx, txt):
            pts += p; motifs.append(f"{motif} (+{p})")
    if re.search(STATUT, txt):
        motifs.append("statut : annonce reportée/annulée/remplacée selon une source (voir note)")
    return min(pts, 90), " ; ".join(motifs) if motifs else "attesté tel quel dans la source"
