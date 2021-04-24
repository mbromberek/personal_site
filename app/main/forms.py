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
from wtforms import StringField, SubmitField, TextAreaField, DecimalField, HiddenField
from wtforms.fields.html5 import DateField, TimeField, IntegerField
from wtforms.validators import Length, NumberRange, InputRequired
from wtforms.widgets import html5 as h5widgets

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class WorkoutForm(FlaskForm):
    wrkt_id = HiddenField()
    type = StringField('Type', validators=[InputRequired()])
    # dttm = DateTimeField('Date Time', validators=[DataRequired()], format='%Y-%m-%d')
    wrkt_dt = DateField('Date', validators=[InputRequired()], format='%Y-%m-%d', default=datetime.now())
    wrkt_tm = TimeField('Time', format='%H:%M', default=datetime.now())
    # wrkt_tm = TimeField('Time', format='%H:%M:%S', render_kw={"step": "1"})

    # duration = TimeField('Duration', format='%H:%M:%S')
    duration_h = IntegerField('h ', widget=h5widgets.NumberInput(min=0,max=29),
        default=0, validators=[InputRequired()])
    duration_m = IntegerField('m ', widget=h5widgets.NumberInput(min=0,max=59),
        default=0, validators=[InputRequired()])
    duration_s = IntegerField('s ', widget=h5widgets.NumberInput(min=0,max=59),
        default=0, validators=[InputRequired()])

    distance = DecimalField('Distance', validators=[InputRequired()], places=2, rounding=decimal.ROUND_UP)
    notes = TextAreaField('Notes', validators=[Length(min=0, max=500)])
    submit = SubmitField('Submit')
