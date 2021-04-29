from flask import Flask, jsonify, render_template, request
#from random import randint

app = Flask(__name__)

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

bootstrap = Bootstrap(app)

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

if __name__ == '__main__':
    app.run(debug=True)