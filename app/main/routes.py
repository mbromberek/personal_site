# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# First party classes
from datetime import datetime
# from datetime import combine

# Third party classes
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required

# Custom classes
from app.main import bp
from app.main.forms import EmptyForm, WorkoutForm
from app.models import User, Workout
from app import db
from app.utils import tm_conv, const
from app import logger

@bp.route('/')
@bp.route('/index')
# @login_required
def index():
    logger.info('index')
    # user = {'displayname': 'Mike'}
    workouts = [{'type':'Running', 'duration':'20m 56s', 'distance': '3.11', 'pace': '6m 44s'}, {'type':'Running', 'duration':'3h 35m 53s', 'distance': '26.2', 'pace': '8m 13s'}]

    return render_template('index.html', title='Home Page', workouts=workouts)

@bp.route('/workouts', methods=['GET','POST'])
@login_required
def workouts():
    logger.info('workouts')
    form = EmptyForm()
    if form.validate_on_submit():
        return redirect(url_for('main.edit_workout'))

    form.submit.label.text = 'New Workout'

    page = request.args.get('page', 1, type=int)
    workoutPages = \
        Workout.query.filter_by(user_id=current_user.id).order_by(Workout.wrkt_dttm.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.workouts', page=workoutPages.next_num) \
        if workoutPages.has_next else None
    prev_url = url_for('main.workouts', page=workoutPages.prev_num) \
        if workoutPages.has_prev else None

    workouts = workoutPages.items
    for workout in workouts:
        workout.duration = workout.dur_str()
        workout.pace = workout.pace_str()
        if workout.notes != None:
            workout.notes_summary = workout.notes[:current_app.config['SIZE_NOTES_SUMMARY']] + '...' if len(workout.notes) > current_app.config['SIZE_NOTES_SUMMARY'] else workout.notes
        else:
            workout.notes_summary = ""
    return render_template('workouts.html', title='Workouts', workouts=workouts, form=form, next_url=next_url, prev_url=prev_url)

@bp.route('/edit_workout', methods=['GET','POST'])
@login_required
def edit_workout():
    logger.info('edit_workout')
    logger.info('wrkt: ' + str(request.args.get('workout')))
    form = WorkoutForm()
    title = 'Create Workout'
    if form.cancel.data:
        return redirect(url_for('main.workouts'))
    if form.validate_on_submit():
        if form.wrkt_id.data == "":
            logger.info('new workout')
            duration = tm_conv.time_to_sec(form.duration_h.data, form.duration_m.data, form.duration_s.data)
            wrkt_dttm = datetime.combine(form.wrkt_dt.data, form.wrkt_tm.data)
            wrkt = Workout(author=current_user, wrkt_dttm=wrkt_dttm)
        else:
            logger.info('update workout')
            usr_id = current_user.id
            wrkt_id = form.wrkt_id.data
            wrkt = Workout.query.filter_by(id=wrkt_id, user_id=usr_id).first_or_404(id)
        wrkt.dur_sec = tm_conv.time_to_sec(form.duration_h.data, form.duration_m.data, form.duration_s.data)
        wrkt.type = form.type.data
        wrkt.dist_mi = form.distance.data
        wrkt.notes = form.notes.data

        wrkt.gear = form.gear.data
        wrkt.clothes = form.clothes.data
        wrkt.ele_up = form.ele_up.data
        wrkt.ele_down = form.ele_down.data
        wrkt.hr = form.hr.data
        wrkt.cal_burn = form.cal_burn.data
        wrkt.category = form.category.data
        wrkt.location = form.location.data
        wrkt.training_type = form.training_type.data

        wrkt.temp_strt = form.temp_strt.data
        wrkt.temp_feels_like_strt = form.temp_feels_like_strt.data
        wrkt.wethr_cond_strt = form.wethr_cond_strt.data
        wrkt.hmdty_strt = form.hmdty_strt.data
        wrkt.wind_speed_strt = form.wind_speed_strt.data
        wrkt.wind_gust_strt = form.wind_gust_strt.data

        wrkt.temp_end = form.temp_end.data
        wrkt.temp_feels_like_end = form.temp_feels_like_end.data
        wrkt.wethr_cond_end = form.wethr_cond_end.data
        wrkt.hmdty_end = form.hmdty_end.data
        wrkt.wind_speed_end = form.wind_speed_end.data
        wrkt.wind_gust_end = form.wind_gust_end.data

        wrkt.warm_up_tot_tm_sec = tm_conv.time_to_sec(form.warm_up_dur_h.data, form.warm_up_dur_m.data, form.warm_up_dur_s.data)
        wrkt.warm_up_tot_dist_mi = form.warm_up_tot_dist.data

        wrkt.cool_down_tot_tm_sec = tm_conv.time_to_sec(        form.cool_down_dur_h.data, form.cool_down_dur_m.data, form.cool_down_dur_s.data)
        wrkt.cool_down_tot_dist_mi = form.cool_down_tot_dist.data

        wrkt.intrvl_tot_tm_sec = tm_conv.time_to_sec(form.intrvl_dur_h.data, form.intrvl_dur_m.data, form.intrvl_dur_s.data)
        wrkt.intrvl_tot_dist_mi = form.intrvl_tot_dist.data

        if form.wrkt_id.data == "":
            db.session.add(wrkt)
            db.session.commit()
            flash('Workout has been created!')
        else:
            db.session.commit()
            flash('Workout has been updated!')

        return redirect(url_for('main.workouts'))
    elif request.method == 'GET' and request.args.get('workout') != None:
        usr_id = current_user.id
        wrkt_id = request.args.get('workout')
        title = 'Update Workout'
        logger.info('Update Workout: ' + str(wrkt_id)+' for user: '+str(usr_id))
        wrkt = Workout.query.filter_by(id=wrkt_id, user_id=usr_id).first_or_404(id)
        form.type.data = wrkt.type
        form.wrkt_dt.data = wrkt.wrkt_dttm
        form.wrkt_tm.data = wrkt.wrkt_dttm
        form.duration_h.data, form.duration_m.data, form.duration_s.data = tm_conv.split_sec_to_time(wrkt.dur_sec)
        form.distance.data = wrkt.dist_mi
        form.notes.data = wrkt.notes
        form.wrkt_id.data = wrkt_id

        form.gear.data = wrkt.gear
        form.clothes.data = wrkt.clothes
        form.ele_up.data = wrkt.ele_up
        form.ele_down.data = wrkt.ele_down
        form.hr.data = wrkt.hr
        form.cal_burn.data = wrkt.cal_burn
        form.category.data = wrkt.category
        form.location.data = wrkt.location
        form.training_type.data = wrkt.training_type

        form.temp_strt.data = wrkt.temp_strt
        form.temp_feels_like_strt.data = wrkt.temp_feels_like_strt
        form.wethr_cond_strt.data = wrkt.wethr_cond_strt
        form.hmdty_strt.data = wrkt.hmdty_strt
        form.wind_speed_strt.data = wrkt.wind_speed_strt
        form.wind_gust_strt.data = wrkt.wind_gust_strt

        form.temp_end.data = wrkt.temp_end
        form.temp_feels_like_end.data = wrkt.temp_feels_like_end
        form.wethr_cond_end.data = wrkt.wethr_cond_end
        form.hmdty_end.data = wrkt.hmdty_end
        form.wind_speed_end.data = wrkt.wind_speed_end
        form.wind_gust_end.data = wrkt.wind_gust_end

        form.warm_up_dur_h.data, form.warm_up_dur_m.data, form.warm_up_dur_s.data = tm_conv.split_sec_to_time(wrkt.warm_up_tot_tm_sec)
        form.warm_up_tot_dist.data = wrkt.warm_up_tot_dist_mi

        form.cool_down_dur_h.data, form.cool_down_dur_m.data, form.cool_down_dur_s.data = tm_conv.split_sec_to_time(wrkt.cool_down_tot_tm_sec)
        form.cool_down_tot_dist.data = wrkt.cool_down_tot_dist_mi

        form.intrvl_dur_h.data, form.intrvl_dur_m.data, form.intrvl_dur_s.data = tm_conv.split_sec_to_time(wrkt.intrvl_tot_tm_sec)
        form.intrvl_tot_dist.data = wrkt.intrvl_tot_dist_mi

    return render_template('edit_workout.html', title=title, form=form)

@bp.route('/testing', methods=['GET','POST'])
def testing():
    logger.info('testing')
    title="Testing CSS Grid"
    return render_template('testing.html', title=title)
