import csv
import io
import os

from flask import Flask, jsonify, render_template, request, Response
from models import db, Athlete

app = Flask(__name__)

# Railway injects DATABASE_URL as postgres:// — SQLAlchemy 2.x requires postgresql://
_db_url = os.environ.get("DATABASE_URL", "sqlite:///roster.db")
if _db_url.startswith("postgres://"):
    _db_url = _db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = _db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    db.create_all()


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# ---------------------------------------------------------------------------
# API — read
# ---------------------------------------------------------------------------

@app.route("/api/athletes")
def get_athletes():
    page        = request.args.get("page", 1, type=int)
    per_page    = request.args.get("per_page", 50, type=int)
    search      = request.args.get("search", "").strip()
    school      = request.args.get("school", "").strip()
    sport       = request.args.get("sport", "").strip()
    roster_match = request.args.get("roster_match", "").strip()
    action_completed = request.args.get("action_completed", "").strip()
    sort_by     = request.args.get("sort", "athlete_name")
    sort_dir    = request.args.get("dir", "asc")

    q = Athlete.query

    if search:
        q = q.filter(
            db.or_(
                Athlete.athlete_name.ilike(f"%{search}%"),
                Athlete.email.ilike(f"%{search}%"),
                Athlete.school.ilike(f"%{search}%"),
            )
        )
    if school:
        q = q.filter(Athlete.school == school)
    if sport:
        q = q.filter(Athlete.sport == sport)
    if roster_match:
        q = q.filter(Athlete.roster_match == roster_match)
    if action_completed == "yes":
        q = q.filter(Athlete.action_completed == True)
    elif action_completed == "no":
        q = q.filter(Athlete.action_completed == False)

    col_map = {
        "athlete_name":     Athlete.athlete_name,
        "school":           Athlete.school,
        "sport":            Athlete.sport,
        "arena_status":     Athlete.arena_status,
        "roster_match":     Athlete.roster_match,
        "action_needed":    Athlete.action_needed,
        "action_completed": Athlete.action_completed,
        "lifetime_sales":   Athlete.lifetime_sales,
        "last_synced":      Athlete.last_synced,
    }
    col = col_map.get(sort_by, Athlete.athlete_name)
    q = q.order_by(col.desc() if sort_dir == "desc" else col.asc())

    total   = q.count()
    paginated = q.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "athletes": [a.to_dict() for a in paginated.items],
        "total":    total,
        "page":     page,
        "per_page": per_page,
        "pages":    paginated.pages,
    })


@app.route("/api/dashboard")
def dashboard_data():
    pivot  = request.args.get("pivot",  "sport")   # "sport" or "school"
    school = request.args.get("school", "").strip()
    sport  = request.args.get("sport",  "").strip()

    col = "sport" if pivot == "sport" else "school"

    where_clauses = []
    params = {}
    if school:
        where_clauses.append("school = :school")
        params["school"] = school
    if sport:
        where_clauses.append("sport = :sport")
        params["sport"] = sport

    where = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    sql = """
        SELECT
            {col},
            COUNT(*) FILTER (WHERE roster_match = '✅ Signed')        AS signed,
            COUNT(*) FILTER (WHERE roster_match = '🚨 Ghost')         AS ghost,
            COUNT(*) FILTER (WHERE roster_match = '⚠️ Gap')           AS gap,
            COUNT(*) FILTER (WHERE roster_match = '🔄 Pending Review') AS pending,
            COUNT(*) AS total
        FROM athletes
        {where}
        GROUP BY {col}
        ORDER BY total DESC
    """.format(col=col, where=where)

    rows = db.session.execute(db.text(sql), params).fetchall()
    return jsonify([
        {"name": r[0], "signed": r[1], "ghost": r[2], "gap": r[3], "pending": r[4], "total": r[5]}
        for r in rows if r[0]
    ])


@app.route("/api/stats")
def stats():
    total    = Athlete.query.count()
    signed   = Athlete.query.filter_by(roster_match="✅ Signed").count()
    ghost    = Athlete.query.filter_by(roster_match="🚨 Ghost").count()
    gap      = Athlete.query.filter_by(roster_match="⚠️ Gap").count()
    pending  = Athlete.query.filter_by(roster_match="🔄 Pending Review").count()
    open_actions = Athlete.query.filter(
        Athlete.action_needed != "None",
        Athlete.action_completed == False,
    ).count()

    return jsonify({
        "total": total, "signed": signed, "ghost": ghost,
        "gap": gap, "pending": pending, "open_actions": open_actions,
    })


@app.route("/api/filter-options")
def filter_options():
    schools = [r[0] for r in db.session.query(Athlete.school).distinct().order_by(Athlete.school).all() if r[0]]
    sports  = [r[0] for r in db.session.query(Athlete.sport).distinct().order_by(Athlete.sport).all() if r[0]]
    return jsonify({"schools": schools, "sports": sports})


# ---------------------------------------------------------------------------
# API — write (team-editable fields only)
# ---------------------------------------------------------------------------

EDITABLE = {"notes", "action_needed", "action_completed", "portal_status", "new_school"}

@app.route("/api/athletes/<int:athlete_id>", methods=["PATCH"])
def update_athlete(athlete_id):
    athlete = db.get_or_404(Athlete, athlete_id)
    data = request.get_json(silent=True) or {}
    for field in EDITABLE:
        if field in data:
            setattr(athlete, field, data[field])
    db.session.commit()
    return jsonify(athlete.to_dict())


# ---------------------------------------------------------------------------
# CSV export
# ---------------------------------------------------------------------------

@app.route("/api/export.csv")
def export_csv():
    athletes = Athlete.query.order_by(Athlete.school, Athlete.athlete_name).all()
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow([
        "Athlete Name", "School", "Sport", "ARENA Status", "Roster Match",
        "Email", "Jersey Number", "Action Needed", "Action Completed",
        "Portal Status", "New School", "Lifetime Sales", "Lifetime Orders",
        "Last Synced", "Notes",
    ])
    for a in athletes:
        w.writerow([
            a.athlete_name, a.school, a.sport, a.arena_status, a.roster_match,
            a.email, a.jersey_number, a.action_needed,
            "Yes" if a.action_completed else "No",
            a.portal_status, a.new_school or "",
            f"${a.lifetime_sales:,.2f}" if a.lifetime_sales else "$0.00",
            a.lifetime_orders or 0,
            a.last_synced, a.notes or "",
        ])
    return Response(
        out.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=roster_intel.csv"},
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
