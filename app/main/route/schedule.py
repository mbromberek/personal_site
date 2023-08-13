# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# First party classes
from datetime import datetime, timedelta, date
import time
import os, math, json, csv

# Third party classes
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app, send_file, send_from_directory
from flask_login import current_user, login_required
# import pandas as pd
# import numpy as np

# Custom classes
from app.main import bp
# from app import db
from app import logger, basedir

@bp.route('/schedule')
# @login_required
def schedule():
    logger.info('schedule')
    
    schedule_json_fname = os.path.join(basedir, "static/data/schedule.json")
    with open(schedule_json_fname) as schedule_file:
        schedule_data = json.load(schedule_file)
    
    return render_template('ai_schedule.html', title='AI Programming Schedule' \
      ,  sch_json=schedule_data, destPage='ai')
