from flask import (render_template, url_for, redirect, request, 
                                abort, flash, jsonify)
from smarthouse.models import AnalyzerModel
from smarthouse import app, db, api
from flask_login import current_user
from flask_restful import Resource, reqparse
import datetime
import os

APPID = os.environ.get('APPID')

class Analyzer():
    def __init__(self):
        if(AnalyzerModel.query.first()):
            self.data = AnalyzerModel.query\
                            .order_by(AnalyzerModel.id.desc()).first().__dict__
            self.time = self.data['date']
            del self.data['date']
            del self.data['_sa_instance_state']
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
        print(time)

analyzer_data = Analyzer()

def add_new_setting_analyzer(name_of_arg):
    new_setting = {}
    if request.form.get(name_of_arg):
        new_settings[name_of_arg] = request.form.get(name_of_arg)
    else:
        if analyzer_data.new_settings.get(name_of_arg):
            new_settings[name_of_arg] = analyzer_data.new_settings[name_of_arg]
    return new_setting

@app.route('/analyzer', methods=['POST', 'GET'])
def analyzer():
    if current_user.is_authenticated:
        if request.method == 'POST':
            new_settings = {}
            new_settings.update(add_new_setting_analyzer('brightness'))
            new_settings.update(add_new_setting_analyzer('sync'))
            analyzer_data.set_new_settings(new_settings)
    data = analyzer_data.data
    return render_template('analyzer.html', data=data, title='Analyzer',
                        today=datetime.datetime.now().strftime('%Y%m%d'), 
                        is_online=is_online()['is_online'],
                        maps=[['Home', 'index'], 'Analyzer'])

@app.route('/analyzer/reboot')
def reboot_analyzer():
    if not current_user.is_authenticated:
        return redirect(url_for('analyzer'))
    analyzer_data.new_settings = {'reboot': True}
    return redirect(url_for('analyzer'))

avg = lambda l: sum(l)/ len(l)

def get_data_with_unique_time(time, data):
    if len(time) != len(data):
        error_message = f'Length of lists are different: {len(time)} != {len(data)}'
        raise Exception(error_message)
    indices = []
    set_of_time = []
    set_of_data = []
    for i in time:
        if i not in set_of_time:
            set_of_time.append(i)
    for i in set_of_time:
        indices.append(time.index(i))
    length = len(indices)
    for i in range(length):
        if(i == length - 1):
            set_of_data.append(avg(data[indices[i]:]))
        else:
            set_of_data.append(avg(data[indices[i]:indices[i+1]]))
            
    return [set_of_time, set_of_data]

@app.route('/analyzer/<string:name>/<string:day>')
def graph(name, day):
    if len(day) != 8:
        flash('Day format is not right')
        return redirect(url_for('analyzer'))
    day = datetime.datetime.strptime(day, '%Y%m%d').date()
    date = datetime.datetime.combine(day, datetime.time(0))
    one_day_ahead = date + datetime.timedelta(days=1)
    one_day_ago = date - datetime.timedelta(days=1)
    names = ['temperature', 'humidity', 'pressure', 'co2']
    if name not in names:
        flash(f'No graph for {name}', category='danger')
        return redirect(url_for('analyzer'))
    data, time = [], []
    all_data = AnalyzerModel.query.filter(AnalyzerModel.date
                                    .between(date, one_day_ahead)).all()
    for data in all_data:
        data.append(getattr(data, name))
        time.append(data.date.strftime('%H:%M'))
    time, data = get_data_with_unique_time(time, data)
    print(data)
    min_y=0
    if data:
        min_y = min(data)
    return render_template('graph.html', name=name.capitalize(), data=data, 
                time=time, title=f'Analyzer - {name.capitalize()}',
                one_day_ahead=one_day_ahead.strftime('%Y%m%d'), 
                one_day_ago=one_day_ago.strftime('%Y%m%d'), min_y=min_y,
                one_day_ahead_dashed=one_day_ahead.strftime('%Y-%m-%d'), 
                one_day_ago_dashed=one_day_ago.strftime('%Y-%m-%d'),
                maps=[['Home', 'index'], ['Analyzer', 'analyzer'], 
                                name + '/' + day.strftime('%Y-%m-%d')])
    
@app.route('/analyzer/status', methods=['POST', 'GET'])
def analyzer_status_api():
    if request.method == 'GET':
        return is_online()


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
analyzer_get_settings.add_argument('api', type=str)


class AnalyzerGettingData(Resource):
    def get(self):
        return jsonify(analyzer_data.data)
    def post(self):
        args = analyzer_get_data.parse_args()
        if(args and 'api' in args and args['api'] == APPID):
            del args['api']
            analyzer_data_post = AnalyzerModel(temperature=args['temp'], 
                                                humidity=args['hum'], 
                                                pressure=args['pressure'],
                                                co2=args['co2'])
            db.session.add(analyzer_data_post)
            db.session.commit()
            analyzer_data.set_data({'temperature':args['temp'], 
                                    'humidity':args['hum'], 
                                    'pressure':args['pressure'], 
                                    'co2':args['co2']})
            analyzer_data.set_time(datetime.datetime.now())
            print(datetime.datetime.now())
            return '', 201
        return 'apiid is absent or incorrect', 404

class AnalyzerCurrentSettings(Resource):
    def get(self):
        return jsonify(analyzer_data.current_settings)
    def post(self):
        args = analyzer_get_settings.parse_args()
        if(args and 'api' in args and args['api'] == APPID):
            analyzer_data.current_settings({'brightness':args['brightness'], 
                                                'sync':args['sync']})
            return '', 202
        return '', 404

def is_online():
    if analyzer_data.time and ((datetime.datetime.now() 
                                - analyzer_data.time).total_seconds() < 15):
        return {'is_online': True}
    else:
        return {'is_online': False}

class AnalyzerStatus(Resource):
    def get(self):
        return is_online()

class AnalyzerNewSettings(Resource):
    def get(self):
        args = analyzer_get_data.parse_args()
        if(args and 'api' in args and args['api'] == APPID):
            new_settings = analyzer_data.new_settings
            analyzer_data.set_new_settings({})
            return new_settings
        return '', 404

api.add_resource(AnalyzerGettingData, '/analyzer/data')
api.add_resource(AnalyzerCurrentSettings, '/analyzer/settings')
api.add_resource(AnalyzerStatus, '/analyzer/status')
api.add_resource(AnalyzerNewSettings, '/analyzer/new_settings')