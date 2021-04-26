# 3rd Party classes
from flask import jsonify, request, url_for, abort

# Custom Classes
from app import db
from app.models import Workout, User
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request
from app import logger
from app.utils import dt_conv

@bp.route('/workout/<int:id>', methods=['GET'])
@token_auth.login_required
def get_workout(id):
    logger.info('get_workout')
    current_user_id = token_auth.current_user().id
    return jsonify(Workout.query.filter_by(id=id, user_id=current_user_id).first_or_404(id).to_dict())
    # return jsonify(Workout.query.get_or_404(id).to_dict())

@bp.route('/workouts/', methods=['GET'])
@token_auth.login_required
def get_workouts():
    logger.info('get_workouts')
    current_user_id = token_auth.current_user().id
    user = User.query.get_or_404(current_user_id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(user.workouts, page, per_page, 'api.get_workouts')
    return jsonify(data)

@bp.route('/workout', methods=['POST'])
@token_auth.login_required
def create_workout():
    logger.info('create_workout')
    pass
    current_user_id = token_auth.current_user().id
    data = request.get_json() or {}
    # Make sure the required fields are in the data dict
    req_fields = ['type', 'wrkt_dttm', 'dur_sec', 'dist_mi']
    for field in req_fields:
        if field not in data:
            return bad_request('must include ' + field + ' field')

    # Should I check if a request for specified workt_dttm already exists?
    # if User.query.filter_by(username=data['username']).first():
    #     return bad_request('please use a different email address')
    workout = Workout()
    workout.from_dict(data, current_user_id)
    db.session.add(workout)
    db.session.commit()
    response = jsonify(workout.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_workout', id=workout.id)
    return response

@bp.route('/workouts/<dttm>', methods=['GET'])
@token_auth.login_required
def get_workouts_by_dttm(dttm):
    logger.info('get_workouts_by_dttm')
    current_user_id = token_auth.current_user().id
    user = User.query.get_or_404(current_user_id)

    wrkt_dt = dt_conv.get_date(dttm)
    logger.info(str(wrkt_dt))
    #TODO covert dttm to datetime type. Try to allow for just date or full date/time being passed
    # Return an array of workouts, not sure how much of workout to return
    return jsonify([{'Status':'Success'}]), 200

@bp.route('/workout/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_workout(id):
    logger.info('update_workout')
    current_user_id = token_auth.current_user().id
    user = User.query.get_or_404(current_user_id)
    pass

# @bp.route('/users/<int:id>', methods=['PUT'])
# @token_auth.login_required
# def update_user(id):
#     if token_auth.current_user().id != id:
#         abort(403)
#     user = User.query.get_or_404(id)
#     data = request.get_json() or {}
#     if 'username' in data and data['username'] != user.username and \
#             User.query.filter_by(username=data['username']).first():
#         return bad_request('please use a different username')
#     if 'email' in data and data.filter_by(email=data['email']).first():
#         return bad_request('please use a different email address')
#     user.from_dict(data, new_user=False)
#     db.session.commit()
#     return jsonify(user.to_dict())
