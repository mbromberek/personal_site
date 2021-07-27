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
    # LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')

    # SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    # token_expires_after = int(CONFIG['user']['token_expires_after'])
