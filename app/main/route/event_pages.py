# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# First party classes
from datetime import datetime, timedelta, date
import os, math
# from datetime import combine

# Third party classes
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
# import pandas as pd

# Custom classes
from app.main import bp
from app.models import User
from app import db
from app import logger

@bp.route('/event', methods=['GET'])
@login_required
def event():
    logger.info('event')
    usr_id = current_user.id
    event_id = request.args.get('event')
    logger.info('event: ' + str(event_id) + ' for user: ' + str(usr_id))

    map_dict = {}
    map_dict['key'] = current_app.config['MAPBOX_API_KEY']
    map_dict['max_zoom'] = current_app.config['MAP_MAX_ZOOM']

    map_dict['center'] = {'lat':'40.756350', 'lon':'-73.993120'}
    map_dict['zoom'] = 13
    map_dict['lat_lon'] = []
    map_dict['mile_markers'] = []

    loc_lst = []
    hotel_det = {'name':'Holiday Inn', 'type':'hotel', 'lat':'40.756350', 'lon':'-73.993120'}
    race_start = {'name':'New York Marathon Start', 'type':'race_start', 'lat':'40.603282429411436', 'lon':'-74.05486822128297'}
    loc_lst = [hotel_det, race_start]

    map_dict['loc_lst'] = loc_lst


    return render_template('event.html', map_dict=map_dict, destPage='event')
