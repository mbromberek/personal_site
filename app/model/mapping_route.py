# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# First Party Classes
from datetime import datetime, timedelta, date

# Third party classes
# from flask_login import UserMixin
# from werkzeug.security import generate_password_hash, check_password_hash
# from flask import url_for, current_app
# from sqlalchemy import or_

# Custom Classes
from app import db
from app.utils import const
from app import logger

class Route(db.Model):
    __table_args__ = {"schema": "mapping", 'comment':'Store manually created routes'}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('fitness.user.id'))
    name = db.Column(db.String(255), nullable=False)
    dist = db.Column(db.Numeric())
    dist_uom = db.Column(db.String(50), nullable=False)
    public = db.Column(db.Boolean(), default=False)
    lat_start = db.Column(db.Numeric())
    lon_start = db.Column(db.Numeric())
    lat_end = db.Column(db.Numeric())
    lon_end = db.Column(db.Numeric())
    isrt_ts = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updt_ts = db.Column(db.DateTime, nullable=False, index=True, default=datetime.utcnow)
    
    def __repr__(self):
        return '<Route: {}, Distance: {} {}>'.format( self.name, self.dist, self.dist_uom)
    
    def __lt__(self, other):
        return ((self.name < other.name))
    def __gt__(self, other):
        return ((self.name > other.name))

    

class Route_coord(db.Model):
    __table_args__ = {"schema": "mapping", 'comment':'Store manually created routes'}
    route_id = db.Column(db.Integer, db.ForeignKey('mapping.route.id'), nullable=False, primary_key=True)
    step = db.Column(db.Integer, nullable=False, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('fitness.user.id'))
    coordinates = db.Column(db.String(), nullable=False)
    
    # def __init__(self, )

    def __repr__(self):
        return '<Route ID: {}, Step: {} {}>'.format( self.route_id, self.dist, self.dist_uom)

    def __lt__(self, other):
        if self.route_id != other.route_id:
            return ((self.route_id < other.route_id))
        return ((self.step < other.step))
    
    def __gt__(self, other):
        if self.route_id != other.route_id:
            return ((self.route_id > other.route_id))
        return ((self.step > other.step))
    
