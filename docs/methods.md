# Methods & caveats

This dashboard communicates one core concept: wind and solar vary locally, but geographic diversity across a wide grid can smooth aggregate availability.

## Harvested mode (Observed)
- Uses BA-visible, utility-scale-visible hourly values built from EIA-930 style API routes.
- Inputs include demand, net generation, interchange, wind, and solar at BA respondent level.
- Wind/solar share shown in the app is based on reported BA net generation for that hour.

## Harvestable mode (Modeled)
- Uses scenario-based, precomputed demo data in this MVP.
- Intended future upgrade: weather-driven + supply-curve-based precomputed scenarios.

## Important caveats
- Harvested values are not a complete accounting of behind-the-meter solar.
- The app does not claim wind+solar alone solve all reliability challenges.
- The app is not a full reliability, resource adequacy, or production-cost simulation.
