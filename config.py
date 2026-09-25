"""
Edit this file to point the system at YOUR market.
Everything else in the codebase reads from here.
"""

# One entry per beach market you operate in.
# - name: just a label for your own reference
# - state: two-letter state code (used for FEMA disaster lookups)
# - fema_state_fips: FEMA's numeric state code (needed for their API)
#     FL=12, SC=45, NC=37, AL=01, MS=28, GA=13, TX=48, CA=06 ...
#     full list: https://www.fema.gov/openfema-data-page/disaster-declarations-summaries-v2
# - nws_zone: National Weather Service public zone code for the county/area
#     look yours up at: https://www.weather.gov/pimar/PubZone  (or just search
#     "NWS public zone [your county]")
# - reddit_keywords: phrases to search for on Reddit, in addition to the
#     global keywords below
MARKETS = [
    {
        "name": "Destin / Fort Walton Beach, FL",
        "state": "FL",
        "fema_state_fips": "12",
        "county_name": "Okaloosa",  # used to filter FEMA results by county
        "nws_zone": "FLZ203",
        "reddit_keywords": ["Destin", "Fort Walton", "Okaloosa", "30A", "Emerald Coast"],
    },
    {
        "name": "Panama City Beach, FL",
        "state": "FL",
        "fema_state_fips": "12",
        "county_name": "Bay",
        "nws_zone": "FLZ207",
        "reddit_keywords": ["Panama City Beach", "PCB", "Bay County FL"],
    },
    # Add more markets here, same shape.
]

# Subreddits to search across all markets.
SUBREDDITS = [
    "TravelNursing",
    "Construction",
    "IBEW",  # electrical/lineman union, common after storms
    "snowbirds",
    "digitalnomad",
    "remotework",
    "Insurance",
]

# Segment-agnostic keywords that suggest someone needs 1-6 month housing.
GLOBAL_KEYWORDS = [
    "travel nurse", "travel contract", "30 day", "60 day", "90 day",
    "month to month", "midterm rental", "mid-term rental", "furnished rental",
    "temporary housing", "housing needed", "relocating for work",
    "insurance is putting us up", "displaced", "storm crew housing",
    "lineman housing", "disaster recovery crew", "FEMA housing",
    "corporate housing", "travel therapist", "locum tenens",
]

# How far back (days) to look when a source supports date filtering.
LOOKBACK_DAYS = 30

# Anthropic model used to classify/extract structured info from raw posts.
# Haiku is fast and cheap, which is what you want for high-volume filtering.
CLASSIFIER_MODEL = "claude-haiku-4-5-20251001"

DB_PATH = "leads.db"
