# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

from flask import Blueprint

bp = Blueprint('main', __name__)

from app.main import routes
from app.main.route import event_pages
from app.main.route import schedule
from app.main.route import data_analysis
from app.main.route import generate_map
from app.main.route import tag
from app.main.route import goal