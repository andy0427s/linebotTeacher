from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import os

# main goal:
# provide a platform for teachers to interact with a SQL database containing student assignments
# allow teachers to give new assignments
#

# Todo:
# clean up readme
# move functions to separate file?
# review homework (by /student/id)
# notifs for students without LINE and homework without students
# teacher example uploading?

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
    sName = db.Column(db.String(50), nullable=False)
    lineId = db.Column(db.String(100), unique=True)

    def __repr__(self):
        return f'[Student ID: {self.sId}, Name: {self.sName}, LINE: {self.lineId}]'


class Homework(db.Model):
    __tablename__ = 'homework'
    aId = db.Column(db.Integer, nullable=False)
    lineId = db.Column(db.String(100), nullable=False)
    file = db.Column(db.String(100), primary_key=True)
    submit_time = db.Column(db.DateTime(timezone=True),
                            server_default=func.now())
    label = db.Column(db.String(100))  # result from Azure

    def __repr__(self):
        return f'[Assignment ID: {self.aId}, LINE: {self.lineId}, File: {self.file}, Submit Time: {self.submit_time}, label: {self.label}]'


class Assignment(db.Model):
    __tablename__ = 'assignment'
    aId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    prompt = db.Column(db.String(100))
    example = db.Column(db.String(100))  # AWS link to sample

    def __repr__(self):
        return f'[Assignment ID: {self.aId}, Prompt: {self.prompt}, Example: {self.example}]'


class userVariables(db.Model):
    __tablename__ = 'variables'
    lineId = db.Column(db.String(100), primary_key=True)
    selectedAssignment = db.Column(db.Integer)
    azureText = db.Column(db.String(100))
    latestScore = db.Column(db.String(100))

    def __repr__(self):
        return f'[line ID: {self.lineId}, Assignment ID: {self.selectedAssignment}, text: {self.azureText}, latest score: {self.latestScore}]'


@app.route('/')
def index():
    return render_template('index.html',
                           page_header="Welcome to AI Academy!")


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
            example = request.form['a-example']
            message = addAssignment(prompt, example)
        flash(message)
    return render_template('create.html',
                           page_header="Add Data to Table")


@app.route('/remove-and-edit', methods=['GET', 'POST'])
def remove_edit():
    if request.method == "GET":
        results = {}
        results['students'] = Student.query.order_by(Student.sId).all()
        results['homeworks'] = Homework.query.order_by(
            Homework.submit_time.desc()).all()
        results['assignments'] = Assignment.query.order_by(
            Assignment.aId).all()
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
        if newLineId in ["", "None", None]:
            newLineId = None
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
        newExample = request.form['new-example']
        message = updateAssignment(
            aId, newId=newId, newPrompt=newPrompt, newExample=newExample)
    else:
        message = "Something went wrong"
    flash(message)
    return redirect(url_for('remove_edit'))


@app.route('/review')
def review():
    return redirect(url_for('review_all'))


@app.route('/review/all')
def review_all():
    query = db.session.query(Homework, Student, Assignment).join(
        Student, Homework.lineId == Student.lineId, isouter=True).join(Assignment, Homework.aId == Assignment.aId, isouter=True).order_by(Homework.submit_time.desc())
    return render_template('review.html',
                           page_header="Review",
                           data=query)


@app.route('/showtables')
# show all tables
def showTables():
    results = {}
    results['students'] = Student.query.order_by(Student.sId).all()
    results['homeworks'] = Homework.query.order_by(
        Homework.submit_time.desc()).all()
    results['assignments'] = Assignment.query.order_by(Assignment.aId).all()
    return render_template('showtables.html',
                           page_header="All tables",
                           data=results)


@app.route('/clear')
def clear():
    db.drop_all()
    db.create_all()
    return redirect('/showtables')


@app.route('/reset')
def reset():
    db.drop_all()
    db.create_all()
    s1 = Student(sId=1, sName="Test", lineId="e109bs")
    s2 = Student(sId=2, sName="Clark")
    s3 = Student(sId=3, sName="Leo")
    s4 = Student(sId=4, sName="Andy")
    s5 = Student(sId=5, sName="YunShan")
    s6 = Student(sId=6, sName="Johnson")
    s7 = Student(sId=7, sName="DemoStudent1")
    s8 = Student(sId=8, sName="DemoStudent2")
    s9 = Student(sId=9, sName="DemoStudent3")
    a1 = Assignment(prompt="You should go to the store",
                    example="https://engscoreaud.s3.amazonaws.com/sample1.mp3")
    a2 = Assignment(prompt="He finished his breakfast early",
                    example="https://engscoreaud.s3.amazonaws.com/sample2.mp3")
    a3 = Assignment(prompt="The flowers bloomed early this year",
                    example="https://engscoreaud.s3.amazonaws.com/sample3.mp3")
    a4 = Assignment(prompt="Don't eat Don's donuts")
    a5 = Assignment(prompt="You can never have too much bread")
    h1 = Homework(aId=1, lineId='e109bs', file="/static/uploaded/test.mp3")
    entries = [s1, s2, s3, s4, s5, s6, s7, s8, s9, a1, a2, a3, a4, a5, h1]
    db.session.add_all(entries)
    db.session.commit()
    return redirect('/showtables')


@app.route('/secret')
def secret():
    query = userVariables.query.all()
    result = ""
    for entry in query:
        result = result+f"<p>{str(entry)}</p>"
    return result


def addStudent(sId, sName, lineId):
    if lineId in ["", "None", None]:
        newlineId = None
    entry = Student(sId=sId, sName=sName, lineId=newlineId)
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


def addAssignment(prompt, example=None):
    # this shouldn't ever error so no need to try/except
    entry = Assignment(prompt=prompt, example=example)
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
        if newLineId in ["", "None", None]:
            query.lineId = None
        try:
            db.session.commit()
            newdata = query.__repr__()
            return f"updated {newdata}!"
        except:
            db.session.rollback()
            return f"failed to update {olddata}"
    else:
        return f"failed to find student {sId}"


def registerStudent(sId, newLineId=None):
    # for students to update info through LINE
    checkExisting = Student.query.filter_by(lineId=newLineId).first()
    if checkExisting:
        return f"This account is already registered to {checkExisting.sName}. If this isn't you, please contact your teacher"

    query = Student.query.get(sId)
    if query:
        if query.lineId in [None, "", "None"]:
            query.lineId = newLineId
        else:
            return f"Student {sId} is already registered to a LINE account, please contact your teacher"
        try:
            db.session.commit()
            return f"Welcome {query.sName}!"
        except:
            db.session.rollback()
            return f"Failed to update, please contact your teacher"
    else:
        return f"Student {sId} does not exist, please contact your teacher"


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


def updateAssignment(aId, newId=None, newPrompt=None, newExample=None):
    query = Assignment.query.get(aId)
    olddata = query.__repr__()
    if query:
        if newId:
            query.aId = newId
        if newPrompt:
            query.prompt = newPrompt
        if newExample:
            query.example = newExample
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
