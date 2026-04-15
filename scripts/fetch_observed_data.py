#!/usr/bin/env python3
"""Fetch observed hourly BA data from EIA API v2 (EIA-930 style routes).

This script pulls:
- electricity/rto/region-data (demand, total generation, interchange)
- electricity/rto/fuel-type-data (wind, solar)

Outputs raw API-like JSON payloads under data/raw/ for downstream processing.
"""

from __future__ import annotations

import argparse
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
REGION_OUT = RAW_DIR / "eia930_region_data.json"
FUEL_OUT = RAW_DIR / "eia930_fuel_type_data.json"
META_OUT = RAW_DIR / "eia930_fetch_metadata.json"

API_BASE = "https://api.eia.gov/v2/electricity/rto"
RESPONDENTS = ["CAL", "ERCO", "ISNE", "MISO", "NYIS", "PJM", "SWPP"]


def _hour_floor(ts: datetime) -> datetime:
    return ts.replace(minute=0, second=0, microsecond=0)


def _default_window() -> tuple[str, str]:
    end = _hour_floor(datetime.now(timezone.utc) - timedelta(hours=1))
    start = end - timedelta(hours=23)
    return start.strftime("%Y-%m-%dT%H"), end.strftime("%Y-%m-%dT%H")


def _build_query(route: str, data_field: str, facets: dict[str, list[str]], start: str, end: str, length: int = 5000, offset: int = 0) -> str:
    params: list[tuple[str, str]] = [
        ("frequency", "hourly"),
        ("data[0]", data_field),
        ("start", start),
        ("end", end),
        ("sort[0][column]", "period"),
        ("sort[0][direction]", "asc"),
        ("length", str(length)),
        ("offset", str(offset)),
    ]
    api_key = os.getenv("EIA_API_KEY", "").strip()
    if api_key:
        params.append(("api_key", api_key))

    for facet_name, values in facets.items():
        for value in values:
            params.append((f"facets[{facet_name}][]", value))

    return f"{API_BASE}/{route}/data/?{urllib.parse.urlencode(params)}"


def _fetch_json(url: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "always-sunny-observed-pipeline/1.0",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _fetch_paginated(route: str, data_field: str, facets: dict[str, list[str]], start: str, end: str) -> dict:
    offset = 0
    all_rows: list[dict] = []
    total = None

    while True:
        url = _build_query(route, data_field, facets, start, end, offset=offset)
        payload = _fetch_json(url)
        response = payload.get("response", {})
        rows = response.get("data", [])
        if total is None:
            total = int(response.get("total", len(rows)))
        all_rows.extend(rows)
        offset += len(rows)
        if not rows or offset >= total:
            break

    return {
        "response": {
            "total": str(total if total is not None else len(all_rows)),
            "data": all_rows,
        }
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", help="UTC hour start, format YYYY-MM-DDTHH")
    parser.add_argument("--end", help="UTC hour end, format YYYY-MM-DDTHH")
    parser.add_argument(
        "--respondents",
        nargs="+",
        default=RESPONDENTS,
        help="EIA respondent codes (default is a representative BA set)",
    )
    return parser.parse_args()


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    args = _parse_args()
    start, end = (args.start, args.end) if args.start and args.end else _default_window()
    respondents = sorted(set(args.respondents))

    try:
        region = _fetch_paginated(
            route="region-data",
            data_field="value",
            facets={"respondent": respondents, "type": ["D", "NG", "TI"]},
            start=start,
            end=end,
        )
        fuel = _fetch_paginated(
            route="fuel-type-data",
            data_field="value",
            facets={"respondent": respondents, "fueltype": ["WND", "SUN"]},
            start=start,
            end=end,
        )

        REGION_OUT.write_text(json.dumps(region, indent=2))
        FUEL_OUT.write_text(json.dumps(fuel, indent=2))
        META_OUT.write_text(
            json.dumps(
                {
                    "fetched_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "source": "EIA API v2 electricity/rto region-data + fuel-type-data",
                    "window_start_utc": start,
                    "window_end_utc": end,
                    "respondents": respondents,
                    "notes": "Observed values are BA-visible and utility-scale-visible.",
                },
                indent=2,
            )
        )
        print(f"Fetched {len(region['response']['data'])} region rows and {len(fuel['response']['data'])} fuel rows.")
    except Exception as exc:  # noqa: BLE001
        print(f"EIA fetch failed ({exc}). Keeping existing raw sample files unchanged.")


if __name__ == "__main__":
    main()
