#! /Users/mikeyb/Applications/python3
# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# First Party Classes
from datetime import datetime, timedelta
import math
import re

# Third party classes
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Custom Classes
from app import db, login


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# class PaginatedAPIMixin(object):
#     @staticmethod
#     def to_collection_dict(query, page, per_page, endpoint, **kwargs):
#         resources = query.paginate(page, per_page, False)
#         data = {
#             'items': [item.to_dict() for item in resources.items],
#             '_meta': {
#                 'page': page,
#                 'per_page': per_page,
#                 'total_pages': resources.pages,
#                 'total_items': resources.total
#             },
#             '_links': {
#                 'self': url_for(endpoint, page=page, per_page=per_page, **kwargs),
#                 'next': url_for(endpoint, page=page +1, per_page=per_page, **kwargs) if resources.has_next else None,
#                 'prev': url_for(endpoint, page=page -1, per_page=per_page, **kwargs) if resources.has_prev else None
#             }
#         }
#         return data
#

'''
Store database table structures and functions for the data
'''
# class User(PaginatedAPIMixin, UserMixin, db.Model):
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    displayname = db.Column(db.String(64))
    workouts = db.relationship('Workout', backref='author', lazy='dynamic')
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # Running | Cycling | Swimming | Indoor Running
    type = db.Column(db.String(50), index=True, nullable=False)
    wrkt_dttm = db.Column(db.DateTime, index=True, nullable=False)
    dur_sec = db.Column(db.Integer())
    dist_mi = db.Column(db.Numeric(8,2))
    pace_sec = db.Column(db.Integer())
    gear = db.Column(db.String(50))
    clothes = db.Column(db.Text())
    ele_up = db.Column(db.Numeric(8,2))
    ele_down = db.Column(db.Numeric(8,2))
    hr = db.Column(db.SmallInteger())
    cal_burn = db.Column(db.Integer())

    # Training | Easy | Long Run
    category = db.Column(db.String(50))
    location = db.Column(db.String(50))
    # 800m repeats | hills
    training_type = db.Column(db.String(50))

    temp_strt = db.Column(db.Numeric(8,2))
    temp_feels_like_strt = db.Column(db.Numeric(8,2))
    wethr_cond_strt = db.Column(db.Numeric(8,2))
    hmdty_strt = db.Column(db.Numeric(8,2))
    wind_speed_strt = db.Column(db.Numeric(8,2))
    wind_gust_strt = db.Column(db.Numeric(8,2))

    temp_end = db.Column(db.Numeric(8,2))
    temp_feels_like_end = db.Column(db.Numeric(8,2))
    wethr_cond_end = db.Column(db.Numeric(8,2))
    hmdty_end = db.Column(db.Numeric(8,2))
    wind_speed_end = db.Column(db.Numeric(8,2))
    wind_gust_end = db.Column(db.Numeric(8,2))

    notes = db.Column(db.Text())

    warm_up_tot_dist_mi = db.Column(db.Numeric(5,2))
    warm_up_tot_tm_sec = db.Column(db.Integer())
    warm_up_tot_pace_sec = db.Column(db.Integer())
    cool_down_tot_dist_mi = db.Column(db.Numeric(5,2))
    cool_down_tot_tm_sec = db.Column(db.Integer())
    cool_down_tot_pace_sec = db.Column(db.Integer())
    intrvl_tot_dist_mi = db.Column(db.Numeric(5,2))
    intrvl_tot_tm_sec = db.Column(db.Integer())
    intrvl_tot_pace_sec = db.Column(db.Integer())
    intrvl_tot_ele_up = db.Column(db.Numeric(8,2))
    intrvl_tot_ele_down = db.Column(db.Numeric(8,2))

    isrt_ts = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    # @staticmethod
    # def sec_to_time(tm_sec):
    #     '''
    #     Convert passed in time from seconds to time string in format ##h ##m ##s
    #     '''
    #     SECONDS_IN_HOUR = 3600
    #     SECONDS_IN_MINUTE = 60
    #     hours = math.floor(tm_sec / SECONDS_IN_HOUR)
    #     minutes = math.floor((tm_sec % SECONDS_IN_HOUR) / SECONDS_IN_MINUTE)
    #     seconds = (tm_sec % SECONDS_IN_HOUR) % SECONDS_IN_MINUTE
    #
    #     tm_str = str(hours) + 'h ' + str(minutes).zfill(2) + 'm ' + str(seconds).zfill(2) + 's'
    #     return tm_str
    #
    # @staticmethod
    # def time_to_sec(tm_str):
    #     '''
    #     Convert passed in time string from format ##h ##m ##s to seconds
    #     '''
    #     SECONDS_IN_HOUR = 3600
    #     SECONDS_IN_MINUTE = 60
    #
    #     hours_sec = int(re.search('(\d*)h', tm_str).group(1))*SECONDS_IN_HOUR if re.search('(\d*)h', tm_str) else 0
    #     minutes_sec = int(re.search('(\d*)m', tm_str).group(1))*SECONDS_IN_MINUTE if re.search('(\d*)m', tm_str) else 0
    #     seconds = int(re.search('(\d*)s', tm_str).group(1)) if re.search('(\d*)s', tm_str) else 0
    #
    #     tm_sec = hours_sec + minutes_sec + seconds
    #
    #     return tm_sec


    def __repr__(self):
        return '<Workout {}: {}>'.format(self.type, self.wrkt_dttm)


# class Workout_Intervals(db.Model):
