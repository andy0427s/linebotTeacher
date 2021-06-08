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
    sid = db.Column(db.Integer, primary_key=True)
    sname = db.Column(db.String(20), nullable=False)
    lineid = db.Column(db.String(30), unique=True, nullable=False)


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


@app.route('/newTables')
def newTables():
    db.create_all()
    print("created Tables")
    return "created"


if __name__ == "__main__":
    app.run(debug=True)
