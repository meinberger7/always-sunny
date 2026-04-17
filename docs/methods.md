# Methods & caveats

This project communicates one core concept: wind and solar vary locally, but geographic diversity across a wide grid can smooth aggregate availability.

## What this dashboard does
- Shows BA-level hourly observed wind/solar (Harvested mode).
- Shows scenario-based hourly modeled harvestable potential (Harvestable mode).

## What this dashboard does not do
- It is **not** a full reliability, resource adequacy, or production-cost simulation.
- It does **not** claim wind+solar alone solve all reliability challenges.

## Data status in MVP
- Observed mode uses a checked-in real EIA-930-style hourly BA sample dataset normalized to the frontend schema.
- Harvestable mode remains schema-compatible synthetic scenarios intended to be replaced later by precomputed weather/supply-curve outputs.
