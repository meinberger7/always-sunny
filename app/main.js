const state = {
  mode: 'harvested',
  hourIndex: 23,
  playing: false,
  selectedBa: null,
  buildout: '60',
  transmission: 'regional'
};

const els = {
  headline: document.getElementById('headline'),
  caveat: document.getElementById('mode-caveat'),
  orientationLayer: document.getElementById('map-orientation-layer'),
  timeSlider: document.getElementById('time-slider'),
  timeLabel: document.getElementById('time-label'),
  playBtn: document.getElementById('play-btn'),
  baLayer: document.getElementById('ba-layer'),
  tooltip: document.getElementById('tooltip'),
  detail: document.getElementById('detail-content'),
  lineChart: document.getElementById('line-chart'),
  harvestedBtn: document.getElementById('mode-harvested'),
  harvestableBtn: document.getElementById('mode-harvestable'),
  harvestableControls: document.getElementById('harvestable-controls'),
  buildoutSelect: document.getElementById('buildout-select'),
  transmissionSelect: document.getElementById('transmission-select')
};

const projection = (lat, lon) => {
  const x = ((lon + 125) / 59) * 760 + 100;
  const y = ((49 - lat) / 25) * 290 + 120;
  return [x, y];
};

const lower48Outline = [
  [48.9, -124.7], [47.8, -124.4], [46.2, -123.8], [44.7, -124.2], [42.0, -124.3],
  [40.0, -124.1], [38.0, -123.1], [36.5, -122.4], [34.8, -120.5], [34.0, -118.4],
  [32.7, -117.2], [31.3, -111.1], [29.7, -108.2], [28.9, -106.5], [29.1, -103.0],
  [28.9, -100.0], [29.2, -97.2], [27.9, -97.0], [27.5, -96.2], [28.9, -94.1],
  [29.7, -92.6], [29.3, -89.6], [30.2, -87.7], [30.4, -85.5], [29.8, -84.1],
  [30.7, -82.5], [28.8, -80.0], [25.2, -80.1], [26.8, -81.7], [30.0, -81.5],
  [31.6, -80.7], [32.2, -79.3], [33.1, -78.4], [34.6, -76.8], [36.5, -75.9],
  [39.0, -74.4], [40.7, -73.5], [41.3, -71.9], [42.9, -70.7], [44.7, -67.0],
  [45.7, -67.1], [47.0, -69.2], [45.0, -72.4], [45.0, -75.1], [44.1, -76.4],
  [43.5, -79.2], [42.3, -82.5], [43.0, -84.8], [46.2, -90.4], [48.8, -95.2],
  [49.0, -104.2], [49.0, -110.2], [49.0, -114.3], [48.9, -124.7]
];

const orientationLines = [
  [[49.0, -120.0], [32.5, -120.0]],
  [[49.0, -112.0], [31.0, -112.0]],
  [[49.0, -104.0], [29.0, -104.0]],
  [[48.5, -96.0], [27.5, -96.0]],
  [[47.0, -88.0], [29.0, -88.0]],
  [[46.5, -80.0], [32.0, -80.0]],
  [[45.0, -124.0], [45.0, -67.0]],
  [[40.0, -124.0], [40.0, -73.5]],
  [[35.0, -121.0], [35.0, -75.5]]
];

function buildMapOrientationLayer() {
  const points = lower48Outline.map(([lat, lon]) => {
    const [x, y] = projection(lat, lon);
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  });

  const outlinePath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  outlinePath.setAttribute('d', `M${points.join(' L')} Z`);
  outlinePath.setAttribute('class', 'us-outline');
  els.orientationLayer.appendChild(outlinePath);

  orientationLines.forEach(([[latA, lonA], [latB, lonB]]) => {
    const [x1, y1] = projection(latA, lonA);
    const [x2, y2] = projection(latB, lonB);
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', x1.toFixed(1));
    line.setAttribute('y1', y1.toFixed(1));
    line.setAttribute('x2', x2.toFixed(1));
    line.setAttribute('y2', y2.toFixed(1));
    line.setAttribute('class', 'state-line');
    els.orientationLayer.appendChild(line);
  });
}

let observed = [];
let harvestable = [];

function fmtPct(v) { return `${(v * 100).toFixed(1)}%`; }
function fmtMw(v) { return `${Math.round(v).toLocaleString()} MW`; }

function groupByHour(rows) {
  return rows.reduce((acc, row) => {
    const key = row.timestamp_utc;
    acc[key] ||= [];
    acc[key].push(row);
    return acc;
  }, {});
}

function getCurrentRows() {
  if (state.mode === 'harvested') {
    const hours = Object.keys(groupByHour(observed)).sort();
    return groupByHour(observed)[hours[state.hourIndex]] ?? [];
  }
  const filtered = harvestable.filter(
    r => String(r.buildout_target_pct_of_annual_demand) === state.buildout && r.transmission_scope === state.transmission
  );
  const hours = Object.keys(groupByHour(filtered)).sort();
  return groupByHour(filtered)[hours[state.hourIndex]] ?? [];
}

function updateHeadline(rows) {
  if (!rows.length) return;
  if (state.mode === 'harvested') {
    const ws = rows.reduce((s, r) => s + r.wind_solar_mw, 0);
    const gen = rows.reduce((s, r) => s + r.total_generation_mw, 0);
    els.headline.textContent = `At this hour, wind and solar provided ${fmtPct(ws / gen)} of BA-visible generation.`;
    els.caveat.textContent = 'Harvested mode shows BA-visible, utility-scale-visible observed values. This is not a full reliability model.';
  } else {
    const harvestTotal = rows.reduce((s, r) => s + r.harvestable_total_mw, 0);
    const demand = observed.filter(o => o.timestamp_utc === rows[0].timestamp_utc).reduce((s, r) => s + r.demand_mw, 0);
    els.headline.textContent = `Under this scenario, a built-out wind/solar fleet could have harvested energy equal to ${fmtPct(harvestTotal / demand)} of demand.`;
    els.caveat.textContent = 'Harvestable mode is modeled and scenario-based. It demonstrates geographic diversity and transmission/storage assumptions.';
  }
}

function drawMap(rows) {
  els.baLayer.innerHTML = '';
  rows.forEach(row => {
    const [cx, cy] = projection(row.lat, row.lon);
    const val = state.mode === 'harvested' ? row.wind_solar_mw : row.harvestable_total_mw;
    const radius = Math.max(5, Math.min(16, val / 2200));
    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute('cx', cx);
    circle.setAttribute('cy', cy);
    circle.setAttribute('r', radius);
    circle.setAttribute('fill', state.mode === 'harvested' ? '#1f6feb' : '#d97706');
    circle.setAttribute('class', 'ba-dot');
    circle.addEventListener('mouseenter', e => {
      els.tooltip.classList.remove('hidden');
      els.tooltip.style.left = `${e.offsetX + 12}px`;
      els.tooltip.style.top = `${e.offsetY + 12}px`;
      els.tooltip.textContent = `${row.ba_code}: ${fmtMw(val)}`;
    });
    circle.addEventListener('mouseleave', () => els.tooltip.classList.add('hidden'));
    circle.addEventListener('click', () => {
      state.selectedBa = row.ba_code;
      updateDetail(row);
    });
    els.baLayer.appendChild(circle);
  });
}

function updateDetail(row) {
  const body = state.mode === 'harvested'
    ? `<strong>${row.ba_name}</strong><br/>Wind: ${fmtMw(row.wind_mw)}<br/>Solar: ${fmtMw(row.solar_mw)}<br/>Wind+Solar share: ${fmtPct(row.wind_solar_share_of_generation)}`
    : `<strong>${row.ba_name}</strong><br/>Scenario: ${row.scenario_id}<br/>Harvestable wind: ${fmtMw(row.harvestable_wind_mw)}<br/>Harvestable solar: ${fmtMw(row.harvestable_solar_mw)}`;
  els.detail.innerHTML = body;
}

function drawLineChart() {
  const width = 960, height = 220, pad = 30;
  const rows = state.mode === 'harvested'
    ? observed
    : harvestable.filter(r => String(r.buildout_target_pct_of_annual_demand) === state.buildout && r.transmission_scope === state.transmission);
  const hourly = Object.entries(groupByHour(rows)).sort(([a], [b]) => a.localeCompare(b)).map(([ts, rs], i) => ({
    i,
    ts,
    value: rs.reduce((sum, r) => sum + (state.mode === 'harvested' ? r.wind_solar_mw : r.harvestable_total_mw), 0)
  }));
  const max = Math.max(...hourly.map(h => h.value));
  const pts = hourly.map(h => {
    const x = pad + (h.i / (hourly.length - 1)) * (width - pad * 2);
    const y = height - pad - (h.value / max) * (height - pad * 2);
    return `${x},${y}`;
  }).join(' ');
  const cursorX = pad + (state.hourIndex / (hourly.length - 1)) * (width - pad * 2);
  els.lineChart.innerHTML = `
    <line x1="${pad}" y1="${height - pad}" x2="${width - pad}" y2="${height - pad}" stroke="#94a3b8" />
    <polyline fill="none" stroke="${state.mode === 'harvested' ? '#1f6feb' : '#d97706'}" stroke-width="3" points="${pts}" />
    <line x1="${cursorX}" y1="${pad}" x2="${cursorX}" y2="${height - pad}" stroke="#111827" stroke-dasharray="4 4"/>
  `;
}

function render() {
  const rows = getCurrentRows();
  if (!rows.length) return;
  els.timeLabel.textContent = rows[0].timestamp_local;
  updateHeadline(rows);
  drawMap(rows);
  drawLineChart();
  const selected = rows.find(r => r.ba_code === state.selectedBa) ?? rows[0];
  updateDetail(selected);
}

function setMode(mode) {
  state.mode = mode;
  els.harvestedBtn.classList.toggle('active', mode === 'harvested');
  els.harvestableBtn.classList.toggle('active', mode === 'harvestable');
  els.harvestableControls.classList.toggle('hidden', mode === 'harvested');
  render();
}

function bindEvents() {
  els.timeSlider.addEventListener('input', e => {
    state.hourIndex = Number(e.target.value);
    render();
  });
  els.playBtn.addEventListener('click', () => {
    state.playing = !state.playing;
    els.playBtn.textContent = state.playing ? 'Pause' : 'Play';
  });
  setInterval(() => {
    if (!state.playing) return;
    state.hourIndex = (state.hourIndex + 1) % 24;
    els.timeSlider.value = state.hourIndex;
    render();
  }, 1100);
  els.harvestedBtn.addEventListener('click', () => setMode('harvested'));
  els.harvestableBtn.addEventListener('click', () => setMode('harvestable'));
  els.buildoutSelect.addEventListener('change', e => { state.buildout = e.target.value; render(); });
  els.transmissionSelect.addEventListener('change', e => { state.transmission = e.target.value; render(); });
}

async function init() {
  buildMapOrientationLayer();
  observed = await fetch('./data/processed/observed_hourly.json').then(r => r.json());
  harvestable = await fetch('./data/demo/harvestable_demo.json').then(r => r.json());
  bindEvents();
  render();
}

init();
