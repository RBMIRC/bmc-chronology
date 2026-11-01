"""Étape 2 : assemble le corps du livre (pages PDF 004-168) en paragraphes.
Entrée /tmp/farm/pages.json (build.py). Sorties : /tmp/farm/out/corps.txt, /tmp/farm/out/corps.json, /tmp/farm/out/appels.json."""
import json, re, os, statistics as st
from wordfreq import zipf_frequency as zf

P = json.load(open("/tmp/farm/pages.json"))
os.makedirs("/tmp/farm/out", exist_ok=True)

# pages PDF → page du livre (établi à la main d'après les en-têtes, la parité et la continuité du texte)
PAGES = json.load(open("/tmp/farm/pagemap.json")) if os.path.exists("/tmp/farm/pagemap.json") else {}
OUVERTURES = {"007": (None, "Introduction"), "012": (1, "Before Black Mountain"), "025": (2, "The Founding of the Farm"), "038": (3, "Pigs and Place"),
              "057": (4, "Moving to Lake Eden"), "070": (5, "Barn Raising"), "083": (6, "Molly Gregory Raises the Roof"),
              "106": (7, "The Quakers"), "129": (8, "“No more of this community horseshit!”"), "150": (9, "Collapse")}
LACUNES = json.load(open("/tmp/farm/lacunes.json")) if os.path.exists("/tmp/farm/lacunes.json") else {}
SPECIAUX = json.load(open("/tmp/farm/speciaux.json")) if os.path.exists("/tmp/farm/speciaux.json") else {}
PLUS = json.load(open("/tmp/farm/out/legendes_plus.json")) if os.path.exists("/tmp/farm/out/legendes_plus.json") else {}
SAUTER = set(json.load(open("/tmp/farm/sauter.json"))) if os.path.exists("/tmp/farm/sauter.json") else set()

RX_SUP_SEUL = re.compile(r"^['‘’!|Il1]?\d{1,3}['’]?$")
RX_SUP_COLLE = re.compile(r"^(.*?[A-Za-z0-9][.,;:!?”’\")\]—]+)(['‘’!|Il]?\d{1,3})$")


def lisse(w):
    return w.replace("’", "'").lower()


def mot_ok(w):
    w = re.sub(r"[^A-Za-z'’-]", "", w)
    return zf(w.lower().replace("’", "'"), "en") >= 2.0 if w else False


def fusion(a, b):
    """a se termine par un trait d'union en fin de ligne ; b commence la ligne suivante."""
    m1 = re.search(r"([A-Za-z’']+)-$", a)
    m2 = re.match(r"([A-Za-z’']+)(.*)$", b)
    if not m1 or not m2:
        return a + b if a.endswith("—") or a.endswith("–") else a + " " + b
    g, d = m1.group(1), m2.group(1)
    colle = g + d
    fc = zf(colle.lower().replace("’", "'"), "en")
    if d[0].isupper() and not g[0].isupper():
        return a + b  # « pre-War » : garder le trait
    if fc >= 2.2:
        return a[:-1] + b
    if zf(g.lower(), "en") >= 3.0 and zf(d.lower(), "en") >= 3.0:
        return a + b  # deux mots courants, forme soudée inconnue : composé à trait d'union
    return a[:-1] + b


ENCRE = json.load(open("/tmp/farm/out/encre.json")) if os.path.exists("/tmp/farm/out/encre.json") else {}
BLOB = json.load(open("/tmp/farm/out/blob_ocr.json")) if os.path.exists("/tmp/farm/out/blob_ocr.json") else {}


def appels(el, n=None, li=None):
    """Repère les appels de note (exposants) dans une ligne ; renvoie le texte avec ⟦brut⟧ à leur place."""
    ws = el["ws"]
    bas = [w[2] + w[4] for w in ws if re.fullmatch(r"[A-Za-z]*[acemnorsuvwxzbdfhiklt][A-Za-z]*[.,;:”’\"']?", w[0]) and not re.search(r"[gjpqy]", w[0])]
    ligne_bas = st.median(bas) if bas else None
    xh = el["xh"] or 23
    out = []
    for i, w in enumerate(ws):
        t = w[0]
        cle = f"{n}|{li}|{i}"
        suiv_sup = i + 1 < len(ws) and RX_SUP_SEUL.match(ws[i + 1][0])
        if cle in ENCRE and not RX_SUP_COLLE.match(t) and not suiv_sup and not RX_SUP_SEUL.match(t) and not t.endswith(('-', '—', '–')):
            out.append(t + f"⟦b{BLOB.get(cle, '')}@{n},{w[1] + w[3]},{w[2]}⟧")
            continue
        if RX_SUP_SEUL.match(t) and i > 0 and ligne_bas and (w[2] + w[4] < ligne_bas - 0.25 * xh or w[4] < 0.9 * xh * 1.35):
            prec = out[-1] if out else ""
            if re.search(r"[A-Za-z.,;:!?”’\")\]]$", prec) and not re.fullmatch(r"\d{4}", re.sub(r"\D", "", t)):
                out[-1] = prec + "⟦_" + t + f"@{n},{w[1]},{w[2]}⟧"
                continue
        m = RX_SUP_COLLE.match(t)
        if m and not re.search(r"\d", m.group(1)[-3:-1] if len(m.group(1)) > 2 else "x"):
            out.append(m.group(1) + "⟦" + m.group(2) + f"@{n},{w[1] + w[3]},{w[2]}⟧")
            continue
        out.append(t)
    return " ".join(out)


def main():
    flux = []          # éléments : {"t": type, "x": texte, "p": [pages]}
    legendes = []      # légendes en attente de la fin du paragraphe
    cour = None        # paragraphe en cours

    def fin_para():
        nonlocal cour
        if cour:
            flux.append(cour); cour = None
        while legendes:
            flux.append(legendes.pop(0))

    for p in P:
        n = p["n"]
        if int(n) < 4 or int(n) > 168 or n in SAUTER:
            continue
        bp = PAGES.get(n, n)
        if n in LACUNES:  # pages du livre absentes du scan, avant cette page
            fin_para()
            flux.append({"t": "lacune", "x": LACUNES[n], "p": [bp]})
        if n in OUVERTURES:
            fin_para()
            c, titre = OUVERTURES[n]
            flux.append({"t": "chapitre", "x": f"CHAPTER {c}\n\n{titre.upper()}" if c else titre.upper(), "p": [bp]})
            continue
        if n in SPECIAUX:
            for it in SPECIAUX[n]["el"]:
                legendes.append({"t": it["t"], "x": it["x"], "p": [bp]})
            if not SPECIAUX[n].get("garder_ocr"):
                continue
        for li, e in enumerate(p["el"]): e["li"] = li
        els = [e for e in p["el"] if e["cls"] != "bruit"]
        # page de photographie (presque pas de lignes de corps mesurées) : tout est légende ;
        # une ligne qui déborde nettement à gauche de la marge du corps est une légende (sous une photo)
        sures = [e_ for e_ in els if (e_["xh"] and e_["xh"] >= 22) or (e_["ah"] and e_["ah"] >= 31.5)]
        for e_ in els:
            if e_["cls"] in ("corps", "corps?", "grand", "legende"):
                if len(sures) < 3 or e_["retrait"] < -60:
                    e_["cls"] = "legende"; e_["fixe"] = True
        # légende ou corps : décision par groupe de lignes rapprochées (une légende est détachée du corps)
        groupes, g_ = [], []
        for e_ in els:
            if g_ and e_["y0"] - g_[-1]["y1"] > 30:
                groupes.append(g_); g_ = []
            g_.append(e_)
        if g_: groupes.append(g_)
        for g_ in groupes:
            votes = []
            for e_ in g_:
                if e_["cls"] not in ("corps", "legende", "corps?", "grand") or e_.get("fixe"): continue
                if e_["xh"]: votes.append("legende" if e_["xh"] <= 20.5 else "corps")
                elif e_["ah"]: votes.append("legende" if e_["ah"] <= 29.0 else "corps")
            if not votes: continue
            maj = "legende" if votes.count("legende") > len(votes) / 2 else "corps"
            for e_ in g_:
                if e_["cls"] in ("corps", "legende", "corps?") and not e_.get("fixe"):
                    e_["cls"] = maj
        # une ligne « légende » isolée entre deux lignes de corps, alignée sur la marge, est du corps (titre en italique…)
        for j in range(1, len(els) - 1):
            a_, e_, b_ = els[j - 1], els[j], els[j + 1]
            if e_["cls"] == "legende" and a_["cls"] in ("corps", "grand") and b_["cls"] in ("corps", "grand") \
                    and abs(e_["retrait"]) < 40 and 0 < e_["y0"] - a_["y0"] < 75 and 0 < b_["y0"] - e_["y0"] < 75:
                e_["cls"] = "corps"
        if len(els) >= 2 and els[-1]["cls"] == "legende" and els[-2]["cls"] in ("corps", "grand") and abs(els[-1]["retrait"]) < 40 \
                and 0 < els[-1]["y0"] - els[-2]["y0"] < 75:
            els[-1]["cls"] = "corps"
        corps = [e for e in els if e["cls"] in ("corps", "grand", "corps?")]
        pas = st.median([b["y0"] - a["y0"] for a, b in zip(corps, corps[1:]) if 0 < b["y0"] - a["y0"] < 120]) if len(corps) > 2 else 60
        # légendes : regroupées par proximité verticale
        i = 0
        prem_corps = True
        while i < len(els):
            e = els[i]
            if e["cls"] == "legende" or (e["cls"] == "titre" and e.get("xh") and e["xh"] < 20):
                bloc = [e]
                while i + 1 < len(els) and els[i + 1]["cls"] == "legende" and els[i + 1]["y0"] - bloc[-1]["y1"] < 40:
                    i += 1; bloc.append(els[i])
                txt = " ".join(PLUS.get(f"{n}|{bloc[0]['y0']}", []))
                for b in bloc:
                    t = appels(b, n, b['li'])
                    txt = fusion(txt, t) if txt.endswith("-") else (txt + " " + t if txt else t)
                legendes.append({"t": "legende", "x": txt.strip(), "p": [bp],
                                 "bbox": [n, min(b["x0"] for b in bloc), bloc[0]["y0"], max(b["x1"] for b in bloc), bloc[-1]["y1"]]})
                i += 1; continue
            if e["cls"] == "titre":
                fin_para()
                flux.append({"t": "titre", "x": e["text"].strip(), "p": [bp]})
                prem_corps = False
                i += 1; continue
            # corps : citation (suite de lignes en retrait) ou paragraphe
            t = appels(e, n, e['li'])
            retrait = e["retrait"] > 70
            suite_retrait = i + 1 < len(els) and els[i + 1]["cls"] in ("corps", "grand", "corps?") and els[i + 1]["retrait"] > 70 \
                and abs(els[i + 1]["retrait"] - e["retrait"]) < 60
            prec_retrait = i > 0 and els[i - 1]["cls"] in ("corps", "grand", "corps?") and els[i - 1]["retrait"] > 70
            ecart = i > 0 and e["y0"] - els[i - 1]["y1"] > 1.0 * pas
            citation = retrait and (suite_retrait or prec_retrait)
            typ = "citation" if citation else "para"
            nouveau = (cour is None or cour["t"] != typ or
                       (typ == "para" and (retrait or (ecart and not prem_corps))) or
                       (typ == "citation" and (ecart or (i > 0 and els[i - 1]["bloc"] != e["bloc"] and ecart))))
            if prem_corps and typ == "para" and not retrait and cour is not None and cour["t"] == "para":
                nouveau = False  # suite du paragraphe de la page précédente
            prem_corps = False
            if typ == "para" and cour is not None and cour["t"] == "citation" and not retrait:
                nouveau = True
            if nouveau:
                fin_para()
                cour = {"t": typ, "x": t, "p": [bp], "lignes": [t] if typ == "citation" else None}
            else:
                if typ == "citation" and cour.get("lignes") is not None:
                    cour["lignes"].append(t)
                cour["x"] = fusion(cour["x"], t) if cour["x"].endswith("-") else (
                    cour["x"] + t if cour["x"].endswith("—") else cour["x"] + " " + t)
                if bp not in cour["p"]: cour["p"].append(bp)
            i += 1
    fin_para()
    json.dump(flux, open("/tmp/farm/out/corps.json", "w"), ensure_ascii=False, indent=0)
    with open("/tmp/farm/out/corps.txt", "w") as f:
        for it in flux:
            x = it["x"]
            if it["t"] == "citation": x = "    " + x
            elif it["t"] == "legende": x = "[" + x + "]"
            elif it["t"] == "titre": x = x.upper()
            elif it["t"] == "lacune": x = "[" + x + "]"
            elif it["t"] == "document":
                l = x.split("\n"); x = l[0] + "\n" + "\n".join("    " + y for y in l[1:])
            f.write(f"{x}\n\n")
    sup = re.findall(r"⟦(.*?)⟧", " ".join(it["x"] for it in flux))
    json.dump(sup, open("/tmp/farm/out/appels.json", "w"))
    print(len(flux), "éléments ;", len(sup), "appels")


if __name__ == "__main__":
    main()
