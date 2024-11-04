# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# First party classes
from datetime import datetime, timedelta, date
# from datetime import combine
import re
import json

# Third party classes
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
# from flask_login import current_user, login_required
from sqlalchemy import or_

# Custom classes
from app.main import bp
from app.main.forms import EmptyForm, WorkoutCreateBtnForm, WorkoutForm, WorkoutFilterForm, WorkoutIntervalForm
from app.models import User, Workout, Workout_interval, Gear_usage, Wrkt_sum, Wkly_mileage, Workout_type, Workout_category
from app.model.tag import Tag, Workout_tag
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
    if 'text' in filterVal and filterVal['text'] != '' and filterVal['text'] != None:
        # txt_srch_lst = filterVal['txt_search'].split(' ')
        txt_srch_lst = filterVal['text']
        for txt_srch in txt_srch_lst:
            txt_srch = txt_srch.strip()
            
            workout_tag_matches = get_workouts_for_tag_search([txt_srch], usr_id)
            query = query.filter(
                or_(Workout.training_type.ilike('%'+txt_srch+'%'), Workout.location.ilike('%'+txt_srch+'%'), Workout.notes.ilike('%'+txt_srch+'%'), Workout.id.in_(workout_tag_matches))
            )
        if wrkt_filter_form != None:
            wrkt_filter_form.txt_search.data = filterVal['txt_search']

    logger.debug('TAG FILTERING')
    workout_tag_matches = None
    if 'tags' in filterVal and len(filterVal['tags']) >0:
        workout_tag_matches = get_workouts_for_tag_search(filterVal['tags'], usr_id)
        query = query.filter(Workout.id.in_(workout_tag_matches))
        
    logger.debug(workout_tag_matches)
    # Add list of workouts to ID for filtering using an AND (I think using and everywhere already)
    logger.debug('TAG FILTERING END')
    

    if 'location' in filterVal and filterVal['location'] != '' and filterVal['location'] != None:
            txt_srch_lst = filterVal['location']
            for txt_srch in txt_srch_lst:
                txt_srch = txt_srch.strip()
                query = query.filter(
                    Workout.location.ilike('%'+txt_srch+'%')
                )
            # if wrkt_filter_form != None:
                # wrkt_filter_form.txt_search.data = filterVal['location']
    if 'training' in filterVal and filterVal['training'] != '' and filterVal['training'] != None:
            txt_srch_lst = filterVal['training']
            for txt_srch in txt_srch_lst:
                txt_srch = txt_srch.strip()
                query = query.filter(
                    Workout.training_type.ilike('%'+txt_srch+'%')
                )
    if 'notes' in filterVal and filterVal['notes'] != '' and filterVal['notes'] != None:
            txt_srch_lst = filterVal['notes']
            for txt_srch in txt_srch_lst:
                txt_srch = txt_srch.strip()
                query = query.filter(
                    Workout.notes.ilike('%'+txt_srch+'%')
                )



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
    
    filter_type_lst = Workout_type.query.filter(Workout_type.grp.in_(filterVal['type']))
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
    workoutPages = query.order_by(Workout.wrkt_dttm.desc()).paginate(page=page, per_page=per_page, error_out=False)

    if endpoint.startswith('api'):
        for_web = False
    else:
        for_web = True

    workouts = workoutPages.items
    wrkt_dict_lst = []
    for workout in workouts:
        logger.debug(workout)
        wrkt_dict = workout.to_dict(for_web=for_web)
        wrkt_dict['duration'] = workout.dur_str()

        wrkt_category_training_loc = []
        if workout.location != None and len(workout.location) > 0:
            wrkt_category_training_loc.append(workout.location)
        if workout.training_type != None and len(workout.training_type) > 0:
            wrkt_category_training_loc.append(workout.training_type)
        wrkt_category_training_loc.append(wrkt_dict['category'])
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
    
    filterVal.pop('location',None)
    filterVal.pop('text',None)
    filterVal.pop('notes',None)
    filterVal.pop('training',None)
    filterVal.pop('tags',None) # TODO NOT SURE IF NEEDED
    filterVal['type'] = ','.join(filterVal['type']) # Change type to string for use in other URLs
    
    kwargs = filterVal
    kwargs.pop('page', None)
    links_dict = {
        'self': url_for(endpoint, page=page, per_page=per_page, **kwargs),
        'next': url_for(endpoint, page=workoutPages.next_num, per_page=per_page, **kwargs) if workoutPages.has_next else None,
        'prev': url_for(endpoint, page=page -1, per_page=per_page, **kwargs) if workoutPages.has_prev else None
    }
    return {'items': wrkt_dict_lst, '_meta':meta_dict, '_links':links_dict}

def getFilterValuesFromPost(form):
    logger.debug('getFilterValuesFromPost')
    filterVal = {}
    filterVal['temperature'] = form.strt_temp_search.data
    filterVal['distance'] = form.distance_search.data

    text_search_split = split_search_query(form.txt_search.data)
    filterVal.update(text_search_split)
    filterVal['txt_search'] = form.txt_search.data
    
    filterVal['strt_dt'] = form.strt_dt_srch.data
    # logger.debug(str(filterVal['strt_dt']))
    filterVal['end_dt'] = form.end_dt_srch.data
    filterVal['min_dist'] = form.min_dist_srch.data
    filterVal['max_dist'] = form.max_dist_srch.data
    filterVal['min_strt_temp'] = form.min_strt_temp_srch.data
    filterVal['max_strt_temp'] = form.max_strt_temp_srch.data

    return filterVal

def getFilterValuesFromUrl():
    logger.debug('getFilterValuesFromUrl')
    filterVal = {}

    filterVal['page'] = request.args.get('page', default=1, type=int)

    filter_item = request.args.get('type', default='')
    filterVal['type'] = set()
    for filter in filter_item.split(','):
        filterVal['type'].add(filter)
    filterVal['category'] = request.args.get('category', default='')

    filterVal['temperature'] = request.args.get('temperature', default='', type=int)
    distance = request.args.get('distance', default='', type=str)
    filterVal['distance'] = round(float(distance),2) if nbrConv.isFloat(distance) else ''
    
    text_search_split = split_search_query(request.args.get('txt_search', default='', type=str))
    filterVal.update(text_search_split)
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
    logger.debug('getFilterValuesFromGet')
    # logger.debug(request.args)
    # logger.debug(request.args.get('type'))
    # logger.debug(request.args.get('type[]'))
    filterVal = {}
    # filterVal['type'] = request.args.get('type')
    getType = request.args.get('type')
    getType = getType if getType != None else []
    # logger.debug('getType:' + str(getType))
    # for t in getType:
    #     logger.debug(t)
    # getType = json.loads(getType)
    if 'endurance' in getType:
        filterVal['type'] = {'run','cycle','swim','walk'}
    elif len(getType) > 0:
        filterVal['type'] = set(getType.split(','))
    else:
        filterVal['type'] = {}
    logger.debug(filterVal)
    
    
    getTags = request.args.get('tags')
    getTags = getTags if getTags != None else []
    if len(getTags) > 0:
        filterVal['tags'] = set(getTags.split(','))
    else:
        filterVal['tags'] = {}
    
    filterVal['category'] = request.args.get('category')
    if 'text_NOT_USED' in request.args:
        # get new fields derived form text field
        filterVal['text'] = request.args.get('text')
        filterVal['location'] = request.args.get('location')
        filterVal['training'] = request.args.get('training')
        filterVal['notes'] = request.args.get('notes')
    else:
        text_search_split = split_search_query(request.args.get('txt_search'))
        filterVal.update(text_search_split)
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


TXT_SEARCH_TERMS = {'loc:':'location', 'location:':'location', 'type:':'training'\
      , 'training:':'training', 'notes:':'notes', 'tags:':'tags', 'tag:':'tags'}
'''
'''
def split_search_query(query_orig):
    ret = {'text':[]}
    if query_orig == '' or query_orig == None:
        return ret
    search_txt = []
    logger.debug(query_orig)
    query = query_orig.lower()
    query_split = split_str(query)
    logger.debug(query_split)
    
    curr_query_key = 'text'
    for query_itm in query_split:
        query_itm = query_itm.replace('"','')
        # If current query item is is special search terms, mark that to be 
        #  the field to add the next query item into
        if query_itm in TXT_SEARCH_TERMS:
          logger.debug(query_itm)
          curr_query_key = TXT_SEARCH_TERMS[query_itm]
          if curr_query_key not in ret:
            ret[curr_query_key] = []
          continue
        # ret[curr_query_key].append(query_itm)
        ret[curr_query_key].extend(query_itm.split(','))
        curr_query_key = 'text'
    logger.debug(ret)
    return ret

'''
Returns split string
'''
def split_str(query):
    # Split by space or : preserving contents of ""
    # regex_pattern = r'[ :]\s*(?=(?:[^"]*"[^"]*")*[^"]*$)'
    
    # Substitute : with ': ' when not surrounded by ""
    regex_sub_pattern = r':\s*(?=(?:[^"]*"[^"]*")*[^"]*$)'
    query = re.sub(regex_sub_pattern, ': ', query)
    
    # Split by space preserving contents of ""
    regex_pattern = r' \s*(?=(?:[^"]*"[^"]*")*[^"]*$)'
    query_split = re.split(regex_pattern, query)
    
    return query_split

'''
Loops through past in tag values to search for
Does a like for each tag name in tag_search_lst
Returns workout IDs for workouts that have tags that match all tag_search_lst
'''
def get_workouts_for_tag_search(tag_search_lst, usr_id):
    logger.debug('get_workouts_for_tag_search')
    # workout_tag_matches = set()
    # first_tag = True
    # Get Tags that match any entry in tags
    workout_tag_matches = None
    logger.debug(tag_search_lst)
    for tag_nm in tag_search_lst:
        tag_query = Tag.query.filter_by(user_id=usr_id)
        logger.debug(tag_nm)
        tag_nm_edit = tag_nm.strip().replace('"','')
        logger.debug(tag_nm_edit)
        tag_query = tag_query.filter(
            Tag.nm.ilike('%'+tag_nm_edit+'%')
        )
        curr_tag_matches = set()
        for read_tag in tag_query:
            logger.debug(read_tag.id)
            logger.debug(str(read_tag.workouts))
            for workout in read_tag.workouts:
                logger.debug(workout)
                logger.debug(workout.workout_id)
                curr_tag_matches.add(workout.workout_id)
        if workout_tag_matches == None:
            workout_tag_matches = curr_tag_matches
        else:
            # Intersection for set with all current matching workouts and matches for latest tag search.
            # Should only contain workouts that match for all tag searches
            workout_tag_matches = workout_tag_matches & curr_tag_matches
    if workout_tag_matches == None:
        workout_tag_matches = set()
    return workout_tag_matches
