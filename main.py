#!/usr/bin/env python3
"""
NCAA Roster Intelligence Platform — CLI entry point.

Commands:
  sync    Pull all live Power 4 athletes from ARENA → upsert into SQLite
  scrape  Scrape school rosters → fuzzy match → update SQLite with Signed/Ghost/Gap
  serve   Start the web server
"""

import logging
import sys
import click

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,
)


def get_app():
    from app import app
    return app


@click.group()
def cli():
    """ARENA Roster Intelligence Platform."""
    pass


# ---------------------------------------------------------------------------
# sync
# ---------------------------------------------------------------------------

@cli.command()
@click.option("--dry-run", is_flag=True, help="Log actions without writing to the database.")
def sync(dry_run):
    """Pull ARENA athletes → upsert into SQLite."""
    from arena_sync import run_sync
    app = get_app()

    if dry_run:
        click.echo("DRY RUN — no changes will be written.")

    with app.app_context():
        stats = run_sync(dry_run=dry_run)

    click.echo("\n=== Sync Results ===")
    click.echo(f"  Created : {stats['created']}")
    click.echo(f"  Updated : {stats['updated']}")
    click.echo(f"  Skipped : {stats['skipped']}")
    click.echo(f"  Errors  : {stats['errors']}")


# ---------------------------------------------------------------------------
# scrape
# ---------------------------------------------------------------------------

@cli.command()
@click.option("--school", default=None, help="Run for a single school (exact name from config).")
@click.option("--sport", default=None, help="Run for a single sport slug (e.g. mens-tennis).")
@click.option("--dry-run", is_flag=True, help="Log actions without writing to the database.")
def scrape(school, sport, dry_run):
    """Scrape rosters → match against ARENA → update database."""
    from roster_scraper import run_scrape
    from config import SCHOOL_DOMAINS
    app = get_app()

    if school and school not in SCHOOL_DOMAINS:
        click.echo(f"Unknown school: '{school}'. Check config.py SCHOOL_DOMAINS.", err=True)
        sys.exit(1)

    if dry_run:
        click.echo("DRY RUN — no changes will be written.")

    with app.app_context():
        result = run_scrape(school=school, sport=sport, dry_run=dry_run)

    click.echo("\n=== Scrape Results ===")
    click.echo(f"  ✅ Signed : {result['signed']}")
    click.echo(f"  🚨 Ghost  : {result['ghost']}")
    click.echo(f"  ⚠️  Gap    : {result['gap']}")
    click.echo(f"  Errors   : {result['errors']}")

    if result.get("js_blocked"):
        click.echo(f"\n  JS-blocked (need Playwright or manual): {result['js_blocked']}")


# ---------------------------------------------------------------------------
# serve
# ---------------------------------------------------------------------------

@cli.command()
@click.option("--port", default=5000, help="Port to run on.")
@click.option("--host", default="0.0.0.0", help="Host to bind to.")
def serve(port, host):
    """Start the web server."""
    import os
    app = get_app()
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    click.echo(f"Starting server on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cli()
