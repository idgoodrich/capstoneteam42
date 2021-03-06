import email
from email.policy import default
from capstone import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(email):
    return accounts.query.get(email)


class accounts(db.Model, UserMixin):
    username = db.Column(db.String(20), unique=True, nullable = False)
    email = db.Column(db.String(100), unique=True, nullable = False, primary_key = True)
    acc_type = db.Column(db.String(10), nullable = False)
    password = db.Column(db.String(), nullable = True)
    approved = db.Column(db.Boolean(), nullable = False, default = False)

    def get_id(self):
       return (self.email)

    __table_args__ = {'extend_existing': True}

    def __repr__(self):
       return f"User('{self.username}', '{self.email}')"

class instructors(db.Model):
    LName = db.Column(db.String(20), unique=True, nullable = False, primary_key = True)
    MaxLoad = db.Column(db.Integer, nullable = False)
    Disciplines = db.Column(db.String(), nullable = False)
    Course_code_1 = db.Column(db.Integer, nullable = True)
    Course_code_2 = db.Column(db.Integer, nullable = True)
    Course_code_3 = db.Column(db.Integer, nullable = True)
    Course_code_4 = db.Column(db.Integer, nullable = True)
    Schedule_Day_1 = db.Column(db.String(30), nullable = True)
    Schedule_Day_2 = db.Column(db.String(30), nullable = True)
    Schedule_Day_3 = db.Column(db.String(30), nullable = True)
    Schedule_Day_4 = db.Column(db.String(30), nullable =True)
    Schedule_Day_5 = db.Column(db.String(30), nullable = True)
    CurrentLoad = db.Column(db.Integer, nullable = False, default=0)



class sections(db.Model):
    Code = db.Column(db.Integer, unique = True, nullable = False, primary_key = True)
    DepartmentCode = db.Column(db.String(4), nullable = False, default='CPSC')
    Day = db.Column(db.String(5), nullable = False, default = 'x')
    Length = db.Column(db.Integer, nullable = False, default = 0)
    StartTime = db.Column(db.Integer, nullable = False, default = 0)
    Disciplines = db.Column(db.String(), nullable = False, default = 'x')
    Periods = db.Column(db.Integer, nullable = False, default = 0)
    Name = db.Column(db.String(), nullable = False)
    instructor = db.Column(db.String(20))
    Time = db.Column(db.Integer, nullable = False, default = 0)

class output_schedule(db.Model):
    Code = db.Column(db.Integer, unique = True, nullable = False, primary_key = True)
    DepartmentCode = db.Column(db.String(4), nullable = False)
    Day = db.Column(db.String(5), nullable = False)
    Length = db.Column(db.Integer, nullable = False)
    StartTime = db.Column(db.Integer, nullable = False)
    Disciplines = db.Column(db.String(), nullable = False)
    Periods = db.Column(db.Integer, nullable = False)
    Name = db.Column(db.String(50), nullable = False)
    instructor = db.Column(db.String(20), nullable = False)
    valid = db.Column(db.Boolean, nullable = False)
 
