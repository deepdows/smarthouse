from smarthouse import app
import os

os.environ['SECRET_KEY'] = '7e404faa12a7fdf4d526acc0578669b5'
os.environ['APPID'] = '86a3cd175_4d5a28eb3f'

if __name__ == '__main__':
    app.run(debug=True, host='192.168.0.104')