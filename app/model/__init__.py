# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

from flask import Blueprint

bp = Blueprint('model', __name__)

from app.model import goals
