# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# First party classes
from datetime import datetime

# Customer classes
from app import logger
from app import db

class Book(db.Model):
    __table_args__ = {"schema": "media", 'comment':'Store current and previous read books'}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('fitness.user.id'))
    status = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(500), nullable=False)
    author = db.Column(db.String(500), nullable=True)
    cover_img_locl_path = db.Column(db.Text(), nullable=True)
    strt_reading_dt = db.Column(db.DateTime, nullable=True)
    finished_reading_dt = db.Column(db.DateTime, nullable=True)
    isrt_ts = db.Column(db.DateTime, nullable=False, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Book: {}, status: {}, lon: {}>'.format( self.title, self.status)

    def __lt__(self, other):
        if not (isNan(self.finished_reading_dt)):
            return ((self.finished_reading_dt < other.finished_reading_dt))
        else:
            return ((self.strt_reading_dt < other.strt_reading_dt))

    def __gt__(self, other):
        if not (isNan(self.finished_reading_dt)):
            return ((self.finished_reading_dt > other.finished_reading_dt))
        else:
            return ((self.strt_reading_dt > other.strt_reading_dt))

