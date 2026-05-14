"""
Scrape school roster pages → fuzzy match against ARENA athletes → update SQLite.

Outcomes per athlete:
  ✅ Signed  — in ARENA + on roster
  🚨 Ghost   — in ARENA + NOT on roster  → Action Needed = "Check Transfer Status"
  ⚠️ Gap     — on roster + NOT in ARENA  → create new row, Action Needed = "Reach Out to Sign"
"""

import logging
import re
from datetime import date
from typing import Optional

import requests
from bs4 import BeautifulSoup
from thefuzz import fuzz, process

from config import (
    ARENA_API_KEY,
    ARENA_BASE_URL,
    ARENA_PAGE_SIZE,
    FUZZY_MATCH_THRESHOLD,
    SCHOOL_DOMAINS,
    SCHOOL_SPORT_SLUG_OVERRIDES,
    SPORT_SLUGS,
    SPORT_ROSTER_YEARS,
    TARGET_SPORTS,
)
from models import db, Athlete

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Name normalisation
# ---------------------------------------------------------------------------

_SUFFIXES = re.compile(r"\b(jr\.?|sr\.?|ii|iii|iv|v)\b", re.I)
_NICK_MAP = {
    "nick": "nicholas", "nicholas": "nick",
    "mike": "michael", "michael": "mike",
    "chris": "christopher", "christopher": "chris",
    "matt": "matthew", "matthew": "matt",
    "jake": "jacob", "jacob": "jake",
    "alex": "alexander", "alexander": "alex",
    "will": "william", "william": "will",
    "rob": "robert", "robert": "rob",
    "tom": "thomas", "thomas": "tom",
    "andy": "andrew", "andrew": "andy",
    "tony": "anthony", "anthony": "tony",
    "joe": "joseph", "joseph": "joe",
    "dan": "daniel", "daniel": "dan",
    "zach": "zachary", "zachary": "zach",
    "ben": "benjamin", "benjamin": "ben",
    "sam": "samuel", "samuel": "sam",
}


def normalise_name(name: str) -> str:
    name = _SUFFIXES.sub("", name.lower().strip()).strip()
    name = name.replace("-", " ")
    parts = name.split()
    if parts:
        parts[0] = _NICK_MAP.get(parts[0], parts[0])
    return " ".join(parts)


def name_similarity(a: str, b: str) -> int:
    na, nb = normalise_name(a), normalise_name(b)
    return max(fuzz.ratio(na, nb), fuzz.token_sort_ratio(na, nb), fuzz.partial_ratio(na, nb))


# ---------------------------------------------------------------------------
# Sidearm scraper
# ---------------------------------------------------------------------------

SIDEARM_SELECTORS = [
    # Modern Sidearm (2024+) — scoped to players section only, not coaching staff
    ".c-rosterpage__players .s-person-card h3",
    ".c-rosterpage__players .s-person-card__content h3",
    # Modern Sidearm without section scoping (fallback)
    ".s-person-card h3",
    ".s-person-card__content h3",
    # Older Sidearm — person details
    ".s-person-details__personal-single-item a",
    ".s-person-details__name",
    # Legacy Sidearm
    ".roster_player_name a",
    ".roster_player_name",
    # Generic fallbacks
    "[data-bind*='full_name']",
    ".player-name a",
    ".player-name",
    "td.name a",
    "td.name",
]


def scrape_roster_html(html: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")

    # Build a set of staff/coach names to exclude — Sidearm puts these in
    # c-rosterpage__coaching-staff sections with the same card markup as players
    staff_selectors = [
        ".c-rosterpage__coaching-staff h3",
        ".c-rosterpage__coaching-staff .s-person-card h3",
        ".c-rosterpage__staff h3",
    ]
    staff_names: set[str] = set()
    for sel in staff_selectors:
        for el in soup.select(sel):
            name = el.get_text(strip=True)
            if name:
                staff_names.add(name)

    for selector in SIDEARM_SELECTORS:
        raw = [el.get_text(strip=True) for el in soup.select(selector) if el.get_text(strip=True)]
        if len(raw) >= 5:
            # Deduplicate (Sidearm renders both card + list view) and strip staff
            seen: set[str] = set()
            names = []
            for n in raw:
                if n not in seen and n not in staff_names:
                    seen.add(n)
                    names.append(n)
            if len(names) >= 5:
                return names
    return []


def fetch_roster_static(url: str) -> tuple[list[str], bool]:
    """Returns (names, got_404). got_404=True means skip Playwright — page doesn't exist."""
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code == 404:
            logger.warning("404 for %s — skipping Playwright", url)
            return [], True
        resp.raise_for_status()
        return scrape_roster_html(resp.text), False
    except Exception as exc:
        logger.warning("Static fetch failed for %s: %s", url, exc)
        return [], False


def fetch_roster_playwright(url: str) -> list[str]:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(2000)
            html = page.content()
            browser.close()
            return scrape_roster_html(html)
    except Exception as exc:
        logger.warning("Playwright fetch failed for %s: %s", url, exc)
        return []


def fetch_roster_new_sidearm(domain: str, sport_slug: str) -> list[str]:
    """
    Fetch roster from new WMT/Sidearm platform (website-api).
    These schools block headless browsers but expose a public JSON API.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
        r = requests.get(
            f"https://{domain}/website-api/rosters",
            params={"include": "season", "sort": "-id", "per_page": 50},
            headers=headers, timeout=10,
        )
        if r.status_code != 200 or not r.text.strip():
            return []
        import re as _re

        # Paginate through all rosters to find sport-specific ones (some schools have 400+)
        all_rosters = r.json().get("data", [])
        meta = r.json().get("meta", {})
        total = meta.get("total", 0)
        page = 2
        while len(all_rosters) < total:
            rp = requests.get(
                f"https://{domain}/website-api/rosters",
                params={"sort": "-id", "per_page": 50, "page": page},
                headers=headers, timeout=10,
            )
            if rp.status_code != 200:
                break
            batch = rp.json().get("data", [])
            if not batch:
                break
            all_rosters.extend(batch)
            page += 1

        sport_rosters = [x for x in all_rosters if sport_slug.lower() in x.get("name", "").lower()]
        if not sport_rosters:
            return []

        # Pick the roster with the most recent year in its name
        def _max_year(roster):
            years = _re.findall(r"\d{4}", roster.get("name", ""))
            return max(int(y) for y in years) if years else 0

        target = max(sport_rosters, key=_max_year)
        roster_name = target.get("name", "")

        # Reject stale rosters — only accept 2023 or newer
        if _max_year(target) < 2023:
            logger.warning("New Sidearm API: most recent %s roster is stale (%s) — skipping", sport_slug, roster_name)
            return []
        logger.info("New Sidearm API: using roster '%s' (id=%s)", roster_name, target["id"])
        roster_id = target["id"]

        r2 = requests.get(
            f"https://{domain}/website-api/player-rosters",
            params={"filter[roster_id]": roster_id, "include": "player", "per_page": 300},
            headers=headers, timeout=10,
        )
        if r2.status_code != 200:
            return []
        entries = r2.json().get("data", [])
        names = []
        for e in entries:
            player = e.get("player") or {}
            name = player.get("full_name") or f"{player.get('first_name', '')} {player.get('last_name', '')}".strip()
            if name:
                names.append(name)
        return names
    except Exception as exc:
        logger.warning("New Sidearm API fetch failed for %s: %s", domain, exc)
        return []


def get_roster(school: str, sport: str) -> tuple[list[str], bool]:
    domain = SCHOOL_DOMAINS.get(school)
    if not domain:
        logger.error("No domain configured for school: %s", school)
        return [], False

    slug = SCHOOL_SPORT_SLUG_OVERRIDES.get((school, sport)) or SPORT_SLUGS.get(sport, sport)
    year = SPORT_ROSTER_YEARS.get(sport)
    base_url = f"https://{domain}/sports/{slug}/roster"

    # Try year-specific URL first, fall back to base (no year) if empty
    urls_to_try = [f"{base_url}/{year}", base_url] if year else [base_url]

    got_404_everywhere = True
    playwright_candidate = None  # first URL that returned 200 but empty (JS-rendered)
    for url in urls_to_try:
        names, got_404 = fetch_roster_static(url)
        if names:
            logger.info("Scraped %d names from %s", len(names), url)
            return names, False
        if not got_404:
            got_404_everywhere = False
            if playwright_candidate is None:
                playwright_candidate = url

    # If every URL returned a 404, the school doesn't use this path — skip Playwright
    if got_404_everywhere:
        logger.warning("All URLs 404 for %s %s — skipping Playwright", school, sport)
        return [], False

    # Try Playwright (works for some JS-rendered pages)
    logger.info("Static empty for %s %s — trying Playwright on %s", school, sport, playwright_candidate)
    names = fetch_roster_playwright(playwright_candidate)
    if names:
        return names, True

    # Playwright failed — try new Sidearm website-api (blocks headless browsers but exposes JSON API)
    logger.info("Playwright empty for %s %s — trying new Sidearm API", school, sport)
    sport_label = slug.replace("-", " ")  # e.g. "baseball", "mens lacrosse"
    names = fetch_roster_new_sidearm(domain, sport_label)
    if names:
        logger.info("New Sidearm API returned %d names for %s %s", len(names), school, sport)
    return names, bool(names)


# ---------------------------------------------------------------------------
# ARENA fetch for one school + sport
# ---------------------------------------------------------------------------

def fetch_arena_for_school_sport(school: str, sport: str) -> list[dict]:
    athletes: list[dict] = []
    page = 1
    while True:
        resp = requests.get(
            ARENA_BASE_URL,
            headers={"X-Internal-Api-Key": ARENA_API_KEY},
            params={"status": "live", "school": school, "sport": sport.replace("-", "_"),
                    "per_page": ARENA_PAGE_SIZE, "page": page},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        batch = data.get("athletes") or data.get("data") or []
        if not batch:
            break
        athletes.extend(batch)
        if len(batch) < ARENA_PAGE_SIZE:
            break
        page += 1
    return athletes


# ---------------------------------------------------------------------------
# Match helper
# ---------------------------------------------------------------------------

def match_to_roster(arena_name: str, roster_names: list[str]) -> Optional[str]:
    if not roster_names:
        return None
    match, score = process.extractOne(arena_name, roster_names, scorer=name_similarity)
    return match if score >= FUZZY_MATCH_THRESHOLD else None


# ---------------------------------------------------------------------------
# Process one school + sport
# ---------------------------------------------------------------------------

def process_school_sport(school: str, sport: str, dry_run: bool = False) -> dict:
    stats = {"signed": 0, "ghost": 0, "gap": 0, "errors": 0}
    today = date.today().isoformat()

    logger.info("--- %s / %s ---", school, sport)

    roster_names, used_playwright = get_roster(school, sport)
    if not roster_names:
        logger.warning("EMPTY ROSTER (JS-blocked?): %s %s", school, sport)
        stats["errors"] += 1
        return stats

    if used_playwright:
        logger.info("Playwright returned %d players for %s %s", len(roster_names), school, sport)

    arena_athletes = fetch_arena_for_school_sport(school, sport)
    logger.info("ARENA: %d live athletes", len(arena_athletes))

    matched_roster: set[str] = set()

    # ARENA athletes → Signed or Ghost
    for athlete in arena_athletes:
        email = (athlete.get("email") or "").lower().strip()
        name  = athlete.get("name", "")
        if not email:
            continue

        roster_match = match_to_roster(name, roster_names)
        if roster_match:
            matched_roster.add(roster_match)
            status = "✅ Signed"
            action = "None"
            portal = "Not Flagged"
        else:
            status = "🚨 Ghost"
            action = "Check Transfer Status"
            portal = "Possible Transfer"

        if dry_run:
            logger.info("[DRY RUN] %s → %s", name, status)
            stats["signed" if status == "✅ Signed" else "ghost"] += 1
            continue

        try:
            row = Athlete.query.filter_by(email=email).first()
            if row:
                row.roster_match  = status
                row.action_needed = action
                row.portal_status = portal
                row.last_synced   = today
            else:
                lifetime = (athlete.get("sales") or {}).get("lifetime") or {}
                row = Athlete(
                    athlete_name     = name,
                    school           = school,
                    sport            = sport,
                    arena_status     = athlete.get("status", "live"),
                    roster_match     = status,
                    email            = email,
                    jersey_number    = str(athlete.get("jersey_number") or "").strip(),
                    action_needed    = action,
                    action_completed = False,
                    portal_status    = portal,
                    lifetime_sales   = lifetime.get("gross_sales") or 0,
                    lifetime_orders  = lifetime.get("order_count") or 0,
                    last_synced      = today,
                )
                db.session.add(row)

            stats["signed" if status == "✅ Signed" else "ghost"] += 1
        except Exception as exc:
            db.session.rollback()
            logger.error("Error on %s: %s", name, exc)
            stats["errors"] += 1

    # Roster-only players → Gap
    unmatched = [n for n in roster_names if n not in matched_roster]
    logger.info("Gap candidates: %d", len(unmatched))

    for roster_name in unmatched:
        if dry_run:
            logger.info("[DRY RUN] GAP: %s @ %s %s", roster_name, school, sport)
            stats["gap"] += 1
            continue

        try:
            existing_gap = Athlete.query.filter_by(
                athlete_name=roster_name, school=school, sport=sport
            ).first()
            if existing_gap:
                existing_gap.last_synced = today
                stats["gap"] += 1
                continue

            row = Athlete(
                athlete_name     = roster_name,
                school           = school,
                sport            = sport,
                arena_status     = "not-in-arena",
                roster_match     = "⚠️ Gap",
                action_needed    = "Reach Out to Sign",
                action_completed = False,
                portal_status    = "Not Flagged",
                lifetime_sales   = 0,
                lifetime_orders  = 0,
                last_synced      = today,
            )
            db.session.add(row)
            stats["gap"] += 1
        except Exception as exc:
            db.session.rollback()
            logger.error("Error creating gap for %s: %s", roster_name, exc)
            stats["errors"] += 1

    db.session.commit()
    logger.info("signed=%d ghost=%d gap=%d errors=%d", stats["signed"], stats["ghost"], stats["gap"], stats["errors"])
    return stats


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run_scrape(school: Optional[str] = None, sport: Optional[str] = None, dry_run: bool = False) -> dict:
    schools = [school] if school else list(SCHOOL_DOMAINS.keys())
    sports  = [sport]  if sport  else TARGET_SPORTS

    totals = {"signed": 0, "ghost": 0, "gap": 0, "errors": 0}
    js_blocked: list[str] = []

    for s in schools:
        for sp in sports:
            result = process_school_sport(s, sp, dry_run=dry_run)
            for k in totals:
                totals[k] += result.get(k, 0)
            if result["errors"] and not any(result[k] for k in ("signed", "ghost", "gap")):
                js_blocked.append(f"{s}/{sp}")

    if js_blocked:
        logger.warning("JS-blocked (need Playwright or manual): %s", js_blocked)

    logger.info("Scrape complete — signed=%d ghost=%d gap=%d errors=%d",
                totals["signed"], totals["ghost"], totals["gap"], totals["errors"])
    return {**totals, "js_blocked": js_blocked}
