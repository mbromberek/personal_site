# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

from flask import Blueprint

bp = Blueprint('main', __name__)

from app.main import routes
