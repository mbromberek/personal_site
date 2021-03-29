# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''
# First party classes
import decimal
from datetime import datetime

# Third party classes
from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, DecimalField
from wtforms.fields.html5 import DateField, TimeField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange
from wtforms.widgets import html5 as h5widgets

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class WorkoutForm(FlaskForm):
    type = StringField('Type', validators=[DataRequired()])
    # dttm = DateTimeField('Date Time', validators=[DataRequired()], format='%Y-%m-%d')
    wrkt_dt = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d', default=datetime.now())
    wrkt_tm = TimeField('Time', format='%H:%M:%S', default=datetime.now())

    # duration = TimeField('Duration', format='%H:%M:%S')
    duration_h = IntegerField('h ', widget=h5widgets.NumberInput(min=0,max=29))
    duration_m = IntegerField('m ', widget=h5widgets.NumberInput(min=0,max=59))
    duration_s = IntegerField('s ', widget=h5widgets.NumberInput(min=0,max=59))

    distance = DecimalField('Distance', validators=[DataRequired()], places=2, rounding=decimal.ROUND_UP)
    notes = TextAreaField('Notes', validators=[DataRequired(), Length(min=1, max=500)])
    submit = SubmitField('Submit')
