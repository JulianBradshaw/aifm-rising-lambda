// Page logic: sliders, the Pyodide worker, and two hand-drawn SVG charts.
// No build step and no chart library; everything here runs as-is from GitHub Pages.

const PYODIDE_VERSION = '314.0.7';
const params = new URLSearchParams(location.search);
// ?pyodide=/local/path/ lets you test against a local copy of the Pyodide distribution.
const PYODIDE_BASE = params.get('pyodide') || `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;

const MILESTONES = ['AC', 'SAR', 'TED-AI', 'ASI'];
const PRESET_LABELS = { 'daniel-08-16-26': 'Daniel', 'eli-08-16-26': 'Eli', 'brendan-08-16-26': 'Brendan' };
const SVGNS = 'http://www.w3.org/2000/svg';

// ---------- formatting ----------
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
function fmtDate(t) {
  if (t == null) return 'not by 2040';
  const y = Math.floor(t);
  return `${MONTHS[Math.min(11, Math.floor((t - y) * 12))]} ${y}`;
}
function fmtMonths(m) {
  if (m == null) return '—';
  return `${m.toFixed(1)} months`;
}
function fmtSig(x) {
  if (x >= 1000) return Math.round(x / 100) * 100 >= 10000 ? `${Math.round(x / 1000)}k` : `${(x / 1000).toFixed(1)}k`;
  if (x >= 100) return String(Math.round(x / 5) * 5);
  return x < 20 ? x.toFixed(1).replace(/\.0$/, '') : String(Math.round(x));
}

// ---------- sliders ----------
// Sliders with `log` store a log10 value in the range input (the labor asymptote).
// Two-λ variant: λ stays at the preset's value for history and calibration; only coding labor growth after today uses the forward λ.
const SLIDERS = {
  lambda: { label: 'Forward λ', min: 0.3, max: 1, step: 0.05, fmt: (v) => v.toFixed(2),
    hint: (p) => `Applies to coding labor growth from today on; history and calibration keep the preset's ${p.lambda}. Small-team estimates today suggest about 0.65` },
  ila: { label: 'Coding-labor asymptote', min: 0.5, max: 4.3, step: 0.01, log: true, fmt: (v) => `${fmtSig(v)}×`,
    hint: (p) => `Preset ${fmtSig(p.ila)}×. Changing it recalibrates all three runs` },
};
const EXAMPLES = [
  { id: 'preset', label: 'Preset λ', set: (p) => ({ lambda: p.lambda, ila: p.ila, eta: 'linear' }) },
  { id: 'estimated', label: 'Estimated λ 0.65', set: (p) => ({ lambda: 0.65, ila: p.ila, eta: 'linear' }) },
  { id: 'full', label: 'λ 1', set: (p) => ({ lambda: 1, ila: p.ila, eta: 'linear' }) },
  { id: 'full100', label: 'λ 1, asymptote 100', set: () => ({ lambda: 1, ila: 100, eta: 'linear' }) },
];
const DEFAULTS = { lambda: 0.65, ila: 15, eta: 'linear', dates: 'native' };
const LABELS = { base: 'Preset λ', scen: 'Two-λ variant', comp: 'Original, one λ' };
// Settings held as strings, with their allowed values.
const CHOICES = { dates: ['native', 'legacy'], eta: ['linear', 'power', 'none'] };

const state = {
  preset: 'daniel-08-16-26',
  settings: { ...DEFAULTS },
  presetInfo: {},
  last: null, // last {baseline, scenario}
};

// ---------- share link: settings live in the URL hash ----------
function readHash() {
  const h = new URLSearchParams(location.hash.slice(1));
  if (PRESET_LABELS[h.get('preset')]) state.preset = h.get('preset');
  for (const key of Object.keys(DEFAULTS)) {
    if (!h.has(key)) continue;
    if (CHOICES[key]) { if (CHOICES[key].includes(h.get(key))) state.settings[key] = h.get(key); }
    else {
      const v = Number(h.get(key));
      if (Number.isFinite(v)) state.settings[key] = v;
    }
  }
}
function writeHash() {
  const h = new URLSearchParams({ preset: state.preset });
  for (const [k, v] of Object.entries(state.settings)) h.set(k, CHOICES[k] ? v : String(+v.toFixed(4)));
  history.replaceState(null, '', '#' + h.toString());
}

const $ = (sel) => document.querySelector(sel);

function buildControls() {
  for (const el of document.querySelectorAll('.slider')) {
    const key = el.dataset.key;
    const cfg = SLIDERS[key];
    el.innerHTML = `
      <div class="row"><label for="s-${key}">${cfg.label}</label><output id="o-${key}"></output></div>
      <input type="range" id="s-${key}" min="${cfg.min}" max="${cfg.max}" step="${cfg.step}">
      <div class="hint" id="h-${key}"></div>`;
    el.querySelector('input').addEventListener('input', (e) => {
      const raw = Number(e.target.value);
      state.settings[key] = cfg.log ? 10 ** raw : raw;
      syncControls();
      schedule();
    });
  }
  for (const key of Object.keys(CHOICES)) {
    $(`#${key}`)?.addEventListener('change', (e) => { state.settings[key] = e.target.value; syncControls(); schedule(0); });
  }
  $('#preset').addEventListener('change', (e) => { state.preset = e.target.value; ensurePreset().then(() => { syncControls(); schedule(0); }); });
  const chips = $('#examples');
  for (const ex of EXAMPLES) {
    const b = document.createElement('button');
    b.type = 'button'; b.textContent = ex.label; b.dataset.id = ex.id;
    b.addEventListener('click', () => {
      Object.assign(state.settings, ex.set(state.presetInfo[state.preset] || { lambda: 0.5, ila: 15 }));
      syncControls();
      schedule(0);
    });
    chips.appendChild(b);
  }
}

function syncControls() {
  const info = state.presetInfo[state.preset] || { lambda: 0.5, ila: 15 };
  for (const [key, cfg] of Object.entries(SLIDERS)) {
    const v = state.settings[key];
    const input = $(`#s-${key}`);
    input.value = cfg.log ? Math.log10(v) : v;
    $(`#o-${key}`).textContent = cfg.fmt(v);
    $(`#h-${key}`).textContent = cfg.hint(info);
  }
  $('#preset').value = state.preset;
  for (const key of Object.keys(CHOICES)) if ($(`#${key}`)) $(`#${key}`).value = state.settings[key];
  for (const b of document.querySelectorAll('#examples button')) {
    const target = EXAMPLES.find((x) => x.id === b.dataset.id).set(info);
    const match = Object.entries(target).every(([k, v]) => (typeof v === 'number' ? Math.abs(state.settings[k] - v) < 1e-6 * Math.max(1, Math.abs(v)) : state.settings[k] === v));
    b.setAttribute('aria-pressed', String(match));
  }
  writeHash();
}

// ---------- worker ----------
const worker = new Worker('worker.js', { type: 'module' });
let ready = false;
let runId = 0;
let inflight = null; // id of the running request
let pending = false; // settings changed while a run was in flight
let timer = null;
const waiters = {};

function setStatus(text, { spin = false, error = false } = {}) {
  const el = $('#status');
  el.classList.toggle('error', error);
  el.innerHTML = (spin ? '<span class="spin" aria-hidden="true"></span>' : '') + `<span></span>`;
  el.lastChild.textContent = text;
}

worker.onmessage = (e) => {
  const msg = e.data;
  if (msg.type === 'progress') setStatus(msg.text + '…', { spin: true });
  else if (msg.type === 'ready') { ready = true; waiters.ready?.(); }
  else if (msg.type === 'preset') { state.presetInfo[msg.preset] = msg.info; waiters[msg.preset]?.(); }
  else if (msg.type === 'result') onResult(msg);
  else if (msg.type === 'error') onError(msg);
};

function waitFor(key) { return new Promise((resolve) => { waiters[key] = resolve; }); }

async function ensurePreset() {
  if (state.presetInfo[state.preset]) return;
  const done = waitFor(state.preset);
  worker.postMessage({ type: 'preset', preset: state.preset, label: PRESET_LABELS[state.preset] });
  await done;
}

function schedule(delay = 200) {
  if (!ready) return;
  clearTimeout(timer);
  timer = setTimeout(send, delay);
}

function send() {
  if (inflight !== null) { pending = true; return; }
  pending = false;
  inflight = ++runId;
  $('.results').classList.add('busy');
  setStatus(state.last ? 'Solving…' : `Solving the ${LABELS.base.toLowerCase()} and ${LABELS.scen.toLowerCase()} runs…`, { spin: true });
  worker.postMessage({ type: 'run', id: inflight, preset: state.preset, settings: { ...state.settings } });
}

function onResult(msg) {
  inflight = null;
  if (pending) { send(); return; }
  $('.results').classList.remove('busy');
  state.last = { ...msg.data, settings: { ...state.settings } };
  const notes = [`Solved in ${(msg.ms / 1000).toFixed(1)} s.`];
  setStatus(notes.join(' '));
  render();
}

function onError(msg) {
  if (msg.stage === 'init' || msg.stage === 'preset') {
    setStatus(`Could not start the model: ${msg.message}`, { error: true });
    return;
  }
  inflight = null;
  if (pending) { send(); return; }
  $('.results').classList.remove('busy');
  setStatus(`The model rejected these settings: ${msg.message}`, { error: true });
}

// ---------- charts ----------
function el(tag, attrs = {}, parent) {
  const node = document.createElementNS(SVGNS, tag);
  for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
  if (parent) parent.appendChild(node);
  return node;
}
function text(parent, x, y, str, attrs = {}) {
  const t = el('text', { x, y, ...attrs }, parent);
  t.textContent = str;
  return t;
}
function linear(d0, d1, r0, r1) {
  const f = (v) => r0 + ((v - d0) / (d1 - d0)) * (r1 - r0);
  f.range0 = r0;
  f.invert = (p) => d0 + ((p - r0) / (r1 - r0)) * (d1 - d0);
  return f;
}

const tooltip = $('#tooltip');
function showTip(evt, html) {
  tooltip.innerHTML = html;
  tooltip.hidden = false;
  const pad = 14;
  const { innerWidth: W, innerHeight: H } = window;
  const r = tooltip.getBoundingClientRect();
  let x = evt.clientX + pad, y = evt.clientY + pad;
  if (x + r.width > W - 8) x = evt.clientX - r.width - pad;
  if (y + r.height > H - 8) y = evt.clientY - r.height - pad;
  tooltip.style.left = `${Math.max(8, x)}px`;
  tooltip.style.top = `${Math.max(8, y)}px`;
}
function hideTip() { tooltip.hidden = true; }

function series(last) {
  return [last.baseline, last.scenario, last.comparison].filter(Boolean);
}

function timeDomain(last) {
  const dates = [];
  for (const r of series(last)) for (const k of MILESTONES) if (r.milestones[k] != null) dates.push(r.milestones[k]);
  const unreached = series(last).some((r) => MILESTONES.some((k) => r.milestones[k] == null));
  let hi = Math.max(...dates);
  if (unreached) hi = Math.max(hi + 2, 2032);
  hi = Math.min(2040, Math.ceil((hi + 0.4) * 2) / 2);
  const lo = 2026.5;
  return [lo, hi];
}

function yearTicks(lo, hi, px) {
  // Keep tick labels at least ~56px apart.
  const step = [0.5, 1, 2, 5].find((s) => (px * s) / (hi - lo) >= (s < 1 ? 64 : 44)) || 5;
  const ticks = [];
  for (let t = Math.ceil(lo / step) * step; t <= hi + 1e-9; t += step) ticks.push(+t.toFixed(2));
  return ticks;
}
function tickLabel(t) { return Number.isInteger(t) ? String(t) : `Jul ${Math.floor(t)}`; }

function drawTimeAxis(svg, x, lo, hi, top, bottom) {
  const g = el('g', {}, svg);
  for (const t of yearTicks(lo, hi, x(hi) - x(lo))) {
    const px = x(t);
    el('line', { class: 'grid', x1: px, x2: px, y1: top, y2: bottom }, g);
    text(g, px, bottom + 16, tickLabel(t), { 'text-anchor': 'middle' });
  }
  el('line', { class: 'axis', x1: x(lo), x2: x(hi), y1: bottom, y2: bottom }, g);
}

function renderMilestones() {
  const { baseline, scenario, comparison } = state.last;
  const host = $('#milestones');
  const W = Math.max(300, host.clientWidth);
  const narrow = W < 520;
  // On narrow screens the row names sit above each row instead of in a left margin.
  const M = { l: narrow ? 12 : 96, r: narrow ? 84 : 96, t: 14, b: 26 };
  const rows = [
    { label: LABELS.base, data: baseline, color: 'var(--base)', dash: '5 4' },
    { label: LABELS.scen, data: scenario, color: 'var(--scen)', dash: null },
  ];
  if (comparison) rows.push({ label: LABELS.comp, data: comparison, color: 'var(--comp)', dash: '1 3' });
  const rowH = narrow ? 70 : 52;
  const H = M.t + rows.length * rowH + M.b;
  const [lo, hi] = timeDomain(state.last);
  const x = linear(lo, hi, M.l, W - M.r);
  const svg = el('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': `Milestone dates: ${rows.map((row) => row.label).join(', ')}` });
  drawTimeAxis(svg, x, lo, hi, M.t, H - M.b);

  rows.forEach((row, i) => {
    const y = M.t + i * rowH + rowH / 2 + (narrow ? 14 : 6);
    if (narrow) text(svg, M.l, y - 30, row.label, { class: 'row-label' });
    else text(svg, M.l - 10, y + 4, row.label, { class: 'row-label', 'text-anchor': 'end' });
    const ms = row.data.milestones;
    const ac = ms.AC, asi = ms.ASI;
    if (ac != null) {
      const end = asi ?? hi;
      el('line', { x1: x(ac), x2: x(end), y1: y, y2: y, stroke: row.color, 'stroke-width': 2,
        'stroke-dasharray': asi == null ? '2 4' : (row.dash || 'none') }, svg);
    }
    // Labels: AC and ASI by name; SAR and TED-AI are named in the tooltip only.
    if (ac != null && asi != null && x(asi) - x(ac) < 46) {
      text(svg, (x(ac) + x(asi)) / 2, y - 12, 'AC→ASI', { class: 'ms-label', 'text-anchor': 'middle' });
    } else {
      if (ac != null) text(svg, x(ac), y - 12, 'AC', { class: 'ms-label', 'text-anchor': 'middle' });
      if (asi != null) text(svg, x(asi), y - 12, 'ASI', { class: 'ms-label', 'text-anchor': 'middle' });
    }
    const right = asi ?? (ac != null ? hi : null);
    const note = asi != null ? fmtMonths(row.data.takeoff_months) : ac != null ? 'no ASI by 2040' : 'no AC by 2040';
    text(svg, (right != null ? x(right) : x(lo)) + 10, y + 4, note, { class: 'takeoff' });
    for (const k of MILESTONES) {
      const t = ms[k];
      if (t == null) continue;
      const big = k === 'AC' || k === 'ASI';
      el('circle', { cx: x(t), cy: y, r: big ? 6 : 4.5, fill: row.color, stroke: 'var(--surface)', 'stroke-width': 2 }, svg);
      const hit = el('circle', { cx: x(t), cy: y, r: 12, fill: 'transparent' }, svg);
      hit.addEventListener('pointermove', (evt) => showTip(evt, `<strong>${row.label}: ${k}</strong><div>${fmtDate(t)} (${t.toFixed(2)})</div>`));
      hit.addEventListener('pointerleave', hideTip);
    }
  });
  host.replaceChildren(svg);
}

function interp(times, values, t) {
  if (!times.length || t < times[0] || t > times[times.length - 1]) return null;
  let a = 0, b = times.length - 1;
  while (b - a > 1) { const m = (a + b) >> 1; if (times[m] <= t) a = m; else b = m; }
  const f = times[b] === times[a] ? 0 : (t - times[a]) / (times[b] - times[a]);
  return values[a] + f * (values[b] - values[a]);
}

function renderTrajectory() {
  const { baseline, scenario, comparison } = state.last;
  const host = $('#trajectory');
  const W = Math.max(300, host.clientWidth);
  const H = W < 520 ? 240 : 300;
  const M = { l: 40, r: 52, t: 10, b: 26 };
  const [lo, hi] = timeDomain(state.last);
  const th = baseline.thresholds;
  const inRange = (r) => r.times.map((t, i) => [t, r.log10_E_eff[i]]).filter(([t]) => t >= lo && t <= hi);
  const pb = inRange(baseline), ps = inRange(scenario), pc = comparison ? inRange(comparison) : [];
  const all = [...pb, ...ps, ...pc].map((p) => p[1]);
  const yLo = Math.floor(Math.min(...all));
  const yHi = Math.ceil(Math.min(Math.max(...all), th.ASI + 3));
  const x = linear(lo, hi, M.l, W - M.r);
  const y = linear(yLo, yHi, H - M.b, M.t);
  const svg = el('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': 'Effective capability over time' });
  const clipId = 'clip-traj';
  const clip = el('clipPath', { id: clipId }, el('defs', {}, svg));
  el('rect', { x: M.l, y: M.t, width: W - M.l - M.r, height: H - M.t - M.b }, clip);

  drawTimeAxis(svg, x, lo, hi, M.t, H - M.b);
  const ystep = yHi - yLo > 12 ? 4 : 2;
  for (let v = Math.ceil(yLo / ystep) * ystep; v <= yHi; v += ystep) {
    el('line', { class: 'grid', x1: M.l, x2: W - M.r, y1: y(v), y2: y(v) }, svg);
    text(svg, M.l - 6, y(v) + 4, String(v), { 'text-anchor': 'end' });
  }
  let lastLabelY = -Infinity;
  for (const k of [...MILESTONES].reverse()) {
    const v = th[k];
    if (v < yLo || v > yHi) continue;
    el('line', { class: 'thresh', x1: M.l, x2: W - M.r, y1: y(v), y2: y(v) }, svg);
    const ly = Math.max(y(v) + 4, lastLabelY + 12);
    text(svg, W - M.r + 6, ly, k, { class: 'ms-label' });
    lastLabelY = ly;
  }
  const path = (pts) => pts.map(([t, v], i) => `${i ? 'L' : 'M'}${x(t).toFixed(1)},${y(v).toFixed(1)}`).join('');
  const g = el('g', { 'clip-path': `url(#${clipId})` }, svg);
  el('path', { d: path(pb), fill: 'none', stroke: 'var(--base)', 'stroke-width': 2, 'stroke-dasharray': '5 4' }, g);
  if (pc.length) el('path', { d: path(pc), fill: 'none', stroke: 'var(--comp)', 'stroke-width': 2, 'stroke-dasharray': '1 3' }, g);
  el('path', { d: path(ps), fill: 'none', stroke: 'var(--scen)', 'stroke-width': 2 }, g);

  // Crosshair and tooltip.
  const cross = el('g', { visibility: 'hidden' }, svg);
  const vline = el('line', { class: 'axis', y1: M.t, y2: H - M.b }, cross);
  const dotB = el('circle', { r: 4, fill: 'var(--base)', stroke: 'var(--surface)', 'stroke-width': 2 }, cross);
  const dotS = el('circle', { r: 4, fill: 'var(--scen)', stroke: 'var(--surface)', 'stroke-width': 2 }, cross);
  const dotC = el('circle', { r: 4, fill: 'var(--comp)', stroke: 'var(--surface)', 'stroke-width': 2, visibility: 'hidden' }, cross);
  const overlay = el('rect', { x: M.l, y: M.t, width: W - M.l - M.r, height: H - M.t - M.b, fill: 'transparent' }, svg);
  overlay.addEventListener('pointermove', (evt) => {
    const box = svg.getBoundingClientRect();
    const px = ((evt.clientX - box.left) / box.width) * W;
    const t = x.invert(px);
    const vb = interp(baseline.times, baseline.log10_E_eff, t);
    const vs = interp(scenario.times, scenario.log10_E_eff, t);
    const vc = comparison ? interp(comparison.times, comparison.log10_E_eff, t) : null;
    cross.setAttribute('visibility', 'visible');
    vline.setAttribute('x1', px); vline.setAttribute('x2', px);
    for (const [dot, v] of [[dotB, vb], [dotS, vs], [dotC, vc]]) {
      const show = v != null && v >= yLo && v <= yHi;
      dot.setAttribute('visibility', show ? 'visible' : 'hidden');
      if (show) { dot.setAttribute('cx', px); dot.setAttribute('cy', y(v)); }
    }
    const row = (name, v) => `<div class="t-row"><span>${name}</span><span>${v == null ? '—' : v.toFixed(1)}</span></div>`;
    showTip(evt, `<strong>${fmtDate(t)}</strong>${row(LABELS.base, vb)}${row(LABELS.scen, vs)}${comparison ? row(LABELS.comp, vc) : ''}`);
  });
  overlay.addEventListener('pointerleave', () => { cross.setAttribute('visibility', 'hidden'); hideTip(); });
  host.replaceChildren(svg);
}

function delta(scen, base, unit, name = LABELS.base.toLowerCase()) {
  if (scen == null || base == null) return '';
  const d = unit === 'date' ? (scen - base) * 12 : scen - base;
  if (Math.abs(d) < 0.05) return `same as ${name}`;
  const word = unit === 'date' ? (d < 0 ? 'earlier' : 'later') : (d < 0 ? 'shorter' : 'longer');
  return `${Math.abs(d).toFixed(1)} months ${word} than ${name}`;
}

function renderStats() {
  const { baseline: b, scenario: s, comparison: c } = state.last;
  const tiles = [
    ['Automated coder (AC)', fmtDate(s.milestones.AC), delta(s.milestones.AC, b.milestones.AC, 'date')],
    ['Superintelligence (ASI)', fmtDate(s.milestones.ASI), delta(s.milestones.ASI, b.milestones.ASI, 'date')],
    ['Takeoff, AC to ASI', fmtMonths(s.takeoff_months), delta(s.takeoff_months, b.takeoff_months, 'months')],
  ];
  if (c) tiles.push([`${LABELS.comp}: takeoff`, fmtMonths(c.takeoff_months), `AC ${fmtDate(c.milestones.AC)}, ASI ${fmtDate(c.milestones.ASI)}`]);
  $('#stats').innerHTML = tiles.map(() => '<div class="stat"><div class="label"></div><div class="value"></div><div class="delta"></div></div>').join('');
  [...$('#stats').children].forEach((node, i) => {
    node.querySelector('.label').textContent = tiles[i][0];
    node.querySelector('.value').textContent = tiles[i][1];
    node.querySelector('.delta').textContent = tiles[i][2] || `${LABELS.base.toLowerCase()} ${i < 2 ? fmtDate([b.milestones.AC, b.milestones.ASI][i]) : fmtMonths(b.takeoff_months)}`;
  });
}

function renderTable() {
  const { baseline: b, scenario: s, comparison: c } = state.last;
  const fmt = (t) => (t == null ? 'not by 2040' : `${fmtDate(t)} (${t.toFixed(3)})`);
  const extra = (v, f) => (c ? `<td>${f(v)}</td>` : '');
  const html = [`<thead><tr><th>Milestone</th><th>${LABELS.base}</th><th>${LABELS.scen}</th><th>Difference</th>${c ? `<th>${LABELS.comp}</th>` : ''}</tr></thead><tbody>`];
  for (const k of MILESTONES) {
    const [tb, ts] = [b.milestones[k], s.milestones[k]];
    html.push(`<tr><td>${k}</td><td>${fmt(tb)}</td><td>${fmt(ts)}</td><td>${delta(ts, tb, 'date') || '—'}</td>${extra(c?.milestones[k], fmt)}</tr>`);
  }
  html.push(`<tr><td>Takeoff</td><td>${fmtMonths(b.takeoff_months)}</td><td>${fmtMonths(s.takeoff_months)}</td><td>${delta(s.takeoff_months, b.takeoff_months, 'months') || '—'}</td>${extra(c?.takeoff_months, fmtMonths)}</tr></tbody>`);
  $('#table').innerHTML = html.join('');
}

function render() {
  if (!state.last) return;
  renderStats();
  renderMilestones();
  renderTrajectory();
  renderTable();
}

let resizeTimer = null;
window.addEventListener('resize', () => { clearTimeout(resizeTimer); resizeTimer = setTimeout(render, 100); });

// ---------- start ----------
readHash();
buildControls();
syncControls();
(async () => {
  const started = performance.now();
  const readyP = waitFor('ready');
  worker.postMessage({ type: 'init', pyodideBase: PYODIDE_BASE });
  await readyP;
  await ensurePreset();
  syncControls();
  window.__loadSeconds = (performance.now() - started) / 1000;
  schedule(0);
})();
