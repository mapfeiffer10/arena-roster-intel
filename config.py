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
# Per-school sport slug overrides
# Some schools use non-standard slugs for certain sports.
# Format: ("School Name", "sport-slug") → "sidearm-slug"
# ---------------------------------------------------------------------------
SCHOOL_SPORT_SLUG_OVERRIDES = {
    ("Louisiana State University", "baseball"): "bsb",
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
    # "Boston College" not in ARENA — still scrape for Gap discovery
    "Boston College":               "bceagles.com",
    "Clemson University":           "clemsontigers.com",
    "Duke University":              "goduke.com",
    "Florida State University":     "seminoles.com",
    "Georgia Tech":                 "ramblinwreck.com",
    "University of Louisville":     "gocards.com",
    # "University of Miami (FL)" not in ARENA — still scrape for Gap discovery
    "University of Miami (FL)":     "hurricanesports.com",
    "North Carolina State University": "gopack.com",
    "University of North Carolina": "goheels.com",
    "University of Notre Dame":     "fightingirish.com",
    "University of Pittsburgh":     "pittsburghpanthers.com",
    "Syracuse University":          "cuse.com",
    "University of Virginia":       "virginiasports.com",
    "Virginia Tech":                "hokiesports.com",
    "Wake Forest University":       "godeacs.com",
    "University of California":     "calbears.com",
    # "SMU" not in ARENA — still scrape for Gap discovery
    "SMU":                          "smumustangs.com",
    "Stanford University":          "gostanford.com",
    # ---- Power 4: Big Ten ----
    "University of Illinois":       "fightingillini.com",
    "Indiana University":           "iuhoosiers.com",
    "University of Iowa":           "hawkeyesports.com",
    "University of Maryland-College Park": "umterps.com",
    "University of Michigan":       "mgoblue.com",
    "Michigan State University":    "msuspartans.com",
    # "University of Minnesota" not in ARENA — still scrape for Gap discovery
    "University of Minnesota":      "gophersports.com",
    "University of Nebraska":       "huskers.com",
    "Northwestern University":      "nusports.com",
    "Ohio State University":        "ohiostatebuckeyes.com",
    "Penn State University":        "gopsusports.com",
    "Purdue University":            "purduesports.com",
    "Rutgers University":           "scarletknights.com",
    "University of Wisconsin Madison": "uwbadgers.com",
    "UCLA":                         "uclabruins.com",
    "University of Southern California": "usctrojans.com",
    # "University of Oregon" not in ARENA — still scrape for Gap discovery
    "University of Oregon":         "goducks.com",
    "University of Washington":     "gohuskies.com",
    # ---- Power 4: Big 12 ----
    "University of Arizona":        "arizonawildcats.com",
    "Arizona State University":     "thesundevils.com",
    "Baylor University":            "baylorbears.com",
    # "BYU" not in ARENA — still scrape for Gap discovery
    "BYU":                          "byucougars.com",
    # "Cincinnati" not in ARENA — still scrape for Gap discovery
    "Cincinnati":                   "gobearcats.com",
    "University of Colorado":       "cubuffs.com",
    "University of Houston":        "uhcougars.com",
    "Iowa State University":        "cyclones.com",
    "University of Kansas":         "kuathletics.com",
    "Kansas State University":      "kstatesports.com",
    # "Oklahoma State University" not in ARENA — still scrape for Gap discovery
    "Oklahoma State University":    "okstate.com",
    "Texas Christian University":   "gofrogs.com",
    "Texas Tech University":        "texastech.com",
    "University of Central Florida": "ucfknights.com",
    "University of Utah":           "utahutes.com",
    "West Virginia University":     "wvusports.com",
    # ---- Power 4: SEC ----
    # "University of Alabama" not in ARENA (only UAB) — still scrape for Gap discovery
    "University of Alabama":        "rolltide.com",
    "University of Arkansas":       "arkansasrazorbacks.com",
    "Auburn University":            "auburntigers.com",
    "University of Florida":        "floridagators.com",
    "University of Georgia":        "georgiadogs.com",
    # "University of Kentucky" not in ARENA — still scrape for Gap discovery
    "University of Kentucky":       "ukathletics.com",
    # "Louisiana State University" not in ARENA — still scrape for Gap discovery
    "Louisiana State University":   "lsusports.net",
    "Mississippi State University": "hailstate.com",
    "University of Missouri":       "mutigers.com",
    # "University of Mississippi" not in ARENA — still scrape for Gap discovery
    "University of Mississippi":    "olemisssports.com",
    "University of South Carolina": "gamecocksonline.com",
    "University of Tennessee":      "utsports.com",
    # "University of Texas at Austin" not in ARENA — still scrape for Gap discovery
    "University of Texas at Austin": "texassports.com",
    "Texas A&M University":         "12thman.com",
    "Vanderbilt University":        "vucommodores.com",
    "University of Oklahoma":       "soonersports.com",

    # ---- Non-Power 4 partners ----
    # ---- American Athletic Conference ----
    "East Carolina University":               "ecupirates.com",
    "University of Memphis":                  "gotigersgo.com",
    "University of South Florida":            "gousfbulls.com",
    "Temple University":                      "owlsports.com",
    "Tulane University":                      "tulanegreenwave.com",
    "University of North Texas":              "meangreensports.com",
    "Rice University":                        "riceowls.com",
    "University of Connecticut":              "uconnhuskies.com",
    # ---- Mountain West ----
    "Boise State University":                 "broncosports.com",
    "Colorado State University":              "csurams.com",
    "San Diego State University":             "goaztecs.com",
    "San Jose State University":              "sjsuspartans.com",
    "University of Nevada":                   "nevadawolfpack.com",
    "University of Nevada, Las Vegas":        "unlvrebels.com",
    "University of New Mexico":               "golobos.com",
    "Utah State University":                  "utahstateaggies.com",
    "Fresno State University":                "gobulldogs.com",
    # ---- MAC ----
    "Ball State University":                  "ballstatesports.com",
    "Bowling Green State University":         "bgsufalcons.com",
    "Central Michigan University":            "cmuchippewas.com",
    "Eastern Michigan University":            "emueagles.com",
    "Kent State University":                  "kentstatesports.com",
    "Miami University (Ohio)":                "miamiredhawks.com",
    "Northern Illinois University":           "niuhuskies.com",
    "Ohio University":                        "ohiobobcats.com",
    "University of Akron":                    "gozips.com",
    "University of Toledo":                   "utrockets.com",
    "Western Michigan University":            "wmubroncos.com",
    # ---- Sun Belt ----
    "Appalachian State University":           "appstatesports.com",
    "Coastal Carolina University":            "goccusports.com",
    "Georgia Southern University":            "gseagles.com",
    "University of Louisiana at Lafayette":   "ragincajuns.com",
    "Marshall University":                    "herdzone.com",
    "Old Dominion University":                "odusports.com",
    "University of South Dakota":             "goyotes.com",
    # ---- Conference USA ----
    "Florida Atlantic University":            "fausports.com",
    "Florida Gulf Coast University":          "fgcuathletics.com",
    "James Madison University":               "jmusports.com",
    "Liberty University":                     "libertyflames.com",
    "Middle Tennessee State University":      "goblueraiders.com",
    "University of Alabama - Birmingham":     "uabsports.com",
    "Western Kentucky University":            "wkusports.com",
    # ---- Big East ----
    "Butler University":                      "butlersports.com",
    "Creighton University":                   "gocreighton.com",
    "Depaul University":                      "depaulbluedemons.com",
    "Georgetown University":                  "guhoyas.com",
    "Marquette University":                   "gomarquette.com",
    "Providence College":                     "friars.com",
    "Seton Hall University":                  "shupirates.com",
    "St. Johns University":                   "redstormsports.com",
    "Villanova University":                   "villanova.com",
    "Xavier University":                      "goxavier.com",
    # ---- Atlantic 10 ----
    "Duquesne University":                    "goduquesne.com",
    "Fordham University":                     "fordhamsports.com",
    "George Washington University":           "gwsports.com",
    "La Salle University":                    "goexplorers.com",
    "Loyola University Chicago":              "loyolaramblers.com",
    "Saint Louis University":                 "slubillikens.com",
    "St. Bonaventure University":             "gobonnies.com",
    "University of Dayton":                   "daytonflyers.com",
    "University of Rhode Island":             "gorhody.com",
    # ---- Missouri Valley ----
    "Drake University":                       "godrakebulldogs.com",
    "Illinois State University":              "goredbirds.com",
    "Indiana State University":               "gosycamores.com",
    "University of Northern Iowa":            "unipanthers.com",
    "Valparaiso University":                  "valpoathletics.com",
    # ---- CAA ----
    "College of William and Mary":            "tribeathletics.com",
    "Drexel University":                      "drexeldragons.com",
    "Elon University":                        "elonphoenix.com",
    "Northeastern University":                "nuhuskies.com",
    "Towson University":                      "towsontigers.com",
    "University of Delaware":                 "bluehens.com",
    "University of North Carolina - Charlotte": "charlotte49ers.com",
    "UNC Pembroke":                           "uncpbraves.com",
    "UNC Wilmington":                         "uncwsports.com",
    # ---- Patriot League / Ivy adjacent ----
    "Johns Hopkins University":               "hopkinssports.com",
    "Bucknell University":                    "bucknellbison.com",
    "Lehigh University":                      "lehighsports.com",
    "Virginia Military Institute":            "vmisports.com",
    # ---- SWAC / MEAC / HBCU ----
    "Howard University":                      "hubison.com",
    "Jackson State University":               "gojsutigers.com",
    # ---- Independent / Other D1 ----
    "Bellarmine University":                  "athletics.bellarmine.edu",
    "Belmont University":                     "belmontbruins.com",
    "Campbell University":                    "gocamels.com",
    "East Tennessee State University":        "etsubucs.com",
    "Gonzaga University":                     "gozags.com",
    "Grand Canyon University":                "gculopes.com",
    "Long Beach State University":            "longbeachstate.com",
    "Mercer University":                      "mercerbears.com",
    "North Dakota State University":          "gobison.com",
    "Samford University":                     "samfordsports.com",
    "Stephen F. Austin State University":     "sfajacks.com",
    "The University of Tulsa":                "tulsahurricane.com",
    "UC Davis":                               "ucdavisaggies.com",
    "UC Irvine":                              "ucirvinesports.com",
    "University at Buffalo":                  "ubbulls.com",
    "University of Denver":                   "denverpioneers.com",
    "University of Hawaii":                   "hawaiiathletics.com",
    "University of Idaho":                    "govandals.com",
    "University of Maine":                    "goblackbears.com",
    "University of Montana":                  "gogriz.com",
    "Washington State University":            "wsucougars.com",
    "Wichita State University":               "goshockers.com",
    "Winthrop University":                    "winthropeagles.com",
    "Youngstown State University":            "ysusports.com",
    # ---- Additional requested ----
    "Lindenwood University":                  "lindenwoodlions.com",
    # ---- NAIA / D2 partners ----
    "Bethel University":                      "bupilots.com",
    "Cal State-San Bernardino":               "csusbathletics.com",
    "California Baptist University":          "cbulancers.com",
    "Rhode Island College":                   "goanchormen.com",
    "Utah Tech University":                   "utahtechtrailblazers.com",
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
