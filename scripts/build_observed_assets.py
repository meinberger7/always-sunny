#!/usr/bin/env python3
"""Build app-ready observed BA hourly assets.

If data/raw/eia930_observed_sample.csv exists, normalize from that file.
Otherwise generate a deterministic synthetic sample for local/browser-first use.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "eia930_observed_sample.csv"
OUT = ROOT / "data" / "processed" / "observed_hourly.json"
META_OUT = ROOT / "data" / "processed" / "ba_metadata.json"


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

FIELDS = [
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
]


def synthesize() -> list[dict]:
    start = datetime(2026, 1, 15, 0, 0, tzinfo=timezone.utc)
    rows: list[dict] = []
    for hr in range(24):
        ts = start + timedelta(hours=hr)
        for i, ba in enumerate(BAS):
            demand = ba.demand_base_mw * (0.88 + 0.18 * abs(12 - hr) / 12)
            solar_shape = max(0.0, 1 - abs((hr - 19) / 7))
            wind_shape = 0.5 + 0.5 * ((hr + i * 2) % 24) / 24
            wind = demand * (0.12 + 0.14 * wind_shape)
            solar = demand * (0.02 + 0.16 * solar_shape)
            total_generation = demand * (0.97 + ((i + hr) % 4) * 0.015)
            interchange = total_generation - demand
            wind_solar = wind + solar
            rows.append(
                {
                    "timestamp_utc": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "timestamp_local": ts.strftime("%Y-%m-%d %H:%M"),
                    "ba_code": ba.ba_code,
                    "ba_name": ba.ba_name,
                    "interconnection": ba.interconnection,
                    "lat": ba.lat,
                    "lon": ba.lon,
                    "demand_mw": round(demand, 2),
                    "total_generation_mw": round(total_generation, 2),
                    "wind_mw": round(wind, 2),
                    "solar_mw": round(solar, 2),
                    "interchange_mw": round(interchange, 2),
                    "wind_solar_mw": round(wind_solar, 2),
                    "wind_solar_share_of_generation": round(wind_solar / total_generation, 4),
                }
            )
    return rows


def normalize_from_raw() -> list[dict]:
    rows = []
    with RAW.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            normalized = {k: row[k] for k in FIELDS if k in row}
            for key in ["lat", "lon", "demand_mw", "total_generation_mw", "wind_mw", "solar_mw", "interchange_mw", "wind_solar_mw", "wind_solar_share_of_generation"]:
                normalized[key] = float(normalized[key])
            rows.append(normalized)
    return rows


def write_metadata() -> None:
    metadata = [ba.__dict__ for ba in BAS]
    META_OUT.write_text(json.dumps(metadata, indent=2))


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rows = normalize_from_raw() if RAW.exists() else []
    if not rows:
        rows = synthesize()
    OUT.write_text(json.dumps(rows, indent=2))
    write_metadata()
    print(f"Wrote {len(rows)} observed hourly rows to {OUT}.")


if __name__ == "__main__":
    main()
