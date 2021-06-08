from enum import unique
from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


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
    sId = db.Column(db.Integer, nullable=False)
    file = db.Column(db.String(50), primary_key=True)
    submit_time = db.Column(db.DateTime, nullable=False, default=datetime.now)


class Assignment(db.Model):
    __tablename__ = 'assignment'
    aId = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.String(80))


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


@app.route('/newTables')
def newTables():
    db.create_all()
    print("created Tables")
    return "created"


@app.route('/adddata')
def addData():
    # create some dummy data
    s1 = Student(sId=1, sName="Bob", lineId="e109bs")
    s2 = Student(sId=2, sName="Alice", lineId="a983g")
    s3 = Student(sId=3, sName="Charlie", lineId="f027k")
    s4 = Student(sId=4, sName="Dylan", lineId="m410p")
    students = [s1, s2, s3, s4]
    db.session.add_all(students)
    a1 = Assignment(aId=2, prompt="go to the store")
    h1 = Homework(aId=2, sId=25, file="/uploaded/zzz.wav")
    entries = [a1, h1]
    db.session.add_all(entries)
    db.session.commit()
    return "added"


@app.route('/clear')
def clearData():
    # for troubleshooting - this clears all data!
    db.session.query(Student).delete()
    db.session.query(Homework).delete()
    db.session.query(Assignment).delete()
    db.session.commit()

    return "tables cleared"


if __name__ == "__main__":
    app.run(debug=True)
