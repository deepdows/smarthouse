from smarthouse import app
import os

os.environ['SECRET_KEY'] = '7e404faa12a7fdf4d526acc0578669b5'

if __name__ == '__main__':
    app.run(debug=True)