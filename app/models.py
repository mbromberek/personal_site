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
from flask import url_for, current_app

# Custom Classes
from app import db, login
from app.utils import tm_conv


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

    last_failed_login_dttm = db.Column(db.DateTime)
    failed_login_ct = db.Column(db.Integer, default=0)

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

    def get_token(self, expires_in=-1):
        if expires_in == -1:
            expires_in = current_app.config['TOKEN_EXPIRES_AFTER']
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token, self.token_expiration
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token, self.token_expiration

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user

    def check_account_status(self):
        # If last_failed_login_dttm has a value
        #  and Has it been over 30 minutes since last failed login attempt
        if self.last_failed_login_dttm and self.last_failed_login_dttm < \
          datetime.utcnow() - timedelta(seconds=current_app.config['ACCOUNT_LOCK_TIME']):
            return True
        # Does user have under 3 failed login attempts
        elif self.failed_login_ct < \
          current_app.config['MAX_FAIL_PASSWORD_ATTEMPTS']:
            return True
        else:
            return False

    def updt_acct_stat(self, login_status):
        if login_status:
            self.failed_login_ct = 0
        else:
            # if this is the first failed attempt since account was unlocked set the failed_login_ct to 1
            if self.last_failed_login_dttm != None and self.last_failed_login_dttm > \
              datetime.utcnow() - timedelta(current_app.config['ACCOUNT_LOCK_TIME']) \
              and self.failed_login_ct >=current_app.config['MAX_FAIL_PASSWORD_ATTEMPTS']:
                self.failed_login_ct = 1
            else:
                self.failed_login_ct += 1
            self.last_failed_login_dttm = datetime.utcnow()
        db.session.commit()



class Workout(PaginatedAPIMixin, db.Model):
    __table_args__ = {"schema": "fitness", 'comment':'Store Workout data'}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('fitness.user.id'))
    # Running | Cycling | Swimming | Indoor Running
    type = db.Column(db.String(50), index=True, nullable=False)
    wrkt_dttm = db.Column(db.DateTime, index=True, nullable=False)
    dur_sec = db.Column(db.Integer())
    dist_mi = db.Column(db.Numeric(8,2))
    pace_sec = db.Column(db.Integer())# replace with function
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
    wethr_cond_strt = db.Column(db.String(50))
    hmdty_strt = db.Column(db.Numeric(8,2))
    wind_speed_strt = db.Column(db.Numeric(8,2))
    wind_gust_strt = db.Column(db.Numeric(8,2))

    temp_end = db.Column(db.Numeric(8,2))
    temp_feels_like_end = db.Column(db.Numeric(8,2))
    wethr_cond_end = db.Column(db.String(50))
    hmdty_end = db.Column(db.Numeric(8,2))
    wind_speed_end = db.Column(db.Numeric(8,2))
    wind_gust_end = db.Column(db.Numeric(8,2))

    notes = db.Column(db.Text())

    warm_up_tot_dist_mi = db.Column(db.Numeric(5,2))
    warm_up_tot_tm_sec = db.Column(db.Integer())
    warm_up_tot_pace_sec = db.Column(db.Integer())#replace with func
    cool_down_tot_dist_mi = db.Column(db.Numeric(5,2))
    cool_down_tot_tm_sec = db.Column(db.Integer())
    cool_down_tot_pace_sec = db.Column(db.Integer())#replace
    intrvl_tot_dist_mi = db.Column(db.Numeric(5,2))
    intrvl_tot_tm_sec = db.Column(db.Integer())
    intrvl_tot_pace_sec = db.Column(db.Integer())#replace
    intrvl_tot_ele_up = db.Column(db.Numeric(8,2))
    intrvl_tot_ele_down = db.Column(db.Numeric(8,2))

    isrt_ts = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    workout_intervals = db.relationship('Workout_interval', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<Workout {}: {}>'.format(self.type, self.wrkt_dttm)

    def pace_str(self):
        return tm_conv.sec_to_time(tm_conv.pace_calc(self.dist_mi, self.dur_sec), 'ms')

    def dur_str(self):
        return tm_conv.sec_to_time(self.dur_sec)
    def intrvl_dur_str(self):
        return tm_conv.sec_to_time(self.intrvl_tot_tm_sec)
    def warm_up_dur_str(self):
        return tm_conv.sec_to_time(self.warm_up_tot_tm_sec)
    def cool_down_dur_str(self):
        return tm_conv.sec_to_time(self.cool_down_tot_tm_sec)

    def intrvl_pace_str(self):
        return tm_conv.sec_to_time(tm_conv.pace_calc(self.intrvl_tot_dist_mi, self.intrvl_tot_tm_sec),'ms')
    def cool_down_pace_str(self):
        return tm_conv.sec_to_time(tm_conv.pace_calc(self.cool_down_tot_dist_mi, self.cool_down_tot_tm_sec),'ms')
    def warm_up_pace_str(self):
        return tm_conv.sec_to_time(tm_conv.pace_calc(self.warm_up_tot_dist_mi, self.warm_up_tot_tm_sec),'ms')

    def to_dict(self, include_calc_fields=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'wrkt_dttm': self.wrkt_dttm.isoformat() + 'Z',
            'dur_sec': self.dur_sec,
            'dist_mi': str(self.dist_mi),
            'pace': self.pace_str(),
            'gear': self.gear,
            'clothes': self.clothes,
            'ele_up': str(self.ele_up),
            'ele_down': str(self.ele_down),
            'hr': self.hr,
            'cal_burn': self.cal_burn,
            'category': self.category,
            'location': self.location,
            'training_type': self.training_type,
            'weather_start': {
                'temp': str(self.temp_strt),
                'temp_feels_like': str(self.temp_feels_like_strt),
                'wethr_cond': self.wethr_cond_strt,
                'hmdty': str(self.hmdty_strt),
                'wind_speed': str(self.wind_speed_strt),
                'wind_gust': str(self.wind_gust_strt)
            },
            'weather_end': {
                'temp': str(self.temp_strt),
                'temp_feels_like': str(self.temp_feels_like_strt),
                'wethr_cond': self.wethr_cond_strt,
                'hmdty': str(self.hmdty_strt),
                'wind_speed': str(self.wind_speed_strt),
                'wind_gust': str(self.wind_gust_strt)
            },
            'notes': self.notes,

            'warm_up_tot_dist_mi': str(self.warm_up_tot_dist_mi),
            'warm_up_tot_tm_sec': str(self.warm_up_tot_tm_sec),
            'warm_up_pace': self.warm_up_pace_str(),
            'cool_down_tot_dist_mi': str(self.cool_down_tot_dist_mi),
            'cool_down_tot_tm_sec': str(self.cool_down_tot_tm_sec),
            'cool_down_pace': self.cool_down_pace_str(),
            'intrvl_tot_dist_mi': str(self.intrvl_tot_dist_mi),
            'intrvl_tot_tm_sec': str(self.intrvl_tot_tm_sec),
            'intrvl_pace': self.intrvl_pace_str(),
            'intrvl_tot_ele_up': str(self.intrvl_tot_ele_up),
            'intrvl_tot_ele_down': str(self.intrvl_tot_ele_down),

            'isrt_ts': self.isrt_ts.isoformat() + 'Z',
            '_links':{
                'self': url_for('api.get_workout', id=self.id)
            }
        }
        return data

    def from_dict(self, data, user_id):

        str_fields = ['type','gear', 'clothes', 'category', 'location', 'training_type', 'notes']
        int_fields = ['dur_sec','hr','cal_burn','warm_up_tot_tm_sec', 'cool_down_tot_tm_sec', 'intrvl_tot_tm_sec']
        float_fields = ['dist_mi','ele_up','ele_down','warm_up_tot_dist_mi','cool_down_tot_dist_mi','intrvl_tot_dist_mi','intrvl_tot_ele_up','intrvl_tot_ele_down']

        setattr(self, 'user_id', user_id)
        # TODO need to validate date format
        if 'wrkt_dttm' in data:
            self.wrkt_dttm = datetime.strptime(data['wrkt_dttm'], '%Y-%m-%dT%H:%M:%SZ')

        for field in str_fields:
            if field in data:
                setattr(self, field, data[field])

        for field in int_fields:
            if field in data:
                setattr(self, field, int(data[field]))

        for field in float_fields:
            if field in data:
                setattr(self, field, float(data[field]))

        # Populate Weather data
        wethr_float_fields = ['temp','temp_feels_like','hmdty', 'wind_speed','wind_gust']
        wethr_str_fields = ['wethr_cond']
        if 'wethr_start' in data:
            wethr_data = data['wethr_start']
            for field in wethr_float_fields:
                setattr(self, field + '_strt', float(wethr_data[field]))
            for field in wethr_str_fields:
                setattr(self, field + '_strt', wethr_data[field])
        if 'wethr_end' in data:
            wethr_data = data['wethr_end']
            for field in wethr_float_fields:
                setattr(self, field + '_end', float(wethr_data[field]))
            for field in wethr_str_fields:
                setattr(self, field + '_end', wethr_data[field])

    def update(self, updt_wrkt):
        merge_fields = ['type', 'wrkt_dttm', 'dur_sec', 'dist_mi', 'gear', 'clothes', 'category', 'location', 'training_type', 'notes','hr','cal_burn','warm_up_tot_tm_sec', 'cool_down_tot_tm_sec', 'intrvl_tot_tm_sec','ele_up','ele_down','warm_up_tot_dist_mi','cool_down_tot_dist_mi','intrvl_tot_dist_mi','intrvl_tot_ele_up','intrvl_tot_ele_down']
        for field in merge_fields:
            if getattr(updt_wrkt, field) != None:
                setattr(self, field, getattr(updt_wrkt, field))

class Workout_interval(db.Model):
    # Constraint unique for id and interval_order
    __table_args__ = {"schema": "fitness", 'comment':'Intervals for a workout'}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('fitness.user.id'))
    workout_id = db.Column(db.Integer, db.ForeignKey('fitness.workout.id'))
    # pause | segment | mile | kilometer | custom
    break_type = db.Column(db.String(50), nullable=False)
    interval_order = db.Column(db.Integer(), nullable=False)
    interval_desc = db.Column(db.String(50), nullable=True)
    dur_sec = db.Column(db.Integer(), nullable=False)
    dist_mi = db.Column(db.Numeric(8,2), nullable=False)
    hr = db.Column(db.SmallInteger(), nullable=True)
    ele_up = db.Column(db.Numeric(8,2), nullable=True)
    ele_down = db.Column(db.Numeric(8,2), nullable=True)
    notes = db.Column(db.Text(), nullable=True)
    isrt_ts = db.Column(db.DateTime, nullable=False, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Workout {}: interval order {} for {}>'.format( self.workout_id, self.interval_order, self.desc)

    def __lt__(self, other):
        if self.workout_id != other.workout_id:
            return self.workout_id < other.workout_id
        if self.break_type != other.break_type:
            return self.break_type < other.break_type
        return self.interval_order < other.interval_order


    def pace_str(self):
        if self.dist_mi == 0 or self.dur_sec == 0:
            return 0
        return tm_conv.sec_to_time(math.floor(self.dur_sec / self.dist_mi), 'ms')

    def dur_str(self):
        return tm_conv.sec_to_time(self.dur_sec)

    def from_dict(self, data, user_id, wrkt_id, break_type):
        str_fields = ['notes', 'interval_desc']
        int_fields = ['interval_order','dur_sec','hr']
        float_fields = ['dist_mi','ele_up','ele_down']

        setattr(self, 'user_id', user_id)
        setattr(self, 'workout_id', wrkt_id)
        setattr(self, 'break_type', break_type)

        for field in str_fields:
            if field in data:
                setattr(self, field, data[field])

        for field in int_fields:
            if field in data:
                setattr(self, field, int(data[field]))

        for field in float_fields:
            if field in data:
                setattr(self, field, float(data[field]))

    def to_dict(self, include_calc_fields=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'workout_id': self.workout_id,
            'break_type': self.break_type,
            'interval_order': self.interval_order,
            'interval_desc': self.interval_desc,
            'dur_sec': self.dur_sec,
            'dist_mi': str(self.dist_mi),
            'hr': str(self.hr),
            'ele_up': str(self.ele_up),
            'ele_down': str(self.ele_down),
            'notes': self.notes,
            'isrt_ts': self.isrt_ts.isoformat() + 'Z'
        }
        return data

    @staticmethod
    def to_intrvl_lst_dict(wrkt_intrvl_lst):
        wrkt_dict_intrvl_lst = []
        for wrkt_inrvl in wrkt_intrvl_lst:
            wrkt_dict_intrvl_lst.append(wrkt_inrvl.to_dict())
        return wrkt_dict_intrvl_lst


    @staticmethod
    def from_intrvl_lst_dict(data, current_user_id, wrkt_id):
        break_type = data['break_type']
        interval_lst = data['intervals']
        wrkt_intrvl_dict_list = []

        for interval in interval_lst:
            wrkt_intrvl = Workout_interval()
            wrkt_intrvl.from_dict(interval, current_user_id, wrkt_id, break_type)
            db.session.add(wrkt_intrvl)

        db.session.commit()
        wrkt_intrvl_dict_list = \
          Workout_interval.to_intrvl_lst_dict( \
          Workout_interval.query.filter_by( \
          workout_id=wrkt_id, user_id=current_user_id))
        # wrkt_intrvl_dict_list.append(wrkt_intrvl.to_dict())

        return wrkt_intrvl_dict_list
