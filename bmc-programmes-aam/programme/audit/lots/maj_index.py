p = '/Users/sylvain/Documents/bmc-programmes-aam/semainier/index.html'
s = open(p).read()
R = [
('''function filtres() {
  const q = etat.q.toLowerCase().trim();
  return D.events.filter(e => (etat.spec || !e.extendedProps.spec) && etat.familles.has(e.extendedProps.fam) && e.extendedProps.pct <= etat.maxPct && (!q || e._txt.includes(q)));
}''',
'''function garde(e) {
  const q = etat.q.toLowerCase().trim();
  return etat.familles.has(e.extendedProps.fam) && e.extendedProps.pct <= etat.maxPct && (!q || e._txt.includes(q));
}
const JOURS_ABR = ["lun", "mar", "mer", "jeu", "ven", "sam", "dim"];
const plusJours = (s, n) => { const x = new Date(s + "T12:00"); x.setDate(x.getDate() + n); return iso(x); };
// couche spéculative : gabarit du trimestre appliqué à chacune de ses semaines, seulement pour les dates demandées
const GAB = {};
for (const [an, Y] of Object.entries(D.spec || {})) for (const g of Y.gabarits) (GAB[an + "|" + g.terme] ||= []).push(g);
function specEntre(a, b) {
  if (!etat.spec) return [];
  const out = [];
  for (const [an, Y] of Object.entries(D.spec || {})) for (const S of Y.semaines) {
    if (S.lundi >= b || plusJours(S.lundi, 7) <= a) continue;
    const jours = new Set(S.jours);
    (GAB[an + "|" + S.terme] || []).forEach((g, k) => {
      const f = FAM_DE[g.type] || FAMILLES[4];
      let start, end, allDay = false;
      if (g.jour === "semaine") { start = S.lundi; end = plusJours(S.lundi, 7); allDay = true; }
      else {
        const d = plusJours(S.lundi, JOURS_ABR.indexOf(g.jour));
        if (!jours.has(d) || d < a || d >= b) return;
        if (g.debut) { start = `${d}T${g.debut}`; end = `${d}T${g.fin || g.debut}`; } else { start = d; end = plusJours(d, 1); allDay = true; }
      }
      const e = { id: `s:${an}:${S.lundi}:${k}`, title: g.activite, start, end, allDay, resourceIds: g.resourceIds,
        backgroundColor: teinte(f[2], .85), textColor: f[2],
        extendedProps: { type: g.type, fam: f[0], qui: g.qui, lieu: g.lieu, note: g.note, pct: g.part_deduite_pct, motifs: g.motifs_deduction,
          rec: false, src: g.document_source, inv: g.inventaire, url: g.url_source, heure: g.debut, fin: g.fin, spec: true, codes: g.codes,
          annee: an, terme: g.libelle_terme, semaine: S.numero, placement: "reconstitution : jour et heure proposés (voir la part déduite)",
          unite: g.unite, discipline: g.discipline, cours_catalogue: g.cours_catalogue, precision: g.precision, candidats: g.candidats,
          chance: g.chance, rattachement: g.rattachement, equivalent_avant: g.equivalent_avant, equivalent_apres: g.equivalent_apres,
          part_case_pct: g.part_case_pct, part_titre_pct: g.part_titre_pct } };
      e._txt = (e.title + " " + g.qui + " " + g.resourceIds.join(" ")).toLowerCase();
      if (garde(e)) out.push(e);
    });
  }
  return out;
}
function evenementsEntre(a, b) {
  return D.events.filter(e => { const d = e.start.slice(0, 10); return d >= a && d < b && garde(e); }).concat(specEntre(a, b));
}'''),
('  events: filtres(),', '  eventSources: [{ events: info => evenementsEntre(iso(info.start), iso(info.end)) }],'),
('  const evs = filtres().filter(e => e.start.slice(0, 10) >= a && e.start.slice(0, 10) < b);', '  const evs = evenementsEntre(a, b);'),
('    const cle = Object.keys(D.analyses || {}).find(k => k >= a && k < b);', '    const cle = sp[0].extendedProps.annee;'),
("""      ${ligne("Couche", p.spec ? `<b>spéculative</b> : reconstitution, pas un fait attesté · codes ${esc(p.codes)} · <a href="#" onclick="analyse('${esc(p.analyse.slice(-13, -3))}');return false">analyse de la semaine</a>` : "")}""",
 """      ${ligne("Couche", p.spec ? `<b>spéculative</b> : reconstitution, pas un fait attesté · ${esc(p.terme)}, semaine ${p.semaine} · codes ${esc(p.codes)} · <a href="#" onclick="analyse('${esc(p.annee)}');return false">analyse de l'année</a>` : "")}"""),
("""      ${p.unite ? ligne("En 1934-35", esc(p.equivalent_1934_35) + ' <span class="legende">(fiche 6577)</span>') : ""}
      ${p.unite ? ligne("En 1936-38", esc(p.equivalent_1936_38) + ' <span class="legende">(2017.40.012)</span>') : ""}""",
 """      ${p.unite ? ligne("Année précédente", esc(p.equivalent_avant)) : ""}
      ${p.unite ? ligne("Année suivante", esc(p.equivalent_apres)) : ""}"""),
('  const md = (D.analyses || {})[k]; if (!md) return;', '  const md = ((D.spec || {})[k] || {}).analyse; if (!md) return;'),
('  ec.setOption("events", filtres());', '  ec.refetchEvents();'),
("""rep.innerHTML += `<optgroup label="Semaines reconstituées (spéculatif)">${Object.keys(D.analyses || {}).map(k => `<option value="${k}">${k} · reconstitution</option>`).join("")}</optgroup>`;""",
 """rep.innerHTML += `<optgroup label="Années reconstituées (spéculatif)">${Object.entries(D.spec || {}).map(([k, Y]) => `<option value="${Y.semaines[0].lundi}">${k} · ${Y.semaines.length} semaines</option>`).join("")}</optgroup>`;"""),
("${sp.length} entrées spéculatives (cadre pointillé), part déduite moyenne ${moy} %.",
 "${sp.length} entrées spéculatives (cadre pointillé), part déduite moyenne ${moy} %, d'après le gabarit « ${esc(sp[0].extendedProps.terme)} »."),
("Aucun document ne donne le programme de cette semaine : tout est reconstitué à partir de catalogues de l'année ou des années voisines.",
 "Aucun document ne donne le programme précis de cette semaine : le gabarit du trimestre est reconstitué à partir des catalogues de l'année et des années voisines."),
("Lire l'analyse et le barème", "Lire l'analyse de l'année et le barème"),
]
for a, b in R:
    assert a in s, a[:70]
    s = s.replace(a, b)
open(p, 'w').write(s)
print('ok')
