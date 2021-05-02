import datetime
from smarthouse import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.id}', '{self.username}')"

class AnalyzerData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Integer, nullable=False)
    pressure = db.Column(db.Float, nullable=False)
    co2 = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False, 
                    default=datetime.date.today)
    time = db.Column(db.Time, nullable=False, 
                    default=datetime.datetime.now().time())

    def __repr__(self):
        return (f"User('{self.temperature}', '{self.humidity}'," 
            + f"'{self.pressure}, '{self.co2}', '{self.date}', '{self.time}')")

class SmartplugData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    current = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, 
                    default=datetime.date.today)
    time = db.Column(db.Time, nullable=False, 
                    default=datetime.datetime.now().time())

    def __repr__(self):
        return f"User('{self.current}', '{self.date}', '{self.time}')"