from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Athlete(db.Model):
    __tablename__ = "athletes"

    id             = db.Column(db.Integer, primary_key=True)
    athlete_name   = db.Column(db.String(200), nullable=False)
    school         = db.Column(db.String(200), index=True)
    sport          = db.Column(db.String(100), index=True)
    arena_status   = db.Column(db.String(50))
    roster_match   = db.Column(db.String(50), default="🔄 Pending Review", index=True)
    email          = db.Column(db.String(200), unique=True, index=True)
    jersey_number  = db.Column(db.String(20))
    action_needed  = db.Column(db.String(100), default="None")
    action_completed = db.Column(db.Boolean, default=False, index=True)
    portal_status  = db.Column(db.String(100), default="Not Flagged")
    new_school     = db.Column(db.String(200))
    lifetime_sales = db.Column(db.Float, default=0)
    lifetime_orders = db.Column(db.Integer, default=0)
    last_synced    = db.Column(db.String(20))
    notes          = db.Column(db.Text)

    def to_dict(self):
        return {
            "id":               self.id,
            "athlete_name":     self.athlete_name,
            "school":           self.school,
            "sport":            self.sport,
            "arena_status":     self.arena_status,
            "roster_match":     self.roster_match,
            "email":            self.email,
            "jersey_number":    self.jersey_number,
            "action_needed":    self.action_needed,
            "action_completed": self.action_completed,
            "portal_status":    self.portal_status,
            "new_school":       self.new_school,
            "lifetime_sales":   self.lifetime_sales,
            "lifetime_orders":  self.lifetime_orders,
            "last_synced":      self.last_synced,
            "notes":            self.notes,
        }
