#!/usr/bin/env python3
"""Fetch observed BA data placeholder for future EIA-930 integration.

Current behavior: writes a tiny CSV scaffold if no raw file exists.
Replace URL and parsing logic in future milestone.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "eia930_observed_sample.csv"

HEADERS = [
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


def main() -> None:
    RAW.parent.mkdir(parents=True, exist_ok=True)
    if RAW.exists():
        print(f"Raw file already exists: {RAW}")
        return
    RAW.write_text(",".join(HEADERS) + "\n")
    print(
        "Created raw observed CSV scaffold. "
        "Next step: implement live EIA-930 fetch/parsing in this script."
    )


if __name__ == "__main__":
    main()
