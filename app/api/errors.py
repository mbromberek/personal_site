from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES

# Custom classes
from app import logger

def error_response(status_code, message=None):
    logger.info('error_response')
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response

def bad_request(message):
    logger.info('bad_request')
    return error_response(400, message)
