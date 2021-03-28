# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# Third party classes
from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class WorkoutForm(FlaskForm):
    type = StringField('Type', validators=[DataRequired()])
    dttm = StringField('Date Time', validators=[DataRequired()])
    duration = StringField('Duration', validators=[DataRequired()])
    distance = StringField('Distance', validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[DataRequired(), Length(min=0, max=500)])
    submit = SubmitField('Submit')
