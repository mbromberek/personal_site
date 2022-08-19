# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# First party classes
from datetime import datetime, timedelta, date
# from datetime import combine

# Third party classes
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
# from flask_login import current_user, login_required
from sqlalchemy import or_

# Custom classes
from app.main import bp
from app.main.forms import EmptyForm, WorkoutCreateBtnForm, WorkoutForm, WorkoutFilterForm, WorkoutIntervalForm
from app.models import User, Workout, Workout_interval, Gear_usage, Wrkt_sum, Wkly_mileage, Workout_type, Workout_category
from app import db
from app.utils import tm_conv, const, nbrConv, dt_conv
from app import logger

def get_workouts_from_filter(usr_id, type_filter, category_filter, filterVal, wrkt_filter_form):
    usingSearch = False
    query = Workout.query.filter_by(user_id=usr_id)
    if len(type_filter) >0:
        query = query.filter(Workout.type_id.in_(type_filter))
    if len(category_filter) >0:
        query = query.filter(Workout.category_id.in_(category_filter))

    if filterVal['temperature'] != '' and filterVal['temperature'] != None:
        # usingSearch = True
        query = query.filter(Workout.temp_strt >= filterVal['temperature'] \
        -current_app.config['TEMPERATURE_RANGE'])
        query = query.filter(Workout.temp_strt <= filterVal['temperature'] \
        +current_app.config['TEMPERATURE_RANGE'])
        if wrkt_filter_form != None:
            wrkt_filter_form.strt_temp_search.data = filterVal['temperature']
    if filterVal['distance'] != '' and filterVal['distance'] != None:
        # usingSearch = True
        query = query.filter(Workout.dist_mi >= filterVal['distance'] \
        *(1-current_app.config['DISTANCE_RANGE']))
        query = query.filter(Workout.dist_mi <= filterVal['distance'] \
        *(1+current_app.config['DISTANCE_RANGE']))
        if wrkt_filter_form != None:
            wrkt_filter_form.distance_search.data = filterVal['distance']
    if filterVal['txt_search'] != '' and filterVal['txt_search'] != None:
        txt_srch_lst = filterVal['txt_search'].split(' ')
        for txt_srch in txt_srch_lst:
            txt_srch = txt_srch.strip()
            query = query.filter(
                or_(Workout.training_type.ilike('%'+txt_srch+'%'), Workout.location.ilike('%'+txt_srch+'%'), Workout.notes.ilike('%'+txt_srch+'%'))
            )
        if wrkt_filter_form != None:
            wrkt_filter_form.txt_search.data = filterVal['txt_search']

    if filterVal['min_strt_temp'] != '' and filterVal['min_strt_temp'] != None:
        usingSearch = True
        if wrkt_filter_form != None:
            wrkt_filter_form.min_strt_temp_srch.data = filterVal['min_strt_temp']
        query = query.filter(Workout.temp_strt >= filterVal['min_strt_temp'])
    if filterVal['max_strt_temp'] != '' and filterVal['max_strt_temp'] != None:
        usingSearch = True
        if wrkt_filter_form != None:
            wrkt_filter_form.max_strt_temp_srch.data = filterVal['max_strt_temp']
        query = query.filter(Workout.temp_strt <= filterVal['max_strt_temp'])
    if filterVal['min_dist'] != '' and filterVal['min_dist'] != None:
        usingSearch = True
        if wrkt_filter_form != None:
            wrkt_filter_form.min_dist_srch.data = filterVal['min_dist']
        query = query.filter(Workout.dist_mi >= filterVal['min_dist'])
    if filterVal['max_dist'] != '' and filterVal['max_dist'] != None:
        usingSearch = True
        if wrkt_filter_form != None:
            wrkt_filter_form.max_dist_srch.data = filterVal['max_dist']
        query = query.filter(Workout.dist_mi <= filterVal['max_dist'])
    if filterVal['strt_dt'] != '' and filterVal['strt_dt'] != None:
        usingSearch = True
        try:
            dt = dt_conv.get_date(filterVal['strt_dt'])
            if wrkt_filter_form != None:
                wrkt_filter_form.strt_dt_srch.data = dt
            query = query.filter(Workout.wrkt_dttm >= dt)
        except:
            pass
    if filterVal['end_dt'] != '' and filterVal['end_dt'] != None:
        usingSearch = True
        try:
            # Add last second of day so end date for workout will be returned regardless of time of day.
            dt = dt_conv.get_date(filterVal['end_dt'] + 'T23:59:59Z')
            if wrkt_filter_form != None:
                wrkt_filter_form.end_dt_srch.data = dt
            query = query.filter(Workout.wrkt_dttm <= dt)
        except:
            pass

    return query, usingSearch

def get_workouts(current_user_id, page, per_page, filterVal, endpoint, wrkt_filter_form=None):
    type_filter = []
    category_filter = []
    filter_type_lst = Workout_type.query.filter_by(grp=filterVal['type'])
    for filter_type in filter_type_lst:
        type_filter.append(filter_type.id)

    if filterVal['category'] == 'training':
        filter_cat_lst = Workout_category.query.filter( Workout_category.nm.in_(['Training', 'Hard']))
        for filter_cat in filter_cat_lst:
            category_filter.append(filter_cat.id)
    if filterVal['category'] == 'long':
        filter_cat_lst = Workout_category.query.filter( Workout_category.nm.in_(['Long Run', 'Long']))
        for filter_cat in filter_cat_lst:
            category_filter.append(filter_cat.id)
    if filterVal['category'] == 'easy':
        filter_cat_lst = Workout_category.query.filter( Workout_category.nm.in_(['Easy']))
        for filter_cat in filter_cat_lst:
            category_filter.append(filter_cat.id)
    if filterVal['category'] == 'race':
        filter_cat_lst = Workout_category.query.filter( Workout_category.nm.in_(['Race', 'Virtual Race']))
        for filter_cat in filter_cat_lst:
            category_filter.append(filter_cat.id)


    query, usingSearch = get_workouts_from_filter(current_user_id, type_filter, category_filter, filterVal, wrkt_filter_form)
    workoutPages = query.order_by(Workout.wrkt_dttm.desc()).paginate(page, per_page, False)

    workouts = workoutPages.items
    wrkt_dict_lst = []
    for workout in workouts:
        logger.debug(workout)
        wrkt_dict = workout.to_dict(for_web=True)
        wrkt_dict['duration'] = workout.dur_str()

        wrkt_category_training_loc = [wrkt_dict['category']]
        if workout.training_type != None and len(workout.training_type) > 0:
            wrkt_category_training_loc.append(workout.training_type)
        if workout.location != None and len(workout.location) > 0:
            wrkt_category_training_loc.append(workout.location)
        wrkt_dict['category_training_loc'] = ' - '.join(wrkt_category_training_loc)


        wrkt_dict_lst.append(wrkt_dict)

    meta_dict = {'page':  page,
        'next_page': workoutPages.next_num,
        'previous_page': workoutPages.prev_num,
        'per_page': per_page,
        'total_pages':workoutPages.pages,
        'total_items':workoutPages.total,
        'using_extra_search_fields':usingSearch
    }
    endpoint = 'main.workout'
    kwargs = filterVal
    kwargs.pop('page', None)
    links_dict = {
        'self': url_for(endpoint, page=page, per_page=per_page, **kwargs),
        'next': url_for(endpoint, page=workoutPages.next_num, per_page=per_page, **kwargs) if workoutPages.has_next else None,
        'prev': url_for(endpoint, page=page -1, per_page=per_page, **kwargs) if workoutPages.has_prev else None
    }
    return {'items': wrkt_dict_lst, '_meta':meta_dict, '_links':links_dict}

def getFilterValuesFromPost(form):
    filterVal = {}
    filterVal['temperature'] = form.strt_temp_search.data
    filterVal['distance'] = form.distance_search.data
    filterVal['txt_search'] = form.txt_search.data
    filterVal['strt_dt'] = form.strt_dt_srch.data
    logger.debug(str(filterVal['strt_dt']))
    filterVal['end_dt'] = form.end_dt_srch.data
    filterVal['min_dist'] = form.min_dist_srch.data
    filterVal['max_dist'] = form.max_dist_srch.data
    filterVal['min_strt_temp'] = form.min_strt_temp_srch.data
    filterVal['max_strt_temp'] = form.max_strt_temp_srch.data

    return filterVal

def getFilterValuesFromUrl():
    filterVal = {}

    filterVal['page'] = request.args.get('page', default=1, type=int)
    filterVal['type'] = request.args.get('type', default='')
    filterVal['category'] = request.args.get('category', default='')

    filterVal['temperature'] = request.args.get('temperature', default='', type=int)
    distance = request.args.get('distance', default='', type=str)
    filterVal['distance'] = round(float(distance),2) if nbrConv.isFloat(distance) else ''
    filterVal['txt_search'] = request.args.get('txt_search', default='', type=str)

    filterVal['strt_dt'] = request.args.get('strt_dt', default='', type=str)
    filterVal['end_dt'] = request.args.get('end_dt', default='', type=str)

    min_dist = request.args.get('min_dist', default='', type=str)
    filterVal['min_dist'] = round(float(min_dist),2) if nbrConv.isFloat(min_dist) else ''
    max_dist = request.args.get('max_dist', default='', type=str)
    filterVal['max_dist'] = round(float(max_dist),2) if nbrConv.isFloat(max_dist) else ''

    filterVal['min_strt_temp'] = request.args.get('min_strt_temp', default='', type=int)
    filterVal['max_strt_temp'] = request.args.get('max_strt_temp', default='', type=int)

    return filterVal

def getFilterValuesFromGet(request):
    filterVal = {}
    filterVal['type'] = request.args.get('type')
    filterVal['category'] = request.args.get('category')
    filterVal['txt_search'] = request.args.get('txt_search')
    try:
        filterVal['temperature'] = request.args.get('temperature', '', type=int)
    except ValueError:
        filterVal['temperature'] = ''
    try:
        filterVal['distance'] = request.args.get('distance', '', type=int)
    except ValueError:
        filterVal['distance'] = ''
    try:
        filterVal['min_strt_temp'] = request.args.get('min_strt_temp', '', type=int)
    except ValueError:
        filterVal['min_strt_temp'] = ''
    try:
        filterVal['max_strt_temp'] = request.args.get('max_strt_temp', '', type=int)
    except ValueError:
        filterVal['max_strt_temp'] = ''
    try:
        filterVal['min_dist'] = request.args.get('min_dist', '', type=int)
    except ValueError:
        filterVal['min_dist'] = ''
    try:
        filterVal['max_dist'] = request.args.get('max_dist', '', type=int)
    except ValueError:
        filterVal['max_dist'] = ''

    filterVal['strt_dt'] = request.args.get('strt_dt', '', type=str)
    filterVal['end_dt'] = request.args.get('end_dt', '', type=str)


    try:
        filterVal['page'] = request.args.get('page', 1, type=int)
    except ValueError:
        filterVal['page'] = 1
    return filterVal
