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
    POSTS_PER_PAGE = 20
    SIZE_NOTES_SUMMARY = 200
    DEBUG = False
    TEMPERATURE_RANGE = 5
    DISTANCE_RANGE = 0.10
    MAX_CONTENT_LENGTH = 1024 * 1024
    UPLOAD_EXTENSIONS = ['.zip', '.fit']
