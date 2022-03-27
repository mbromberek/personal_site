# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# First Party Classes
from datetime import datetime, timedelta, date

# Custom Classes
from app import db, login
from app import logger
from app.models import User, Workout

class Workout_point(db.Model):
    __table_args__ = {"schema": "fitness", 'comment':'Store GPS points and other data during Workout'}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('fitness.user.id'))
    workout_id = db.Column(db.Integer, db.ForeignKey('fitness.workout.id'))

    lat = db.Column(db.Numeric(), nullable=True)
    lon = db.Column(db.Numeric(), nullable=True)

    ts = db.Column(db.DateTime, nullable=False)
    delta_ts_sec = db.Column(db.Numeric(), nullable=True)
    dur_sec = db.Column(db.Integer(), nullable=True)

    hr = db.Column(db.Numeric(8,2), nullable=True)
    cadence = db.Column(db.Numeric(), nullable=True)
    speed = db.Column(db.Numeric(), nullable=True)

    dist_m = db.Column(db.Numeric(), nullable=True)
    dist_mi = db.Column(db.Numeric(), nullable=True)
    dist_km = db.Column(db.Numeric(), nullable=True)
    delta_dist_mi = db.Column(db.Numeric(), nullable=True)
    delta_dist_km = db.Column(db.Numeric(), nullable=True)

    ele_up = db.Column(db.Numeric(), nullable=True)
    ele_down = db.Column(db.Numeric(), nullable=True)
    delta_ele_ft = db.Column(db.Numeric(), nullable=True)

    altitude_m = db.Column(db.Numeric(), nullable=True)
    altitude_ft = db.Column(db.Numeric(), nullable=True)

    lap = db.Column(db.Integer(), nullable=False)
    mile = db.Column(db.Integer(), nullable=False)
    kilometer = db.Column(db.Integer(), nullable=False)
    resume = db.Column(db.Integer(), nullable=False)
    isrt_ts = db.Column(db.DateTime, nullable=False, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Workout {}: points lat:{} lon:{}>'.format( self.workout_id, str(self.lat), str(self.lon))

    def __lt__(self, other):
        if self.workout_id != other.workout_id:
            return self.workout_id < other.workout_id
        return self.ts < other.ts

    def to_dict(self, include_calc_fields=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'workout_id': self.workout_id,
        }
        if self.lat != None:
            data['lat'] = (self.lat)
        if self.lon != None:
            data['lon'] = (self.lon)
        if self.ts != None:
            data['ts'] = self.ts.isoformat() + 'Z'
        if self.delta_ts_sec != None:
            data['delta_ts_sec'] = (self.delta_ts_sec)
        if self.dur_sec != None:
            data['dur_sec'] = (self.dur_sec)
        if self.hr != None:
            data['hr'] = (self.hr)
        if self.cadence != None:
            data['cadence'] = (self.cadence)
        if self.speed != None:
            data['speed'] = (self.speed)
        if self.dist_m != None:
            data['dist_m'] = self.dist_m
        if self.dist_mi != None:
            data['dist_mi'] = self.dist_mi
        if self.dist_km != None:
            data['dist_km'] = self.dist_km
        if self.delta_dist_mi != None:
            data['delta_dist_mi'] = (self.delta_dist_mi)
        if self.delta_dist_km != None:
            data['delta_dist_km'] = (self.delta_dist_km)
        if self.ele_up != None:
            data['ele_up'] = (self.ele_up)
        if self.ele_down != None:
            data['ele_down'] = (self.ele_down)
        if self.delta_ele_ft != None:
            data['delta_ele_ft'] = (self.delta_ele_ft)
        if self.altitude_m != None:
            data['altitude_m'] = (self.altitude_m)
        if self.altitude_ft != None:
            data['altitude_ft'] = (self.altitude_ft)
        if self.lap != None:
            data['lap'] = (self.lap)
        if self.mile != None:
            data['mile'] = (self.mile)
        if self.kilometer != None:
            data['kilometer'] = (self.kilometer)
        if self.resume != None:
            data['resume'] = (self.resume)
        # }
        return data

    def from_dict(self, data, user_id, wrkt_id):
        str_fields = []
        int_fields = ['dur_sec', 'lap', 'mile', 'kilometer', 'resume']
        float_fields = ['lat','lon', 'delta_ts_sec', 'hr', 'cadence', 'speed', 'dist_m', 'dist_mi', 'dist_km', 'delta_dist_mi', 'delta_dist_km', 'ele_up', 'ele_down', 'delta_ele_ft', 'altitude_m', 'altitude_ft']
        ts_fields = ['ts']

        setattr(self, 'user_id', user_id)
        setattr(self, 'workout_id', wrkt_id)

        for field in str_fields:
            if field in data and data[field] != None:
                setattr(self, field, data[field])

        for field in int_fields:
            if field in data and data[field] != None:
                setattr(self, field, int(data[field]))

        for field in float_fields:
            if field in data and data[field] != None:
                setattr(self, field, float(data[field]))
        for field in ts_fields:
            if field in data and data[field] != None:
                setattr(self, field, data[field])

    @staticmethod
    def to_pt_lst_dict(wrkt_pt_lst):
        wrkt_dict_pt_lst = []
        for wrkt_pt in wrkt_pt_lst:
            wrkt_dict_pt_lst.append(wrkt_pt.to_dict())
        return wrkt_dict_pt_lst


    @staticmethod
    def from_pt_lst_dict(data, current_user_id, wrkt_id):
        pt_lst = data
        wrkt_pt_dict_list = []

        for pt in pt_lst:
            wrkt_pt = Workout_point()
            wrkt_pt.from_dict(pt, current_user_id, wrkt_id)
            db.session.add(wrkt_pt)

        db.session.commit()
        wrkt_pt_dict_list = \
          Workout_point.to_pt_lst_dict( \
          Workout_point.query.filter_by( \
          workout_id=wrkt_id, user_id=current_user_id))

        return wrkt_pt_dict_list
