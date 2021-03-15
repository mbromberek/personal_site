# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# Custom imports
from app import app
from app.main import bp

@bp.route('/')
@bp.route('/index')
def index():
    return "Mike Bromberek Personal Website!"
