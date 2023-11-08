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
from app import db
from app.model.mapping_route import Route, Route_coord
from app import logger, basedir
from app.utils import const, dist_conv

@bp.route('/generate_map', methods=['GET'])
@login_required
def generate_map():
    logger.info('generate_map')
    
    direction_json_fname = os.path.join(basedir, "static/data/direction.json")
    with open(direction_json_fname) as direction_file:
        direction_data = json.load(direction_file)
    map_dict = parse_directions(direction_data)
    
    map_dict['key'] = current_app.config['MAPBOX_API_KEY']
    map_dict['max_zoom'] = current_app.config['MAP_MAX_ZOOM']
    
    mapbox_url_parms_lst = []
    mapbox_url_parms_lst.append('access_token={}'.format(current_app.config['MAPBOX_API_KEY']))
    mapbox_url_parms_lst.append('annotations=distance')
    mapbox_url_parms_lst.append('steps=true')
    mapbox_url_parms_lst.append('geometries=geojson')
    mapbox_url_parms = '&'.join(mapbox_url_parms_lst)
    map_dict['mapbox_url_parms'] = mapbox_url_parms
    
    return render_template('generate_map.html', title='Generate Workout map' \
      ,  map_json=map_dict, destPage='generate_map')

@bp.route('/edit_route', methods=['GET'])
@login_required
def edit_route():
    logger.info('edit_route')
    usr_id = current_user.id
    route_id = ''
    if 'route' in request.args:
        route_id = request.args.get('route')
    
    map_dict = {}
    map_dict['key'] = current_app.config['MAPBOX_API_KEY']
    map_dict['max_zoom'] = current_app.config['MAP_MAX_ZOOM']
    
    map_dict['mapbox_url_parms'] = gen_mapbox_parms_url()
    
    mapbox_url_parms_lst = []
    mapbox_url_parms_lst.append('access_token={}'.format(current_app.config['MAPBOX_API_KEY']))
    mapbox_url_parms_lst.append('annotations=distance')
    mapbox_url_parms_lst.append('steps=true')
    mapbox_url_parms_lst.append('geometries=geojson')
    mapbox_url_parms = '&'.join(mapbox_url_parms_lst)
    map_dict['mapbox_url_parms'] = mapbox_url_parms
    
    # Morton Trail Start
    lat_center = 40.619374
    lon_center = -89.471065
    # RCO
    lat_center = 40.6877
    lon_center = -89.5905


    # Start with blank route or load from DB if there is a route ID
    if route_id == '':
        map_dict['total_distance'] = 0
        map_dict['distance_uom'] = 'miles'
        map_dict['coordinates'] = []
        map_dict['center'] = {'lat':lat_center, 'lon':lon_center}
        map_dict['zoom'] = 16
    else:
        route = Route.query.filter_by(id=route_id, user_id=usr_id).first_or_404(description="Route not found for current user")
        route_coord_lst = sorted(Route_coord.query.filter_by( \
          route_id=route_id, user_id=usr_id))
        # direction_json_fname = os.path.join(basedir, "static/data/direction.json")
        # with open(direction_json_fname) as direction_file:
            # direction_data = json.load(direction_file)
        map_dict.update(parse_route(route, route_coord_lst))
    
    return render_template('generate_map.html', title='Generate Workout map' \
        ,  map_json=map_dict, destPage='generate_map')

@bp.route('/route', methods=['GET'])
@login_required
def route():
    logger.info('route')

@bp.route('/routes', methods=['GET'])
@login_required
def routes():
    logger.info('routes')


@bp.route('/save_route', methods=['GET','POST'])
@login_required
def save_route():
    usr_id = current_user.id
    # TODO Check if USER_ID, NAME already exist and if they do ask user about override
    logger.info('save_route POST')
    data = request.form
    logger.info(data.keys())
    if 'route_id' in data:
        req_route_id = data['route_id']
        # Check if route exists for user name
    else:
        req_route_id = ''
    req_route_name = data['route_name']
    req_dist = float(data['dist']) #TODO handle string to float
    req_dist_uom = data['dist_uom']
    req_coord_dict = json.loads(data['route_coord_lst'])
    logger.info('Route \'{}\' is {} {}'.format(\
        req_route_name, req_dist, req_dist_uom))
    # logger.info(req_coord_dict)
    logger.info(len(req_coord_dict))
    req_coord_str = str(req_coord_dict)
    
    coord_lst = []
    
    for coord in req_coord_dict:
        coord_lst.extend(coord['lat_lon'])
        logger.info('Group distance: ' + str(coord['dist']))
    logger.info(len(coord_lst))
    logger.info(coord_lst[0])
    coord_str = str(coord_lst)
    logger.info('Length of Coordinates String: ' + str(len(coord_str))) # Max size is 10,485,760
    
    if req_route_id == '':
        route = Route()
    else:
        route = Route.query.filter_by(id=req_route_id, user_id=usr_id).first_or_404(description="Route not found for current user")
        route_coord_lst = sorted(Route_coord.query.filter_by( \
          route_id=req_route_id, user_id=usr_id))
        for route_coord in route_coord_lst:
            db.session.delete(route_coord)
    
    route.user_id = usr_id
    if len(req_route_name) <= 255:
        route.name = req_route_name
    else:
        logger.error('Route Name: {} is longer than max of 255'.format(req_route_name))
    POSTGRES_VARCHAR_MAX_LENGTH = 10485760
    if (len(coord_str) > POSTGRES_VARCHAR_MAX_LENGTH):
        err_msg = 'Route contains too many coordinates'
        logger.error(err_msg)
        return jsonify({'ERR_MSG':err_msg})
    route.dist = dist_conv.dist_to_meters(req_dist, req_dist_uom)
    route.dist_uom = 'meters'
    route.public = False
    route.lat_start = coord_lst[0][0]
    route.lon_start = coord_lst[0][1]
    route.lat_end = coord_lst[-1][0]
    route.lon_end = coord_lst[-1][1]
    route.updt_ts = datetime.utcnow()
    db.session.add(route)
    db.session.commit()
    db.session.refresh(route)
    
    route_coord = Route_coord()
    route_coord.route_id = route.id
    route_coord.step = 1
    route_coord.user_id = current_user.id
    route_coord.coordinates = coord_str
    db.session.add(route_coord)
    db.session.commit()
    
    return jsonify({})

'''
Parse data for route read from database
Combine all rows that are in route_coord_lst to get one list with all coordinates
'''
def parse_route(route, route_coord_lst):
    map_dict = {}
    map_dict['total_distance'] = dist_conv.dist_to_miles(route.dist, route.dist_uom)
    map_dict['distance_uom'] = 'miles'
    map_dict['name'] = route.name
    map_dict['route_id'] = route.id
    
    coordinate_lst = []
    lon_max = -999
    lat_max = -999
    lon_min = 999
    lat_min = 999
    
    for idx, step in enumerate(route_coord_lst):
        coordinates = json.loads(step.coordinates)
        # coordinates = list(step.coordinates)
        logger.info('Step {}: {} coordinates'.format(\
            step.step, len(coordinates)))
        for coordinate in coordinates:
            lon = float(coordinate[1])
            lat = float(coordinate[0])
            if lon_max < lon: lon_max = lon
            if lon_min > lon: lon_min = lon
            if lat_max < lat: lat_max = lat
            if lat_min > lat: lat_min = lat
            
            coordinate_lst.append([lat,lon])

    map_dict['coordinates'] = coordinate_lst
    map_dict['center'] = genMap.calc_center(lats=[lat_max, lat_min], lons=[lon_max, lon_min])
    map_dict['zoom'] = genMap.calc_zoom(lats=[lat_min, lat_max], lons=[lon_min, lon_max], img_dim={'height':1300, 'width':1600})
     
    return map_dict
    
def parse_directions(data):
    meters_to_miles = float(const.METERS_TO_MILES)
    
    waypoints = data['waypoints']
    logger.info('*** Waypoints ***')
    for waypoint in waypoints:
      logger.info(waypoint['name'] + str(waypoint['distance']))
    
    route = data['routes'][0]
    logger.info('Route: ' + route['weight_name'])
    tot_dist_mi = float(route['distance']) * meters_to_miles
    logger.info('Distance: ' + str(tot_dist_mi))
    
    
    leg = route['legs'][0]
    steps = leg['steps']
    coordinate_lst = []
    lon_max = -999
    lat_max = -999
    lon_min = 999
    lat_min = 999

    for idx, step in enumerate(steps):
        dist_mi = round(float(step['distance']) * meters_to_miles, 2)
        coordinates = step['geometry']['coordinates']
        logger.info('Step {}: {} {} miles, {} coordinates'.format(\
            idx, step['name'], dist_mi, len(coordinates)))
        for coordinate in coordinates:
            if lon_max < coordinate[0]: lon_max = coordinate[0]
            if lon_min > coordinate[0]: lon_min = coordinate[0]
            if lat_max < coordinate[1]: lat_max = coordinate[1]
            if lat_min > coordinate[1]: lat_min = coordinate[1]
            # [0]=longitude, [1]=latitude
            # coordinate_lst.append([coordinate[1],coordinate[0], idx])
            # TODO determine how to pass Step start coordinates and determine if they are useful
            coordinate_lst.append([coordinate[1],coordinate[0]])
    
    map_dict = {}
    map_dict['total_distance'] = tot_dist_mi
    map_dict['distance_uom'] = 'miles'
    map_dict['coordinates'] = coordinate_lst
    map_dict['center'] = genMap.calc_center(lats=[lat_max, lat_min], lons=[lon_max, lon_min])
    map_dict['zoom'] = genMap.calc_zoom(lats=[lat_min, lat_max], lons=[lon_min, lon_max], img_dim={'height':1300, 'width':1600})
     
    return map_dict
    # return {'total_distance':dist_mi, 'distance_uom':'miles','coordinates':coordinate_lst}
    # return {'total_distance':dist_mi, 'distance_uom':'miles','coordinates':coordinate_lst, 'zoom':zoom, 'center':{'lon':center_lon, 'lat':center_lat}}

def gen_mapbox_parms_url():
    mapbox_url_parms_lst = []
    mapbox_url_parms_lst.append('access_token={}'.format(current_app.config['MAPBOX_API_KEY']))
    mapbox_url_parms_lst.append('annotations=distance')
    mapbox_url_parms_lst.append('steps=true')
    mapbox_url_parms_lst.append('geometries=geojson')
    mapbox_url_parms = '&'.join(mapbox_url_parms_lst)
    return mapbox_url_parms