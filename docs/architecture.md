# Architecture

## v1 goals
- Static-first browser app (no backend/db requirement).
- Stable frontend contract for observed + harvestable datasets.
- Deterministic ETL scripts that emit app-ready JSON.

## Data flow
1. `scripts/fetch_observed_data.py` pulls raw observed hourly payloads from EIA API v2:
   - `electricity/rto/region-data` (D, NG, TI)
   - `electricity/rto/fuel-type-data` (WND, SUN)
   and saves them in `data/raw/`.
2. `scripts/build_observed_assets.py` joins raw payloads by `(period, respondent)` and maps respondents to BA metadata/timezones.
3. Processed output is written to `data/processed/observed_hourly.json` and `data/processed/ba_metadata.json`.
4. Frontend reads processed observed + demo harvestable JSON directly.

## Contracts
- Observed schema: `schemas/observed.schema.json`
- Harvestable schema: `schemas/harvestable.schema.json`
- Metadata schema: `schemas/metadata.schema.json`

## Observed mode caveat
Observed values are BA-visible and utility-scale-visible. They are not a complete measure of all behind-the-meter solar or all reliability dynamics.

## Future harvestable integration slots
- Replace synthetic `build_demo_harvestable_assets.py` internals with:
  - supply-curve site selection by scenario
  - weather-driven hourly production aggregation
  - optional transmission/storage post-processing
- Keep harvestable output fields unchanged to avoid frontend rewrites.

## Deployment
- GitHub Pages serves the static root plus `/data` assets.
- Scheduled workflow can refresh observed raw/processed assets.
