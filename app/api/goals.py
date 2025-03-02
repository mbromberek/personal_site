# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# First party classes
import os
import datetime
import string

# 3rd Party classes
from flask import jsonify, request, url_for, abort, current_app

# Custom Classes
from app import db
from app.models import User
from app.model.goals import Goal, Goal_type
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request
from app import logger
from app.utils import dt_conv

@bp.route('/goals/', methods=['GET'])
@token_auth.login_required
def get_goals():
    '''
    Get goals for calling user
    Optional arguments
        active: default all, values are Y|N|all
        page: ?
        per_page: ?
        workout_type: default all, possible values are all|run|cycle|swim|strength
        
    '''
    logger.info('get_goals')
    usr_id = token_auth.current_user().id
    user = User.query.get_or_404(usr_id)
    # per_page = min(request.args.get('per_page', current_app.config['POSTS_PER_PAGE'], type=int), 100)
    # active = request.args.get('active', 'all')
    goal_lst = Goal.query.filter_by(user_id=usr_id)
    for goal in goal_lst:
        logger.info(goal.description)
    goal_dict_lst = Goal.lst_to_dict(goal_lst)
    return jsonify(goal_dict_lst)
    