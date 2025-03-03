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
        is_active: default all, values are Y|N|all
        page: ?
        per_page: ?
        workout_type: default all, possible values are all|run|cycle|swim|strength
        
    '''
    logger.info('get_goals')
    goal_dict_lst = []
    ret_dict = {}
    endpoint = 'api.get_goals'
    usr_id = token_auth.current_user().id
    user = User.query.get_or_404(usr_id)
    per_page = min(request.args.get('per_page', current_app.config['POSTS_PER_PAGE'], type=int), 100)
    page = request.args.get('page', 1, type=int)
    is_active = request.args.get('is_active')
    query = Goal.query.filter_by(user_id=usr_id)
    if is_active != None and is_active.upper() != 'ALL':
        query = query.filter(Goal.is_active==is_active)
    goal_page = query.order_by(Goal.ordr).paginate(page=page, per_page=per_page)
    
    kwargs = {}
    kwargs['is_active'] = is_active
    
    meta_dict = {'page':  page,
        'next_page': goal_page.next_num,
        'previous_page': goal_page.prev_num,
        'per_page': per_page,
        'total_pages':goal_page.pages,
        'total_items':goal_page.total
    }
    ret_dict['_meta'] = meta_dict
    
    links_dict = {
        'self': url_for(endpoint, page=page, per_page=per_page, **kwargs),
        'next': url_for(endpoint, page=goal_page.next_num, per_page=per_page, **kwargs) if goal_page.has_next else None,
        'prev': url_for(endpoint, page=page -1, per_page=per_page, **kwargs) if goal_page.has_prev else None
    }
    ret_dict['_links'] = links_dict
    
    # for goal in goal_page:
    #     logger.info(goal.description)
    goal_dict_lst.extend(Goal.lst_to_dict(goal_page))
    ret_dict['items'] = goal_dict_lst
    
    return jsonify(ret_dict)
    