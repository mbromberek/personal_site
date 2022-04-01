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
from flask import current_app

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
        '''
        center_point: dictionary with items lat and lon
        new_point: dictionary with items lat and lon
        Returns distance between center_point and new_point in miles
        '''
        center_point_tuple = (center_point['lat'], center_point['lon'])
        point_tuple = (new_point['lat'], new_point['lon'])

        dist = distance.distance(center_point_tuple, point_tuple).miles
        return dist

    @staticmethod
    def closest_location(center_points, point, min_radius=-1):
        '''
        Returns the name of center_point that is closest to point
        center_points: list of Location
        point: dictionary with items lat and lon
        min_radius: minimum distance to consider for a location in miles, can be overrided by Location.radius
        '''
        if min_radius <0:
            min_radius = current_app.config['MIN_LOC_RADIUS']
        location_name = ''
        lowest_dist = 9999 # Earths diameter is less than 8000 miles

        for location in center_points:
            center_point = {'lat':location.lat, 'lon':location.lon}
            dist = Location.get_distance(center_point, point)
            if location.radius != None:
                min_dist = location.radius
            else:
                min_dist = min_radius
            if dist < lowest_dist and dist < min_dist:
                lowest_dist = dist
                location_name = location.name
        return location_name
