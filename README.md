# Always Sunny Explorer

Public-facing browser-first MVP dashboard showing hourly wind/solar diversity across U.S. balancing authorities (BAs).

## Purpose
The app is designed to communicate:

> Wind and solar are variable locally, but across a large, connected grid they are geographically diverse. It is often windy or sunny somewhere.

## MVP features
- Single contiguous-U.S. map with BA markers.
- One time slider + play control.
- Two modes:
  - **Harvested** (observed BA-visible utility-scale-visible values).
  - **Harvestable** (modeled scenario-based values).
- Harvestable controls:
  - Buildout target: 20/40/60/80% of annual demand.
  - Transmission assumption: local / regional / national.
- Linked 24-hour line chart.
- BA detail panel + tooltip.
- Methods/caveats page.

## Browser-first workflow
No backend required for v1.

### Option A: GitHub Pages (recommended)
1. Push to GitHub.
2. Enable Pages using GitHub Actions.
3. `deploy.yml` publishes static assets from `app/` and `data/`.

### Option B: Local static preview
```bash
python -m http.server 8000
# open http://localhost:8000/app/
```

## Data layout
- `data/raw/`: incoming observed raw files (EIA-930 integration slot).
- `data/processed/`: app-ready normalized observed assets.
- `data/demo/`: demo harvestable scenario outputs and manifest.

## Scripts
```bash
python scripts/fetch_observed_data.py
python scripts/build_observed_assets.py
python scripts/build_demo_harvestable_assets.py
python tests/validate_assets.py
```

## Cloud/Codex-friendly notes
- Minimal dependencies (Python stdlib + vanilla HTML/CSS/JS).
- Deterministic script outputs.
- Committed sample processed/demo data so UI runs without fresh pulls.

## Data refresh notes
- `refresh_observed.yml` can run on schedule and commit updated observed assets.
- Current `fetch_observed_data.py` is a scaffold placeholder for live EIA-930 ingestion.

## Known limitations
- Map is simplified projected SVG (clarity-first, not full GIS fidelity).
- Observed mode currently uses synthetic scaffolded sample data.
- Harvestable mode is intentionally synthetic until real precomputed scenarios are integrated.
- Dashboard is not a reliability adequacy simulator.
