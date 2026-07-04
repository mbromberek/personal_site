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
import re
import zipfile
import json

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
    user_id = token_auth.current_user().id
    logger.info('User ID: ' + str(user_id))
    # dataLst = request.get_json() or [{}]
    logger.info(request.files)
    if 'file' not in request.files:
        logger.info('no file')
        return jsonify("No file found"), 400
    logger.info(str(request.files['file']))
    uploaded_file = request.files['file']
    fname = secure_filename(uploaded_file.filename)
    file_ext = os.path.splitext(fname)[-1]
    if file_ext not in current_app.config['UPLOAD_EXTENSIONS']:
        logger.info('{} is an invalid file extension'.format(file_ext))
        abort(400)
    
    tempDir = os.path.join(current_app.config['WRKT_FILE_DIR'], str(user_id), 'temp')
    workDir = os.path.join(current_app.config['WRKT_FILE_DIR'], str(user_id), 'work')
    
    if not os.path.exists(workDir):
        os.makedirs(os.path.join(workDir))
    else:
        # TODO: should I remove this and just ensure files from this function get removed?
        fao.clean_dir(workDir)
    if not os.path.exists(tempDir):
            os.makedirs(os.path.join(current_app.config['WRKT_FILE_DIR'], str(user_id), 'temp'))
    
    # If zip file
    # fileExtension = file_ext(fname)
    logger.info('Filename: ' + fname + ' extension ' + file_ext)
    if file_ext == '.zip' and fname.split('_')[0] == 'Fartlek':
      logger.info('Got export zip file from Fartlek app')
      uploaded_file.save(os.path.join(tempDir, fname))
      (zipFiles, directoriesToProcess) = uncompressToTemp(tempDir, workDir)
      for directory in directoriesToProcess:
        processFartlekData(directory)
      
    elif file_ext == '.fit':
      logger.info('Fit file processing not enabled yet')
      # uploaded_file.save(os.path.join(tempDir, fname))
      fao.clean_dir(workDir)
      fao.clean_dir(tempDir)
      return jsonify("Fit file processing not enabled yet"), 400
    else:
      logger.info('No file to process')
      fao.clean_dir(workDir)
      fao.clean_dir(tempDir)
      return jsonify("No valid files to process"), 400

    # fao.extract_files(fname, workDir, tempDir)

    logger.info('end')

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
    
    response.status_code = 201
    # response.headers['Location'] = url_for('api.get_workout', id=workout.id)
    return response
    '''
    return jsonify('testing'), 201

def uncompressToTemp(monitorDir: str, tempDir: str) -> ([str], [str]):
    '''
    Uncompress files from monitor directory into temp directory
    '''
    zipFiles = []
    compressFileRegex = re.compile(r'(.zip|.gz)$')
    for filename in os.listdir(monitorDir):
        # Checks if compressed file
        if compressFileRegex.search(filename):
            z = zipfile.ZipFile(os.path.join(monitorDir, filename),mode='r')
            z.extractall(path=tempDir)
            zipFiles.append(os.path.join(monitorDir, filename))
    unzippedFiles = os.listdir(monitorDir)
    return (zipFiles, unzippedFiles)

def processFartlekData(directory: str, userId: int):
  logger.info('directory: ' + directory)
  fullDirectoryPath = os.path.join(monitorDir, directory)
  # Confirm this is a directory, if not return false
  
  thumbnailImageName = ''
  fitFileName = ''
  jsonFileName = ''
  # Get list of files
  files = os.listdir(fullDirectoryPath)
  for filename in files:
    if filename.endswith('Thumbnail-Light.png'):
      thumbnailImageName = filename
    elif filename.endswith('.json'):
      jsonFileName = filename
    elif filename.endswith('.fit'):
      fitFileName = filename
  workout = createWorkoutFromFartlekFiles(
    userId, 
    os.path.join(fullDirectoryPath, jsonFileName), 
    os.path.join(fullDirectoryPath, fitFileName), 
    os.path.join(fullDirectoryPath, thumbnailImageName)
  )
  # updateWorkoutFromFit(workout, os.path.join(fullDirectoryPath, fitFileName))
  # Function to get weather using updated data
  # Function generate workout thumbnail or use the one that was provided (assuming there was one)


def createWorkoutFromFartlekFiles(userId: int, jsonFile: str, fitFile: str, thumbnailImage: str = '') -> Workout:
  with open(jsonFile, 'r') as data_file:
    workoutData = json.load(data_file)
  req_fields = ['type', 'dateTime', 'duration']
  for field in req_fields:
    if field not in data:
        return bad_request('must include ' + field + ' field')
  
  # Should I check if a request for specified workt_dttm already exists?
  # if User.query.filter_by(username=data['username']).first():
  #     return bad_request('please use a different email address')
  workout = Workout()
  workout.from_fartlek_dict(workoutData, userId)
  logger.debug(workout)
  return workout
    