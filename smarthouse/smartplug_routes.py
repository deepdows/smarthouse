# from flask import (render_template, url_for, redirect, request, 
#                                 abort, flash, jsonify)
# from smarthouse.models import SmartplugModel
# from smarthouse import app, db, api
# from flask_login import current_user
# from flask_restful import Resource, reqparse
# import datetime
# import os

# APPID = os.environ.get('APPID')

# class Smartplug():
#     def __init__(self):
#         if(SmartplugModel.query.first()):
#             self.data = SmartplugModel.query\
#                             .order_by(SmartplugModel.id.desc()).first().__dict__
#             self.time = self.data['date']
#             del self.data['date']
#             del self.data['_sa_instance_state']
#             del self.data['id']
#         else:
#             self.data = {}
#             self.time = 0
#         self.new_settings = {}
#         self.current_settings = {}

#     def set_data(self, data):
#         self.data = data
#     def set_new_settings(self, new_settings):
#         self.new_settings = new_settings
#     def set_current_settings(self, current_settings):
#         self.current_settings = current_settings
#     def set_time(self, time):
#         self.time = time
#     def is_online(self):
#         if self.time and ((datetime.datetime.now() 
#                                     - self.time).total_seconds() < 15):
#             return {'is_online': True}
#         else:
#             return {'is_online': False}

# smartplug_data = Smartplug()

# def add_new_setting_smartplug(name_of_arg):
#     new_settings = {}
#     if request.form.get(name_of_arg):
#         new_settings[name_of_arg] = request.form.get(name_of_arg)
#         new_settings['new_'+name_of_arg] = True
#     else:
#         if smartplug_data.new_settings.get(name_of_arg):
#             new_settings[name_of_arg] = smartplug_data.new_settings[name_of_arg]
#             new_settings['new_'+name_of_arg] = True
#     return new_settings

# @app.route('/smartplug', methods=['POST', 'GET'])
# def smartplug():
#     if current_user.is_authenticated:
#         if request.method == 'POST':
#             new_settings = {}
#             new_settings.update(add_new_setting_smartplug('mode'))
#             new_settings.update(add_new_setting_smartplug('state'))
#             new_settings.update(add_new_setting_smartplug('time_on'))
#             new_settings.update(add_new_setting_smartplug('time_off'))
#             smartplug_data.set_new_settings(new_settings)
#     data = smartplug_data.data
#     return render_template('smartplug.html', data=data, title='Smartplug',
#                         today=datetime.datetime.now().strftime('%Y%m%d'), 
#                         is_online=smartplug_data.is_online()['is_online'],
#                         maps=[['Home', 'index'], 'Smartplug'])

# @app.route('/smartplug/reboot')
# def reboot_smartplug():
#     if not current_user.is_authenticated:
#         return redirect(url_for('smartplug'))
#     smartplug_data.new_settings = {'reboot': True}
#     return redirect(url_for('smartplug'))

# avg = lambda l: round(sum(l)/len(l),2)

# def get_data_with_unique_time(time, data):
#     if len(time) != len(data):
#         error_message = f'Length of lists are different: {len(time)} != {len(data)}'
#         raise Exception(error_message)
#     indices = []
#     set_of_time = []
#     set_of_data = []
#     for i in time:
#         if i not in set_of_time:
#             set_of_time.append(i)
#     for i in set_of_time:
#         indices.append(time.index(i))
#     length = len(indices)
#     for i in range(length):
#         if(i == length - 1):
#             set_of_data.append(avg(data[indices[i]:]))
#         else:
#             set_of_data.append(avg(data[indices[i]:indices[i+1]]))
            
#     return [set_of_time, set_of_data]

# @app.route('/smartplug/<string:name>/<string:day>')
# def graph(name, day):
#     if len(day) != 8:
#         flash('Day format is not right')
#         return redirect(url_for('smartplug'))
#     day = datetime.datetime.strptime(day, '%Y%m%d').date()
#     date = datetime.datetime.combine(day, datetime.time(0))
#     one_day_ahead = date + datetime.timedelta(days=1)
#     one_day_ago = date - datetime.timedelta(days=1)
#     if name != 'current':
#         flash(f'No graph for {name}', category='danger')
#         return redirect(url_for('smartplug'))
#     data, time = [], []
#     all_data = SmartplugModel.query.filter(SmartplugModel.date
#                                     .between(date, one_day_ahead)).all()
#     for single_data in all_data:
#         data.append(getattr(single_data, name))
#         time.append(single_data.date.strftime('%H:%M'))
#     time, data = get_data_with_unique_time(time, data)
#     print(data)
#     min_y=0
#     if data:
#         min_y = min(data)
#     return render_template('graph.html', name=name.capitalize(), 
#                 name_lower=name, data=data, 
#                 time=time, title=f'Smartplug - {name.capitalize()}',
#                 one_day_ahead=one_day_ahead.strftime('%Y%m%d'), 
#                 one_day_ago=one_day_ago.strftime('%Y%m%d'), min_y=min_y-0.5,
#                 one_day_ahead_dashed=one_day_ahead.strftime('%Y-%m-%d'), 
#                 one_day_ago_dashed=one_day_ago.strftime('%Y-%m-%d'),
#                 maps=[['Home', 'index'], ['Smartplug', 'smartplug'], 
#                                 name + '/' + day.strftime('%Y-%m-%d')])

# # API SMARTPLUG

# smartplug_get_data = reqparse.RequestParser()
# smartplug_get_data.add_argument('current', type=float)
# smartplug_get_data.add_argument('api', type=str)

# smartplug_get_settings = reqparse.RequestParser()
# smartplug_get_settings.add_argument('mode', type=bool)
# smartplug_get_settings.add_argument('state', type=bool)
# smartplug_get_settings.add_argument('time_on', type=str)
# smartplug_get_settings.add_argument('time_off', type=str)
# smartplug_get_settings.add_argument('api', type=str)


# class SmartplugGettingData(Resource):
#     def get(self):
#         return jsonify(smartplug_data.data)
#     def post(self):
#         args = smartplug_get_data.parse_args()
#         if(args and 'api' in args and args['api'] == APPID):
#             del args['api']
#             smartplug_data_post = SmartplugModel(current=args['current'])
#             db.session.add(smartplug_data_post)
#             db.session.commit()
#             smartplug_data.set_data({'current':args['current']})
#             smartplug_data.set_time(datetime.datetime.now())
#             print(datetime.datetime.now())
#             return '', 201
#         return 'apiid is absent or incorrect', 404

# class SmartplugCurrentSettings(Resource):
#     def get(self):
#         return jsonify(smartplug_data.current_settings)
#     def post(self):
#         args = smartplug_get_settings.parse_args()
#         if(args and 'api' in args and args['api'] == APPID):
#             smartplug_data.set_current_settings({'state':args['state'], 
#                                                 'mode':args['mode'],
#                                                 'time_on':args['time_on'],
#                                                 'time_off':args['time_off']})
#             return '', 202
#         return '', 404

# class SmartplugStatus(Resource):
#     def get(self):
#         return smartplug_data.is_online()

# class SmartplugNewSettings(Resource):
#     def post(self):
#         args = smartplug_get_settings.parse_args()
#         if(args and 'api' in args and args['api'] == APPID):
#             new_settings = smartplug_data.new_settings
#             smartplug_data.set_new_settings({})
#             print(new_settings)
#             return jsonify(new_settings)
#         return '', 404
        

# api.add_resource(SmartplugGettingData, '/smartplug/data')
# api.add_resource(SmartplugCurrentSettings, '/smartplug/settings')
# api.add_resource(SmartplugStatus, '/smartplug/status')
# api.add_resource(SmartplugNewSettings, '/smartplug/new_settings')