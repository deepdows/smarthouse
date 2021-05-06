from flask import render_template, url_for, redirect, request, abort, flash, jsonify
from smarthouse.models import User
from smarthouse.forms import LoginForm
from smarthouse import app, db, bcrypt
from flask_login import login_user, current_user, logout_user
from smarthouse import analyzer_routes, smartplug_routes

@app.route('/')
def index():
    return render_template('index.html', maps=['Home'])

@app.route('/login', methods=['POST','GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            return redirect(url_for('index'))
        else:
            flash('Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form, 
                                maps=[['Home', 'index'], 'Login'])

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))