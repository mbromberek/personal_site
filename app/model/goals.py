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
from app.utils import tm_conv, const
from app import logger

class Yrly_goal(object):
    description = ''
    goal = 0
    tot_dist = 0

    def __repr__(self):
        return '<Yearly_goal {}: type {}>'.format(self.description, str(self.goal))

    def calc_pct_comp(self):
        return 1-((self.goal - self.tot_dist) / self.goal)

    def remaining(self):
        return self.goal - self.tot_dist

    def calc_miles_per_day(self, days_remaining):
        if days_remaining == 0:
            return self.remaining()
        return self.remaining() / (days_remaining)
