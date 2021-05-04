from flask import render_template, url_for, redirect, request, abort, flash, jsonify
from smarthouse.models import User, AnalyzerData, SmartplugData
from smarthouse.forms import LoginForm
from smarthouse import app, db, bcrypt, api
from flask_login import login_user, current_user, logout_user
from flask_restful import Resource, reqparse, abort, fields
import datetime

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
            self.data = AnalyzerData.query.order_by(AnalyzerData.id.desc()).first().__dict__
            self.time = datetime.datetime.combine(self.data['date'], self.data['time'])
            del self.data['date']
            del self.data['_sa_instance_state']
            del self.data['time']
            del self.data['id']
        else:
            self.data = {}
            self.time = 0
        self.new_settings = {}
        self.current_settings = {}

    def set_data(self, data):
        self.data = data
    def set_new_settings(self, new_settings):
        self.new_settings = new_settings
    def set_current_settings(self, current_settings):
        self.current_settings = current_settings
    def set_time(self, time):
        self.time = time

analyzer_data = Analyzer()

@app.route('/analyzer', methods=['POST', 'GET'])
def analyzer():
    if current_user.is_authenticated:
        if request.method == 'POST':
            new_settings = {}
            if request.form.get('brightness'):
                new_settings['brightness'] = request.form.get('brightness')
            else:
                if analyzer_data.new_settings.get('brightness'):
                    new_settings['brightness'] = analyzer_data.new_settings['brightness']
            if request.form.get('sync'):
                new_settings['sync'] = request.form.get('sync')
            else:
                if analyzer_data.new_settings.get('sync'):
                    new_settings['sync'] = analyzer_data.new_settings['sync']
            print(new_settings)
            analyzer_data.set_new_settings(new_settings)
    data = analyzer_data.data
    return render_template('analyzer.html', data=data, 
                            is_online=is_online()['is_online'])

@app.route('/analyzer/reboot')
def reboot_analyzer():
    if not current_user.is_authenticated:
        return redirect(url_for('analyzer'))
    Analyzer.new_settings = {'reboot': True}
    return redirect(url_for('analyzer'))


# API ANALYZER

analyzer_get_data = reqparse.RequestParser()
analyzer_get_data.add_argument('temp', type=float)
analyzer_get_data.add_argument('hum', type=int)
analyzer_get_data.add_argument('pressure', type=float)
analyzer_get_data.add_argument('co2', type=int)
analyzer_get_data.add_argument('api', type=str)

analyzer_get_settings = reqparse.RequestParser()
analyzer_get_settings.add_argument('brightness', type=int)
analyzer_get_settings.add_argument('sync', type=int)

class AnalyzerGettingData(Resource):
    def get(self):
        return jsonify(analyzer_data.data)
    def post(self):
        args = analyzer_get_data.parse_args()
        if(args and 'api' in args and args['api'] == '1234321'):
            del args['api']
            analyzer_data_post = AnalyzerData(temperature=args['temp'], 
                               humidity=args['hum'], pressure=args['pressure'],
                               co2=args['co2'])
            db.session.add(analyzer_data_post)
            db.session.commit()
            analyzer_data.set_data({'temperature':args['temp'], 'humidity':args['hum'], 
                                    'pressure':args['pressure'], 'co2':args['co2']})
            analyzer_data.set_time(datetime.datetime.now())
            return '', 201

class AnalyzerCurrentSettings(Resource):
    def get(self):
        return jsonify(analyzer_data.current_settings)
    def post(self):
        args = analyzer_get_settings.parse_args()
        if(args and 'api' in args and args['api'] == '1234321'):
            analyzer_data.current_settings({'brightness':args['brightness'], 
                                                'sync':args['sync']})
            return '', 201

def is_online():
    if analyzer_data.time and ((datetime.datetime.now() - analyzer_data.time).total_seconds() < 10):
        return {'is_online': True}
    else:
        return {'is_online': False}

class AnalyzerStatus(Resource):
    def get(self):
        return is_online()

class AnalyzerNewSettings(Resource):
    def get(self):
        new_settings = analyzer_data.new_settings
        analyzer_data.set_new_settings({})
        return new_settings

api.add_resource(AnalyzerGettingData, '/analyzer/data')
api.add_resource(AnalyzerCurrentSettings, '/analyzer/settings')
api.add_resource(AnalyzerStatus, '/analyzer/status')
api.add_resource(AnalyzerNewSettings, '/analyzer/new_settings')