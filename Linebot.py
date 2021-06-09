# 匯入所需模組


import os
from datetime import datetime

from flask import Flask, render_template, abort, request
from app import app, db, Student, Homework, Assignment
# https://github.com/line/line-bot-sdk-python
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# Audio recongnition
import speech_recognition as sr



# import for database (SQLalchemy)


# LINE 聊天機器人的基本資料

# app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("CHANNEL_SECRET"))


# 瀏覽器介面for Teacher to review database (GiAI)


######
# testing if db changes can work from here
@app.route('/addone')
def addOne():
    # add one student
    s1 = Student(sId=99, sName="lineman", lineId="f814h")
    db.session.add(s1)
    db.session.commit()
    return "success!"
#####


# Linebot part


@app.route("/callback", methods=["GET", "POST"])
def callback():

    if request.method == "GET":
        return "Hello Heroku"

    if request.method == "POST":
        signature = request.headers["X-Line-Signature"]
        body = request.get_data(as_text=True)

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            abort(400)

        return "OK"


# 接收 LINE 的資訊 / 回傳相同資訊

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    get_message = event.message.text

    # Send To Line
    reply = TextSendMessage(text=f"{get_message}")
    line_bot_api.reply_message(event.reply_token, reply)






# Run app on Heroku server
if __name__ == "__main__":
    app.run(debug=True)
