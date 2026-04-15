# Methods & caveats

This project communicates one core concept: wind and solar vary locally, but geographic diversity across a wide grid can smooth aggregate availability.

## What this dashboard does
- Shows BA-level hourly observed wind/solar (Harvested mode).
- Shows scenario-based hourly modeled harvestable potential (Harvestable mode).

## What this dashboard does not do
- It is **not** a full reliability, resource adequacy, or production-cost simulation.
- It does **not** claim wind+solar alone solve all reliability challenges.

## Data status in MVP
- Observed mode uses schema-compatible sample data and ETL scaffolding intended for EIA-930 style ingestion.
- Harvestable mode uses schema-compatible synthetic scenarios intended to be replaced by precomputed weather/supply-curve outputs.
