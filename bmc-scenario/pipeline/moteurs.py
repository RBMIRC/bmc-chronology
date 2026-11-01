"""Appels au modèle, communs à 04 (extraction) et 06 (synthèses).

claude : API Anthropic, ANTHROPIC_API_KEY saisie dans le terminal ; sorties
         structurées garanties ; lots via l'API Batches (-50 %).
zai    : GLM via z.ai, jeton lu dans ~/.claude/settings.json ; JSON demandé dans
         le prompt puis vérifié ici. Pas de lots.
"""
import json
import os
import re
import sys
import time
from pathlib import Path

PRIX = {  # $ / M tokens (entrée, sortie), tarif standard ; lots = moitié
    "claude-opus-5-5": (4.0, 20.0), "claude-sonnet-5-5": (2.0, 10.0), "claude-haiku-5-5": (0.10, 0.50),
}
MAX_TOKENS = 64000  # une année peut dépasser 30 k tokens de sortie
MODELE_DEFAUT = {"claude": "claude-opus-5-5", "zai": "glm-5.2"}


FICHIER_CLE = Path.home() / ".config/anthropic/cle_bmc_scenario"


class ReponseInvalide(Exception):
    pass


def client(moteur):
    import anthropic
    if moteur == "claude":
        cle = os.environ.get("ANTHROPIC_API_KEY")
        if not cle and FICHIER_CLE.exists():  # posée par l'utilisateur, lue sans jamais être affichée
            cle = FICHIER_CLE.read_text().strip()
        if not cle:
            sys.exit(f"Clé absente : export ANTHROPIC_API_KEY, ou la poser dans {FICHIER_CLE} (chmod 600)")
        # la config de Claude Code pointe vers z.ai : on force l'API Anthropic (les scripts .sh retirent le jeton z.ai)
        return anthropic.Anthropic(api_key=cle, auth_token=None,
                                   base_url="https://api.anthropic.com", max_retries=5)
    env = json.load(open(Path.home() / ".claude/settings.json"))["env"]
    return anthropic.Anthropic(api_key=env["ANTHROPIC_AUTH_TOKEN"], base_url=env["ANTHROPIC_BASE_URL"],
                               max_retries=2, timeout=900)


def params(modele, systeme, message, schema, effort):
    """Requête Claude avec sortie structurée ; le prompt système est mis en cache."""
    return {
        "model": modele,
        "max_tokens": MAX_TOKENS,
        "system": [{"type": "text", "text": systeme, "cache_control": {"type": "ephemeral"}}],
        "messages": [{"role": "user", "content": message}],
        "output_config": {"effort": effort, "format": {"type": "json_schema", "schema": schema}},
    }


def texte(msg):
    if msg.stop_reason == "refusal":
        raise ReponseInvalide("refus du modèle")
    if msg.stop_reason == "max_tokens":
        raise ReponseInvalide("réponse tronquée (max_tokens)")
    return next(b.text for b in msg.content if b.type == "text")


def usage(u):
    return {"entree": u.input_tokens, "sortie": u.output_tokens,
            "cache_lu": getattr(u, "cache_read_input_tokens", 0) or 0,
            "cache_ecrit": getattr(u, "cache_creation_input_tokens", 0) or 0}


def json_du_texte(t):
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t.strip())
    return json.loads(t[t.find("{"): t.rfind("}") + 1])


ATTENTE_QUOTA = 600  # s : z.ai coupe par fenêtres de 5 h ; on attend au lieu d'échouer


def flux_avec_attente(cl, **p):
    """Appel z.ai qui patiente quand le quota est atteint ou le service saturé."""
    import anthropic
    while True:
        try:
            with cl.messages.stream(**p) as flux:
                return flux.get_final_message()
        except (anthropic.RateLimitError, anthropic.InternalServerError, anthropic.APIConnectionError) as e:
            raison = type(e).__name__
        except anthropic.APIStatusError as e:
            if e.status_code not in (429, 502, 503, 529):
                raise
            raison = f"HTTP {e.status_code}"
        print(f"    [{time.strftime('%H:%M')}] {raison} : quota ou service, nouvel essai dans "
              f"{ATTENTE_QUOTA // 60} min", flush=True)
        time.sleep(ATTENTE_QUOTA)


def appeler(moteur, cl, modele, systeme, message, schema, effort="medium"):
    """Un appel direct ; renvoie (objet JSON, usage)."""
    if moteur == "claude":
        with cl.messages.stream(**params(modele, systeme, message, schema, effort)) as flux:
            msg = flux.get_final_message()
        return json.loads(texte(msg)), usage(msg.usage)
    consigne = ("\n\nRéponds uniquement par un objet JSON valide, sans texte autour, conforme à ce schéma "
                "(tous les champs présents, null ou [] si rien) :\n" + json.dumps(schema, ensure_ascii=False))
    erreur = None
    for _ in range(3):
        msg = flux_avec_attente(cl, model=modele, max_tokens=MAX_TOKENS, system=systeme + consigne,
                                messages=[{"role": "user", "content": message}])
        try:
            t = texte(msg)
            if re.search(r"[\u3040-\u30ff\u4e00-\u9fff\uac00-\ud7af]", t):  # GLM glisse parfois du chinois
                raise ValueError("caractères CJK parasites")
            return json_du_texte(t), usage(msg.usage)
        except (ValueError, json.JSONDecodeError) as e:
            erreur = e
    raise ReponseInvalide(f"JSON invalide après 3 essais : {erreur}")


# ---------------------------------------------------------------- lots (claude seulement)

def soumettre(cl, requetes, journal, modele, taille=500):
    """requetes : [(custom_id, params)] ; une ligne par lot dans le journal."""
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request
    en_attente = set()
    if journal.exists():  # ne pas renvoyer ce qui attend déjà dans un lot ouvert
        for l in open(journal):
            r = json.loads(l)
            if cl.messages.batches.retrieve(r["lot"]).processing_status != "ended":
                en_attente |= set(r["ids"])
    requetes = [(i, p) for i, p in requetes if i not in en_attente]
    for k in range(0, len(requetes), taille):
        paquet = requetes[k:k + taille]
        b = cl.messages.batches.create(requests=[
            Request(custom_id=i, params=MessageCreateParamsNonStreaming(**p)) for i, p in paquet])
        with open(journal, "a") as f:
            f.write(json.dumps({"lot": b.id, "modele": modele, "cree": time.strftime("%Y-%m-%d %H:%M"),
                                "ids": [i for i, _ in paquet]}) + "\n")
        print(f"lot {b.id} : {len(paquet)} requêtes envoyées")
    if not requetes:
        print("rien à envoyer (tout est fait ou déjà en attente)")


def attendre(cl, journal, pause=180):
    """Patiente jusqu'à ce que tous les lots du journal soient terminés."""
    while journal.exists():
        ouverts = [json.loads(l)["lot"] for l in open(journal)]
        restants = [b for b in ouverts if cl.messages.batches.retrieve(b).processing_status != "ended"]
        if not restants:
            return
        print(f"    [{time.strftime('%H:%M')}] {len(restants)} lot(s) en cours, nouvel examen dans {pause // 60} min",
              flush=True)
        time.sleep(pause)


def relever(cl, journal):
    """Itère (custom_id, modele, objet | None, usage | None, erreur) sur les lots terminés."""
    if not journal.exists():
        print("aucun lot envoyé")
        return
    for l in open(journal):
        r = json.loads(l)
        b = cl.messages.batches.retrieve(r["lot"])
        c = b.request_counts
        print(f"{r['lot']} {b.processing_status} : {c.succeeded} ok, {c.errored} erreurs, "
              f"{c.processing} en cours, {c.expired} expirés")
        if b.processing_status != "ended":
            continue
        for res in cl.messages.batches.results(r["lot"]):
            if res.result.type != "succeeded":
                yield res.custom_id, r["modele"], None, None, res.result.type
                continue
            try:
                msg = res.result.message
                yield res.custom_id, r["modele"], json.loads(texte(msg)), usage(msg.usage), None
            except (ReponseInvalide, json.JSONDecodeError) as e:
                yield res.custom_id, r["modele"], None, None, str(e)
