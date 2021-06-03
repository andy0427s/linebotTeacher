from flask import Flask, render_template, url_for
import sqlite3


connect = sqlite3.connect('question.db', check_same_thread=False)
cursor = connect.cursor()
sentences = cursor.execute("SELECT * FROM Database")
data = cursor.fetchall()

#Start Flask


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('Data.html',id=id,Sentence=Sentence,data=data,
                           page_header="Home")






if __name__ == "__main__":
    app.run(debug=True)
