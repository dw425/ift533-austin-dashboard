"""
IFT 533 Phase III - data preprocessing (Daniel Warren, Data lead)

Input : Inside Airbnb, Austin TX detailed listings, Sep 17 2026 scrape
        https://data.insideairbnb.com/united-states/tx/austin/2026-09-17/data/listings.csv.gz
Output: austin_listings_tidy.csv   (one row per listing, clean types, derived columns)
        data_dictionary.csv        (column, type, domain, source)

Tool  : DuckDB (SQL over the CSV) - the preprocessing tool declared for extra credit.

Run   : python preprocess.py listings.csv.gz
"""
import sys
import duckdb

SRC = sys.argv[1] if len(sys.argv) > 1 else "listings.csv.gz"
OUT = "austin_listings_tidy.csv"

con = duckdb.connect()
# Read every column as text first so nothing is silently mis-typed.
con.execute(f"""
CREATE TABLE raw AS
SELECT * FROM read_csv('{SRC}', all_varchar = true, header = true, quote = '"', escape = '"')
""")
raw_rows = con.execute("SELECT count(*) FROM raw").fetchone()[0]

con.execute(r"""
CREATE TABLE tidy AS
WITH t AS (
  SELECT
    CAST(id AS VARCHAR)                                   AS listing_id,
    CAST(host_id AS VARCHAR)                              AS host_id,
    host_is_superhost = 't'                               AS superhost,
    TRY_CAST(calculated_host_listings_count AS INTEGER)   AS host_listings,
    TRY_CAST(hosts_time_as_host_years AS INTEGER)         AS host_years,
    CAST(neighbourhood_cleansed AS VARCHAR)               AS zip,
    TRY_CAST(latitude AS DOUBLE)                          AS latitude,
    TRY_CAST(longitude AS DOUBLE)                         AS longitude,
    property_type,
    room_type,
    TRY_CAST(accommodates AS INTEGER)                     AS accommodates,
    TRY_CAST(bedrooms AS INTEGER)                         AS bedrooms,
    TRY_CAST(beds AS INTEGER)                             AS beds,
    TRY_CAST(replace(replace(price, '$', ''), ',', '') AS DOUBLE) AS price,
    TRY_CAST(minimum_nights AS INTEGER)                   AS minimum_nights,
    TRY_CAST(availability_365 AS INTEGER)                 AS availability_365,
    TRY_CAST(number_of_reviews AS INTEGER)                AS number_of_reviews,
    TRY_CAST(number_of_reviews_ltm AS INTEGER)            AS reviews_ltm,
    TRY_CAST(first_review AS DATE)                        AS first_review,
    TRY_CAST(last_review AS DATE)                         AS last_review,
    TRY_CAST(review_scores_rating AS DOUBLE)              AS rating,
    TRY_CAST(review_scores_cleanliness AS DOUBLE)         AS cleanliness,
    TRY_CAST(review_scores_location AS DOUBLE)            AS location_score,
    TRY_CAST(estimated_occupancy_l365d AS INTEGER)        AS occupancy_nights,
    TRY_CAST(estimated_revenue_l365d AS DOUBLE)           AS revenue,
    NULLIF(trim(license), '')                             AS license,
    TRY_CAST(reviews_per_month AS DOUBLE)                 AS reviews_per_month
  FROM raw
)
SELECT *,
  license IS NOT NULL                                     AS license_shown,
  rating IS NOT NULL                                      AS has_reviews,
  occupancy_nights / 365.0                                AS occupancy_rate,
  CASE WHEN bedrooms > 0 THEN revenue / bedrooms END      AS revenue_per_bedroom,
  year(first_review)                                      AS first_review_year,
  CASE WHEN host_listings = 1 THEN '1 single'
       WHEN host_listings <= 5 THEN '2 small (2-5)'
       ELSE '3 commercial (6+)' END                       AS host_type,
  CASE WHEN price IS NULL THEN NULL
       WHEN price < 100 THEN '1 <$100'
       WHEN price < 250 THEN '2 $100-249'
       WHEN price < 500 THEN '3 $250-499'
       ELSE '4 $500+' END                                 AS price_tier,
  CASE WHEN rating IS NULL THEN NULL
       WHEN rating < 4.5  THEN '1 <4.5'
       WHEN rating < 4.8  THEN '2 4.5-4.79'
       WHEN rating < 4.95 THEN '3 4.8-4.94'
       ELSE '4 4.95-5' END                                AS rating_band,
  CASE WHEN minimum_nights >= 30 THEN '2 monthly (30+)'
       ELSE '1 nightly (<30)' END                         AS stay_type,
  price > 5000                                            AS price_outlier
FROM t
""")

checks = con.execute("""
SELECT count(*) rows,
       count(price) priced,
       count(rating) reviewed,
       sum(price_outlier::INT) outliers,
       sum(license_shown::INT) licensed,
       count(DISTINCT host_id) hosts,
       count(DISTINCT zip) zips
FROM tidy""").fetchone()

con.execute(f"COPY tidy TO '{OUT}' (HEADER, DELIMITER ',')")

DICT = [
 ("listing_id","Categorical","unique listing ID","id"),
 ("host_id","Categorical","host ID (FK)","host_id"),
 ("superhost","Categorical","true / false","host_is_superhost"),
 ("host_listings","Ratio","listings the host runs in Austin","calculated_host_listings_count"),
 ("host_years","Ratio","years hosting","hosts_time_as_host_years"),
 ("zip","Categorical","43 ZIP codes 78701-78759","neighbourhood_cleansed"),
 ("latitude","Interval","30.11-30.52","latitude"),
 ("longitude","Interval","-98.05 to -97.56","longitude"),
 ("property_type","Categorical","60 types","property_type"),
 ("room_type","Categorical","Entire home/apt, Private room, Hotel room, Shared room","room_type"),
 ("accommodates","Ratio","guests","accommodates"),
 ("bedrooms","Ratio","bedrooms","bedrooms"),
 ("beds","Ratio","beds","beds"),
 ("price","Ratio","USD per night (text cast to number)","price"),
 ("minimum_nights","Ratio","nights","minimum_nights"),
 ("availability_365","Ratio","0-365 days","availability_365"),
 ("number_of_reviews","Ratio","count","number_of_reviews"),
 ("reviews_ltm","Ratio","reviews in last 12 months","number_of_reviews_ltm"),
 ("first_review","Interval","date","first_review"),
 ("last_review","Interval","date","last_review"),
 ("rating","Interval","1-5 scale","review_scores_rating"),
 ("cleanliness","Interval","1-5 scale","review_scores_cleanliness"),
 ("location_score","Interval","1-5 scale","review_scores_location"),
 ("occupancy_nights","Ratio","estimated nights booked, last 365 days","estimated_occupancy_l365d"),
 ("revenue","Ratio","estimated USD, last 365 days","estimated_revenue_l365d"),
 ("license","Categorical","license ID / Exempt / null","license"),
 ("reviews_per_month","Ratio","reviews per month","reviews_per_month"),
 ("license_shown","Categorical","true / false","derived from license"),
 ("has_reviews","Categorical","true / false","derived from rating"),
 ("occupancy_rate","Ratio","0-1","occupancy_nights / 365"),
 ("revenue_per_bedroom","Ratio","USD","revenue / bedrooms"),
 ("first_review_year","Interval","2009-2026","year(first_review)"),
 ("host_type","Ordinal","single < small (2-5) < commercial (6+)","host_listings"),
 ("price_tier","Ordinal","<$100 < $100-249 < $250-499 < $500+","price"),
 ("rating_band","Ordinal","<4.5 < 4.5-4.79 < 4.8-4.94 < 4.95-5","rating"),
 ("stay_type","Ordinal","nightly (<30) < monthly (30+)","minimum_nights"),
 ("price_outlier","Categorical","true when price > $5,000","price"),
]
with open("data_dictionary.csv", "w") as f:
    f.write("column,type,domain,source\n")
    for r in DICT:
        f.write(",".join('"' + x + '"' for x in r) + "\n")

print(f"raw rows            {raw_rows:,}")
print(f"tidy rows           {checks[0]:,}")
print(f"with price          {checks[1]:,}")
print(f"with reviews        {checks[2]:,}")
print(f"price > $5,000      {checks[3]:,} (flagged, kept)")
print(f"license shown       {checks[4]:,}")
print(f"hosts / ZIPs        {checks[5]:,} / {checks[6]}")
print(f"wrote {OUT} and data_dictionary.csv")
