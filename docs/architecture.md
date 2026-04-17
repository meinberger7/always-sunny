# Architecture

## v1 goals
- Static-first browser app (no backend/db requirement).
- Hourly BA-level observed and harvestable contracts with stable schemas.
- Deterministic ETL scripts that emit app-ready JSON.

## Data flow
1. `data/raw/eia930_observed_sample.csv` stores a checked-in EIA-930-style hourly BA sample extract used by the app.
2. `scripts/build_observed_assets.py` normalizes that sample into `data/processed/observed_hourly.json` and BA metadata.
3. `scripts/fetch_observed_data.py` is intentionally still a placeholder integration slot for future live pulls.
4. `scripts/build_demo_harvestable_assets.py` builds scenario manifest + demo harvestable records in `data/demo/`.
5. Frontend (`app/main.js`) reads processed/demo JSON directly.

## Frontend contract
- Observed schema: `schemas/observed.schema.json`
- Harvestable schema: `schemas/harvestable.schema.json`
- Metadata schema: `schemas/metadata.schema.json`

## Future harvestable integration slots
- Replace synthetic `build_demo_harvestable_assets.py` internals with:
  - real supply-curve site selection by scenario
  - weather-driven hourly production aggregation
  - optional transmission/storage post-processing
- Keep output fields unchanged to avoid frontend rewrites.

## Deployment
- GitHub Pages serves `app/` + repo data assets.
- Scheduled workflow refreshes observed assets and commits outputs.
