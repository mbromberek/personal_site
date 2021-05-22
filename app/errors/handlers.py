# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# First party classes

# Third party classes
from flask import render_template, request

# Custom classes
from app import db
from app.errors import bp
from app.api.errors import error_response as api_error_response
from app import logger

def wants_json_response():
    return request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']

@bp.app_errorhandler(404)
def not_found_error(error):
    logger.info(str(error))
    if wants_json_response():
        return api_error_response(404)
    return render_template('errors/404.html', err_desc=error.description), 404

@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    if wants_json_response():
        return api_error_response(500)
    return render_template('errors/500.html'), 500
