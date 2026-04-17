#!/usr/bin/env python3
"""Placeholder for future live EIA-930 ingestion.

Current behavior: validates/creates an empty checked-in sample template in the
same wide hourly format consumed by scripts/build_observed_assets.py.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "eia930_observed_sample.csv"

HEADERS = [
    "timestamp_utc",
    "ba_code",
    "demand_mw",
    "total_generation_mw",
    "wind_mw",
    "solar_mw",
    "interchange_mw",
]


def main() -> None:
    RAW.parent.mkdir(parents=True, exist_ok=True)
    if RAW.exists() and RAW.read_text().strip():
        print(f"Raw file already exists: {RAW}")
        return
    RAW.write_text(",".join(HEADERS) + "\n")
    print(
        "Created raw observed CSV template. "
        "Future work: replace this placeholder with live EIA-930 fetch/parsing."
    )


if __name__ == "__main__":
    main()
