#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_OBS = {
    "timestamp_utc",
    "timestamp_local",
    "ba_code",
    "ba_name",
    "interconnection",
    "lat",
    "lon",
    "demand_mw",
    "total_generation_mw",
    "wind_mw",
    "solar_mw",
    "interchange_mw",
    "wind_solar_mw",
    "wind_solar_share_of_generation",
}

REQUIRED_HARV = {
    "scenario_id",
    "buildout_target_pct_of_annual_demand",
    "transmission_scope",
    "timestamp_utc",
    "timestamp_local",
    "ba_code",
    "ba_name",
    "interconnection",
    "lat",
    "lon",
    "harvestable_wind_mw",
    "harvestable_solar_mw",
    "harvestable_total_mw",
}


def main() -> None:
    obs = json.loads((ROOT / "data/processed/observed_hourly.json").read_text())
    harv = json.loads((ROOT / "data/demo/harvestable_demo.json").read_text())

    assert obs, "Observed data must not be empty"
    assert harv, "Harvestable data must not be empty"
    assert REQUIRED_OBS.issubset(obs[0]), "Observed schema mismatch"
    assert REQUIRED_HARV.issubset(harv[0]), "Harvestable schema mismatch"

    ts = {r["timestamp_utc"] for r in obs}
    bas = {r["ba_code"] for r in obs}
    assert len(ts) >= 24, "Observed sample should include at least 24 hourly timestamps"
    assert len(bas) >= 5, "Observed sample should include multiple balancing authorities"

    raw_path = ROOT / "data/raw/eia930_observed_sample.csv"
    with raw_path.open() as f:
        raw_rows = list(csv.DictReader(f))
    assert raw_rows, "Checked-in raw EIA sample must not be empty"

    print("Asset validation passed.")


if __name__ == "__main__":
    main()
