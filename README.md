# Austin Short-Term Rentals Dashboard — IFT 533 Data Visualization

**Live dashboard:** https://dw425.github.io/ift533-austin-dashboard/

Interactive dashboard of Austin, TX Airbnb listings (Sep 2026) for city
short-term-rental compliance staff and prospective hosts.

**Team:** Daniel Warren (dwarre26@asu.edu), Data lead · [Teammate name] ·
[Teammate name] · [Teammate name]

## Data

- Source: Inside Airbnb — Austin, TX detailed listings, scraped 17 Sep 2026
  (<https://insideairbnb.com/get-the-data/>)
- 11,111 listings × 90 raw columns → 11,111 × 37 clean columns
- Column types and domains: [`data/data_dictionary.csv`](data/data_dictionary.csv)
- 37 columns typed: 15 Ratio · 10 Categorical · 8 Interval · 4 Ordinal

The raw `listings.csv.gz` is not committed. Download it from the Inside Airbnb
link above (Austin, Texas → 17 September 2026 → Detailed Listings data).

## How it was built

- **`preprocess.py`** — DuckDB. Reads every column as text so nothing is
  silently mis-typed, `TRY_CAST`s each to its real type, derives 10 columns,
  and flags — does not delete — the 21 listings priced over $5,000.
  Nulls are kept honest: 1,106 listings have no price, 1,855 no rating.
- **`dashboard.py`** — Python Bokeh. 10 plots and 6 controls. All
  interactivity runs in the browser through CustomJS, so `index.html` is
  self-contained and needs no server.

## Reproduce

```bash
pip install duckdb bokeh pandas numpy xyzservices
python preprocess.py listings.csv.gz   # -> data/austin_listings_tidy.csv, data/data_dictionary.csv
python dashboard.py                    # -> austin_str_dashboard.html, copied to index.html
```

Built and verified against DuckDB 2.0.0, Bokeh 3.10.0, pandas 3.0.1,
Python 3.13.

## Plots

| | Plot | Answers |
|---|---|---|
| P1 | Map, one dot per listing (orange = entire home) | Where listings concentrate; where unlicensed ones are |
| P2 | Histogram of nightly price, $50 bins | How prices are spread |
| P3 | Median price, 15 busiest ZIPs | Typical night by ZIP |
| P4 | Median price by room type, with % booked | Entire home vs private room |
| P5 | % of listings showing a license, by ZIP | License share |
| P6 | Listings or revenue by host type | How much is commercial |
| P7 | Box plot, superhost vs other | Do superhosts score better |
| P8 | Pareto of revenue by host | Revenue concentration |
| P9 | Price vs bedrooms, with median line | Do bedrooms raise price |
| P10 | Listings by year of first review | New listings per year |

Palette: blue `#2F6FD6` data · orange `#E07B12` highlight only ·
grey `#9AA3AE` reference lines.

## Controls

| | Control | Drives |
|---|---|---|
| C1 | Room type (checkboxes) | all plots |
| C3 | ZIP code (multi-select, empty = all 43) | P1, P3, P5 |
| C2 | Nightly price $10–$1,000 (range slider) | P2, P4, P9 |
| C4 | Listings / Revenue (radio) | P6 |
| C6 | Overall / Cleanliness / Location (select) | P7 |
| C5 | First-review year 2009–2026 (range slider) | P10 |

## What the data says

- Median night: **$230**. 467 listings above $1,000.
- Entire home 9,264 · Private room 1,640 · Hotel room 171 · Shared room 36
- **32%** of listings show a license.
- 5,507 distinct hosts, of whom 5,000 carry a revenue estimate.
- **36.1%** of listings belong to hosts running six or more.
- The top 10% of hosts earn **59.9%** of all estimated revenue.

P10 counts only listings still active in September 2026, so early years
undercount listings that have since closed.
