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

    '''
    Adds two years distance, number, and duration together.
    If entries have different user id than returns empty string for user id
    If entries have different type then sets type to Total
    Throws an error if the dates do not match
    Returns combined yearly mileage
    '''
    def __add__(self, new):
        yr = Yrly_mileage()
        if self.dt_by_yr != new.dt_by_yr:
            raise ValidationError('Yearly mileages must have same year')
        yr.dt_by_yr = self.dt_by_yr
        yr.user_id = self.user_id if self.user_id == new.user_id else ''
        yr.type = self.type if self.type == new.type else 'Total'
        yr.nbr = self.nbr + new.nbr
        if self.tot_dist is None:
            yr.tot_dist = new.tot_dist
        if new.tot_dist is None:
            yr.tot_dist = self.tot_dist
        else:
            yr.tot_dist = self.tot_dist + new.tot_dist
        
        yr.tot_sec = self.tot_sec + new.tot_sec
        return yr