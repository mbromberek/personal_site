# 3rd party classes
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth

# Customer classes
from app.models import User
from app.api.errors import error_response
from app import logger

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

@basic_auth.verify_password
def verify_password(email, password):
    logger.info("verify_password: " + email)
    user = User.query.filter_by(email=email).first()

    if user is None:
        logger.info('Invalid username: {}'.format(email))
    elif not user.check_account_status():
        logger.info('Attempt login by locked account: {}'.format(email))
    elif not user.check_password(password):
        logger.info('Invalid password for: {}'.format(email))
        user.updt_acct_stat(False)
    else:
        user.updt_acct_stat(True)
        return user


@basic_auth.error_handler
def basic_auth_error(status):
    return error_response(status)

@token_auth.verify_token
def verify_token(token):
    logger.info("verify_token")
    # TODO Add log message when token verification fails
    return User.check_token(token) if token else None

@token_auth.error_handler
def token_auth_error(status):
    logger.info('token_auth_error')
    return error_response(status)
