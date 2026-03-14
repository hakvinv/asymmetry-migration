#!/usr/bin/env python3
"""
01_openalex_query.py
====================
Fetch bibliometric time series from OpenAlex API for the Regulatory Waterbed paper.
All queries are reproducible; results cached to data/openalex_raw.json.

Usage: python src/01_openalex_query.py
"""
import requests
import json
import time
import os
from pathlib import Path

BASE = "https://api.openalex.org"
MAIL = "mailto=vosteen@uni-bremen.de"
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

QUERIES = {
    # Processing layer
    "esg_disclosure": "ESG disclosure",
    "esg_rating_disagreement": "ESG rating disagreement",
    # Supply chain layer
    "scope3_emissions": "Scope 3 emissions",
    "scope1_scope2_emissions": "Scope 1 Scope 2 emissions",
    # Audit layer
    "sustainability_assurance": "sustainability assurance",
    # Extended evidence
    "greenwashing": "greenwashing",
    "esg_data_quality": "ESG data quality",
    "double_materiality": "double materiality",
}

YEARS = list(range(2015, 2026))


def query_openalex(search_term: str, year: int) -> int:
    """Return number of works matching search_term published in year."""
    url = (
        f"{BASE}/works?"
        f"search={requests.utils.quote(search_term)}"
        f"&filter=publication_year:{year}"
        f"&per_page=1&{MAIL}"
    )
    try:
        r = requests.get(url, timeout=20)
        if r.ok:
            return r.json()["meta"]["count"]
    except Exception as e:
        print(f"  WARNING: query failed for '{search_term}' {year}: {e}")
    return 0


def main():
    print("=" * 60)
    print("OpenAlex Bibliometric Data Collection")
    print("=" * 60)

    results = {}

    for key, term in QUERIES.items():
        print(f"\n  Querying: {term}")
        counts = {}
        for year in YEARS:
            n = query_openalex(term, year)
            counts[year] = n
            print(f"    {year}: {n:>6,}")
            time.sleep(0.2)  # rate limit courtesy
        results[key] = counts

    # Save raw results
    outpath = DATA_DIR / "openalex_raw.json"
    with open(outpath, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Saved to {outpath}")

    # Print summary table
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  {'Query':<30s} {'2015':>6s} {'2020':>6s} {'2025':>6s} {'Growth':>8s}")
    for key, counts in results.items():
        v15, v25 = counts.get(2015, 0), counts.get(2025, 0)
        growth = f"+{(v25/max(v15,1)-1)*100:.0f}%" if v15 > 0 else "n/a"
        print(f"  {key:<30s} {v15:>6,} {counts.get(2020,0):>6,} {v25:>6,} {growth:>8s}")


if __name__ == "__main__":
    main()
