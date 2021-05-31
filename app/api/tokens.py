# 3rd Party Classes
from flask import jsonify

# Custom Classes
from app import db
from app.api import bp
from app.api.auth import basic_auth, token_auth
from app import logger

@bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    logger.info('get_token')
    token, expiration_dttm = basic_auth.current_user().get_token()
    db.session.commit()
    return jsonify({'token': token, 'expiration_datetime':expiration_dttm})

@bp.route('/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    token_auth.current_user().revoke_token()
    db.session.commit()
    return '', 204
