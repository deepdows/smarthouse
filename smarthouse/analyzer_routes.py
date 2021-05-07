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
    def init(self):
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
        self.count = 0

    def set_data(self, data):
        self.data = data
    def set_new_settings(self, new_settings):
        self.new_settings = new_settings
    def set_current_settings(self, current_settings):
        self.current_settings = current_settings
    def set_time(self, time):
        global test_time1
        self.count += 1
        test_time1 = time
        self.time = time

test_time1 = 0
analyzer_data = Analyzer().init()

@app.route('/analyzer', methods=['POST', 'GET'])
def analyzer():
    if current_user.is_authenticated:
        if request.method == 'POST':
            new_settings = {}
            if request.form.get('brightness'):
                new_settings['brightness'] = request.form.get('brightness')
            else:
                if analyzer_data.new_settings.get('brightness'):
                    new_settings['brightness'] = analyzer_data\
                                                    .new_settings['brightness']
            if request.form.get('sync'):
                new_settings['sync'] = request.form.get('sync')
            else:
                if analyzer_data.new_settings.get('sync'):
                    new_settings['sync'] = analyzer_data.new_settings['sync']
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
    all_data_today = AnalyzerModel.query.filter(AnalyzerModel.date
                                    .between(date, one_day_ahead)).all()
    for data_today in all_data_today:
        data.append(getattr(data_today, name))
        time.append(data_today.date.strftime('%H:%M:%S'))
    return render_template('graph.html', name=name.capitalize(), data=data, 
                    time=time, title=f'Analyzer - {name.capitalize()}',
                    one_day_ahead=one_day_ahead.strftime('%Y%m%d'), 
                    one_day_ago=one_day_ago.strftime('%Y%m%d'),
                    one_day_ahead_dashed=one_day_ahead.strftime('%Y-%m-%d'), 
                    one_day_ago_dashed=one_day_ago.strftime('%Y-%m-%d'),
                    maps=[['Home', 'index'], ['Analyzer', 'analyzer'], 
                                    name + '/' + day.strftime('%Y-%m-%d')])
    


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

analyzer_get_new_settings = reqparse.RequestParser()
analyzer_get_new_settings.add_argument('api', type=str)


class AnalyzerGettingData(Resource):
    def get(self):
        d = analyzer_data.data
        d.update({'test': analyzer_data.time, 'test2': test_time1, 
                        'test3': analyzer_data.count})
        return jsonify(d)
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
            return '', 201
        return '', 404

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
        args = analyzer_get_new_settings.parse_args()
        if(args and 'api' in args and args['api'] == APPID):
            new_settings = analyzer_data.new_settings
            analyzer_data.set_new_settings({})
            return new_settings
        return '', 404

api.add_resource(AnalyzerGettingData, '/analyzer/data')
api.add_resource(AnalyzerCurrentSettings, '/analyzer/settings')
api.add_resource(AnalyzerStatus, '/analyzer/status')
api.add_resource(AnalyzerNewSettings, '/analyzer/new_settings')