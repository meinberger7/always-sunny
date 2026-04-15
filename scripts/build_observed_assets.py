#!/usr/bin/env python3
"""Build app-ready observed BA hourly assets from fetched EIA-930 raw payloads."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
RAW_REGION = ROOT / "data" / "raw" / "eia930_region_data.json"
RAW_FUEL = ROOT / "data" / "raw" / "eia930_fuel_type_data.json"
OUT = ROOT / "data" / "processed" / "observed_hourly.json"
META_OUT = ROOT / "data" / "processed" / "ba_metadata.json"


@dataclass(frozen=True)
class BA:
    respondent: str
    ba_code: str
    ba_name: str
    interconnection: str
    lat: float
    lon: float
    timezone: str


BAS = [
    BA("CAL", "CAISO", "California ISO", "western", 38.58, -121.49, "America/Los_Angeles"),
    BA("MISO", "MISO", "Midcontinent ISO", "eastern", 42.0, -93.0, "America/Chicago"),
    BA("PJM", "PJM", "PJM Interconnection", "eastern", 39.95, -75.16, "America/New_York"),
    BA("ERCO", "ERCOT", "Electric Reliability Council of Texas", "ercot", 30.27, -97.74, "America/Chicago"),
    BA("SWPP", "SPP", "Southwest Power Pool", "eastern", 35.47, -97.52, "America/Chicago"),
    BA("NYIS", "NYISO", "New York ISO", "eastern", 42.65, -73.75, "America/New_York"),
    BA("ISNE", "ISONE", "ISO New England", "eastern", 42.36, -71.06, "America/New_York"),
]

BA_BY_RESP = {b.respondent: b for b in BAS}


def _load_rows(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Required raw file is missing: {path}")
    payload = json.loads(path.read_text())
    return payload.get("response", {}).get("data", [])


def _parse_period_utc(period: str) -> datetime:
    # EIA hourly periods are UTC-like timestamps such as 2026-01-15T13
    return datetime.strptime(period, "%Y-%m-%dT%H").replace(tzinfo=ZoneInfo("UTC"))


def _to_local_str(ts_utc: datetime, tz_name: str) -> str:
    return ts_utc.astimezone(ZoneInfo(tz_name)).strftime("%Y-%m-%d %H:%M")


def _as_float(value: str | int | float | None) -> float:
    if value is None or value == "":
        return 0.0
    return float(value)


def build_records() -> tuple[list[dict], list[dict]]:
    region_rows = _load_rows(RAW_REGION)
    fuel_rows = _load_rows(RAW_FUEL)

    region_index: dict[tuple[str, str], dict[str, float]] = {}
    for row in region_rows:
        respondent = row.get("respondent")
        period = row.get("period")
        metric_type = row.get("type")
        if respondent not in BA_BY_RESP or not period or not metric_type:
            continue
        key = (period, respondent)
        region_index.setdefault(key, {})[metric_type] = _as_float(row.get("value"))

    fuel_index: dict[tuple[str, str], dict[str, float]] = {}
    for row in fuel_rows:
        respondent = row.get("respondent")
        period = row.get("period")
        fuel_type = row.get("fueltype")
        if respondent not in BA_BY_RESP or not period or not fuel_type:
            continue
        key = (period, respondent)
        fuel_index.setdefault(key, {})[fuel_type] = _as_float(row.get("value"))

    records: list[dict] = []
    for period, respondent in sorted(region_index.keys()):
        ba = BA_BY_RESP[respondent]
        region = region_index[(period, respondent)]
        fuels = fuel_index.get((period, respondent), {})

        demand = region.get("D", 0.0)
        generation = region.get("NG", 0.0)
        interchange = region.get("TI", 0.0)
        wind = fuels.get("WND", 0.0)
        solar = fuels.get("SUN", 0.0)
        ws = wind + solar
        share = (ws / generation) if generation > 0 else 0.0

        ts_utc = _parse_period_utc(period)
        records.append(
            {
                "timestamp_utc": ts_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "timestamp_local": _to_local_str(ts_utc, ba.timezone),
                "ba_code": ba.ba_code,
                "ba_name": ba.ba_name,
                "interconnection": ba.interconnection,
                "lat": ba.lat,
                "lon": ba.lon,
                "demand_mw": round(demand, 2),
                "total_generation_mw": round(generation, 2),
                "wind_mw": round(wind, 2),
                "solar_mw": round(solar, 2),
                "interchange_mw": round(interchange, 2),
                "wind_solar_mw": round(ws, 2),
                "wind_solar_share_of_generation": round(share, 4),
            }
        )

    ba_metadata = [
        {
            "ba_code": b.ba_code,
            "ba_name": b.ba_name,
            "interconnection": b.interconnection,
            "lat": b.lat,
            "lon": b.lon,
            "timezone": b.timezone,
            "respondent": b.respondent,
        }
        for b in BAS
    ]

    return records, ba_metadata


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rows, ba_metadata = build_records()
    if not rows:
        raise RuntimeError("No observed rows were built from raw EIA payloads.")
    OUT.write_text(json.dumps(rows, indent=2))
    META_OUT.write_text(json.dumps(ba_metadata, indent=2))
    print(f"Wrote {len(rows)} observed rows for {len(ba_metadata)} BAs.")


if __name__ == "__main__":
    main()
