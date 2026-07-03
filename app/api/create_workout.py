# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# First party classes
import os
import datetime
import string

# 3rd Party classes
from flask import jsonify, request, url_for, abort, current_app, send_from_directory
from werkzeug.utils import secure_filename
import pandas as pd
import numpy as np

# Custom Classes from github
import NormalizeWorkout.dao.files as fao
import NormalizeWorkout.parse.fitParse as fitParse
import NormalizeWorkout.parse.hkParse as hkNorm
import NormalizeWorkout.parse.rungapMetadata as rungapMeta
import NormalizeWorkout.WrktSplits as wrktSplits
# import GenerateMapImage.gen_map_img as genMap

# Custom Classes
from app import db
from app.models import Workout, User, Workout_interval, Gear, Wrkt_sum
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request
from app import logger
from app.utils import dt_conv
from app.model.location import Location
from app.main import filtering
from app.utils import wrkt_summary
from app.model.tag import Workout_tag, Tag
from app.utils import gen_map_img_2 as genMap



@bp.route('/create_workout', methods=['POST'])
@token_auth.login_required
def create_workout_from_file():
    logger.info('create_workout_from_file')
    current_user_id = token_auth.current_user().id
    dataLst = request.get_json() or [{}]

    '''
    wrkt_list = []
    for data in dataLst:
        # Make sure the required fields are in the data dict
        req_fields = ['type', 'wrkt_dttm', 'dur_sec', 'dist_mi']
        req_fields = ['type', 'wrkt_dttm', 'dur_sec']
        for field in req_fields:
            if field not in data:
                return bad_request('must include ' + field + ' field')

        # Should I check if a request for specified workt_dttm already exists?
        # if User.query.filter_by(username=data['username']).first():
        #     return bad_request('please use a different email address')
        workout = Workout()
        workout.from_dict(data, current_user_id)
        logger.debug(workout)
        if workout.gear_id is None:
            logger.debug('no gear passed')
            predicted_gear = Gear.predict_gear(current_user_id, workout.category_id, workout.type_id)
            logger.debug('Gear predicted to be used: {}'.format(predicted_gear['nm']))
            workout.gear_id = predicted_gear['id']
        else:
            logger.debug('Gear passed ({})'.format(workout.gear_id))
        db.session.add(workout)
        
        if 'tags' in data:
            logger.debug(data['tags'])
            for tag in data['tags']:
                new_workout_tag = Workout_tag()
                new_workout_tag.user_id = current_user_id
                new_workout_tag.tag_id = Tag.get_tag_id(tag)
                new_workout_tag.workout_id = workout.id
                db.session.add(new_workout_tag)
        
        db.session.commit()

        if workout.location != None and workout.location != '' and workout.lat_strt != None and workout.lat_strt != '':
            Location.create_loc_if_not_exist(workout.location, current_user_id, workout.lat_strt, workout.long_strt)
        
        if 'intervals' in data:
            interval_types = ['lap','mile','resume','segment']
            for intrvl_type in interval_types:
                if intrvl_type in data['intervals']:
                    Workout_interval.from_intrvl_type_dict(data['intervals'][intrvl_type], current_user_id, workout.id, intrvl_type)
        wrkt_list.append(workout.to_dict())
    response = jsonify(wrkt_list)
    '''
    response = jsonify('Testing')
    response.status_code = 201
    # response.headers['Location'] = url_for('api.get_workout', id=workout.id)
    return response
