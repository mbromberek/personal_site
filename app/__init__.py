#! /Users/mikeyb/Applications/python3
# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# First party classes
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os

# Third party imports
from flask import Flask

# Custom imports
from config import Config

app = Flask(__name__)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    if app.config['LOG_TO_STDOUT']:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)
    else:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/personal_site.log',
                                           maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('personal_site startup')

    return app

# from app import routes
