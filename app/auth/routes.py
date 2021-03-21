# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# First party classes

# Third party classes
from flask import render_template, redirect, url_for, flash, request

# Custom classes
from app.auth import bp
from app.auth.forms import LoginForm


@bp.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    return render_template('auth/login.html', title='Sign In', form=form)
    # if current_user.is_authenticated:
    #     return flask.redirect(flask.url_for('main.index'))
    # form = LoginForm()
    # if form.validate_on_submit():
    #     user = User.query.filter_by(username=form.username.data).first()
    #     if user is None or not user.check_password(form.password.data):
    #         flask.flash(_('Invalid username or password'))
    #         return flask.redirect(flask.url_for('auth.login'))
    #     login_user(user, remember=form.remember_me.data)
    #     next_page = request.args.get('next')
    #     if not next_page or url_parse(next_page).netloc != '':
    #         next_page = flask.url_for('main.index')
    #     return flask.redirect(next_page)
    # return flask.render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return flask.redirect(flask.url_for('main.index'))
