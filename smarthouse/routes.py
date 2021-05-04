from flask import render_template, url_for, redirect, request, abort, flash, jsonify
from smarthouse.models import User, AnalyzerData, SmartplugData
from smarthouse.forms import LoginForm
from smarthouse import app, db, bcrypt, api
from flask_login import login_user, current_user, logout_user

@app.route('/')
def index():
    return render_template('index.html')

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
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# ANALYZER

class Analyzer():
    def __init__(self):
        if(AnalyzerData.query.first()):
            self.data = {} #jsonify(AnalyzerData.query.order_by(AnalyzerData.id.desc()).first())
        else:
            self.data = {}
        self.new_settings = {}
        self.current_settings = {}
    def set_data(self, data):
        self.data = data
    def set_new_settings(self, new_settings):
        self.new_settings = new_settings
    def set_current_settings(self, current_settings):
        self.current_settings = current_settings

analyzerData = Analyzer()

@app.route('/analyzer', methods=['POST', 'GET'])
def analyzer():
    data = analyzerData.data
    return render_template('analyzer.html', data=data)

@app.route('/analyzer/reboot')
def reboot_analyzer():
    if not current_user.is_authenticated:
        return redirect(url_for('analyzer'))
    Analyzer.new_settings = {'reboot': True}
    return redirect(url_for('analyzer'))