# First Party Classes
from datetime import datetime, timedelta, date
# import math
# import re
# import os
# import base64

# Third party classes
from flask import current_app
# from sqlalchemy import or_

# Custom Classes
from app import db, login
# from app.utils import tm_conv, const
from app import logger


class Tag(db.Model):
  __table_args__ = {"schema": "fitness", 'comment':'Tags that can be used for additional details about a workout. '}
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('fitness.user.id'))
  nm = db.Column(db.String(50), index=True, nullable=False, unique=True)
  isrt_ts = db.Column(db.DateTime, nullable=False, index=True, default=datetime.utcnow)
  workouts = db.relationship('Workout_tag', backref='workout_tag', lazy='dynamic')
  
  def __repr__(self):
    return '<Tag {}: id {}>'.format( self.nm, self.id)

class Workout_tag(db.Model):
  __table_args__ = {"schema": "fitness", 'comment':'Tags that can be used for additional details about a workout. '}
  workout_id = db.Column(db.Integer, db.ForeignKey('fitness.workout.id'), primary_key=True, nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('fitness.user.id'), nullable=False)
  tag_id = db.Column(db.Integer, db.ForeignKey('fitness.tag.id'), primary_key=True, nullable=False)
  isrt_ts = db.Column(db.DateTime, nullable=False, index=True, default=datetime.utcnow)
  
  def __repr__(self):
    return '<Workout {} Tag {}>'.format( self.workout_id, self.tag_id)


class Tag_usage(db.Model):
  __table_args__ = {"schema": "fitness", 'comment':'Tag usage'}
  id = db.Column(db.Integer, db.ForeignKey('fitness.tag.id'), nullable=False, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('fitness.user.id'))
  nm = db.Column(db.String(50), index=True, nullable=False, unique=True)
  usage_count = db.Column(db.Integer)
  on_workout = None

  def __repr__(self):
    return '<Tag {}: id {}, used {} times>'.format( self.nm, self.id, self.usage_count)
  
  def __lt__(self, other):
    if self.on_workout != None and other.on_workout != None and self.on_workout != other.on_workout:
      return self.workout < other.workout
    if self.usage_count == other.usage_count:
      return self.nm < other.nm
    else:
      return self.usage_count > other.usage_count
  
  def __gt__(self, other):
    if self.on_workout != None and other.on_workout != None and self.on_workout != other.on_workout:
      return self.on_workout > other.on_workout
    if self.usage_count < other.usage_count:
      return self.nm > other.nm
    else:
      return self.usage_count < other.usage_count
  
  def to_dict(self):
    data = {
      'id': self.id,
      'user_id':self.user_id,
      'nm':self.nm,
      'usage_count':self.usage_count
    }
    if self.on_workout != None:
      data['on_workout'] = self.on_workout
    return data

  @staticmethod
  def to_dict_lst(tag_usage_lst):
    tag_lst = []
    for tag in tag_usage_lst:
      tag_lst.append(tag.to_dict())
    return tag_lst
    