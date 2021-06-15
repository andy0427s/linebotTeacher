from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# main goal:
# provide a platform for teachers to interact with a SQL database containing student assignments
# allow teachers to give new assignments
#

# Todo:
# move functions to separate file?
# timezone setting
# review homework (/all and by /student/id)

# Linebot:
# name registration

app = Flask(__name__)
app.secret_key = 'secretkeyzzz'


# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# path_to_db = "/db/new.db"
# app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite://{path_to_db}'
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://jymwsjbzlanqbt:bdf219a8a2653c2d6c6e226c90071b4b0093960241e4f8a60f63c170732a517c@ec2-54-243-92-68.compute-1.amazonaws.com:5432/d9f853hbcsdg12'
# Use upper one for development, lower one for deployment, By Johnson
db = SQLAlchemy(app)


class Student(db.Model):
    __tablename__ = 'student'
    sId = db.Column(db.Integer, primary_key=True)
    sName = db.Column(db.String(20), nullable=False)
    lineId = db.Column(db.String(30), unique=True, nullable=False)

    def __repr__(self):
        return f'[Student ID: {self.sId}, Name: {self.sName}, LINE: {self.lineId}]'


class Homework(db.Model):
    __tablename__ = 'homework'
    aId = db.Column(db.Integer, nullable=False)
    lineId = db.Column(db.String, nullable=False)
    file = db.Column(db.String(50), primary_key=True)
    submit_time = db.Column(db.DateTime, nullable=False,
                            default=datetime.now().replace(microsecond=0))
    # result from Azure
    label = db.Column(db.String(100))

    def __repr__(self):
        return f'[Assignment ID: {self.aId}, LINE: {self.lineId}, File: {self.file}, Submit Time: {self.submit_time}, label: {self.label}]'


class Assignment(db.Model):
    __tablename__ = 'assignment'
    aId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    prompt = db.Column(db.String(100))

    def __repr__(self):
        return f'[Assignment ID: {self.aId}, Prompt: {self.prompt}]'


@app.route('/')
def index():
    return render_template('index.html',
                           page_header="Home")


@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.form:
        tab_type = request.form['table']
        if tab_type == "students":
            sId = request.form['s-sId']
            sName = request.form['s-sName']
            lineId = request.form['s-lineId']
            message = addStudent(sId, sName, lineId)
        elif tab_type == "homeworks":
            aId = request.form['h-aId']
            lineId = request.form['h-lineId']
            file = request.form['h-file']
            label = request.form['h-label']
            message = addHomework(aId, lineId, file, label)
        elif tab_type == "assignments":
            prompt = request.form['a-prompt']
            message = addAssignment(prompt)
        flash(message)
    return render_template('create.html',
                           page_header="Add Data to Table")


@app.route('/remove-and-edit', methods=['GET', 'POST'])
def remove_edit():
    if request.method == "GET":
        results = {}
        results['students'] = Student.query.all()
        results['homeworks'] = Homework.query.all()
        results['assignments'] = Assignment.query.all()
        return render_template('remove-and-edit.html',
                               page_header="Remove or Edit Rows",
                               data=results)
    if request.method == "POST":
        edit_type = request.form['type']
        if edit_type == "student":
            edit_id = request.form['s-sId']
            query = Student.query.get(edit_id)
        elif edit_type == "homework":
            edit_id = request.form['h-file']
            query = Homework.query.get(edit_id)
        elif edit_type == "assignment":
            edit_id = request.form['a-aId']
            query = Assignment.query.get(edit_id)
        print(query)
        return render_template('edit-entry.html',
                               page_header=f"Edit {edit_type.capitalize()} Entry",
                               data_type=edit_type,
                               data=query)


@app.route('/remove', methods=['POST'])
def remove():
    if request.form:
        remove_type = request.form['type']
        if remove_type == "student":
            message = deleteStudent(request.form['s-sId'])
        elif remove_type == "homework":
            message = deleteHomework(request.form['h-file'])
        elif remove_type == "assignment":
            message = deleteAssignment(request.form['a-aId'])
    flash(message)
    return redirect(url_for('remove_edit'))


@app.route('/edit', methods=["POST"])
def edit():
    edit_type = request.form['type']
    if edit_type == "student":
        sId = request.form['s-sId']
        newId = request.form['new-sId']
        newName = request.form['new-sName']
        newLineId = request.form['new-lineId']
        message = updateStudent(sId, newId=newId, newName=newName,
                                newLineId=newLineId)
    elif edit_type == "homework":
        file = request.form['h-file']
        newaId = request.form['new-aId']
        newLineId = request.form['new-lineId']
        newFile = request.form['new-file']
        newLabel = request.form['new-label']
        message = updateHomework(
            file, newaId=newaId, newLineId=newLineId, newFile=newFile, newLabel=newLabel)
    elif edit_type == "assignment":
        aId = request.form['a-aId']
        newId = request.form['new-aId']
        newPrompt = request.form['new-prompt']
        message = updateAssignment(aId, newId=newId, newPrompt=newPrompt)
    else:
        message = "Something went wrong"
    flash(message)
    return redirect(url_for('remove_edit'))


@app.route('/review')
def review():
    return redirect(url_for('review_all'))


@app.route('/review/all')
def review_all():
    # query = db.session.query(Homework, Student).join(
    #     Student, Homework.lineId == Student.lineId)
    query = db.session.query(Homework, Student, Assignment).join(
        Student, Homework.lineId == Student.lineId).join(Assignment, Homework.aId == Assignment.aId)
    return render_template('review.html',
                           page_header="Review",
                           data=query)


@app.route('/showtables')
# show all tables
def showTables():
    results = {}
    results['students'] = Student.query.all()
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


@app.route('/reset')
def reset():
    db.drop_all()
    db.create_all()
    s1 = Student(sId=1, sName="Bob", lineId="e109bs")
    s2 = Student(sId=2, sName="Alice", lineId="a983g")
    s3 = Student(sId=3, sName="Charlie", lineId="f027k")
    s4 = Student(sId=4, sName="Dylan", lineId="m410p")
    a1 = Assignment(prompt="You should go to the store")
    a2 = Assignment(prompt="He finished his breakfast early")
    a3 = Assignment(prompt="The flowers bloomed early this year")
    h1 = Homework(aId=2, lineId='f027k', file="/uploaded/h1.wav")
    h2 = Homework(aId=1, lineId='f027k', file="/uploaded/h2.wav")
    h3 = Homework(aId=2, lineId='m410p', file="/uploaded/h3.wav")
    h4 = Homework(aId=3, lineId='f027k', file="/uploaded/h4.wav")
    h5 = Homework(aId=3, lineId='e109bs', file="/uploaded/h5.wav")
    entries = [s1, s2, s3, s4, a1, a2, a3, h1, h2, h3, h4, h5]
    db.session.add_all(entries)
    db.session.commit()
    return redirect('/showtables')


def addStudent(sId, sName, lineId):
    entry = Student(sId=sId, sName=sName, lineId=lineId)
    try:
        db.session.add(entry)
        db.session.commit()
        return f"added student {entry}!"
    except:
        db.session.rollback()
        return f"failed to add student {entry}"


def addHomework(aId, lineId, file, label=None):
    entry = Homework(aId=aId, lineId=lineId, file=file, label=label)
    try:
        db.session.add(entry)
        db.session.commit()
        return f"added homework {entry}!"
    except:
        db.session.rollback()
        return f"failed to add homework {entry}"


def addAssignment(prompt):
    # this shouldn't ever error so no need to try/except
    entry = Assignment(prompt=prompt)
    db.session.add(entry)
    db.session.commit()
    return f"added assignment {entry}!"


def deleteStudent(sId):
    query = Student.query.get(sId)
    try:
        db.session.delete(query)
        db.session.commit()
        return f"deleted student {query}"
    except:
        db.session.rollback()
        return f"failed to delete student {sId}"


def deleteHomework(file):
    query = Homework.query.get(file)
    try:
        db.session.delete(query)
        db.session.commit()
        return f"deleted homework {query}"
    except:
        db.session.rollback()
        return f"failed to delete homework {file}"


def deleteAssignment(aId):
    query = Assignment.query.get(aId)
    try:
        db.session.delete(query)
        db.session.commit()
        return f"deleted assignment {query}"
    except:
        db.session.rollback()
        return f"failed to delete assignment {aId}"


def updateStudent(sId, newId=None, newName=None, newLineId=None):
    query = Student.query.get(sId)
    olddata = query.__repr__()
    if query:
        if newId:
            query.sId = newId
        if newName:
            query.sName = newName
        if newLineId:
            query.lineId = newLineId
        try:
            db.session.commit()
            newdata = query.__repr__()
            return f"updated {newdata}!"
        except:
            db.session.rollback()
            return f"failed to update {olddata}"
    else:
        return f"failed to find student {sId}"


def updateHomework(file, newaId=None, newLineId=None, newFile=None, newLabel=None):
    query = Homework.query.get(file)
    olddata = query.__repr__()
    if query:
        if newaId:
            query.aId = newaId
        if newLineId:
            query.lineId = newLineId
        if newFile:
            query.file = newFile
        if newLabel:
            query.label = newLabel
        try:
            db.session.commit()
            newdata = query.__repr__()
            return f"updated {newdata}!"
        except:
            db.session.rollback()
            return f"failed to update {olddata}"
    else:
        return f"failed to find homework {file}"


def updateAssignment(aId, newId=None, newPrompt=None):
    query = Assignment.query.get(aId)
    olddata = query.__repr__()
    if query:
        if newId:
            query.aId = newId
        if newPrompt:
            query.prompt = newPrompt
            print(newPrompt)
        try:
            db.session.commit()
            newdata = query.__repr__()
            return f"updated {newdata}!"
        except:
            db.session.rollback()
            return f"failed to update {olddata}"
    else:
        return f"failed to find assignment {aId}"


if __name__ == "__main__":
    app.run(debug=True)
