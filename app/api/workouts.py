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

@bp.route('/workouts/<dttm_str>', methods=['GET'])
@token_auth.login_required
def get_workouts_by_dt(dttm_str):
    '''
    Get list of workouts for the passed in date
    '''
    logger.info('get_workouts_by_dttm')
    current_user_id = token_auth.current_user().id

    dttm = dt_conv.get_date(dttm_str)
    logger.info("Get workout for User: " + str(current_user_id) + " for date: " + str(dttm))

    wrkt_lst = Workout.query.filter_by(user_id=current_user_id, wrkt_dttm=dttm)
    wrkt_dict_lst = []
    for wrkt in wrkt_lst:
        wrkt_dict_lst.append(wrkt.to_dict())

    if len(wrkt_dict_lst) >0:
        return jsonify(wrkt_dict_lst), 200
    else:
        return jsonify("No records found"), 400

@bp.route('/workout', methods=['PUT'])
@token_auth.login_required
def update_workout():
    '''
    Passed workout needs to contain the below required fields. All other fields are optional and if not passed will use existing value.
    '''
    logger.info('update_workout')
    current_user_id = token_auth.current_user().id
    data = request.get_json() or {}
    req_fields = ['id','type', 'wrkt_dttm', 'dur_sec', 'dist_mi']
    for field in req_fields:
        if field not in data:
            return bad_request('must include ' + field + ' field')
    wrkt_id = data['id']
    passed_workout = Workout()
    passed_workout.from_dict(data, current_user_id)
    passed_workout.id = wrkt_id
    logger.info('passed wrkt_id:' + str(wrkt_id))
    orig_workout = Workout.query.filter_by(id=wrkt_id, user_id=current_user_id).first_or_404(wrkt_id)
    logger.info(orig_workout)
    orig_workout.update(passed_workout)
    logger.info(passed_workout)
    logger.info(orig_workout)

    db.session.commit()
    response = jsonify(orig_workout.to_dict())
    response.status_code = 200
    response.headers['Location'] = url_for('api.get_workout', id=orig_workout.id)
    return response
