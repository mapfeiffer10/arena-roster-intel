import os
from dotenv import load_dotenv

load_dotenv()

ARENA_API_KEY = os.environ["ARENA_API_KEY"]
DATABASE_URL  = os.environ.get("DATABASE_URL", "sqlite:///roster.db")

ARENA_BASE_URL = "https://athletes.campus.ink/api/internal/athletes"
ARENA_PAGE_SIZE = 200


FUZZY_MATCH_THRESHOLD = 82  # out of 100

TARGET_SPORTS = ["baseball", "softball", "mens-lacrosse", "womens-lacrosse"]

# Sidearm sport slug mapping
SPORT_SLUGS = {
    "baseball": "baseball",
    "softball": "softball",
    "mens-lacrosse": "mens-lacrosse",
    "womens-lacrosse": "womens-lacrosse",
}

# 69 Power 4 schools: {school_name: domain}
SCHOOL_DOMAINS = {
    # ACC
    "Boston College": "bceagles.com",
    "Clemson": "clemsontigers.com",
    "Duke": "goduke.com",
    "Florida State": "seminoles.com",
    "Georgia Tech": "ramblinwreck.com",
    "Louisville": "gocards.com",
    "Miami": "hurricanesports.com",
    "NC State": "gopack.com",
    "North Carolina": "goheels.com",
    "Notre Dame": "und.com",
    "Pittsburgh": "pittsburghpanthers.com",
    "Syracuse": "cuse.com",
    "Virginia": "virginiasports.com",
    "Virginia Tech": "hokiesports.com",
    "Wake Forest": "godeacs.com",
    "California": "calbears.com",
    "SMU": "smumustangs.com",
    "Stanford": "gostanford.com",
    # Big Ten
    "Illinois": "fightingillini.com",
    "Indiana": "iuhoosiers.com",
    "Iowa": "hawkeyesports.com",
    "Maryland": "umterps.com",
    "Michigan": "mgoblue.com",
    "Michigan State": "msuspartans.com",
    "Minnesota": "gophersports.com",
    "Nebraska": "huskers.com",
    "Northwestern": "nusports.com",
    "Ohio State": "ohiostatebuckeyes.com",
    "Penn State": "gopsusports.com",
    "Purdue": "purduesports.com",
    "Rutgers": "scarletknights.com",
    "Wisconsin": "uwbadgers.com",
    "UCLA": "uclabruins.com",
    "USC": "usctrojans.com",
    "Oregon": "goducks.com",
    "Washington": "gohuskies.com",
    # Big 12
    "Arizona": "arizonawildcats.com",
    "Arizona State": "thesundevils.com",
    "Baylor": "baylorbears.com",
    "BYU": "byucougars.com",
    "Cincinnati": "gobearcats.com",
    "Colorado": "cubuffs.com",
    "Houston": "uhcougars.com",
    "Iowa State": "cyclones.com",
    "Kansas": "kuathletics.com",
    "Kansas State": "kstatesports.com",
    "Oklahoma State": "okstate.com",
    "TCU": "gofrogs.com",
    "Texas Tech": "texastech.com",
    "UCF": "ucfknights.com",
    "Utah": "utahutes.com",
    "West Virginia": "wvusports.com",
    # SEC
    "Alabama": "rolltide.com",
    "Arkansas": "arkansasrazorbacks.com",
    "Auburn": "auburntigers.com",
    "Florida": "floridagators.com",
    "Georgia": "georgiadogs.com",
    "Kentucky": "ukathletics.com",
    "LSU": "lsusports.net",
    "Mississippi State": "hailstate.com",
    "Missouri": "mutigers.com",
    "Ole Miss": "olemisssports.com",
    "South Carolina": "gamecocksonline.com",
    "Tennessee": "utsports.com",
    "Texas": "texassports.com",
    "Texas A&M": "12thman.com",
    "Vanderbilt": "vucommodores.com",
    "Oklahoma": "soonersports.com",
}

POWER_4_SCHOOLS = set(SCHOOL_DOMAINS.keys())

# Used to validate sport values before writing to the Notion select field.
# Values outside this set are coerced to "other".
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

# Keyword-based Power 4 check — more forgiving than exact-set matching since
# ARENA school names sometimes include state suffixes or abbreviations.
POWER_4_KEYWORDS = {kw.lower() for kw in POWER_4_SCHOOLS}
