# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# First Party Classes

# Custom Classes
from app import db, login
from app import logger
from app.models import Workout_zone

class Workout_zones(object):
    pace_zone_lst = ''
    hr_zone_lst = ''

    def __init__(self, user_id):
        zone_dict = {}
        zone_results = Workout_zone.query.filter_by(user_id=user_id).order_by('zone')
        hr_lst = []
        pace_lst = []
        for zone in zone_results:
            if zone.type == 'hr':
                hr_lst.append(zone)
            if zone.type == 'pace':
                pace_lst.append(zone)
        self.hr_zone_lst = hr_lst
        self.pace_zone_lst = pace_lst

    def pace_zone(self, pace_val):
        if pace_val == 0:
            return ''
        for zone in self.pace_zone_lst:
            if pace_val >= zone.val:
                return zone.zone
        return ''

    def hr_zone(self, hr_val):
        if hr_val == 0:
            return ''
        for zone in self.hr_zone_lst:
            if hr_val <= zone.val:
                return zone.zone
        return ''
