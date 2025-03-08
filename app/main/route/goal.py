# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# First party classes
from datetime import datetime, timedelta, date, time

# Third party classes
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app, send_file, send_from_directory
from flask_login import current_user, login_required

# Custom classes
from app.main import bp
from app import logger
from app import db
from app.main.forms import GoalForm
from app.model.goals import Goal, Goal_type
from app.models import Workout_type

@bp.route('/edit_goal', methods=['GET','POST'])
@login_required
def edit_goal():
    usr_id = current_user.id
    goal_id = request.args.get('goal')
    logger.info('edit_goal: {}'.format(str(goal_id)))
    
    goal_form = GoalForm()
    label_val = 'Update Goal'
    
    wrkt_type_lst = sorted(Workout_type.query)
    wrkt_type_select_lst = [[-1, '──────────']]
    wrkt_type_dict = {}
    for g in wrkt_type_lst:
        if g.grp not in wrkt_type_dict:
            wrkt_type_dict[g.grp] = g.id
            wrkt_type_select_lst.append([g.id, g.grp])
    goal_form.workout_type_lst.choices = wrkt_type_select_lst

    goal_type_lst = sorted(Goal_type.query)
    goal_type_select_lst = []
    goal_type_dict = {}
    for g in goal_type_lst:
        goal_type_dict[g.nm] = g.id
        goal_type_select_lst.append([g.id, g.nm])
    goal_form.goal_type_lst.choices = goal_type_select_lst

    
    # gear_type_dict = current_app.config['GEAR_TYPE_MAP']
    # gear_type_select_lst = list(gear_type_dict.items())
    # gear_form.type.choices = gear_type_select_lst
    
    if request.method == 'GET':
        logger.info('edit_goal GET')
    elif request.method == 'POST' and goal_form.cancel.data:
        logger.info('edit_goal POST Cancel button pressed')
        return redirect(url_for('main.settings'))
    elif request.method == 'POST' and goal_form.delete.data:
        logger.info('edit_goal POST Delete button pressed')
        try:
            goal = Goal.query.filter_by(id=goal_id, user_id = usr_id).one()
        except:
            flash("Goal not found")
            return redirect(url_for('main.settings'))
        db.session.delete(goal)
        db.session.commit()
        flash("Goal deleted")
        return redirect(url_for('main.settings'))
    elif request.method == 'POST':
        if not goal_form.validate_on_submit():
            # if goal_id is not None:
                # gear_usage = Goal.query.filter_by(id=goal_id, user_id = usr_id).one()
                # gear_usage.tot_dur = gear_usage.tot_dur_str()
            # else:
                # gear_usage = None
            return render_template('edit_goal.html', destPage = 'settings', goal_form=goal_form, label_val=label_val)
    
        logger.info('edit_goal POST Submit button pressed')
        if goal_id is None:
            goal = Goal()
            goal.user_id = usr_id
        else:
            goal = Goal.query.filter_by(id=goal_id, user_id = usr_id).one()
        goal.description = goal_form.description.data
        goal.start_dt = goal_form.start_dt.data
        end_day_time = time(23, 59, 59)
        goal.end_dt = datetime.combine(goal_form.end_dt.data, end_day_time)
        goal.goal_total = goal_form.goal_total.data
        goal.goal_total = goal_form.goal_total.data
        goal.is_active = goal_form.is_active.data
        goal.ordr = goal_form.order.data
        
        # goal.workout_type_id = workout_type_dict[str(goal_form.type.data)]
        if goal_form.workout_type_lst.data == -1:
            goal.workout_type_id = None
        else:
            goal.workout_type_id = goal_form.workout_type_lst.data
        goal.goal_type_id = goal_form.goal_type_lst.data

        goal.updt_ts = datetime.utcnow()
        if goal_id is None:
            db.session.add(goal)
        db.session.commit()
        flash('Goal has been updated')
        return redirect(url_for('main.settings'))
    
    
    
    
    if goal_id is None:
        label_val = 'Create Goal'
        goal_form.is_active.data = True
        return render_template('edit_goal.html', destPage = 'settings', goal_form=goal_form, label_val=label_val)

    try:
        goal = Goal.query.filter_by(id=goal_id, user_id = usr_id).one()
    except Exception as e:
        flash("Goal not found")
        logger.error("ERROR: Goal not found for goal_id: {} for user: {}".format(goal_id, usr_id))
        logger.error(f"ERROR: {e}")
        return redirect(url_for('main.settings'))
    
    default_type = None
    for key, value in wrkt_type_dict.items():
        if value == goal.workout_type_id:
            default_type = value
            break
    goal_form.workout_type_lst.default = default_type if default_type != None else None
    
    default_type = None
    for key, value in goal_type_dict.items():
        if value == goal.goal_type_id:
            default_type = value
            break
    goal_form.goal_type_lst.default = default_type if default_type != None else None
    
    goal_form.process()
    goal_form.id.data = goal.id
    goal_form.description.data = goal.description
    goal_form.start_dt.data = goal.start_dt
    goal_form.end_dt.data = goal.end_dt
    goal_form.goal_total.data = goal.goal_total
    goal_form.is_active.data = goal.is_active
    goal_form.order.data = goal.ordr
    
    # logger.info(goal_form)
    
    return render_template('edit_goal.html', destPage = 'settings', goal_form=goal_form, label_val=label_val)
