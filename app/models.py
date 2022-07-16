# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# First Party Classes
from datetime import datetime, timedelta, date
import math
import re
import os
import base64

# Third party classes
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask import url_for, current_app
from sqlalchemy import or_

# Custom Classes
from app import db, login
from app.utils import tm_conv, const
from app import logger


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
    settings = db.relationship('User_setting', backref='author', lazy='dynamic')
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

    def get_settings(self):
        settings = self.settings.first()
        if settings is None:
            settings = User_setting()
        return settings

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
    # type = db.Column(db.String(50), index=True, nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('fitness.workout_type.id'))
    wrkt_dttm = db.Column(db.DateTime, index=True, nullable=False)
    dur_sec = db.Column(db.Integer())
    dist_mi = db.Column(db.Numeric(8,2))
    pace_sec = db.Column(db.Integer())# replace with function
    # gear = db.Column(db.String(50))
    gear_id = db.Column(db.Integer, db.ForeignKey('fitness.gear.id'))
    clothes = db.Column(db.Text())
    ele_up = db.Column(db.Numeric(8,2))
    ele_down = db.Column(db.Numeric(8,2))
    hr = db.Column(db.Numeric(8,2))
    cal_burn = db.Column(db.Integer())

    # Training | Easy | Long Run
    # category = db.Column(db.String(50))
    category_id = db.Column(db.Integer, db.ForeignKey('fitness.workout_category.id'))
    location = db.Column(db.String(50))
    # 800m repeats | hills
    training_type = db.Column(db.String(50))

    temp_strt = db.Column(db.Numeric(8,2))
    temp_feels_like_strt = db.Column(db.Numeric(8,2))
    wethr_cond_strt = db.Column(db.String(50))
    hmdty_strt = db.Column(db.Numeric(8,2))
    wind_speed_strt = db.Column(db.Numeric(8,2))
    wind_gust_strt = db.Column(db.Numeric(8,2))
    dew_point_strt = db.Column(db.Numeric(8,2))

    temp_end = db.Column(db.Numeric(8,2))
    temp_feels_like_end = db.Column(db.Numeric(8,2))
    wethr_cond_end = db.Column(db.String(50))
    hmdty_end = db.Column(db.Numeric(8,2))
    wind_speed_end = db.Column(db.Numeric(8,2))
    wind_gust_end = db.Column(db.Numeric(8,2))
    dew_point_end = db.Column(db.Numeric(8,2))

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

    show_pause = db.Column(db.Boolean())
    source = db.Column(db.String(50))

    wrkt_dir = db.Column(db.String())
    lat_strt = db.Column(db.Numeric())
    long_strt = db.Column(db.Numeric())
    lat_end = db.Column(db.Numeric())
    long_end = db.Column(db.Numeric())
    thumb_path = db.Column(db.Text())

    show_map_laps = db.Column(db.Boolean())
    show_map_miles = db.Column(db.Boolean())

    isrt_ts = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    workout_intervals = db.relationship('Workout_interval', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<Workout {}: {}>'.format(self.type_id, self.wrkt_dttm)

    def pace_str(self):
        # if self.type in ['Cycling','Indoor Cycling']:
        if self.type_det.nm in ['Cycling','Indoor Cycling']:
            return str(round(tm_conv.mph_calc(self.dist_mi, self.dur_sec),2))
        else:
            return tm_conv.sec_to_time(self.pace_sec(), 'ms')
    def pace_sec(self):
        return tm_conv.pace_calc(self.dist_mi, self.dur_sec)

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

    def weather_str(self):
        weather_strt_str = 'Start: {} degrees {}, {} percent humidity, wind speed {} mph, wind gust {} mpn, feels like {} degrees, dew point {}.'.format(self.temp_strt, self.wethr_cond_strt, self.hmdty_strt, self.wind_speed_strt, self.wind_gust_strt, self.temp_feels_like_strt, self.dew_point_strt)
        weather_end_str = 'End: {} degrees {}, {} percent humidity, wind speed {} mph, wind gust {} mpn, feels like {} degrees, dew point {}.'.format(self.temp_end, self.wethr_cond_end, self.hmdty_end, self.wind_speed_end, self.wind_gust_end, self.temp_feels_like_end, self.dew_point_end)
        return '{}\n{}'.format(weather_strt_str,weather_end_str)

    # Parameter export_fields is a list of the fields to export
    def to_dict_export(self, export_fields):
        data = {}
        for field in export_fields:
            # TODO should user_id be replaced by user_name?
            if field not in const.EXPORT_FIELDS:
                data[field] = ''
            elif const.EXPORT_FIELD_MAPPING.get(field) == 'wrkt_dttm':
                data[field] = self.wrkt_dttm.strftime('%m/%d/%Y %H:%M:%S')
            elif const.EXPORT_FIELD_MAPPING.get(field) == 'gear':
                gear_rec = Gear.query.filter_by(id=self.gear_id, user_id=self.user_id).first()
                data[field] = gear_rec.nm if gear_rec != None else ''
            elif const.EXPORT_FIELD_MAPPING.get(field) == 'type':
                data[field] = self.type_det.nm
            elif const.EXPORT_FIELD_MAPPING.get(field) == 'category':
                data[field] = self.category_det.nm
            elif const.EXPORT_FIELD_MAPPING.get(field) == 'duration':
                data[field] = self.dur_str()
            elif const.EXPORT_FIELD_MAPPING.get(field) == 'pace':
                data[field] = self.pace_str()
            elif const.EXPORT_FIELD_MAPPING.get(field) == 'pace_sec':
                data[field] = self.pace_sec()
            elif const.EXPORT_FIELD_MAPPING.get(field) == 'notes+':
                data[field] = '{}\n{}\n{}'.format(self.weather_str(), self.clothes, self.notes)
            elif const.EXPORT_FIELD_MAPPING.get(field) == 'elevation':
                data[field] = '{}↑\n{}↓'.format(self.ele_up, self.ele_down)
            elif const.EXPORT_FIELD_MAPPING.get(field) == 'weather':
                data[field] = self.weather_str()
            else:
                data[field] = getattr(self, const.EXPORT_FIELD_MAPPING.get(field,''), '')
        return data

    def to_dict(self, include_calc_fields=False):
        gear_rec = Gear.query.filter_by(id=self.gear_id, user_id=self.user_id).first()
        logger.debug('to_dict category_id: ' + str(self.category_id))
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type_det.nm,
            'wrkt_dttm': self.wrkt_dttm.isoformat() + 'Z',
            'dur_sec': self.dur_sec,
            'dist_mi': str(self.dist_mi),
            'pace': self.pace_str(),
            'gear': gear_rec.nm if gear_rec != None else None,
            'clothes': self.clothes,
            'ele_up': str(self.ele_up),
            'ele_down': str(self.ele_down),
            'hr': str(self.hr),
            'cal_burn': self.cal_burn,
            'category': self.category_det.nm,
            'location': self.location,
            'training_type': self.training_type,
            'weather_start': {
                'temp': str(self.temp_strt),
                'temp_feels_like': str(self.temp_feels_like_strt),
                'wethr_cond': self.wethr_cond_strt,
                'hmdty': str(self.hmdty_strt),
                'wind_speed': str(self.wind_speed_strt),
                'wind_gust': str(self.wind_gust_strt),
                'dew_point' : str(self.dew_point_strt)
            },
            'weather_end': {
                'temp': str(self.temp_end),
                'temp_feels_like': str(self.temp_feels_like_end),
                'wethr_cond': self.wethr_cond_end,
                'hmdty': str(self.hmdty_end),
                'wind_speed': str(self.wind_speed_end),
                'wind_gust': str(self.wind_gust_end),
                'dew_point' : str(self.dew_point_end)
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
            'location_coordinates':{
                'start':{
                    'lat': str(self.lat_strt),
                    'long': str(self.long_strt)
                },
                'end':{
                    'lat': str(self.lat_end),
                    'long': str(self.long_end)
                }
            },

            'isrt_ts': self.isrt_ts.isoformat() + 'Z',
            '_links':{
                'self': url_for('api.get_workout', id=self.id)
            }
        }
        return data

    def from_dict(self, data, user_id):

        str_fields = ['clothes', 'location', 'training_type', 'notes']
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

        if 'gear' in data and data['gear'] != None and data['gear'] != '' :
            self.gear_id = Gear.get_gear_id(data['gear'])
            if self.gear_id is None:
                # Create gear
                new_gear = Gear(nm=data['gear'], type='Shoe', user_id=user_id)
                db.session.add(new_gear)
                db.session.commit()
                self.gear_id = Gear.get_gear_id(data['gear'])

        if 'type' in data and data['type'] != None and data['type'] != '' :
            self.type_id = Workout_type.get_wrkt_type_id(data['type'])
        logger.debug('from_dict category: ' + str(data['category']))
        if 'category' in data and data['category'] != None and data['category'] != '' :
            self.category_id = Workout_category.get_wrkt_cat_id(data['category'])

        # Populate Weather data
        wethr_float_fields = ['temp','temp_feels_like','hmdty', 'wind_speed','wind_gust','dew_point']
        wethr_str_fields = ['wethr_cond']
        if 'wethr_start' in data:
            wethr_data = data['wethr_start']
            for field in wethr_float_fields:
                if field in wethr_data:
                    setattr(self, field + '_strt', float(wethr_data[field]))
            for field in wethr_str_fields:
                if field in wethr_data:
                    setattr(self, field + '_strt', wethr_data[field])
        if 'wethr_end' in data:
            wethr_data = data['wethr_end']
            for field in wethr_float_fields:
                if field in wethr_data:
                    setattr(self, field + '_end', float(wethr_data[field]))
            for field in wethr_str_fields:
                if field in wethr_data:
                    setattr(self, field + '_end', wethr_data[field])


    def update(self, updt_wrkt):
        merge_fields = ['type_id', 'wrkt_dttm', 'dur_sec', 'dist_mi', 'clothes', 'category_id', 'location', 'training_type', 'notes','hr','cal_burn','warm_up_tot_tm_sec', 'cool_down_tot_tm_sec', 'intrvl_tot_tm_sec','ele_up','ele_down','warm_up_tot_dist_mi','cool_down_tot_dist_mi','intrvl_tot_dist_mi','intrvl_tot_ele_up','intrvl_tot_ele_down', 'gear_id']
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
    hr = db.Column(db.Numeric(8,2), nullable=True)
    ele_up = db.Column(db.Numeric(8,2), nullable=True)
    ele_down = db.Column(db.Numeric(8,2), nullable=True)
    notes = db.Column(db.Text(), nullable=True)
    lat = db.Column(db.String(), nullable=True)
    lon = db.Column(db.String(), nullable=True)
    isrt_ts = db.Column(db.DateTime, nullable=False, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Workout {}: interval order {} for {}>'.format( self.workout_id, self.interval_order, self.break_type)

    def __lt__(self, other):
        if self.workout_id != other.workout_id:
            return self.workout_id < other.workout_id
        if self.break_type != other.break_type:
            return self.break_type < other.break_type
        return self.interval_order < other.interval_order


    def pace_str(self):
        return tm_conv.sec_to_time(tm_conv.pace_calc(self.dist_mi, self.dur_sec), 'ms')

    def pace_sec(self):
        return tm_conv.pace_calc(self.dist_mi, self.dur_sec)

    def dur_str(self):
        return tm_conv.sec_to_time(self.dur_sec, 'ms')

    def from_dict(self, data, user_id, wrkt_id, break_type):
        str_fields = ['notes', 'interval_desc', 'lat', 'lon']
        int_fields = ['interval_order','dur_sec']
        float_fields = ['dist_mi','ele_up','ele_down','hr']

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
            'lat': self.lat,
            'lon': self.lon,
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


class Gear(db.Model):
    __table_args__ = {"schema": "fitness", 'comment':'Details about workout gear: shoes, bike, insoles'}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('fitness.user.id'))
    nm = db.Column(db.String(50), index=True, nullable=False, unique=True)
    workouts = db.relationship('Workout', backref='gear_det', lazy='dynamic')
    prchse_dt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    price = db.Column(db.Numeric(8,2))
    retired = db.Column(db.Boolean, nullable=True, default=False)
    confirmed = db.Column(db.Boolean, nullable=True, default=False)
    type = db.Column(db.String(50), index=True, nullable=False)
    company = db.Column(db.String(50))
    isrt_ts = db.Column(db.DateTime, nullable=False, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Gear {}: id {} type {}>'.format( self.nm, self.id, self.type)

    @staticmethod
    def get_gear_id(gear_nm):
        gear_rec = Gear.query.filter_by(nm=gear_nm).first()
        if gear_rec is None:
            return None
        return gear_rec.id

    @staticmethod
    def predict_gear(user_id, category_id, type_id):
        if Workout_type.query.filter_by(id=type_id, grp='run').first() != None:
            return Gear.get_next_shoe(user_id, category_id)
        elif Workout_type.query.filter_by(id=type_id, grp='cycle').first() != None:
            dft_cycl_gear = current_app.config['DFT_CYCL_GEAR']
            return {'nm':dft_cycl_gear, 'id':Gear.get_gear_id(dft_cycl_gear)}
        elif Workout_type.query.filter_by(id=type_id, grp='swim').first() != None:
            dft_swim_gear = current_app.config['DFT_SWIM_GEAR']
            return {'nm':dft_swim_gear, 'id':Gear.get_gear_id(dft_swim_gear)}

    @staticmethod
    def get_next_shoe(user_id, category_id, dt=datetime.today()):
        '''
        Gets suggestion for shoe to wear on next run based on passed in category
        The number of miles run in shoes and number of times they were used determines which category they fit into.
        '''
        user = User.query.get_or_404(user_id)
        settings = user.get_settings()
        shoe_mile_max = settings.get_field('shoe_mile_max')
        shoe_mile_warning = settings.get_field('shoe_mile_warning')
        shoe_min_brkin_ct = settings.get_field('shoe_min_brkin_ct')

        shoe_age_warning = shoe_mile_warning
        nbr_brk_in_runs = shoe_min_brkin_ct
        gear_nm = ''
        gear_id = None
        type='Shoe'
        gear_lst = []
        gear_ct = -1

        cat_rec = Workout_category.query.filter_by(id=category_id).first_or_404()
        if cat_rec.nm in ['Training', 'Long Run', 'Race', 'Hard']:
            # Use gear that has <300 miles on them and used more than 5 times
            gear_lst = sorted(Gear_usage.query.filter(Gear_usage.user_id==user_id, Gear_usage.retired==False, Gear_usage.type==type, Gear_usage.tot_dist <shoe_age_warning, Gear_usage.usage_count >nbr_brk_in_runs), reverse=False)
            gear_ct = len(gear_lst)
        elif cat_rec.nm in ['Easy']:
            # Use gear with >=300 miles on them or used <=5 times
            gear_lst = sorted(Gear_usage.query.filter(Gear_usage.user_id==user_id, Gear_usage.retired==False, Gear_usage.type==type, or_( Gear_usage.tot_dist >=shoe_age_warning, Gear_usage.usage_count <=nbr_brk_in_runs)), reverse=False)
            gear_ct = len(gear_lst)
        if gear_ct <1:
            # If not a known Category or no records returned for Category
            gear_lst = sorted(Gear_usage.query.filter(Gear_usage.user_id==user_id, Gear_usage.retired==False, Gear_usage.type==type), reverse=False)
            gear_ct = len(gear_lst)
        if gear_ct >0:
            gear_nm = gear_lst[0].nm
            gear_id = gear_lst[0].gear_id

        return {'nm':gear_nm, 'id':gear_id}

    def __lt__(self, other):
        if self.retired == False and other.retired == True:
            return False
        if self.retired == True and other.retired == False:
            return True
        self_dt = datetime.combine(self.prchse_dt,datetime.min.time())
        other_dt = datetime.combine(other.prchse_dt,datetime.min.time())
        return ((self_dt < other_dt))

    def __gt__(self, other):
        if self.retired == False and other.retired == True:
            return True
        if self.retired == True and other.retired == False:
            return False
        self_dt = datetime.combine(self.prchse_dt,datetime.min.time())
        other_dt = datetime.combine(other.prchse_dt,datetime.min.time())
        return ((self_dt > other_dt))


class Gear_relationship(db.Model):
    __table_args__ = {"schema": "fitness", 'comment':'Connection between gear like which shoes are used which with insoles'}
    primary_gear_id = db.Column(db.Integer, db.ForeignKey('fitness.gear.id'), primary_key=True)
    secondary_gear_id = db.Column(db.Integer, db.ForeignKey('fitness.gear.id'), primary_key=True)
    adjust_miles = db.Column(db.Numeric(8,2))
    link_strt_dt = db.Column(db.DateTime)
    isrt_ts = db.Column(db.DateTime, nullable=False, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Primary {}: Secondary: {}>'.format( self.primary_gear_id, self.secondary_gear_id)

class Gear_usage(db.Model):
    __table_args__ = {"schema": "fitness", 'comment':'Gear usage'}
    nm = db.Column(db.String(50), index=True, nullable=False)
    usage_count = db.Column(db.Integer)
    tot_dist = db.Column(db.Numeric(8,2))
    tot_dur_sec = db.Column(db.Integer)
    latest_workout = db.Column(db.DateTime)
    first_workout = db.Column(db.DateTime)
    prchse_dt = db.Column(db.DateTime)
    price = db.Column(db.Numeric(8,2))
    retired = db.Column(db.Boolean)
    confirmed = db.Column(db.Boolean)
    type = db.Column(db.String(50))
    company = db.Column(db.String(50))
    gear_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)

    def __repr__(self):
        return '<Gear {}: id {} dt {} retired {}>'.format( self.nm, self.gear_id, str(self.latest_workout), str(self.retired))

    def __lt__(self, other):
        if self.retired == False and other.retired == True:
            return False
        if self.retired == True and other.retired == False:
            return True
        self_dt = self.latest_workout if self.latest_workout else datetime.combine(self.prchse_dt,datetime.min.time())
        other_dt = other.latest_workout if other.latest_workout else datetime.combine(other.prchse_dt,datetime.min.time())
        return ((self_dt < other_dt))

    def __gt__(self, other):
        if self.retired == False and other.retired == True:
            return True
        if self.retired == True and other.retired == False:
            return False
        self_dt = self.latest_workout if self.latest_workout else datetime.combine(self.prchse_dt,datetime.min.time())
        other_dt = other.latest_workout if other.latest_workout else datetime.combine(other.prchse_dt,datetime.min.time())
        return ((self_dt > other_dt))

    def tot_dur_str(self):
        return tm_conv.sec_to_time(self.tot_dur_sec, 'hms')

class Workout_type(db.Model):
    __table_args__ = {"schema": "fitness", 'comment':'Type of workout: Running, Cycling, Swimming, Indoor Running'}
    id = db.Column(db.Integer, primary_key=True)
    workouts = db.relationship('Workout', backref='type_det', lazy='dynamic')
    nm = db.Column(db.String(50), index=True, nullable=False, unique=True)
    grp = db.Column(db.String(50), nullable=True)
    ordr = db.Column(db.Integer, nullable=False)
    isrt_ts = db.Column(db.DateTime, nullable=False, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Workout Type {}: id {}>'.format( self.nm, self.id)

    @staticmethod
    def get_wrkt_type_id(wrkt_nm):
        type_rec = Workout_type.query.filter_by(nm=wrkt_nm).first()
        if type_rec is None:
            return None
        return type_rec.id

    def __lt__(self, other):
        return ((self.ordr < other.ordr))

    def __gt__(self, other):
        return ((self.ordr > other.ordr))

class Workout_category(db.Model):
    __table_args__ = {"schema": "fitness", 'comment':'Category of workout: Easy, Long Run, Training'}
    id = db.Column(db.Integer, primary_key=True)
    workouts = db.relationship('Workout', backref='category_det', lazy='dynamic')
    nm = db.Column(db.String(50), index=True, nullable=False, unique=True)
    ordr = db.Column(db.Integer, nullable=False)
    isrt_ts = db.Column(db.DateTime, nullable=False, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Workout Category {}: id {}>'.format( self.nm, self.id)

    @staticmethod
    def get_wrkt_cat_id(wrkt_nm):
        type_rec = Workout_category.query.filter_by(nm=wrkt_nm).first()
        if type_rec is None:
            return None
        return type_rec.id

    def __lt__(self, other):
        return ((self.ordr < other.ordr))

    def __gt__(self, other):
        return ((self.ordr > other.ordr))


class Wrkt_sum(db.Model):
    __table_args__ = {"schema": "fitness", 'comment':'summary of workouts by type and different date ranges'}
    user_id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), primary_key=True)
    rng = db.Column(db.String(50), primary_key=True)
    tot_sec = db.Column(db.Integer())
    tot_dist = db.Column(db.Numeric(8,2))
    nbr = db.Column(db.Integer())
    oldest_workout = db.Column(db.DateTime)
    newest_workout = db.Column(db.DateTime)

    def __repr__(self):
        return '<Wrkt_sum {}: type {}>'.format(self.rng, self.type)

    def dur_str(self):
        return tm_conv.sec_to_time(self.tot_sec, 'hms')

    @staticmethod
    def generate_missing_summaries(sum_lst, sum_typ):
        sum_lst_mod = sum_lst
        rng_chk_lst = ["Current Week", "Current Month", "Current Year","Past 7 days","Past 30 days"]

        for rng_chk in rng_chk_lst:
            if not (any(summary.rng == rng_chk and summary.type == sum_typ for summary in sum_lst_mod)):
                # Create entry for Current Week that has 0 miles and 0 times
                new_sum = Wrkt_sum()
                new_sum.rng = rng_chk
                new_sum.type = sum_typ
                new_sum.nbr = 0
                new_sum.tot_dist = 0
                new_sum.tot_sec = 0
                sum_lst_mod.append(new_sum)

        return sum_lst_mod

    @staticmethod
    def getInsertPoint(wrkt_sum, wrkt_sum_lst):
        i=0
        while i <len(wrkt_sum_lst):
            if wrkt_sum_lst[i].rng == 'Past 7 days':
                if wrkt_sum.rng == 'Current Week':
                    return i
            elif wrkt_sum_lst[i].rng == 'Current Month':
                if wrkt_sum.rng in ['Past 7 days','Current Week']:
                    return i
            elif wrkt_sum_lst[i].rng == 'Past 30 days':
                if wrkt_sum.rng in ['Past 7 days','Current Week','Current Month']:
                    return i
            elif wrkt_sum_lst[i].rng == 'Current Year':
                if wrkt_sum.rng in ['Past 7 days','Current Week','Current Month','Past 30 days']:
                    return i
            elif wrkt_sum_lst[i].rng == 'Past 365 days':
                if wrkt_sum.rng in ['Past 7 days','Current Week','Current Month','Past 30 days','Current Year']:
                    return i
            i=i+1
        return i

class Wkly_mileage(db.Model):
    __table_args__ = {"schema": "fitness", 'comment':'summary of workouts by type and week'}
    user_id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), primary_key=True)
    nbr = db.Column(db.Integer())
    dt_by_wk = db.Column(db.DateTime, primary_key=True)
    tot_dist = db.Column(db.Numeric(8,2))
    tot_sec = db.Column(db.Integer())
    dist_delta_pct = db.Column(db.Numeric(8,2))
    tm_delta_pct = db.Column(db.Numeric(8,2))

    def __repr__(self):
        return '<Weekly_mileage {}: type {}>'.format(str(self.dt_by_wk), self.type)

    def dur_str(self):
        return tm_conv.sec_to_time(self.tot_sec, 'hms')

    def __lt__(self, other):
        return ((self.dt_by_wk < other.dt_by_wk))

    def __gt__(self, other):
        return ((self.dt_by_wk > other.dt_by_wk))

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

class Workout_zone(db.Model):
    __table_args__ = {"schema": "fitness", 'comment':'workout zones'}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('fitness.user.id'))
    # hr | pace
    type = db.Column(db.String(50), nullable=False)
    zone = db.Column(db.String(50), nullable=False)
    val = db.Column(db.Integer(), nullable=False)

class User_setting(db.Model):
    __table_args__ = {"schema": "fitness", 'comment':'fitness settings for user'}
    user_id = db.Column(db.Integer, db.ForeignKey('fitness.user.id'), primary_key=True)
    shoe_mile_warning = db.Column(db.Numeric(8))
    shoe_mile_max = db.Column(db.Numeric(8))
    shoe_min_brkin_ct = db.Column(db.Numeric(8))
    updt_ts = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    isrt_ts = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<Setting for {}: Value {}>'.format( self.user_id, str(self.shoe_mile_warning))

    def to_dict():
        '''
        Convert object to dictionary and return it
        If any setting field is not populated the default value will be returned
        '''
        data = {'user_id': s.user_id}

        dict_fields_str = []
        dict_fields_nbr = ['shoe_mile_warning' ,'shoe_mile_max' ,'shoe_min_brkin_ct']
        dict_fields_date = ['updt_ts' ,'isrt_ts']

        for field in dict_fields_str:
            data[field] = self.get_field(field)
        for field in dict_fields_nbr:
            data[field] = str(self.get_field(field))
        for field in dict_fields_date:
            if getattr(self, field) is not None:
                data[field] = getattr(self, field).isoformat() + 'Z'

        return data

    def get_field(self, field):
        if getattr(self, field) is not None:
            return getattr(self, field)
        if 'USR_DFT_'+field.upper() in current_app.config:
            return current_app.config['USR_DFT_'+field.upper()]
        else:
            return None
