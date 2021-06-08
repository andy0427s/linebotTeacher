# 匯入所需模組

import os
from datetime import datetime

from flask import Flask, abort, request

# https://github.com/line/line-bot-sdk-python
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage


# import for database (SQLalchemy)



# LINE 聊天機器人的基本資料

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("CHANNEL_SECRET"))


# 瀏覽器介面for Teacher to review (if needed)

@app.route('/rec', methods=['GET', 'POST'])
def get_file():
    if request.method == "GET":
        return "Hello Teacher Andy"
        # return render_template('file.html', page_header="upload hand write picture")

    # elif request.method == "POST":
    #     file = request.files['file']
    #     if file:
    #         filename = str(uuid.uuid4())+"_"+file.filename
    #         file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
    #         predict = model.recog_digit(filename)
    #     return render_template('recog_result.html', page_header="hand writing digit recognition", predict = predict, src = url_for('static', filename=f'uploaded/{filename}'))


# Linebot part 

@app.route("/", methods=["GET", "POST"])
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



# Run app on Heroku
if __name__ == "__main__":
    app.run(debug=True)
