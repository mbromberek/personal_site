# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# First party classes
from datetime import datetime, timedelta, date
import time
import os, math, json

# Third party classes
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app, send_file, send_from_directory
from flask_login import current_user, login_required
# import pandas as pd
# import numpy as np

# Custom classes
from app.main import bp
from app import db
from app.model.mapping_route import Route, Route_coord
from app import logger, basedir
from app.utils import const, dist_conv
from app.model.tag import Workout_tag, Tag_usage, Tag_usage_wrkt


@bp.route('/get_workout_tags', methods=['GET'])
@login_required
def get_workout_tags():
    logger.info('get_workout_tags')

    usr_id = current_user.id
    wrkt_id = request.args.get('wrkt_id')
    logger.info(wrkt_id)
    
    # Get all tags for user
    tag_usage_lst = Tag_usage.query.filter_by(user_id=usr_id)
    
    # Get all tags for workout
    workout_tag_lst = Workout_tag.query.filter_by(user_id=usr_id, workout_id=wrkt_id)
    workout_tags = []
    for workout_tag in workout_tag_lst:
      workout_tags.append(workout_tag.tag_id)
    
    tag_usage_for_workout_lst = []
    # Loop through all tags marking if on workout or not
    for idx, tag_usage in enumerate(tag_usage_lst):
      if tag_usage.id in workout_tags:
        tag_usage_for_workout_lst.append(Tag_usage_wrkt(tag_usage, tag_on_workout=True))
      else:
        tag_usage_for_workout_lst.append(Tag_usage_wrkt(tag_usage, tag_on_workout=False))
    
    tag_usage_for_workout_lst = sorted(tag_usage_for_workout_lst)
    # logger.debug(Tag_usage_wrkt.to_dict_lst(tag_usage_for_workout_lst))
    
    return jsonify({'items':Tag_usage_wrkt.to_dict_lst(tag_usage_for_workout_lst), 'wrkt_id':wrkt_id})

@bp.route('/update_workout_tags', methods=['POST'])
@login_required
def update_workout_tags():
    logger.info('update_workout_tags')

    usr_id = current_user.id
    wrkt_id = request.form['wrkt_id']
    tag_id_str_lst = json.loads(request.form['tags'])
    logger.debug(tag_id_str_lst)
    
    # Get workouts Tag Ids
    wrkt_tag_lst = Workout_tag.query.filter_by(user_id=usr_id, workout_id=wrkt_id)
    
    tag_id_lst = [int(tag_id) for tag_id in tag_id_str_lst]
    
    # Loop through workout tags
    wrkt_tag_id_lst = []
    for wrkt_tag in wrkt_tag_lst:
      # If workout tag is not in tag_lst then delete it
      if wrkt_tag.tag_id not in tag_id_lst:
        logger.debug('delete tag ' + str(wrkt_tag.tag_id))
        db.session.delete(wrkt_tag)
      else:
        wrkt_tag_id_lst.append(wrkt_tag.tag_id)
    
    # Loop through tag_lst
    for tag_id in tag_id_lst:
      # If tag is not in workout tag list then add it
      if tag_id not in wrkt_tag_id_lst:
        logger.debug('add tag ' + str(tag_id))
        new_workout_tag = Workout_tag()
        new_workout_tag.tag_id = tag_id
        new_workout_tag.workout_id = wrkt_id
        new_workout_tag.user_id = usr_id
        db.session.add(new_workout_tag)
    
    db.session.commit()
    
    # Get new list of tags for workout and return it or reload the Workout page
    # Get workouts tags and sort by when tag was added to workout
    tags_query = Workout_tag.query.filter_by(workout_id=wrkt_id, user_id=usr_id)
    tags = sorted(tags_query, key=lambda x: x.isrt_ts)
    tag_name_lst = []
    for tag in tags:
        tag_name_lst.append(tag.workout_tag.nm)
    return jsonify({'wrkt_id':wrkt_id, 'items':tag_name_lst})
    # return redirect(url_for('main.workout', workout=wrkt_id))
    # return redirect(url_for('main.workouts'))
    
