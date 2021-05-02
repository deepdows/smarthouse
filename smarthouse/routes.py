from flask import render_template, url_for, redirect, request, abort, flash
from smarthouse.models import User, AnalyzerData, SmartplugData
from smarthouse.forms import LoginForm
from smarthouse import app, db, bcrypt, api
from flask_login import login_user, current_user, logout_user, login_required
from flask_restful import Resource, reqparse, abort, fields

# settings = None

# @app.route('/data', methods=['GET','POST'])
# def get_data():
#     data = None
#     if request.method == 'POST':
#         global settings
#         data = request.get_json()
#         if data and 'api' in data and data['api'] == '1234321':
#             print(data)
#             return jsonify(settings)
#         return ('', 204)
#     if request.method == 'GET':
#         print(data)
#         return jsonify(data)

# @app.route('/settings', methods=['POST'])
# def upload_settings():
#     global settings
    
#     data = request.args
#     if data:
#         settings = data['brightness']
#         return ('Success')

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

@app.route('/analyzer', methods=['POST', 'GET'])
def analyzer():
    data = AnalyzerData.query.order_by(AnalyzerData.id.desc()).first()
    data = {
        'temp': data.temperature,
        'hum': data.humidity,
        'pressure': data.pressure,
        'co2': data.co2
    }
    return render_template('analyzer.html', data=data, sync=34, brightness=2)

@app.route('/analyzer/reboot')
def reboot_analyzer():
    return redirect(url_for('analyzer'))

# API SECTION

analyzer_data = reqparse.RequestParser()
analyzer_data.add_argument('temp', type=float)
analyzer_data.add_argument('hum', type=int)
analyzer_data.add_argument('pressure', type=float)
analyzer_data.add_argument('co2', type=int)
analyzer_data.add_argument('api', type=str)


class AnalyzerGettingData(Resource):
    def get(self):
        new_data = AnalyzerData.query.order_by(AnalyzerData.id.desc()).first()
        data = {
            'temp': str(new_data.temperature),
            'hum': str(new_data.humidity),
            'pressure': str(new_data.pressure),
            'co2': str(new_data.co2)
        }
        return data
    def post(self):
        args = analyzer_data.parse_args()
        if(args and 'api' in args and args['api'] == '1234321'):
            del args['api']
            analyzer_data_post = AnalyzerData(temperature=args['temp'], 
                               humidity=args['hum'], pressure=args['pressure'],
                               co2=args['co2'])
            db.session.add(analyzer_data_post)
            db.session.commit()
            return '', 201

class AnalyzerSendingSettings(Resource):
    def get(self):
        pass
    def post(self):
        pass

api.add_resource(AnalyzerGettingData, '/analyzer/data')
api.add_resource(AnalyzerSendingSettings, '/analyzer/settings')