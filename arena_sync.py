"""
Pull all live Power 4 athletes from ARENA API and upsert into SQLite.
Unique key: email address (lowercase).
"""

import logging
from datetime import date

import requests

from config import (
    ARENA_API_KEY,
    ARENA_BASE_URL,
    ARENA_PAGE_SIZE,
    VALID_SPORTS,
    POWER_4_KEYWORDS,
)
from models import db, Athlete

logger = logging.getLogger(__name__)
TODAY = date.today().isoformat()


def is_power4(school_name: str) -> bool:
    if not school_name:
        return False
    s = school_name.lower()
    return any(kw in s for kw in POWER_4_KEYWORDS)


def fetch_all_arena_athletes() -> list[dict]:
    logger.info("Fetching athletes from ARENA…")
    athletes: list[dict] = []
    page = 1
    total = None

    while True:
        resp = requests.get(
            ARENA_BASE_URL,
            headers={"X-Internal-Api-Key": ARENA_API_KEY},
            params={"status": "live", "per_page": ARENA_PAGE_SIZE, "page": page},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        if total is None:
            total = data.get("total", 0)
            logger.info("Total live athletes in ARENA: %d", total)

        batch = data.get("athletes", [])
        athletes.extend(batch)

        if len(athletes) >= total or len(batch) < ARENA_PAGE_SIZE:
            break
        page += 1

    p4 = [a for a in athletes if is_power4(a.get("school", ""))]
    logger.info("Power 4 athletes: %d", len(p4))
    return p4


def _upsert(athlete: dict) -> str:
    """Write one athlete to the DB. Returns 'created' or 'updated'."""
    email = (athlete.get("email") or "").lower().strip()
    if not email:
        return "skipped"

    sport = (athlete.get("sport") or "").strip()
    sport_val = sport if sport in VALID_SPORTS else "other"

    jersey = athlete.get("jersey_number")
    jersey_str = str(jersey).strip() if jersey is not None else ""

    lifetime = (athlete.get("sales") or {}).get("lifetime") or {}

    existing = Athlete.query.filter_by(email=email).first()

    if existing:
        existing.athlete_name    = athlete.get("name", existing.athlete_name)
        existing.school          = athlete.get("school") or existing.school
        existing.sport           = sport_val
        existing.arena_status    = athlete.get("status", "live")
        existing.jersey_number   = jersey_str
        existing.lifetime_sales  = lifetime.get("gross_sales") or 0
        existing.lifetime_orders = lifetime.get("order_count") or 0
        existing.last_synced     = TODAY
        return "updated"
    else:
        row = Athlete(
            athlete_name    = athlete.get("name", ""),
            school          = athlete.get("school") or "",
            sport           = sport_val,
            arena_status    = athlete.get("status", "live"),
            roster_match    = "🔄 Pending Review",
            email           = email,
            jersey_number   = jersey_str,
            action_needed   = "None",
            action_completed = False,
            portal_status   = "Not Flagged",
            lifetime_sales  = lifetime.get("gross_sales") or 0,
            lifetime_orders = lifetime.get("order_count") or 0,
            last_synced     = TODAY,
        )
        db.session.add(row)
        return "created"


def run_sync(dry_run: bool = False) -> dict:
    athletes = fetch_all_arena_athletes()
    stats = {"created": 0, "updated": 0, "skipped": 0, "errors": 0}
    total = len(athletes)

    logger.info("Syncing %d athletes to database…", total)

    for i, athlete in enumerate(athletes):
        email = (athlete.get("email") or "").lower().strip()
        if not email:
            logger.warning("No email for %s — skipping", athlete.get("name"))
            stats["skipped"] += 1
            continue

        if dry_run:
            exists = Athlete.query.filter_by(email=email).first()
            logger.info("[DRY RUN] %s → %s", athlete.get("name"), "update" if exists else "create")
            continue

        try:
            action = _upsert(athlete)
            stats[action] += 1
        except Exception as exc:
            db.session.rollback()
            logger.error("Error on %s: %s", athlete.get("name"), exc)
            stats["errors"] += 1

        # Commit in batches of 200 for performance
        if (i + 1) % 200 == 0:
            db.session.commit()
            logger.info("Progress: %d / %d", i + 1, total)

    db.session.commit()
    logger.info(
        "Sync complete — created: %d, updated: %d, skipped: %d, errors: %d",
        stats["created"], stats["updated"], stats["skipped"], stats["errors"],
    )
    return stats
