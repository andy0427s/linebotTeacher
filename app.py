from flask import Flask, render_template, url_for, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from sqlalchemy.orm import query

# main goal:
# provide a platform for teachers to interact with a SQL database containing student assignments
# allow teachers to give new assignments
#

app = Flask(__name__)


path_to_db = "/db/new.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite://{path_to_db}'
db = SQLAlchemy(app)


class Student(db.Model):
    __tablename__ = 'student'
    sId = db.Column(db.Integer, primary_key=True)
    sName = db.Column(db.String(20), nullable=False)
    lineId = db.Column(db.String(30), unique=True, nullable=False)

    def __repr__(self):
        return f'<Student ID: {self.sId}, Name: {self.sName}, LINE: {self.lineId}>'


class Homework(db.Model):
    __tablename__ = 'homework'
    aId = db.Column(db.Integer, nullable=False)
    lineId = db.Column(db.Integer, nullable=False)
    file = db.Column(db.String(50), primary_key=True)
    submit_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    # result from Azure
    label = db.Column(db.String(100))


class Assignment(db.Model):
    __tablename__ = 'assignment'
    aId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    prompt = db.Column(db.String(100))


@app.route('/')
def index():
    return render_template('index.html',
                           page_header="Home")


@app.route('/create')
def create():
    return render_template('create.html',
                           page_header="Create")


@app.route('/review')
def review():
    return render_template('review.html',
                           page_header="Review")


@app.route('/students')
def students():
    results = Student.query.all()
    # for i in results:
    #     print(i.sId, i.sName, i.lineId)
    return render_template('students.html',
                           page_header="Students",
                           data=results)

@app.route('/showtables')
# show all tables
def showTables():
    results = {}
    results['students'] =  Student.query.all()
    results['homeworks'] = Homework.query.all()
    results['assignments'] = Assignment.query.all()
    return render_template('showtables.html',
                           page_header="All tables",
                           data=results)

@app.route('/createall')
def newTables():
    db.create_all()
    return "created"

@app.route('/dropall')
def clearData():
    # this drops all tables (not just rows)
    db.drop_all()
    return "tables dropped"


@app.route('/adddata')
def addData():
    # create some dummy data
    s1 = Student(sId=1, sName="Bob", lineId="e109bs")
    s2 = Student(sId=2, sName="Alice", lineId="a983g")
    s3 = Student(sId=3, sName="Charlie", lineId="f027k")
    s4 = Student(sId=4, sName="Dylan", lineId="m410p")
    students = [s1, s2, s3, s4]
    db.session.add_all(students)
    a1 = Assignment(prompt="go to the store")
    h1 = Homework(aId=2, lineId='f027k', file="/uploaded/zzz.wav")
    entries = [a1, h1]
    db.session.add_all(entries)
    db.session.commit()
    return "added"



@app.route('/addstu')
def addStu():
    addStudent(22, "Eve", "o147v")
    return "added student!"

@app.route('/addhw')
def addHw():
    addHomework(22, "a983g", "/uploaded/sss.wav")
    return "added homework!"

@app.route('/addass')
def addAss():
    addAssignment("He went to Spain")
    return "added assignment!"

@app.route('/delstu')
def delStu():
    try:
        deleteStudent(2)
        return "deleted student"
    except:
        return "failed to delete"

@app.route('/delhw')
def delHw():
    try:
        deleteHomework("/uploaded/sss.wav")
        return "deleted homework"
    except:
        return "failed to delete"

@app.route('/delass')
def delAss():
    try:
        deleteAssignment(2)
        return "deleted assignment"
    except:
        return "failed to delete"

def addStudent(sId, sName, lineId):
    entry = Student(sId=sId, sName=sName, lineId=lineId)
    db.session.add(entry)
    db.session.commit()

def addHomework(aId, lineId, file):
    entry = Homework(aId=aId, lineId=lineId, file=file)
    db.session.add(entry)
    db.session.commit()

def addAssignment(prompt):
    entry = Assignment(prompt=prompt)
    db.session.add(entry)
    db.session.commit()

def deleteStudent(sId):
    query = Student.query.get(sId)
    db.session.delete(query)
    db.session.commit()

def deleteHomework(file):
    query = Homework.query.get(file)
    db.session.delete(query)
    db.session.commit()

def deleteAssignment(aId):
    query = Assignment.query.get(aId)
    db.session.delete(query)
    db.session.commit()

# if __name__ == "__main__":
#     app.run(debug=True)
