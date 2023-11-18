# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# First party classes

# Third party classes
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
# from werkzeug.urls import url_parse

# Custom classes
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User, Workout
from app import logger


@bp.route('/login', methods=['GET','POST'])
def login():
    # return render_template('auth/login.html', title='Sign In', form=form)
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        user = User.query.filter_by(email=email).first()
        # if user is None or not user.check_password(form.password.data):
        #     flash('Invalid email or password')
        #     return redirect(url_for('auth.login'))
        if user is None:
            flash('Invalid email or password')
            logger.info('Invalid username: {}'.format(email))
            return redirect(url_for('auth.login'))
        elif not user.check_account_status():
            flash('Account is locked')
            logger.info('Attempt login by locked account: {}'.format(email))
            return redirect(url_for('auth.login'))
        elif not user.check_password(form.password.data):
            flash('Invalid email or password')
            logger.info('Invalid password for: {}'.format(email))
            user.updt_acct_stat(False)
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        user.updt_acct_stat(True)
        next_page = request.args.get('next')
        # if not next_page or url_parse(next_page).netloc != '':
        #     next_page = url_for('main.index')
        if not next_page :
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

'''
@bp.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        user = User(displayname=form.displayname.data, email=email)
        user.set_password(form.password.data)
        # db.session.add(user)
        # db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)
'''
