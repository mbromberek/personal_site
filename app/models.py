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
import os
import base64

# Third party classes
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask import url_for

# Custom Classes
from app import db, login
from app.utils import utils


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page, **kwargs),
                'next': url_for(endpoint, page=page +1, per_page=per_page, **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page -1, per_page=per_page, **kwargs) if resources.has_prev else None
            }
        }
        return data


'''
Store database table structures and functions for the data
'''
class User(PaginatedAPIMixin, UserMixin, db.Model):
# class User(UserMixin, db.Model):
    __table_args__ = {"schema": "fitness", 'comment':'Stores user login details'}
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    displayname = db.Column(db.String(64))
    workouts = db.relationship('Workout', backref='author', lazy='dynamic')
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

    def __repr__(self):
        return '<User {}>'.format(self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        data = {
            'id': self.id,
            'email': self.email,
            'displayname': self.displayname,
            'last_seen': self.last_seen.isoformat() + 'Z',
            '_links':{
                'self': url_for('api.get_user', id=self.id)
                # 'workouts': url_for('api.get_workouts', id=self.id)
            }
        }
        return data

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user


class Workout(PaginatedAPIMixin, db.Model):
    __table_args__ = {"schema": "fitness", 'comment':'Store Workout data'}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('fitness.user.id'))
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

    def __repr__(self):
        return '<Workout {}: {}>'.format(self.type, self.wrkt_dttm)

    def pace_str(self):
        if self.dist_mi == 0 or self.dur_sec == 0:
            return 0
        return utils.sec_to_time(math.floor(self.dur_sec / self.dist_mi), 'ms')

    def dur_str(self):
        return utils.sec_to_time(self.dur_sec)

    def to_dict(self):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'wrkt_dttm': self.wrkt_dttm.isoformat() + 'Z',
            'dur_sec': self.dur_sec,
            'dist_mi': str(self.dist_mi),
            'pace_sec': self.pace_sec,
            '_links':{
                'self': url_for('api.get_workout', id=self.id)
            }
        }
        return data


# class Workout_Intervals(db.Model):
