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

@bp.route('/generate_map', methods=['GET'])
@login_required
def generate_map():
    logger.info('generate_map')
    
    direction_json_fname = os.path.join(basedir, "static/data/direction.json")
    with open(direction_json_fname) as direction_file:
        direction_data = json.load(direction_file)
    
    return render_template('generate_map.html', title='Generate Workout map' \
      ,  map_json=direction_data, destPage='generate_map')
