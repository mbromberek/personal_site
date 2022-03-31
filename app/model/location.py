# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# First party classes
from datetime import datetime, timedelta, date

# Third party classes
from geopy import distance

# Customer classes
from app import logger
from app import db

class Location(db.Model):
    __table_args__ = {"schema": "fitness", 'comment':'Store location names based on GPS Coordinate'}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('fitness.user.id'))
    name = db.Column(db.String(50), index=False, nullable=False)
    lat = db.Column(db.String(), nullable=False)
    lon = db.Column(db.String(), nullable=False)
    radius = db.Column(db.Numeric(8,2), nullable=True)
    isrt_ts = db.Column(db.DateTime, nullable=False, index=True, default=datetime.utcnow)
    updt_ts = db.Column(db.DateTime, nullable=False, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Location Name: {}, lat: {}, lon: {}>'.format( self.name, self.lat, self.lon)




    @staticmethod
    def get_distance(center_point, new_point):
        center_point_tuple = tuple(center_point.values())
        point_tuple = tuple(new_point.values())

        dist = distance.distance(center_point_tuple, point_tuple).miles
        return dist

    @staticmethod
    def closest_location(center_points, point, min_dist=1):
        '''
        min_dist is minimum distance to consider for a location in miles
        '''
        location_name = ''

        for location in center_points:
            center_point = {'lat':location.lat, 'lon':location.lon}
            dist = Location.get_distance(center_point, point)
            if dist < min_dist:
                min_dist = dist
                location_name = location.name
        return location_name
