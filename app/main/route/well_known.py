# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# First party classes
import os

# Third party classes
from flask import send_from_directory

# Custom classes
from app.main import bp
from app import basedir

# .well-known directory at the root of the project (not tracked in git)
WELL_KNOWN_DIR = os.path.abspath(os.path.join(basedir, '..', '.well-known'))


@bp.route('/.well-known/apple-app-site-association', methods=['GET'])
def apple_app_site_association():
    # Apple requires this at the site root, over HTTPS, with no redirects, as JSON
    return send_from_directory(WELL_KNOWN_DIR, 'apple-app-site-association', mimetype='application/json')
