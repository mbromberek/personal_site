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
from wtforms import StringField, SubmitField, TextAreaField, DecimalField, HiddenField, SelectField, FieldList, FormField, BooleanField
from wtforms.fields import DateField, TimeField, IntegerField
from wtforms.validators import Length, NumberRange, InputRequired, Optional
from wtforms import widgets as h5widgets

# Custom classes
from app import logger

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

class WorkoutCreateBtnForm(FlaskForm):
    workt_create_btn = SubmitField('+')

class WorkoutFilterForm(FlaskForm):
    category_run_btn = SubmitField(label='Run')
    category_cycle_btn = SubmitField(label='Cycle')
    category_swim_btn = SubmitField(label='Swim')

    category_training_btn = SubmitField(label='Training')
    category_long_btn = SubmitField(label='Long Run')
    category_easy_btn = SubmitField(label='Easy')
    category_race_btn = SubmitField(label='Race')

    clear_filter_btn = SubmitField(label='Clear Filter')

    strt_temp_search = DecimalField('Temperature', validators=[Optional()], places=0, rounding=decimal.ROUND_UP)
    distance_search = DecimalField('Distance', validators=[Optional()], places=2, rounding=decimal.ROUND_UP)
    submit_search_btn = SubmitField('🔎')

    txt_search = StringField('Text', validators=[Optional()])

    show_filter_btn = SubmitField(label='Show Filters')

    strt_dt_srch = DateField('Start Dt:', format='%Y-%m-%d',validators=[Optional()])
    end_dt_srch = DateField('End Dt:', format='%Y-%m-%d',validators=[Optional()])
    min_dist_srch = DecimalField('Min Dist:', validators=[Optional()], places=0, rounding=decimal.ROUND_UP)
    max_dist_srch = DecimalField('Max Dist:', validators=[Optional()], places=0, rounding=decimal.ROUND_UP)
    min_strt_temp_srch = DecimalField('Min Temp:', validators=[Optional()], places=0, rounding=decimal.ROUND_UP)
    max_strt_temp_srch = DecimalField('Max Temp:', validators=[Optional()], places=0, rounding=decimal.ROUND_UP)

class WorkoutExportForm(FlaskForm):
    max_export_records = IntegerField('Max nbr of records', widget=h5widgets.NumberInput(),
        default='', validators=[Optional()])
    download_csv_btn = SubmitField(label='Export')
    duration_hms_chk = BooleanField("Duration h:m:s", default="checked")
    duration_sec_chk = BooleanField("Duration Seconds")
    distance_chk = BooleanField("Distance", default="checked")
    hr_chk = BooleanField("HR", default="checked")
    pace_chk = BooleanField("Pace", default="checked")
    pace_sec_chk = BooleanField("Pace Seconds")
    clothes_chk = BooleanField("Clothes")
    gear_chk = BooleanField("Gear", default="checked")
    category_chk = BooleanField("Category", default="checked")
    training_type_chk = BooleanField("Training Type")
    calories_chk = BooleanField("Calories")
    elevation_chk = BooleanField("Elevation", default="checked")
    elevation_up_chk = BooleanField("Elevation Up")
    elevation_down_chk = BooleanField("Elevation Down")
    location_chk = BooleanField("Location")
    weather_chk = BooleanField("Weather")
    notes_plus_chk = BooleanField("Notes+", default="checked")
    notes_chk = BooleanField("Notes")



class WorkoutIntervalForm(FlaskForm):
    wrkt_intrvl_id = HiddenField()
    # break_type
    interval_order = IntegerField('Order',
        widget=h5widgets.NumberInput(min=0),
        validators=[Optional()])
    interval_desc = StringField('Type', validators=[Optional()])
    dur_h = IntegerField('h ',
        widget=h5widgets.NumberInput(min=0,max=29),
        default=0, validators=[Optional()])
    dur_m = IntegerField('m ',
        widget=h5widgets.NumberInput(min=0,max=59),
        default=0, validators=[Optional()])
    dur_s = IntegerField('s ',
        widget=h5widgets.NumberInput(min=0,max=59),
        default=0, validators=[Optional()])
    dist = DecimalField('Distance', validators=[InputRequired()], places=2, rounding=decimal.ROUND_UP)
    hr = IntegerField('Heart Rate', validators=[Optional()])
    ele_up = DecimalField('Elevation Up', validators=[Optional()], places=2, rounding=decimal.ROUND_UP)
    ele_down = DecimalField('Elevation Down', validators=[Optional()], places=2, rounding=decimal.ROUND_UP)
    notes = TextAreaField('Notes', validators=[Length(min=0, max=30000)])

    split_dist = DecimalField('Split Distance', validators=[Optional()], places=2, rounding=decimal.ROUND_UP)
    # submit = SubmitField('Submit')
    # cancel = SubmitField('Cancel')
    def __repr__(self):
        return '<WorkoutIntervals {}, {}>'.format(self.interval_order, self.interval_desc)


class WorkoutForm(FlaskForm):
    wrkt_id = HiddenField()
    # type = StringField('Type', validators=[InputRequired()])
    type_lst = SelectField('Type', validate_choice=True, coerce=int)
    wrkt_dt = DateField('Date', format='%Y-%m-%d', default=datetime.now(), validators=[InputRequired("Workout date is required")])
    wrkt_tm = TimeField('Time', format='%H:%M', default=datetime.now())

    duration_h = IntegerField('h ', widget=h5widgets.NumberInput(min=0,max=29),
        default=0, validators=[InputRequired()])
    duration_m = IntegerField('m ', widget=h5widgets.NumberInput(min=0,max=59),
        default=0, validators=[InputRequired()])
    duration_s = IntegerField('s ', widget=h5widgets.NumberInput(min=0,max=59),
        default=0, validators=[InputRequired()])

    distance = DecimalField('Distance', validators=[InputRequired()], places=2, rounding=decimal.ROUND_UP)
    notes = TextAreaField('Notes', validators=[Length(min=0, max=30000)])
    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel')
    edit_interval = SubmitField('Edit Intervals')
    delete_btn = SubmitField('Delete')

    # gear = StringField('Gear')
    gear_lst = SelectField('Gear', validate_choice=True, coerce=int)

    clothes = StringField('Clothes')
    ele_up = DecimalField('Elevation Up', validators=[Optional()], places=2, rounding=decimal.ROUND_UP)
    ele_down = DecimalField('Elevation Down', validators=[Optional()], places=2, rounding=decimal.ROUND_UP)
    hr = IntegerField('Heart Rate', validators=[Optional()])
    cal_burn = IntegerField('Calories Burned', validators=[Optional()])
    # category = StringField('Category')
    cat_lst = SelectField('Category', validate_choice=True, coerce=int)
    location = StringField('Location')
    training_type = StringField('Training Type')

    temp_strt = DecimalField('Temperature', validators=[Optional()], places=2, rounding=decimal.ROUND_UP)
    dew_point_strt = DecimalField('Dew Point', validators=[Optional()], places=2, rounding=decimal.ROUND_UP)
    temp_feels_like_strt = DecimalField('Feels Like', validators=[Optional()], places=2, rounding=decimal.ROUND_UP)
    wethr_cond_strt = StringField('Condition')
    hmdty_strt = DecimalField('Percent Humidity', validators=[Optional()], places=2, rounding=decimal.ROUND_UP)
    wind_speed_strt = DecimalField('Wind Speed', validators=[Optional()], places=2, rounding=decimal.ROUND_UP)
    wind_gust_strt = DecimalField('Wind Gust', validators=[Optional()], places=2, rounding=decimal.ROUND_UP)

    temp_end = DecimalField('Temperature', validators=[Optional()], places=2, rounding=decimal.ROUND_UP)
    dew_point_end = DecimalField('Dew Point', validators=[Optional()], places=2, rounding=decimal.ROUND_UP)
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

    # wrkt_intrvl_segment_form = WorkoutIntervalForm()
    wrkt_intrvl_segment_form = FieldList(FormField(WorkoutIntervalForm))
    show_pause = BooleanField("Show Pause Segments")
    show_map_laps = BooleanField("Show Lap Markers on map")
    show_map_miles = BooleanField("Show Mile Markers on map")

class UserSettingsForm(FlaskForm):
    user_id = HiddenField()
    displayname = StringField('Display Name', validators=[InputRequired()])
    shoe_mile_warning = IntegerField('Shoe Mileage Warning',
        widget=h5widgets.NumberInput(min=0),
        # default=100,
        validators=[Optional()])
    shoe_mile_max = IntegerField('Shoe Mileage Max',
        widget=h5widgets.NumberInput(min=0),
         validators=[Optional()])
    shoe_min_brkin_ct = IntegerField('Shoe Breaking Count',
        widget=h5widgets.NumberInput(min=0),
        validators=[Optional()])
    submit = SubmitField('Save')
    cancel = SubmitField('Cancel')

class GearForm(FlaskForm):
    id = HiddenField()
    nm = StringField('Name', validators=[InputRequired()])
    prchse_dt = DateField('Purchase Date', format='%Y-%m-%d',validators=[InputRequired()])
    price = DecimalField('Price', validators=[Optional()], places=2, rounding=decimal.ROUND_UP)
    retired = BooleanField("Retired")
    no_suggest = BooleanField("Do not suggest")
    confirmed = BooleanField("Confirmed")
    type = SelectField('Gear Type', validate_choice=True, coerce=int)
    company = StringField('Company', validators=[Optional()])

    submit = SubmitField('Save')
    cancel = SubmitField('Cancel')
    def __repr__(self):
        return '<Gear {}: {}>'.format(self.type.data, self.nm.data)

class LocForm(FlaskForm):
    id = HiddenField()
    name = StringField('Name', validators=[InputRequired()])
    lat = StringField('Latitude')
    lon = StringField('Longitude')
    radius = DecimalField('Radius', validators=[InputRequired()], places=2, rounding=decimal.ROUND_UP)

    submit = SubmitField('Save')
    cancel = SubmitField('Cancel')
    delete = SubmitField('Delete')
    def __repr__(self):
        return '<Location {}: {}>'.format(self.name.data, self.radius.data)
