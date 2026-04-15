#!/usr/bin/env python3
from __future__ import annotations

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
    region_raw = json.loads((ROOT / "data/raw/eia930_region_data.json").read_text())
    fuel_raw = json.loads((ROOT / "data/raw/eia930_fuel_type_data.json").read_text())

    assert obs, "Observed data must not be empty"
    assert harv, "Harvestable data must not be empty"
    assert REQUIRED_OBS.issubset(obs[0]), "Observed schema mismatch"
    assert REQUIRED_HARV.issubset(harv[0]), "Harvestable schema mismatch"

    hours = sorted({r["timestamp_utc"] for r in obs})
    assert len(hours) >= 24, "Observed sample should include at least 24 hourly timestamps"
    assert region_raw.get("response", {}).get("data"), "Region raw payload is missing rows"
    assert fuel_raw.get("response", {}).get("data"), "Fuel raw payload is missing rows"
    print("Asset validation passed.")


if __name__ == "__main__":
    main()
