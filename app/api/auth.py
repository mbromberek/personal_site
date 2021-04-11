# 3rd party classes
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth

# Customer classes
from app.models import User
from app.api.errors import error_response

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

@basic_auth.verify_password
def verify_password(email, password):
    print("verify_password: " + email)
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        return user

@basic_auth.error_handler
def basic_auth_error(status):
    return error_response(status)

@token_auth.verify_token
def verify_token(token):
    return User.check_token(token) if token else None

@token_auth.error_handler
def token_auth_error(status):
    return error_response(status)
