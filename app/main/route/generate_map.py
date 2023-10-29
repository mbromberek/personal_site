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

# Custom classes from GitHub
import GenerateMapImage.gen_map_img as genMap

# Custom classes
from app.main import bp
# from app import db
from app import logger, basedir
from app.utils import const

@bp.route('/generate_map', methods=['GET'])
@login_required
def generate_map():
    logger.info('generate_map')
    
    direction_json_fname = os.path.join(basedir, "static/data/direction.json")
    with open(direction_json_fname) as direction_file:
        direction_data = json.load(direction_file)
    map_json = parse_directions(direction_data)
    
    return render_template('generate_map.html', title='Generate Workout map' \
      ,  map_json=map_json, destPage='maps')

def parse_directions(data):
      meters_to_miles = float(const.METERS_TO_MILES)
      
      waypoints = data['waypoints']
      logger.info('*** Waypoints ***')
      for waypoint in waypoints:
          logger.info(waypoint['name'] + str(waypoint['distance']))
      
      route = data['routes'][0]
      logger.info('Route: ' + route['weight_name'])
      dist_mi = float(route['distance']) * meters_to_miles
      logger.info('Distance: ' + str(dist_mi))
      
      
      leg = route['legs'][0]
      steps = leg['steps']
      coordinate_lst = []
      for idx, step in enumerate(steps):
          dist_mi = round(float(step['distance']) * meters_to_miles, 2)
          coordinates = step['geometry']['coordinates']
          logger.info('Step {}: {} {} miles, {} coordinates'.format(\
              idx, step['name'], dist_mi, len(coordinates)))
          for coordinate in coordinates:
              # longitude, latitude
              coordinate_lst.append([coordinate[0],coordinate[1], idx])
      
      return {'total_distance':dist_mi, 'distance_uom':'miles','coordinates':coordinate_lst}
      # return {'total_distance':dist_mi, 'distance_uom':'miles','coordinates':coordinate_lst, 'zoom':zoom, 'center':{'lon':center_lon, 'lat':center_lat}}
