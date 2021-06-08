# import flask related
from flask import Flask, request, abort
# import linebot related
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage
)

# import for database (SQLalchemy)






# create flask server
app = Flask(__name__)

# LINE 聊天機器人的基本資料

# Johnson linebot message API - Channel access token (from LINE Developer)
line_bot_api = LineBotApi(os.environ.get("CHANNEL_ACCESS_TOKEN"))
# Johnson linebot message API - Channel secret
handler = WebhookHandler(os.environ.get("CHANNEL_SECRET"))


# connect to database(SQLalchemy)



# 接收 LINE 的資訊

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        # print('receive msg') - Testing
        handler.handle(body, signature)
    except InvalidSignatureError:
        # print("Invalid signature. Please check your channel access token/channel secret.") -Testing
        abort(400)
    return 'OK'


# Our main code (handle msg) 









# run app
if __name__ == "__main__":
    app.run(host='', port=) # change to Heroku port/host

