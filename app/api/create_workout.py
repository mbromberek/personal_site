# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# First party classes
import os, glob, shutil
from datetime import datetime, timedelta, date
import string
import random
import re
import zipfile
import json
from zoneinfo import ZoneInfo

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
from app.models import Workout, User, Workout_interval, Gear, Wrkt_sum, Workout_type
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
        # fao.clean_dir(workDir)
        logger.info('should clean directorty')
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
        workout = processFartlekData(directory, user_id)
      db.session.commit()
      clean_dir(tempDir)
      clean_dir(workDir)
    elif file_ext == '.fit':
      logger.info('Fit file processing not enabled yet')
      # uploaded_file.save(os.path.join(tempDir, fname))
      clean_dir(workDir)
      clean_dir(tempDir)
      return jsonify("Fit file processing not enabled yet"), 400
    else:
      logger.info('No file to process')
      clean_dir(workDir)
      clean_dir(tempDir)
      return jsonify("No valid files to process"), 400

    responseDict = {}
    responseDict['status'] = 'Success'
    responseDict['workout_id'] = str(workout.id)
    responseDict['link'] = url_for('main.workout', 
        workout=workout.id, 
        _external=True,
        _scheme=current_app.config['URL_SCHEME']
    )
    logger.info('⏲️ ')
    logger.info(workout.wrkt_dttm)
    responseDict['workout_datetime'] = workout.wrkt_dttm.isoformat(sep=' ') + 'Z'
    
    response = jsonify(responseDict)
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_workout', id=workout.id)

    logger.info('end')
    return response

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
    unzippedFiles = os.listdir(tempDir)
    return (zipFiles, unzippedFiles)

def processFartlekData(directory: str, userId: int) -> Workout:
    logger.info('directory: ' + directory)
    workDir = os.path.join(current_app.config['WRKT_FILE_DIR'], str(userId), 'work')
    fullDirectoryPath = os.path.join(workDir, directory)
    # Confirm this is a directory, if not return false
    if not os.path.isdir(fullDirectoryPath):
        return
  
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

    jsonFile = os.path.join(fullDirectoryPath, jsonFileName)    
    with open(jsonFile, 'r') as data_file:
        workoutData = json.load(data_file)
    
    workout: Workout = None
    if 'dateTime' in workoutData:
        workoutDateTime = datetime.strptime(workoutData['dateTime'], '%Y-%m-%dT%H:%M:%SZ')
        workoutDateTime = workoutDateTime.replace(tzinfo=ZoneInfo("UTC"))
        if 'timeZoneIdentifier' in workoutData:
            workoutDateTime = workoutDateTime.astimezone(ZoneInfo(workoutData['timeZoneIdentifier']))
        workout = Workout.query.filter_by(user_id=userId, wrkt_dttm=workoutDateTime).first()
    
    if workout == None:
        if thumbnailImageName == '':
            workout = createWorkoutFromFartlekFiles(
                userId, 
                workoutData, 
                os.path.join(fullDirectoryPath, fitFileName)
            )  
        else:
            workout = createWorkoutFromFartlekFiles(
                userId, 
                workoutData, 
                os.path.join(fullDirectoryPath, fitFileName), 
                os.path.join(fullDirectoryPath, thumbnailImageName)
            )
    else:
        updateWorkoutFromFartlekFiles(
            userId, 
            workout,
            workoutData
        )
    return workout


def createWorkoutFromFartlekFiles(userId: int, workoutData, fitFile: str, thumbnailImage: str = '') -> Workout:
    logger.debug('createWorkoutFromFartlekFiles')
    req_fields = ['type', 'dateTime', 'duration']
    for field in req_fields:
        if field not in workoutData:
            return bad_request('must include ' + field + ' field')
    
    # Should I check if a request for specified workt_dttm already exists?
    # if User.query.filter_by(username=data['username']).first():
    #     return bad_request('please use a different email address')
    workout = Workout()
    workout.from_dict_fartlek(workoutData, userId)
    logger.info('⏲️ Workout Created:')
    logger.info(workout.wrkt_dttm)
    db.session.add(workout)
    db.session.flush() # Send insert to DB but does not commit
    
    if 'splits' in workoutData:
        # split_types = ['kilometer','pause','lap','mile']
        for split in workoutData['splits']:
            workoutInterval = Workout_interval()
            workoutInterval.from_dict_fartlek(split, userId, workout.id)
            db.session.add(workoutInterval)
    
    generateMap = True
    if thumbnailImage != '' and current_app.config['USE_FARTLEK_THUMBNAIL'] == 'Y':
        generateMap = False
    
    if workoutData['type'] != 'strength':
        updateWorkoutFromFit(workout, fitFile, userId, generateMap=generateMap)
    
    if not generateMap and thumbnailImage != '':
        tumbnailDir = os.path.join(current_app.config['WRKT_FILE_DIR'], str(userId), current_app.config['USER_THUMBNAIL_DIR'])
        # tumbnailDir = os.path.join(current_app.config['WRKT_FILE_DIR'], str(userId), current_app.config['USER_THUMBNAIL_DIR'], workout.wrkt_dttm.strftime('%Y'))
        #os.makedirs(tumbnailDir, exist_ok=True)
        thumbnail_nm = 'thumb_200_200_' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=50)) + '.png'
        # genMap.generate_map_img(actv_df, tumbnailDir, img_dim={'height':200, 'width':200}, img_name=thumbnail_nm)
        
        # Move thumbnail image to folder, and rename it
        os.rename(thumbnailImage, os.path.join(tumbnailDir, thumbnail_nm))
        # Add thumbnail name to workout.thumb_path
        workout.thumb_path = thumbnail_nm
    
    logger.debug(workout)
    return workout

def updateWorkoutFromFit(workout, fitFile, userId, generateMap: bool = True):
  workDir = os.path.join(current_app.config['WRKT_FILE_DIR'], str(userId), 'work')
  tempDir = os.path.join(current_app.config['WRKT_FILE_DIR'], str(userId), 'temp')
  lapsDf, pointsDf = fitParse.get_dataframes(fitFile)
  actv_df = fitParse.normalize_laps_points(lapsDf, pointsDf)
  
  wrktStrtTm = workout.wrkt_dttm
  wrktTypeId = workout.type_id
  type = Workout_type.query.get(workout.type_id)
  wrktType = type.nm.replace(' ','-').lower()
  wrktSrc = 'com.mikebromberek.fartlek'
  
  # TODO Below not ready
  # Create folder for long term storage of file
  wrktDirNm = wrktStrtTm.strftime('%Y-%m-%d_%H%M%S') + '_' + wrktType + '_' + wrktSrc
  wrktFullPath = os.path.join(current_app.config['WRKT_FILE_DIR'], str(userId), wrktStrtTm.strftime('%Y'), wrktStrtTm.strftime('%m'), wrktDirNm)
  os.makedirs(wrktFullPath, exist_ok=True)
  
  tumbnailDir = os.path.join(current_app.config['WRKT_FILE_DIR'], str(userId), current_app.config['USER_THUMBNAIL_DIR'])
  os.makedirs(tumbnailDir, exist_ok=True)
  
  # Move saved file from temp to new directory and export data frame as pickle to new directory.
  # os.rename(os.path.join(tempDir, fname), os.path.join(wrktFullPath, fname))
  fao.save_df(actv_df, wrktFullPath,'workout', frmt=['pickle'])
  # fao.clean_dir(workDir)
  
  # Update workout passed in wrkt_id for user_id
  # orig_workout = Workout.query.filter_by(id=wrkt_id, user_id=userId).first_or_404(wrkt_id)
  orig_workout = workout
  orig_workout.wrkt_dir = os.path.join(wrktStrtTm.strftime('%Y'), wrktStrtTm.strftime('%m'), wrktDirNm)
  
  logger.debug('workout ID: ' + str(workout.id))
  auto_wrkt_tags = wrkt_summary.generate_workout_tags(actv_df)
  logger.debug(auto_wrkt_tags)
  for tag in auto_wrkt_tags:
      new_workout_tag = Workout_tag()
      new_workout_tag.user_id = userId
      new_workout_tag.tag_id = tag
      new_workout_tag.workout_id = workout.id
      db.session.add(new_workout_tag)
  
  if 'latitude' in actv_df and 'longitude' in actv_df:
      coord_df = actv_df[['latitude','longitude']].dropna()
  else:
      coord_df = pd.DataFrame()
  if coord_df.shape[0] >1:
      # strt_coord = actv_df[['latitude','longitude']].dropna().iloc[0]
      # end_coord = actv_df[['latitude','longitude']].dropna().iloc[-1]
      # orig_workout.lat_strt = np.float64(strt_coord['latitude']).item() # Need to convert from np.float64 to Python number
      # orig_workout.long_strt = np.float64(strt_coord['longitude']).item()
      # orig_workout.lat_end = np.float64(end_coord['latitude']).item()
      # orig_workout.long_end = np.float64(end_coord['longitude']).item()
      if generateMap:
        thumbnail_nm = 'thumb_200_200_' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=50)) + '.png'
        genMap.generate_map_img(actv_df, tumbnailDir, img_dim={'height':200, 'width':200}, img_name=thumbnail_nm)
        orig_workout.thumb_path = thumbnail_nm
      orig_workout.show_map_laps = True
      if orig_workout.category_det != None and orig_workout.category_det.nm == 'Training':
          orig_workout.show_map_miles = False
      else:
          orig_workout.show_map_miles = True
  
      if orig_workout.location == '' or orig_workout.location == None:
          loc_lst = Location.query.filter_by(user_id=userId)
          wrkt_loc = Location.closest_location(loc_lst, {'lat':orig_workout.lat_strt,'lon':orig_workout.long_strt})
          if wrkt_loc != '':
              orig_workout.location = wrkt_loc

  return
    
def clean_dir(dir):
    files = glob.glob(dir + '/*')
    for f in files:
        if os.path.isdir(f):
            shutil.rmtree(f)
        else:
            os.remove(f)

def updateWorkoutFromFartlekFiles(userId: int, workout: Workout, workoutData):
    logger.debug('updateWorkoutFromFartlekFiles')
    # Update Clothes if empty in workout
    if (workout.clothes == None or workout.clothes == '') and 'clothes' in workoutData and workoutData['clothes'] != None and workoutData['clothes'] != '' :
        workout.clothes = workoutData['clothes']
        
    # Update Gear (regardless if already populated)
    if 'gear' in workoutData and workoutData['gear'] != None and workoutData['gear'] != '' :
        workout.gear_id = Gear.get_gear_id(workoutData['gear'])
        if workout.gear_id is None:
            # Create gear
            new_gear = Gear(nm=workoutData['gear'], type='Shoe', user_id=user_id)
            db.session.add(new_gear)
            db.session.commit()
            workout.gear_id = Gear.get_gear_id(workoutData['gear'])

    # Append to Notes
    if 'notes' in workoutData and workoutData['notes'] != None and workoutData['notes'] != '':
        if workout.notes == None:
            workout.notes = workoutData['notes']
        elif workout.notes != workoutData['notes']:
            workout.notes = workout.notes + '\n\n' + workoutData['notes']
    
    if workoutData['type'] == 'strength' and 'title' in workoutData:
        workout.training_type = workoutData['title']
    
    # Update other fields?
    # Add new Tags
    return