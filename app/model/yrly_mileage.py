# Customer classes
from app import logger
from app import db
from app.utils import tm_conv, const

class Yrly_mileage(db.Model):
    __table_args__ = {"schema": "fitness", 'comment':'summary of workouts by type and year'}
    user_id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), primary_key=True)
    nbr = db.Column(db.Integer())
    dt_by_yr = db.Column(db.DateTime, primary_key=True)
    tot_dist = db.Column(db.Numeric(8,2))
    tot_sec = db.Column(db.Integer())
    dist_delta_pct = db.Column(db.Numeric(8,2))
    tm_delta_pct = db.Column(db.Numeric(8,2))

    def __repr__(self):
        return '<Yearly_mileage {}: type {}>'.format(str(self.dt_by_yr), self.type)

    def dur_str(self):
        return tm_conv.sec_to_time(self.tot_sec, 'dhms')

    def pace_str(self):
        return tm_conv.sec_to_time(tm_conv.pace_calc(self.tot_dist, self.tot_sec), 'ms')

    def __lt__(self, other):
        if self.type == other.type:
            return ((self.dt_by_yr < other.dt_by_yr))
        else:
            return ((self.type < other.type))

    def __gt__(self, other):
        if self.type == other.type:
            return ((self.dt_by_yr > other.dt_by_yr))
        else:
            return ((self.type > other.type))

    def dt_year(self):
        return self.dt_by_yr.strftime('%Y')
