# Rebuilding this dashboard in Tableau

Everything the Bokeh dashboard (`dashboard.py` → `index.html`) shows can be
rebuilt in Tableau Desktop from one file: **`data/austin_listings_tidy.csv`**.
No preprocessing is needed — `preprocess.py` already did the cleaning, type
casting and derived columns, and `data/data_dictionary.csv` lists every column
with its measurement type (Categorical / Ordinal / Interval / Ratio) and the
raw Inside Airbnb column it came from.

If you want to start from the raw scrape instead, it is committed at
`data/listings.csv.gz`; run `python preprocess.py data/listings.csv.gz` to
regenerate the tidy file, or redo the equivalent casts in Tableau Prep.

## 1. Connect and type the data

1. Connect → Text file → `austin_listings_tidy.csv`.
2. Fix the fields Tableau will guess wrong:
   - `zip`, `listing_id`, `host_id`, `license` → **String** (Tableau reads
     them as numbers; ZIP codes must stay text).
   - `zip` → geographic role **ZIP Code/Postcode**; `latitude` / `longitude`
     already carry the Latitude / Longitude roles.
   - `superhost`, `license_shown`, `has_reviews`, `price_outlier` → Boolean.
   - `first_review`, `last_review` → Date.
   - `host_type`, `price_tier`, `rating_band`, `stay_type` are **Ordinal** —
     their values are prefixed `1 …`, `2 …`, `3 …` precisely so a default
     alphabetical sort is the correct order. Keep them as strings.
3. Nulls are honest and deliberate: 1,106 listings have no price, 1,855 no
   rating. Do not filter them globally — each sheet below excludes nulls only
   for the measure it plots.

## 2. Calculated fields

Create these once; the worksheets reference them.

| Name | Formula | Used by |
|---|---|---|
| `City Median Price` | `{ FIXED : MEDIAN([price]) }` | P3 reference line |
| `City License %` | `{ FIXED : AVG(INT([license_shown])) }` | P5 reference line + color |
| `ZIP License %` | `AVG(INT([license_shown]))` | P5 bars |
| `Below City License` | `AVG(INT([license_shown])) < MIN([City License %])` | P5 bar color |
| `Is Entire Home` | `[room_type] = "Entire home/apt"` | P1 dot color |
| `P6 Measure` | `CASE [p Measure] WHEN "Listings" THEN 1 ELSE ZN([revenue]) END` | P6 (see parameter below) |
| `P7 Score` | `CASE [p Score] WHEN "Overall" THEN [rating] WHEN "Cleanliness" THEN [cleanliness] ELSE [location_score] END` | P7 |
| `Revenue Running %` | `RUNNING_SUM(SUM([revenue])) / TOTAL(SUM([revenue]))` | P8 (table calc) |
| `Host Rank %` | `INDEX() / SIZE()` | P8 (table calc) |

Parameters (these replace the two Bokeh widget groups that swap measures):

- **`p Measure`** — string list: `Listings`, `Revenue` (drives P6, like radio C4).
- **`p Score`** — string list: `Overall`, `Cleanliness`, `Location` (drives P7,
  like select C6).

## 3. The ten worksheets

Same titles, same encodings. Palette: data blue `#2F6FD6`, highlight orange
`#E07B12` (highlight **only**, never decoration), reference grey `#9AA3AE`.

**P1 — Map.** Marks = circles on `longitude`/`latitude` (drag both as
continuous). Size 3 px, 50% opacity, no border. Color = `Is Entire Home`
(true → orange, false → blue). Background map: a light grey style (Map →
Background Maps → Light) matches the Esri WorldGrayCanvas tiles.

**P2 — Price histogram.** Right-click `price` → Create → Bins, size **50**.
Columns = price bins, Rows = `COUNT(listing_id)`. Blue bars. Exclude null price.

**P3 — Median price by ZIP.** Horizontal bar: Rows = `zip`, Columns =
`MEDIAN(price)`. Filter `zip` by **Top 15 by COUNT(listing_id)** (the "15
busiest ZIPs"). Sort descending by the median. Add a reference line from
`City Median Price`, dashed grey — the Bokeh version labels it "dashed = city".
Label each bar with its median, `$0` format.

**P4 — Price by room type.** Horizontal bar: Rows = `room_type`, Columns =
`MEDIAN(price)`. Label = median price plus median `occupancy_rate` as a
percent (the Bokeh labels read like `$230 · 54%`): put
`MEDIAN(occupancy_rate)` on Label and format `0%`.

**P5 — % licensed by ZIP.** Horizontal bar: Rows = `zip` (same Top-15 filter
as P3), Columns = `ZIP License %`, axis format `0%`. Color = `Below City
License` (true → orange, false → blue). Dashed grey reference line at
`City License %`.

**P6 — Host type.** Vertical bar: Columns = `host_type`, Rows =
`SUM(P6 Measure)`. Show the `p Measure` parameter control. Color: orange for
`3 commercial (6+)`, blue otherwise. Title should follow the parameter
("Listings by host type" / "Estimated revenue by host type"); axis format
`0,0` for listings, `$0.0a` for revenue. Label = % of total
(quick table calc → Percent of Total).

**P7 — Superhost box plot.** Columns = `superhost` (alias true → "Superhost",
false → "Other host"), Rows = `P7 Score`, disaggregated (Analysis → uncheck
Aggregate Measures), box-and-whisker from Show Me. Show the `p Score`
parameter control. The Bokeh version draws whiskers at the 5th/95th
percentiles rather than Tableau's default 1.5×IQR — note the difference or
set the whiskers accordingly.

**P8 — Pareto of host revenue.** Columns = `host_id` sorted descending by
`SUM(revenue)`, Rows = `Revenue Running %` (compute using `host_id`). Then
drag `Host Rank %` to Columns as the axis (standard Tableau Pareto recipe:
both table calcs computed along `host_id`), mark type Line. The headline
number — top 10% of hosts earn **59.9%** of estimated revenue — is the
running % read at rank 0.10.

**P9 — Price vs bedrooms.** Scatter: Columns = `bedrooms` (cap at 8:
`MIN([bedrooms], 8)`), Rows = `price`, disaggregated, small transparent
circles. The Bokeh version jitters x by ±0.25 (`bed_j`); in Tableau either
jitter with `MIN([bedrooms],8) + (RANDOM() - 0.5) / 2` or accept the column
stacking. Overlay the per-bedroom median as a dual axis: `MEDIAN(price)` by
bedroom count, line + circle marks, only for bedroom counts with ≥ 10
listings (filter via `{ FIXED MIN([bedrooms],8) : COUNT([listing_id]) } >= 10`).

**P10 — Listings per first-review year.** Line: Columns =
`first_review_year` (continuous), Rows = `COUNT(listing_id)`. Keep the
caveat from the README: only listings still active in Sep 2026 are counted,
so early years undercount.

## 4. The six controls → Tableau filters and parameters

| Bokeh | What it is | Tableau equivalent | Scope |
|---|---|---|---|
| C1 | Room type checkboxes | `room_type` filter, checkbox list | **All ten sheets** (apply to all using this data source) |
| C2 | Price range slider $10–$1,000 | `price` continuous range filter | P2, P4, P9 only |
| C3 | ZIP multi-select (empty = all 43) | `zip` multi-value dropdown filter | P1, P3, P5 only |
| C4 | Listings / Revenue radio | `p Measure` parameter | P6 |
| C5 | First-review year range 2009–2026 | `first_review_year` range filter | P10 only |
| C6 | Overall / Cleanliness / Location select | `p Score` parameter | P7 |

The per-plot scoping matters: in Bokeh each control deliberately drives only
some plots (so, e.g., the price slider never hides unpriced listings from the
map). Reproduce that with Tableau's "Apply to selected worksheets" on each
filter rather than applying everything globally.

## 5. Dashboard layout and header

Size ~1300 × 1400. Four rows, every plot 300 px tall:

1. Title block ("Austin short-term rentals, September 2026" + source line) and
   the C1 room-type filter, then a live summary line — in Tableau, a sheet
   with `COUNT(listing_id)`, `City Median Price` and `City License %` on Text
   reproduces the "N of 11,111 listings shown · city median $230 · 32% show a
   license" header.
2. P1 map · P3 median price · P5 license % (C3 beside them)
3. P2 histogram · P4 room type · P9 scatter (C2 beside them)
4. P6 host type · P7 box plot · P8 Pareto, then P10 with C5 under it

Tooltips: P3 shows ZIP / median / listing count; keep tooltips everywhere —
they stand in for Bokeh's hover tools.

## 6. Sanity checks after the rebuild

Match these against the live Bokeh page
(<https://dw425.github.io/ift533-austin-dashboard/>), all filters at default:

- 11,111 listings; city median price **$230**; **32%** show a license
- Room type counts: Entire home 9,264 · Private 1,640 · Hotel 171 · Shared 36
- 5,507 distinct hosts; top 10% of hosts earn **59.9%** of estimated revenue
- 36.1% of listings belong to hosts running six or more
