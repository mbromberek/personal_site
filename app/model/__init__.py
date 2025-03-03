# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

from flask import Blueprint

bp = Blueprint('model', __name__)

# Commented out when setting up Goal table on DB and goal APIs, this was causing circular logic issue. Was not sure the reason for it and commenting it out did not cause any issues in testing.
# from app.model import goals
