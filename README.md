# Always Sunny Explorer

Public-facing browser-first MVP dashboard showing hourly wind/solar diversity across U.S. balancing authorities (BAs).

## Purpose
The app communicates:

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
3. `deploy.yml` publishes static assets to site root with `data/` under `/data`.

### Option B: Local static preview
```bash
python -m http.server 8000
# open http://localhost:8000/
```

## Observed mode data pipeline (EIA-930 style)
- `scripts/fetch_observed_data.py`
  - pulls EIA API v2 `electricity/rto/region-data` (Demand/Net Gen/Interchange)
  - pulls EIA API v2 `electricity/rto/fuel-type-data` (Wind/Solar)
  - writes raw payloads to `data/raw/`
- `scripts/build_observed_assets.py`
  - joins raw payloads by hour + BA respondent
  - converts to app contract (`data/processed/observed_hourly.json`)
  - writes BA metadata (`data/processed/ba_metadata.json`)

Set `EIA_API_KEY` (optional but recommended for stable rate limits):
```bash
EIA_API_KEY=your_key python scripts/fetch_observed_data.py
python scripts/build_observed_assets.py
```

## Data layout
- `data/raw/`: raw EIA API payload snapshots for observed mode.
- `data/processed/`: app-ready normalized observed assets.
- `data/demo/`: demo harvestable scenario outputs and manifest.

A committed small observed sample is included so the app still runs without a fresh fetch.

## Scripts
```bash
python scripts/fetch_observed_data.py
python scripts/build_observed_assets.py
python scripts/build_demo_harvestable_assets.py
python tests/validate_assets.py
```

## Caveats
- Harvested mode is BA-visible / utility-scale-visible and may not fully capture behind-the-meter solar.
- Dashboard demonstrates geographic diversity; it is not a full reliability or production-cost model.
- Harvestable mode remains scenario-based demo data in this phase.
