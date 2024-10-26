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
