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
from wtforms.validators import Length, NumberRange, InputRequired, Optional
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
    cancel = SubmitField('Cancel')

    gear = StringField('Gear')
    clothes = StringField('Clothes')
    ele_up = DecimalField('Elevation Up', validators=[Optional()], places=2, rounding=decimal.ROUND_UP)
    ele_down = DecimalField('Elevation Down', validators=[Optional()], places=2, rounding=decimal.ROUND_UP)
    hr = IntegerField('Heart Rate', validators=[Optional()])
    cal_burn = IntegerField('Calories Burned', validators=[Optional()])
    category = StringField('Category')
    location = StringField('Location')
    training_type = StringField('Training Type')

    temp_strt = DecimalField('Temperature', validators=[Optional()], places=2, rounding=decimal.ROUND_UP)
    temp_feels_like_strt = DecimalField('Feels Like', validators=[Optional()], places=2, rounding=decimal.ROUND_UP)
    wethr_cond_strt = StringField('Condition')
    hmdty_strt = DecimalField('Percent Humidity', validators=[Optional()], places=2, rounding=decimal.ROUND_UP)
    wind_speed_strt = DecimalField('Wind Speed', validators=[Optional()], places=2, rounding=decimal.ROUND_UP)
    wind_gust_strt = DecimalField('Wind Gust', validators=[Optional()], places=2, rounding=decimal.ROUND_UP)

    temp_end = DecimalField('Temperature', validators=[Optional()], places=2, rounding=decimal.ROUND_UP)
    temp_feels_like_end = DecimalField('Feels Like', validators=[Optional()], places=2, rounding=decimal.ROUND_UP)
    wethr_cond_end = StringField('Condition')
    hmdty_end = DecimalField('Percent Humidity', validators=[Optional()], places=2, rounding=decimal.ROUND_UP)
    wind_speed_end = DecimalField('Wind Speed', validators=[Optional()], places=2, rounding=decimal.ROUND_UP)
    wind_gust_end = DecimalField('Wind Gust', validators=[Optional()], places=2, rounding=decimal.ROUND_UP)

    warm_up_dur_h = IntegerField('h ',
        widget=h5widgets.NumberInput(min=0,max=29),
        default=0, validators=[Optional()])
    warm_up_dur_m = IntegerField('m ',
        widget=h5widgets.NumberInput(min=0,max=59),
        default=0, validators=[Optional()])
    warm_up_dur_s = IntegerField('s ',
        widget=h5widgets.NumberInput(min=0,max=59),
        default=0, validators=[Optional()])
    warm_up_tot_dist = DecimalField('Distance', validators=[Optional()], places=2, rounding=decimal.ROUND_UP)

    cool_down_dur_h = IntegerField('h ',
        widget=h5widgets.NumberInput(min=0,max=29),
        default=0, validators=[Optional()])
    cool_down_dur_m = IntegerField('m ',
        widget=h5widgets.NumberInput(min=0,max=59),
        default=0, validators=[Optional()])
    cool_down_dur_s = IntegerField('s ',
        widget=h5widgets.NumberInput(min=0,max=59),
        default=0, validators=[Optional()])
    cool_down_tot_dist = DecimalField('Distance', validators=[Optional()], places=2, rounding=decimal.ROUND_UP)

    intrvl_dur_h = IntegerField('h ',
        widget=h5widgets.NumberInput(min=0,max=29),
        default=0, validators=[Optional()])
    intrvl_dur_m = IntegerField('m ',
        widget=h5widgets.NumberInput(min=0,max=59),
        default=0, validators=[Optional()])
    intrvl_dur_s = IntegerField('s ',
        widget=h5widgets.NumberInput(min=0,max=59),
        default=0, validators=[Optional()])
    intrvl_tot_dist = DecimalField('Distance', validators=[Optional()], places=2, rounding=decimal.ROUND_UP)
