# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# 3rd Party classes
from flask import jsonify, request, url_for, abort

# Custom Classes
from app import db
from app.models import Workout, User, Workout_interval
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request
from app import logger
from app.utils import dt_conv

@bp.route('/workout_intervals/<int:wrkt_id>', methods=['GET'])
@token_auth.login_required
def get_workout_intervals(wrkt_id):
    logger.info('get_workout_intervals')
    current_user_id = token_auth.current_user().id
    return jsonify(Workout_interval.to_intrvl_lst_dict( \
      sorted(Workout_interval.query.filter_by( \
      workout_id=wrkt_id, user_id=current_user_id))))


@bp.route('/workout_intervals', methods=['POST'])
@token_auth.login_required
def create_workout_intervals():
    logger.info('create_workout_intervals')
    current_user_id = token_auth.current_user().id
    dataLst = request.get_json() or [{}]

    wrkt_id = ''
    wrkt_intrvl_dict_list = []
    for data in dataLst:
        # Make sure the required fields are in the data dict
        req_fields = ['workout_id', 'break_type', 'intervals']
        for field in req_fields:
            if field not in data:
                err_msg = 'must include ' + field + ' field'
                logger.info(err_msg)
                return bad_request(err_msg)
        wrkt_id = data['workout_id']
        wrkt_intrvl_dict_list = Workout_interval.from_intrvl_lst_dict(data, current_user_id, wrkt_id)

    response = jsonify(wrkt_intrvl_dict_list)
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_workout_intervals', wrkt_id=wrkt_id)
    return response


'''
Input is an array of workout interval dictionaries. 
Interval types allowed are lap, mile, resume, segment. Any other types will be ignored. 
Replaced intervals for types passed. 
'''
@bp.route('/workout_intervals', methods=['PUT'])
@token_auth.login_required
def update_workout_intervals():
    logger.info('update_workout_intervals')
    current_user_id = token_auth.current_user().id

    data = request.get_json() or [{}]
    req_fields = ['workout_id', 'intervals']
    interval_types = ['lap','mile','resume','segment']
    ret_data_lst = []
    logger.info(data)
    for wrkt_data in data:
        # Check required fields are in call
        for field in req_fields:
            if field not in wrkt_data:
                logger.error('must include ' + field + ' field')
                return bad_request('must include ' + field + ' field')
        wrkt_id = wrkt_data['workout_id']
        wrkt_intrvls = wrkt_data['intervals']
        ret_wrkt = {'workout_id':wrkt_id}
        ret_intrvls = {}
        for intrvl_type in interval_types:
            if intrvl_type in wrkt_intrvls:
                # Delete old workout_interval for wrkt_id, break_type, current_user_id
                Workout_interval.query.filter_by(user_id=current_user_id, workout_id=wrkt_id, break_type=intrvl_type).delete()
                # Create new interval
                ret_intrvls.update(Workout_interval.from_intrvl_type_dict(wrkt_intrvls[intrvl_type], current_user_id, wrkt_id, intrvl_type))
                # Commit delete and create
                db.session.commit()
        logger.info('passed wrkt_id:' + str(wrkt_id))

        ret_wrkt['intervals'] = ret_intrvls
        ret_data_lst.append(ret_wrkt)

        
    response = jsonify(ret_data_lst)
    response.status_code = 200
    return response

@bp.route('/v2/workout_intervals/<int:wrkt_id>', methods=['GET'])
@token_auth.login_required
def get_workout_intervals_v2(wrkt_id):
    logger.info('get_workout_intervals_v2')
    current_user_id = token_auth.current_user().id
    wrkt_intrvl_dict = Workout_interval.to_intrvl_lst_dict_v2( \
      sorted(Workout_interval.query.filter_by( \
      workout_id=wrkt_id, user_id=current_user_id)))
    return jsonify({'workout_id':wrkt_id, 'intervals':wrkt_intrvl_dict})
