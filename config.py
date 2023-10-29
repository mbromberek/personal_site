# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2020, Mike Bromberek
All rights reserved.
'''

# First party classes
import os
# from dotenv import load_dotenv
import configparser

basedir = os.path.abspath(os.path.dirname(__file__))
# load_dotenv(os.path.join(basedir, '.env'))

class Config(object):

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTS_PER_PAGE = 10
    SIZE_NOTES_SUMMARY = 200
    DEBUG = False
    TEMPERATURE_RANGE = 5 #degrees farenheight
    DISTANCE_RANGE = 0.10 #percent
    MAX_CONTENT_LENGTH = 1024 * 1024
    UPLOAD_EXTENSIONS = ['.zip', '.fit']
    DFT_LOC_RADIUS = 0.5 #miles
    MAP_MAX_ZOOM = 20
    LOCATION_MAP_ZOOM = 14

    USR_DFT_DISPLAY_NAME = 'User'
    USR_DFT_SHOE_MILE_WARNING = 300
    USR_DFT_SHOE_MILE_MAX = 350
    USR_DFT_SHOE_MIN_BRKIN_CT = 5

    GEAR_TYPE_MAP = {'1': 'Shoe', '2':'Bike', '3':'Pool', '4':'Insole', '5':'Trainer'}
    DFT_CYCL_GEAR = 'Cannondale'
    DFT_SWIM_GEAR = 'Bamas pool'

