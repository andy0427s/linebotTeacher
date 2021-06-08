from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
# import os


app = Flask(__name__)

db = SQLAlchemy()


# prereqs:
# SQL database

# main goal:
# provide a platform for teachers to interact with a SQL database containing student assignments
# allow teachers to give new assignments
#

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


if __name__ == "__main__":
    app.run(debug=True)
