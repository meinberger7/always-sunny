#!/usr/bin/env python3
"""Build app-ready observed BA hourly assets from checked-in EIA-style sample input."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime
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


BAS = [
    BA("CAISO", "California ISO", "western", 38.58, -121.49),
    BA("MISO", "Midcontinent ISO", "eastern", 42.0, -93.0),
    BA("PJM", "PJM Interconnection", "eastern", 39.95, -75.16),
    BA("ERCOT", "Electric Reliability Council of Texas", "ercot", 30.27, -97.74),
    BA("SPP", "Southwest Power Pool", "eastern", 35.47, -97.52),
    BA("NYISO", "New York ISO", "eastern", 42.65, -73.75),
]

BA_BY_CODE = {ba.ba_code: ba for ba in BAS}


def _to_local(ts_utc: str) -> str:
    dt = datetime.strptime(ts_utc, "%Y-%m-%dT%H:%M:%SZ")
    return dt.strftime("%Y-%m-%d %H:%M")


def normalize_from_raw() -> list[dict]:
    if not RAW.exists():
        raise FileNotFoundError(f"Missing checked-in observed sample: {RAW}")

    rows: list[dict] = []
    with RAW.open() as f:
        reader = csv.DictReader(f)
        required = {
            "timestamp_utc",
            "ba_code",
            "demand_mw",
            "total_generation_mw",
            "wind_mw",
            "solar_mw",
            "interchange_mw",
        }
        if not required.issubset(set(reader.fieldnames or [])):
            missing = sorted(required - set(reader.fieldnames or []))
            raise ValueError(f"Raw observed sample is missing columns: {missing}")

        for row in reader:
            ba_code = row["ba_code"]
            if ba_code not in BA_BY_CODE:
                raise ValueError(f"Unknown BA code in raw observed sample: {ba_code}")
            ba = BA_BY_CODE[ba_code]

            demand = float(row["demand_mw"])
            total_generation = float(row["total_generation_mw"])
            wind = float(row["wind_mw"])
            solar = float(row["solar_mw"])
            interchange = float(row["interchange_mw"])
            wind_solar = wind + solar

            rows.append(
                {
                    "timestamp_utc": row["timestamp_utc"],
                    "timestamp_local": _to_local(row["timestamp_utc"]),
                    "ba_code": ba.ba_code,
                    "ba_name": ba.ba_name,
                    "interconnection": ba.interconnection,
                    "lat": ba.lat,
                    "lon": ba.lon,
                    "demand_mw": demand,
                    "total_generation_mw": total_generation,
                    "wind_mw": wind,
                    "solar_mw": solar,
                    "interchange_mw": interchange,
                    "wind_solar_mw": wind_solar,
                    "wind_solar_share_of_generation": round(wind_solar / total_generation, 4)
                    if total_generation > 0
                    else 0.0,
                }
            )

    rows.sort(key=lambda r: (r["timestamp_utc"], r["ba_code"]))
    return rows


def write_metadata() -> None:
    metadata = [ba.__dict__ for ba in BAS]
    META_OUT.write_text(json.dumps(metadata, indent=2))


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rows = normalize_from_raw()
    OUT.write_text(json.dumps(rows, indent=2))
    write_metadata()
    print(f"Wrote {len(rows)} observed hourly rows to {OUT}.")


if __name__ == "__main__":
    main()
