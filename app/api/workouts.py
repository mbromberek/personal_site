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
import random

# 3rd Party classes
from flask import jsonify, request, url_for, abort, current_app
from werkzeug.utils import secure_filename
import pandas as pd

# Custom Classes from github
import NormalizeWorkout.dao.files as fao
import NormalizeWorkout.parse.rungapParse as rgNorm
import NormalizeWorkout.parse.fitParse as fitParse
import NormalizeWorkout.parse.rungapMetadata as rungapMeta
import NormalizeWorkout.WrktSplits as wrktSplits
import GenerateMapImage.gen_map_img as genMap

# Custom Classes
from app import db
from app.models import Workout, User, Workout_interval
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request
from app import logger
from app.utils import dt_conv
from app.model.location import Location


@bp.route('/workout/<int:id>', methods=['GET'])
@token_auth.login_required
def get_workout(id):
    logger.info('get_workout')
    current_user_id = token_auth.current_user().id
    return jsonify(Workout.query.filter_by(id=id, user_id=current_user_id).first_or_404(id).to_dict())
    # return jsonify(Workout.query.get_or_404(id).to_dict())

@bp.route('/workouts/', methods=['GET'])
@token_auth.login_required
def get_workouts():
    logger.info('get_workouts')
    current_user_id = token_auth.current_user().id
    user = User.query.get_or_404(current_user_id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(user.workouts, page, per_page, 'api.get_workouts')
    return jsonify(data)

@bp.route('/workout', methods=['POST'])
@token_auth.login_required
def create_workout():
    logger.info('create_workout')
    current_user_id = token_auth.current_user().id
    dataLst = request.get_json() or [{}]

    wrkt_list = []
    for data in dataLst:
        # Make sure the required fields are in the data dict
        req_fields = ['type', 'wrkt_dttm', 'dur_sec', 'dist_mi']
        for field in req_fields:
            if field not in data:
                return bad_request('must include ' + field + ' field')

        # Should I check if a request for specified workt_dttm already exists?
        # if User.query.filter_by(username=data['username']).first():
        #     return bad_request('please use a different email address')
        workout = Workout()
        workout.from_dict(data, current_user_id)
        db.session.add(workout)
        db.session.commit()

        if workout.location != None and workout.location != '' and workout.lat_strt != None and workout.lat_strt != '':
            Location.create_loc_if_not_exist(workout.location, current_user_id, workout.lat_strt, workout.long_strt)

        if 'mile_splits' in data:
            wrkt_intrvl = {
                'break_type': 'mile',
                'intervals': data['mile_splits']
            }
            Workout_interval.from_intrvl_lst_dict(wrkt_intrvl, current_user_id, workout.id)

        if 'interval_splits' in data:
            wrkt_intrvl = {
                'break_type': 'segment',
                'intervals': data['interval_splits']
            }
            Workout_interval.from_intrvl_lst_dict(wrkt_intrvl, current_user_id, workout.id)

        if 'pause_splits' in data:
            wrkt_intrvl = {
                'break_type': 'resume',
                'intervals': data['pause_splits']
            }
            Workout_interval.from_intrvl_lst_dict(wrkt_intrvl, current_user_id, workout.id)

        if 'lap_splits' in data:
            wrkt_intrvl = {
                'break_type': 'lap',
                'intervals': data['lap_splits']
            }
            Workout_interval.from_intrvl_lst_dict(wrkt_intrvl, current_user_id, workout.id)

        wrkt_list.append(workout.to_dict())
    response = jsonify(wrkt_list)
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_workout', id=workout.id)
    return response

@bp.route('/workouts/<dttm_str>', methods=['GET'])
@token_auth.login_required
def get_workouts_by_dt(dttm_str):
    '''
    Get list of workouts for the passed in date
    '''
    logger.info('get_workouts_by_dttm')
    current_user_id = token_auth.current_user().id

    dttm = dt_conv.get_date(dttm_str)
    logger.info("Get workout for User: " + str(current_user_id) + " for date: " + str(dttm))

    wrkt_lst = Workout.query.filter_by(user_id=current_user_id, wrkt_dttm=dttm)
    wrkt_dict_lst = []
    for wrkt in wrkt_lst:
        wrkt_dict_lst.append(wrkt.to_dict())

    if len(wrkt_dict_lst) >0:
        return jsonify(wrkt_dict_lst), 200
    else:
        return jsonify("No records found"), 400

@bp.route('/workouts/since/<dt>', methods=['GET'])
@token_auth.login_required
def get_workouts_since_dt(dt):
    '''
    Get list of workouts since the passed in date
    '''
    logger.info('get_workouts_since_dt')
    current_user_id = token_auth.current_user().id

    workout_since_dt = dt_conv.get_date(dt)
    logger.info("Get workouts for User: " + str(current_user_id) + " since date: " + str(workout_since_dt))

    query = Workout.query.filter_by(user_id=current_user_id)
    wrkt_lst = query.filter(Workout.wrkt_dttm>=workout_since_dt).order_by(Workout.wrkt_dttm.desc())
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = Workout.to_collection_dict(wrkt_lst, page, per_page, 'api.get_workouts_since_dt', dt=dt)

    wrkt_dict_lst = []
    for wrkt in wrkt_lst:
        wrkt_dict_lst.append(wrkt.to_dict())

    if len(wrkt_dict_lst) >0:
        return jsonify(data), 200
    else:
        return jsonify("No records found"), 400

    # logger.info('get_workouts')
    # current_user_id = token_auth.current_user().id
    # user = User.query.get_or_404(current_user_id)
    # page = request.args.get('page', 1, type=int)
    # per_page = min(request.args.get('per_page', 10, type=int), 100)
    # data = User.to_collection_dict(user.workouts, page, per_page, 'api.get_workouts')
    # return jsonify(data)


@bp.route('/workout', methods=['PUT'])
@token_auth.login_required
def update_workout():
    '''
    Passed workout needs to contain the below required fields. All other fields are optional and if not passed will use existing value.
    '''
    logger.info('update_workout')
    current_user_id = token_auth.current_user().id
    data = request.get_json() or {}
    req_fields = ['id']
    ret_data_lst = []
    logger.info(data)
    for wrkt_data in data:
        for field in req_fields:
            if field not in wrkt_data:
                return bad_request('must include ' + field + ' field')
        wrkt_id = wrkt_data['id']
        passed_workout = Workout()
        passed_workout.from_dict(wrkt_data, current_user_id)
        passed_workout.id = wrkt_id
        logger.info('passed wrkt_id:' + str(wrkt_id))
        orig_workout = Workout.query.filter_by(id=wrkt_id, user_id=current_user_id).first_or_404(wrkt_id)
        logger.info(orig_workout)
        orig_workout.update(passed_workout)
        logger.info(passed_workout)
        logger.info(orig_workout)
        ret_data_lst.append(orig_workout.to_dict())

        db.session.commit()
    response = jsonify(ret_data_lst)
    response.status_code = 200
    # response.headers['Location'] = url_for('api.get_workout', id=orig_workout.id)
    return response

@bp.route('/generate_workout', methods=['PUT'])
@token_auth.login_required
def generate_workout_from_file():
    logger.info('generate_workout_from_file')
    logger.debug(request.files)
    logger.debug('workout_id: ' + str(request.values['workout_id']))
    wrkt_id = request.values['workout_id']
    if 'file' not in request.files:
        logger.info('no file')
        return jsonify("No file found"), 400
    logger.info(str(request.files['file']))
    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        logger.info('no filename in uploaded_file')
        return jsonify("No file found"), 400

    fname = secure_filename(uploaded_file.filename)
    file_ext = os.path.splitext(fname)[-1]
    if file_ext not in current_app.config['UPLOAD_EXTENSIONS']:
        logger.info('{} is an invalid file extension'.format(file_ext))
        abort(400)

    user_id = token_auth.current_user().id

    tempDir = os.path.join(current_app.config['WRKT_FILE_DIR'], str(user_id), 'temp')
    workDir = os.path.join(current_app.config['WRKT_FILE_DIR'], str(user_id), 'work')

    if not os.path.exists(workDir):
        os.makedirs(os.path.join(workDir))
    else:
        fao.clean_dir(workDir)

    if not os.path.exists(tempDir):
        os.makedirs(os.path.join(current_app.config['WRKT_FILE_DIR'], str(user_id), 'temp'))
    uploaded_file.save(os.path.join(tempDir, fname))

    fao.extract_files(fname, workDir, tempDir)

    if fao.file_with_ext(workDir, ext='fit') != '':
        logger.info('fit file exists')
        fitFile = fao.file_with_ext(workDir, ext='fit')
        lapsDf, pointsDf = fitParse.get_dataframes(workDir + '/' + fitFile)
        actv_df = fitParse.normalize_laps_points(lapsDf, pointsDf)
    elif fao.file_with_ext(workDir, ext='rungap.json') != '':
        logger.info('Rungap JSON file')
        data = fao.get_workout_data(workDir)
        actv_df = rgNorm.normalize_activity(data)
    else:
        logger.info('No file to process')
        fao.clean_dir(workDir)
        fao.clean_dir(tempDir)
        return jsonify("No valid files to process"), 400

    dataJson = rungapMeta.get_workout_data(workDir)
    wrktStrtTmStr = dataJson['startTime']['time']
    wrktType = rungapMeta.get_wrkt_type(dataJson).replace(' ','-').lower()
    wrktSrc = dataJson['source'].replace(' ','-').lower()
    wrktStrtTm = datetime.datetime.strptime(wrktStrtTmStr, '%Y-%m-%dT%H:%M:%SZ')

    # Create folder for long term storage of file
    wrktDirNm = wrktStrtTm.strftime('%Y-%m-%d_%H%M%S') + '_' + wrktType + '_' + wrktSrc
    wrktFullPath = os.path.join(current_app.config['WRKT_FILE_DIR'], str(user_id), wrktStrtTm.strftime('%Y'), wrktStrtTm.strftime('%m'), wrktDirNm)
    os.makedirs(wrktFullPath, exist_ok=True)
    tumbnailDir = os.path.join(current_app.config['WRKT_FILE_DIR'], str(user_id), current_app.config['USER_THUMBNAIL_DIR'])
    os.makedirs(tumbnailDir, exist_ok=True)

    # Move saved file from temp to new directory and export data frame as pickle to new directory.
    os.rename(os.path.join(tempDir, fname), os.path.join(wrktFullPath, fname))
    fao.save_df(actv_df, wrktFullPath,'workout', frmt=['pickle'])
    fao.clean_dir(workDir)

    # Update workout passed in wrkt_id for user_id
    orig_workout = Workout.query.filter_by(id=wrkt_id, user_id=user_id).first_or_404(wrkt_id)
    orig_workout.wrkt_dir = os.path.join(wrktStrtTm.strftime('%Y'), wrktStrtTm.strftime('%m'), wrktDirNm)

    if 'latitude' in actv_df and 'longitude' in actv_df:
        coord_df = actv_df[['latitude','longitude']].dropna()
    else:
        coord_df = pd.DataFrame()
    if coord_df.shape[0] >1:
        strt_coord = actv_df[['latitude','longitude']].dropna().iloc[0]
        end_coord = actv_df[['latitude','longitude']].dropna().iloc[-1]
        orig_workout.lat_strt = strt_coord['latitude']
        orig_workout.long_strt = strt_coord['longitude']
        orig_workout.lat_end = end_coord['latitude']
        orig_workout.long_end = end_coord['longitude']
        thumbnail_nm = 'thumb_200_200_' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=50)) + '.png'
        genMap.generate_map_img(actv_df, tumbnailDir, img_dim={'height':200, 'width':200}, img_name=thumbnail_nm)
        orig_workout.thumb_path = thumbnail_nm
        orig_workout.show_map_laps = True
        if orig_workout.category == 'Training':
            orig_workout.show_map_miles = False
        else:
            orig_workout.show_map_miles = True

        if orig_workout.location == '' or orig_workout.location == None:
            loc_lst = Location.query.filter_by(user_id=user_id)
            wrkt_loc = Location.closest_location(loc_lst, {'lat':orig_workout.lat_strt,'lon':orig_workout.long_strt})
            if wrkt_loc != '':
                orig_workout.location = wrkt_loc

    db.session.commit()

    # Generate Workout_intervals using DataFrame

    return jsonify('Success'), 200

@bp.route('/update_workout_from_pickle', methods=['PUT'])
@token_auth.login_required
def update_workout_from_pickle():
    '''
    Receives a list of workout ids to perform update on
    Used for OTO updates
    '''
    logger.info('update_workout_from_pickle')
    current_user_id = token_auth.current_user().id
    data = request.get_json() or {}
    req_fields = ['workout_id']
    ret_data_lst = []
    logger.info(data)
    for wrkt_data in data:
        for field in req_fields:
            if field not in wrkt_data:
                return bad_request('must include ' + field + ' field')
        wrkt_id = wrkt_data['workout_id']
        workout = Workout.query.filter_by(id=wrkt_id, user_id=current_user_id).first_or_404(wrkt_id)
        if workout.wrkt_dir == None:
            logger.info('No workout directory for: {}'.format(str(wrkt_id)))
            continue
        wrkt_df = pd.read_pickle(os.path.join(current_app.config['WRKT_FILE_DIR'], str(workout.user_id), workout.wrkt_dir, 'workout.pickle'))
        lap_df = wrktSplits.group_actv(wrkt_df, 'lap')
        lap_lat_lon = lap_df[['lat','lon']].to_dict(orient='records')
        mile_df = wrktSplits.group_actv(wrkt_df, 'mile')
        mile_lat_lon = mile_df[['lat','lon']].to_dict(orient='records')
        pause_df = wrktSplits.group_actv(wrkt_df, 'resume')
        pause_lat_lon = pause_df[['lat','lon']].to_dict(orient='records')

        logger.info(str(lap_df))
        intvl_lst = sorted(Workout_interval.query.filter_by( workout_id=wrkt_id, user_id=current_user_id))
        for intrvl in intvl_lst:
            if intrvl.break_type == 'mile':
                if len(mile_lat_lon) >intrvl.interval_order:
                    intrvl.lat = mile_lat_lon[intrvl.interval_order]['lat']
                    intrvl.lon = mile_lat_lon[intrvl.interval_order]['lon']
            if intrvl.break_type == 'lap':
                if len(lap_lat_lon) >intrvl.interval_order:
                    intrvl.lat = lap_lat_lon[intrvl.interval_order]['lat']
                    intrvl.lon = lap_lat_lon[intrvl.interval_order]['lon']
            if intrvl.break_type == 'resume':
                if len(pause_lat_lon) >intrvl.interval_order:
                    intrvl.lat = pause_lat_lon[intrvl.interval_order]['lat']
                    intrvl.lon = pause_lat_lon[intrvl.interval_order]['lon']
        db.session.commit()

    return jsonify('Success'), 200
