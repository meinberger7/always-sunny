#!/usr/bin/env python3
"""Build deterministic demo harvestable scenario assets.

This script creates scenario-based hourly BA-level harvestable data matching the
frontend contract. It is intentionally synthetic but schema-compatible so that
real optimization/weather outputs can replace it without frontend changes.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "demo"


@dataclass(frozen=True)
class BA:
    ba_code: str
    ba_name: str
    interconnection: str
    lat: float
    lon: float
    demand_base_mw: float


BAS = [
    BA("CAISO", "California ISO", "western", 38.58, -121.49, 28000),
    BA("MISO", "Midcontinent ISO", "eastern", 42.0, -93.0, 52000),
    BA("PJM", "PJM Interconnection", "eastern", 39.95, -75.16, 68000),
    BA("ERCOT", "Electric Reliability Council of Texas", "ercot", 30.27, -97.74, 48000),
    BA("SPP", "Southwest Power Pool", "eastern", 35.47, -97.52, 22000),
    BA("NYISO", "New York ISO", "eastern", 42.65, -73.75, 24000),
]

BUILDOUTS = [20, 40, 60, 80]
SCOPES = ["local", "regional", "national"]


def scope_multiplier(scope: str) -> float:
    return {"local": 0.88, "regional": 1.0, "national": 1.12}[scope]


def build_assets() -> tuple[list[dict], list[dict]]:
    start = datetime(2026, 1, 15, 0, 0, tzinfo=timezone.utc)
    records: list[dict] = []
    scenarios: list[dict] = []

    for buildout in BUILDOUTS:
        for scope in SCOPES:
            scenario_id = f"b{buildout}_{scope}"
            scenarios.append(
                {
                    "scenario_id": scenario_id,
                    "buildout_target_pct_of_annual_demand": buildout,
                    "transmission_scope": scope,
                    "label": f"{buildout}% demand target / {scope}",
                    "is_demo": True,
                    "notes": "Synthetic precomputed scenario for MVP wiring.",
                }
            )
            for hr in range(24):
                ts = start + timedelta(hours=hr)
                for idx, ba in enumerate(BAS):
                    daylight = max(0.0, 1 - abs((hr - 19) / 8))
                    wind_shape = 0.65 + 0.35 * ((hr + idx * 3) % 24) / 24
                    scale = (buildout / 60.0) * scope_multiplier(scope)
                    solar = ba.demand_base_mw * 0.18 * daylight * scale
                    wind = ba.demand_base_mw * 0.22 * wind_shape * scale
                    total = solar + wind
                    records.append(
                        {
                            "scenario_id": scenario_id,
                            "buildout_target_pct_of_annual_demand": buildout,
                            "transmission_scope": scope,
                            "timestamp_utc": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "timestamp_local": ts.strftime("%Y-%m-%d %H:%M"),
                            "ba_code": ba.ba_code,
                            "ba_name": ba.ba_name,
                            "interconnection": ba.interconnection,
                            "lat": ba.lat,
                            "lon": ba.lon,
                            "harvestable_wind_mw": round(wind, 2),
                            "harvestable_solar_mw": round(solar, 2),
                            "harvestable_total_mw": round(total, 2),
                        }
                    )
    return records, scenarios


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    records, scenarios = build_assets()
    (OUT_DIR / "harvestable_demo.json").write_text(json.dumps(records, indent=2))
    (OUT_DIR / "scenario_manifest.json").write_text(json.dumps(scenarios, indent=2))
    print(f"Wrote {len(records)} demo harvestable records.")


if __name__ == "__main__":
    main()
