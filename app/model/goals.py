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
from app.model.yrly_mileage import Yrly_mileage
from app.models import Workout_type
from app.models import PaginatedAPIMixin

class Yrly_goal(object):
    description = ''
    goal = 0
    tot = 0

    def __repr__(self):
        return '<Yearly_goal {}: type {}>'.format(self.description, str(self.goal))

    def __lt__(self, other):
        return ((self.description > other.description))
    
    def __gt__(self, other):
        return ((self.description < other.description))
    

    def calc_pct_comp(self):
        return 1-((self.goal - self.tot) / self.goal)

    def remaining(self):
        return self.goal - self.tot

    def calc_miles_per_day(self, days_remaining):
        if days_remaining == 0:
            return self.remaining()
        return self.remaining() / (days_remaining)
    
    def to_dict(self):
        d = {
            'description':self.description,
            'goal':self.goal,
            'tot':self.tot,
            'uom':self.uom,
            'pct_comp':self.calc_pct_comp(),
            'remaining':self.remaining()
        }
        return d
    
    @staticmethod 
    def lst_to_dict(goal_lst):
        goal_dict_lst = []
        for goal in goal_lst:
            logger.info(goal)
            goal_dict_lst.append(goal.to_dict())
        return goal_dict_lst

    @staticmethod
    def create_goal(yr_mileage, newType=''):
        type_to_use = yr_mileage.type if newType == '' else newType
        yr_goal = Yrly_goal()
        yrly_goals_lst = []

        if type_to_use == 'Running':
            yr_goal.description = 'Run'
            yr_goal.goal = 1779
            yr_goal.tot = yr_mileage.tot_dist
            yr_goal.uom = 'miles'
            yr_goal.pct_comp = yr_goal.calc_pct_comp() *100
            yr_goal.miles_per_day = yr_goal.calc_miles_per_day(365-datetime.now().timetuple().tm_yday) if yr_goal.pct_comp <100 else 0
            yr_goal.miles_needed_per_month = yr_goal.miles_per_day * 30
            # logger.debug(yr_goal.description + ' ' + str(yr_goal.tot) + ' ' + str(round(yr_goal.pct_comp,4)) + ' ' + str(round(yr_goal.miles_per_day,4)) + ' ' + str(round(yr_goal.miles_needed_per_month,4)))
            yr_goal.miles_needed_per_week = yr_goal.miles_per_day * 7
            yrly_goals_lst.append(yr_goal)
            run_set = True
        elif type_to_use == 'Cycling':
            yr_goal = Yrly_goal()
            yr_goal.goal = 300
            yr_goal.uom = 'miles'
            yr_goal.description = 'Cycle'
            yr_goal.tot = yr_mileage.tot_dist
            yr_goal.pct_comp = yr_goal.calc_pct_comp() *100
            yr_goal.miles_per_day = yr_goal.calc_miles_per_day(365-datetime.now().timetuple().tm_yday) if yr_goal.pct_comp <100 else 0
            yr_goal.miles_needed_per_month = yr_goal.miles_per_day * 30
            # logger.debug(yr_goal.description + ' ' + str(yr_goal.tot) + ' ' + str(round(yr_goal.pct_comp,4)) + ' ' + str(round(yr_goal.miles_per_day,4)) + ' ' + str(round(yr_goal.miles_needed_per_month,4)))
            yr_goal.miles_needed_per_week = yr_goal.miles_per_day * 7
            yrly_goals_lst.append(yr_goal)
            cycle_set = True

            yr_goal = Yrly_goal()
            yr_goal.goal = 25
            yr_goal.uom = 'times'
            yr_goal.description = 'Cycle'
            yr_goal.tot = yr_mileage.nbr
            yr_goal.pct_comp = yr_goal.calc_pct_comp() *100

            yr_goal.miles_per_day = yr_goal.calc_miles_per_day(365-datetime.now().timetuple().tm_yday) if yr_goal.pct_comp <100 else 0
            yr_goal.miles_needed_per_month = yr_goal.miles_per_day * 30

            yrly_goals_lst.append(yr_goal)
        elif type_to_use == 'Total':
            yr_goal.description = 'Total'
            yr_goal.goal = 2025
            yr_goal.tot = yr_mileage.tot_dist
            yr_goal.uom = 'miles'
            yr_goal.pct_comp = yr_goal.calc_pct_comp() *100
            yr_goal.miles_per_day = yr_goal.calc_miles_per_day(365-datetime.now().timetuple().tm_yday) if yr_goal.pct_comp <100 else 0
            yr_goal.miles_needed_per_month = yr_goal.miles_per_day * 30
            # logger.debug(yr_goal.description + ' ' + str(yr_goal.tot) + ' ' + str(round(yr_goal.pct_comp,4)) + ' ' + str(round(yr_goal.miles_per_day,4)) + ' ' + str(round(yr_goal.miles_needed_per_month,4)))
            yr_goal.miles_needed_per_week = yr_goal.miles_per_day * 7
            yrly_goals_lst.append(yr_goal)
        return yrly_goals_lst

    @staticmethod
    def generate_nonstarted_goals(yrly_goals_lst):
        yrly_goals_mod_lst = yrly_goals_lst
        if not (any(yr_goal.description == "Run" for yr_goal in yrly_goals_lst)):
            # Create entry for running that has 0 miles and 0 times
            yr = Yrly_mileage()
            yr.type = 'Running'
            yr.nbr = 0
            yr.tot_dist = 0
            yr.tot_sec = 0
            yrly_goals_mod_lst.extend(Yrly_goal.create_goal(yr))
        
        if not (any(yr_goal.description == "Cycle" for yr_goal in yrly_goals_lst)):
            # Create entry for cycling that has 0 miles and 0 times
            yr = Yrly_mileage()
            yr.type = 'Cycling'
            yr.nbr = 0
            yr.tot_dist = 0
            yr.tot_sec = 0
            yrly_goals_mod_lst.extend(Yrly_goal.create_goal(yr))
        
        if not (any(yr_goal.description == "Total" for yr_goal in yrly_goals_lst)):
            yr = Yrly_mileage()
            yr.type = 'Total'
            yr.nbr = 0
            yr.tot_dist = 0
            yr.tot_sec = 0
            yrly_goals_mod_lst.extend(Yrly_goal.create_goal(yr))

        return yrly_goals_mod_lst

class Goal(PaginatedAPIMixin, db.Model):
    __table_args__ = {"schema": "fitness", 'comment':'Stores goals for user'}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('fitness.user.id'))
    description = db.Column(db.String(100), nullable=False)
    start_dt = db.Column(db.DateTime, nullable=False)
    end_dt = db.Column(db.DateTime, nullable=False)
    workout_type_id = db.Column(db.Integer, db.ForeignKey('fitness.workout_type.id'))
    goal_type_id = db.Column(db.Integer, db.ForeignKey('fitness.goal_type.id'))
    goal_total = db.Column(db.Numeric(8,2), nullable=False)
    ordr = db.Column(db.Integer)
    is_active = db.Column(db.Boolean(), nullable=False)
    isrt_ts = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updt_ts = db.Column(db.DateTime, nullable=False, index=True, default=datetime.utcnow)
    
    def __repr__(self):
        return '<Goal {}>'.format(self.description)
    
    def to_dict(self):
        d = {
            'id': self.id,
            'user_id': self.user_id,
            'description':self.description,
            'start_dt': self.start_dt.strftime('%Y-%m-%d %H:%M:%S'),
            'end_dt': self.end_dt.strftime('%Y-%m-%d %H:%M:%S'),
            'workout_type': self.workout_type_det.grp if self.workout_type_id != None else '',
            'goal_type': self.goal_type_det.nm,
            'goal_total':self.goal_total,
            'order': self.ordr,
            'is_active': self.is_active,
            'isrt_ts': self.isrt_ts.strftime('%Y-%m-%d %H:%M:%S'),
            'updt_ts': self.updt_ts.strftime('%Y-%m-%d %H:%M:%S')
        }
        return d

    @staticmethod 
    def lst_to_dict(goal_lst):
        goal_dict_lst = []
        for goal in goal_lst:
            # logger.info(goal)
            goal_dict_lst.append(goal.to_dict())
        return goal_dict_lst

    
class Goal_type(db.Model):
    __table_args__ = {"schema": "fitness", 'comment':'Type of Goal: distance, count, time'}
    id = db.Column(db.Integer, primary_key=True)
    goals = db.relationship('Goal', backref='goal_type_det', lazy='dynamic')
    nm = db.Column(db.String(100), index=True, nullable=False, unique=True)
    isrt_ts = db.Column(db.DateTime, nullable=False, index=True, default=datetime.utcnow)
    
    def __lt__(self, other):
        return ((self.nm < other.nm))
    
    def __gt__(self, other):
        return ((self.nm > other.nm))


class Goal_results(PaginatedAPIMixin,db.Model):
    __table_args__ = {"schema": "fitness", 'comment':'Stores goals and results for user'}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('fitness.user.id'))
    description = db.Column(db.String(100), nullable=False)
    start_dt = db.Column(db.DateTime, nullable=False)
    end_dt = db.Column(db.DateTime, nullable=False)
    workout_type_grp = db.Column(db.String(50))
    goal_type_nm = db.Column(db.String(50))
    goal_total = db.Column(db.Numeric(8,2))
    ordr = db.Column(db.Integer)
    is_active = db.Column(db.Boolean(), nullable=False)
    total_distance_miles = db.Column(db.Numeric(8,2))
    total_workouts = db.Column(db.Numeric(8,2))
    total_duration_seconds = db.Column(db.Numeric(8,2))

    def __repr__(self):
        return '<Goal Result {}>'.format(self.description)
    
    def get_completed_value(self):
        completed_value = 0.0
        if self.goal_type_nm == 'distance':
            completed_value = self.total_distance_miles if self.total_distance_miles != None else 0.0
        elif self.goal_type_nm == 'count':
            completed_value = self.total_workouts
        elif self.goal_type_nm == 'time':
            completed_value = self.total_duration_seconds if self.total_duration_seconds != None else 0
        return float(completed_value)
            
    def percent_complete(self):
        completed_value = self.get_completed_value()
        goal_total_float = float(self.goal_total)
        return 1-((goal_total_float - completed_value) / goal_total_float)
        
    def total_remaining(self):
        completed_value = self.get_completed_value()
        if self.goal_total < completed_value:
            return 0
        else:
            return float(self.goal_total) - completed_value
    
    def avg_need_per_day(self, current_dt = datetime.now()):
        # If date pased is before the start date then use start date
        dateValue = self.start_dt if current_dt < self.start_dt else current_dt
        if dateValue > self.end_dt:
            return 0
        # days_remaining = (self.end_dt.date() - dateValue.date()) / const.SECONDS_IN_DAY
        days_remaining = (self.end_dt.date() - dateValue.date()) / timedelta(days=1)
        return self.total_remaining() / days_remaining
    def avg_need_per_week(self, current_dt = datetime.now()):
        curr_avg_need_per_day = self.avg_need_per_day(current_dt)
        return curr_avg_need_per_day * 7
    def avg_need_per_month(self, current_dt = datetime.now()):
        curr_avg_need_per_day = self.avg_need_per_day(current_dt)
        return curr_avg_need_per_day * 30
    
    def unit_of_measure(self):
        if self.goal_type_nm == 'distance':
            return 'miles'
        elif self.goal_type_nm == 'count':
            return 'times'
        elif self.goal_type_nm == 'time':
            return 'seconds'
            
    def to_dict(self):
        d = {
            'id': self.id,
            'user_id': self.user_id,
            'description':self.description,
            'start_dt': self.start_dt.strftime('%Y-%m-%d %H:%M:%S'),
            'end_dt': self.end_dt.strftime('%Y-%m-%d %H:%M:%S'),
            'workout_type_grp': self.workout_type_grp,
            'goal_type_nm': self.goal_type_nm,
            'goal_total':self.goal_total,
            'order': self.ordr,
            'is_active': self.is_active,
            'total_distance_miles': self.total_distance_miles,
            'total_workouts': self.total_workouts,
            'total_duration_seconds': self.total_duration_seconds,
            'avg_need_per_day': self.avg_need_per_day(),
            'avg_need_per_week': self.avg_need_per_week(),
            'avg_need_per_month': self.avg_need_per_month()
        }
        return d
    
    def to_web_dict(self):
        completed_value = self.get_completed_value()
        percent_complete = self.percent_complete()
        
        d = {
            'id': self.id,
            'user_id': self.user_id,
            'description':self.description,
            'start_dt': self.start_dt.strftime('%Y-%m-%d %H:%M:%S'),
            'end_dt': self.end_dt.strftime('%Y-%m-%d %H:%M:%S'),
            'workout_type_grp': self.workout_type_grp,
            'goal_total':self.goal_total,
            'order': self.ordr,
            'is_active': self.is_active,
            'goal_type_nm': self.goal_type_nm,
            'completed_value': completed_value,
            'percent_complete': percent_complete*100,
            'uom': self.unit_of_measure(),
            'avg_need_per_day': self.avg_need_per_day(),
            'avg_need_per_week': self.avg_need_per_week(),
            'avg_need_per_month': self.avg_need_per_month()
        }
        return d
    
    
    @staticmethod 
    def lst_to_dict(goal_result_lst):
        goal_result_dict_lst = []
        for goal_result in goal_result_lst:
            # logger.info(goal)
            goal_result_dict_lst.append(goal_result.to_dict())
        return goal_result_dict_lst
