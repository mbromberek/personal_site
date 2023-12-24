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

# Custom classes
from app.main import bp
# from app import db
from app import logger, basedir

@bp.route('/data_analysis', methods=['GET'])
def data_analysis():
    logger.info('data_analysis')
    if 'id' in request.args:
      id = request.args.get('id')
    else:
      return render_template(os.path.join('data_analysis','index.html'), title='Data Analysis' \
        ,  destPage='data_analysis')
    
    if id == '1':
      fname = 'Steamboat_15K_Race_analysis.html'
      page_title = 'Steamboat 15K'
    elif id == '2':
      fname = 'Steamboat_4mi_Race_analysis.html'
      page_title = 'Steamboat 4 mile'
    
    return render_template(os.path.join('data_analysis',fname), title=page_title \
      ,  destPage='data_analysis')
