# # import flask related
# from flask import Flask, request, abort
# # import linebot related
# from linebot import (
#     LineBotApi, WebhookHandler
# )
# from linebot.exceptions import (
#     InvalidSignatureError
# )
# from linebot.models import (
#     MessageEvent, TextMessage, TextSendMessage
# )

# # import for database (SQLalchemy)






# # create flask server
# app = Flask(__name__)

# # LINE 聊天機器人的基本資料

# # Johnson linebot message API - Channel access token (from LINE Developer)
# line_bot_api = LineBotApi(os.environ.get("CHANNEL_ACCESS_TOKEN"))
# # Johnson linebot message API - Channel secret
# handler = WebhookHandler(os.environ.get("CHANNEL_SECRET"))


# # connect to database(SQLalchemy)



# # 接收 LINE 的資訊

# @app.route("/callback", methods=['POST'])
# def callback():
#     # get X-Line-Signature header value
#     signature = request.headers['X-Line-Signature']

#     # get request body as text
#     body = request.get_data(as_text=True)
#     app.logger.info("Request body: " + body)

#     # handle webhook body
#     try:
#         # print('receive msg') - Testing
#         handler.handle(body, signature)
#     except InvalidSignatureError:
#         # print("Invalid signature. Please check your channel access token/channel secret.") -Testing
#         abort(400)
#     return 'OK'


# # Our main code (handle msg) 









# # run app
# if __name__ == "__main__":
#     app.run(host='', port=) # change to Heroku port/host

##############################################################################################################################
import os
from datetime import datetime

from flask import Flask, abort, request

# https://github.com/line/line-bot-sdk-python
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("CHANNEL_SECRET"))


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


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    get_message = event.message.text

    # Send To Line
    reply = TextSendMessage(text=f"{get_message}")
    line_bot_api.reply_message(event.reply_token, reply)
