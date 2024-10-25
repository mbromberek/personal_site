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
from app.model.tag import Workout_tag, Tag_usage


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
    
    # Loop through all tags marking 
    for tag_usage in tag_usage_lst:
      if tag_usage.id in workout_tags:
        tag_usage.on_workout = True
      else:
        tag_usage.on_workout = False
    
    tag_usage_lst = sorted(tag_usage_lst)
    logger.info(Tag_usage.to_dict_lst(tag_usage_lst))
    
    return jsonify(Tag_usage.to_dict_lst(tag_usage_lst))
