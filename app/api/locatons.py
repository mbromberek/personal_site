# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# First party classes
import datetime
import string

# 3rd Party classes
from flask import jsonify, current_app

# Custom Classes
from app import db
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request
from app import logger
from app.model.location import Location

@bp.route('/location/<int:id>', methods=['GET'])
@token_auth.login_required
def get_location(id):
    logger.info('get_location')
    usr_id = token_auth.current_user().id
    return jsonify("No records found"), 400

@bp.route('/locations', methods=['GET'])
@token_auth.login_required
def get_locations():
    logger.info('get_locations')
    usr_id = token_auth.current_user().id
    return jsonify("No records found"), 400

@bp.route('/location', methods=['POST'])
@token_auth.login_required
def create_location():
    logger.info('create_workout')
    usr_id = token_auth.current_user().id
    return jsonify("No records found"), 400

@bp.route('/location', methods=['PUT'])
@token_auth.login_required
def update_location():
    logger.info('update_location')
    usr_id = token_auth.current_user().id
    return jsonify("No records found"), 400
