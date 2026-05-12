import os
from dotenv import load_dotenv

load_dotenv()

ARENA_API_KEY = os.environ["ARENA_API_KEY"]
DATABASE_URL  = os.environ.get("DATABASE_URL", "sqlite:///roster.db")

ARENA_BASE_URL = "https://athletes.campus.ink/api/internal/athletes"
ARENA_PAGE_SIZE = 200

FUZZY_MATCH_THRESHOLD = 82  # out of 100

# Sports actively scraped in each run
TARGET_SPORTS = ["baseball", "softball", "mens-lacrosse", "womens-lacrosse"]

# ---------------------------------------------------------------------------
# Sport roster year config
#
# Sidearm supports year-specific URLs: /sports/{slug}/roster/{year}
# Map each sport slug to the correct season year to scrape.
#
# Season conventions:
#   Spring sports  (baseball, softball, lacrosse, tennis, golf, rowing, track): calendar year of season
#   Fall sports    (football, soccer, cross country, volleyball):               upcoming fall year
#   Winter sports  (basketball, swimming, wrestling, gymnastics, hockey):       spring end year of season
#
# To advance a sport to the next season, increment its year here.
# ---------------------------------------------------------------------------
SPORT_ROSTER_YEARS = {
    # --- Currently active (Spring 2026) ---
    "baseball":               2026,
    "softball":               2026,
    "mens-lacrosse":          2026,
    "womens-lacrosse":        2026,

    # --- Ready to activate when rosters publish ---
    "football":               2026,   # Fall 2026 — hold until rosters are posted
    "mens-soccer":            2026,
    "womens-soccer":          2026,
    "mens-cross-country":     2026,
    "womens-cross-country":   2026,
    "womens-volleyball":      2026,
    "mens-volleyball":        2026,

    # --- Winter 2025-26 ---
    "mens-basketball":        2026,
    "womens-basketball":      2026,
    "mens-swimming-and-diving":   2026,
    "womens-swimming-and-diving": 2026,
    "mens-wrestling":         2026,
    "womens-gymnastics":      2026,
    "mens-gymnastics":        2026,
    "mens-ice-hockey":        2026,
    "womens-ice-hockey":      2026,

    # --- Spring 2026 (non-active yet) ---
    "mens-tennis":            2026,
    "womens-tennis":          2026,
    "mens-golf":              2026,
    "womens-golf":            2026,
    "mens-track-and-field":   2026,
    "womens-track-and-field": 2026,
    "rowing":                 2026,
    "womens-rowing":          2026,
}

# ---------------------------------------------------------------------------
# Sidearm sport slug mapping
# ARENA internal key  →  Sidearm URL slug
# ---------------------------------------------------------------------------
SPORT_SLUGS = {
    # Active
    "baseball":               "baseball",
    "softball":               "softball",
    "mens-lacrosse":          "mens-lacrosse",
    "womens-lacrosse":        "womens-lacrosse",
    # Fall
    "football":               "football",
    "mens-soccer":            "mens-soccer",
    "womens-soccer":          "womens-soccer",
    "mens-cross-country":     "mens-cross-country",
    "womens-cross-country":   "womens-cross-country",
    "womens-volleyball":      "womens-volleyball",
    "mens-volleyball":        "mens-volleyball",
    # Winter
    "mens-basketball":        "mens-basketball",
    "womens-basketball":      "womens-basketball",
    "mens-swimming-and-diving":   "mens-swimming-and-diving",
    "womens-swimming-and-diving": "womens-swimming-and-diving",
    "mens-wrestling":         "wrestling",
    "womens-gymnastics":      "womens-gymnastics",
    "mens-gymnastics":        "mens-gymnastics",
    "mens-ice-hockey":        "mens-ice-hockey",
    "womens-ice-hockey":      "womens-ice-hockey",
    # Spring (non-active)
    "mens-tennis":            "mens-tennis",
    "womens-tennis":          "womens-tennis",
    "mens-golf":              "mens-golf",
    "womens-golf":            "womens-golf",
    "mens-track-and-field":   "mens-track-and-field",
    "womens-track-and-field": "womens-track-and-field",
    "rowing":                 "rowing",
    "womens-rowing":          "womens-rowing",
}

# ---------------------------------------------------------------------------
# Schools
#
# To add a non-Power 4 school, append it to the relevant section below.
# Format: "School Name": "sidearm-domain.com"
# It will automatically be included in scrape runs.
# ---------------------------------------------------------------------------
SCHOOL_DOMAINS = {
    # ---- Power 4: ACC ----
    "Boston College":   "bceagles.com",
    "Clemson":          "clemsontigers.com",
    "Duke":             "goduke.com",
    "Florida State":    "seminoles.com",
    "Georgia Tech":     "ramblinwreck.com",
    "Louisville":       "gocards.com",
    "Miami":            "hurricanesports.com",
    "NC State":         "gopack.com",
    "North Carolina":   "goheels.com",
    "Notre Dame":       "und.com",
    "Pittsburgh":       "pittsburghpanthers.com",
    "Syracuse":         "cuse.com",
    "Virginia":         "virginiasports.com",
    "Virginia Tech":    "hokiesports.com",
    "Wake Forest":      "godeacs.com",
    "California":       "calbears.com",
    "SMU":              "smumustangs.com",
    "Stanford":         "gostanford.com",
    # ---- Power 4: Big Ten ----
    "Illinois":         "fightingillini.com",
    "Indiana":          "iuhoosiers.com",
    "Iowa":             "hawkeyesports.com",
    "Maryland":         "umterps.com",
    "Michigan":         "mgoblue.com",
    "Michigan State":   "msuspartans.com",
    "Minnesota":        "gophersports.com",
    "Nebraska":         "huskers.com",
    "Northwestern":     "nusports.com",
    "Ohio State":       "ohiostatebuckeyes.com",
    "Penn State":       "gopsusports.com",
    "Purdue":           "purduesports.com",
    "Rutgers":          "scarletknights.com",
    "Wisconsin":        "uwbadgers.com",
    "UCLA":             "uclabruins.com",
    "USC":              "usctrojans.com",
    "Oregon":           "goducks.com",
    "Washington":       "gohuskies.com",
    # ---- Power 4: Big 12 ----
    "Arizona":          "arizonawildcats.com",
    "Arizona State":    "thesundevils.com",
    "Baylor":           "baylorbears.com",
    "BYU":              "byucougars.com",
    "Cincinnati":       "gobearcats.com",
    "Colorado":         "cubuffs.com",
    "Houston":          "uhcougars.com",
    "Iowa State":       "cyclones.com",
    "Kansas":           "kuathletics.com",
    "Kansas State":     "kstatesports.com",
    "Oklahoma State":   "okstate.com",
    "TCU":              "gofrogs.com",
    "Texas Tech":       "texastech.com",
    "UCF":              "ucfknights.com",
    "Utah":             "utahutes.com",
    "West Virginia":    "wvusports.com",
    # ---- Power 4: SEC ----
    "Alabama":          "rolltide.com",
    "Arkansas":         "arkansasrazorbacks.com",
    "Auburn":           "auburntigers.com",
    "Florida":          "floridagators.com",
    "Georgia":          "georgiadogs.com",
    "Kentucky":         "ukathletics.com",
    "LSU":              "lsusports.net",
    "Mississippi State": "hailstate.com",
    "Missouri":         "mutigers.com",
    "Ole Miss":         "olemisssports.com",
    "South Carolina":   "gamecocksonline.com",
    "Tennessee":        "utsports.com",
    "Texas":            "texassports.com",
    "Texas A&M":        "12thman.com",
    "Vanderbilt":       "vucommodores.com",
    "Oklahoma":         "soonersports.com",

    # ---- Non-Power 4 partners (add below as needed) ----
    # "Liberty":        "libertyflames.com",
    # "App State":      "appstatesports.com",
}

ALL_SCHOOLS = set(SCHOOL_DOMAINS.keys())

# Used for ARENA API filtering — keyword match against school name field
POWER_4_KEYWORDS = {kw.lower() for kw in ALL_SCHOOLS}

# Kept for backward compatibility
POWER_4_SCHOOLS = ALL_SCHOOLS

# ---------------------------------------------------------------------------
# Valid ARENA sport enum values — anything outside this set → "other"
# ---------------------------------------------------------------------------
VALID_SPORTS = {
    "baseball", "football", "softball",
    "mens_basketball", "womens_basketball",
    "mens_soccer", "womens_soccer",
    "mens_track_and_field", "womens_track_and_field",
    "mens_swim_and_dive", "womens_swim_and_dive",
    "mens_tennis", "womens_tennis",
    "mens_golf", "womens_golf",
    "mens_lacrosse", "womens_lacrosse",
    "mens_volleyball", "womens_volleyball",
    "mens_gymnastics", "womens_gymnastics",
    "mens_ice_hockey", "womens_ice_hockey",
    "mens_wrestling", "womens_wrestling",
    "rowing", "womens_rowing",
    "mens_cross_country", "womens_cross_country",
}
