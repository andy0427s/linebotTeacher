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

# import for database
import sqlite3

# create flask server
app = Flask(__name__)
# your linebot message API - Channel access token (from LINE Developer)
line_bot_api = LineBotApi('8Ts4CK+L4y61wlM8vH+isb6A/mjewJ2Mo0El/M/oyLN9LRjPtug+5aHn8UHkh9kGpdSF7R4ozJI1N/6+XZJAs1vHPJT+lMfLvDZ8Or1i4dy+MwwP9ezTZvGwNn6dlbqz+Pf3i7LjNsDLjSN0PAaEuwdB04t89/1O/w1cDnyilFU=')
# your linebot message API - Channel secret
handler = WebhookHandler('8f10addcf9b18aafcb17b5766500f17b')

# connect to database
connect = sqlite3.connect('game.db', check_same_thread=False)
cursor = connect.cursor()

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        print('receive msg')
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'

# handle msg
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # get user info & message
    user_id = event.source.user_id
    msg = event.message.text
    user_name = line_bot_api.get_profile(user_id).display_name
    
    # implement reservation
    if msg == '想看遊戲種類':
        games = cursor.execute("SELECT * FROM reservation WHERE user_id IS NULL")
        game_text = '尚可預約遊戲：\n'
        for game in games:
            game_text = game_text + game[1] + '\n'
        line_bot_api.reply_message(event.reply_token, 
                                   TextSendMessage(text = game_text))
    elif msg[0:3] == '想預約':
        game_name = msg[3:]
        games = cursor.execute("SELECT * FROM reservation")
        found = False
        for game in games:
            if game[1] == game_name:
                found = True
                if game[2] is None:
                    cursor.execute("UPDATE reservation \
                                   SET user_id = ? \
                                   WHERE game = ? ", (user_id, game_name))
                    connect.commit()
                    line_bot_api.reply_message(event.reply_token, 
                                   TextSendMessage(text = '已為您預約完成：' + game_name))
                else:
                    line_bot_api.reply_message(event.reply_token, 
                                   TextSendMessage(text = '此遊戲已被預約！抱歉'))
        if found == False:
            line_bot_api.reply_message(event.reply_token, 
                                   TextSendMessage(text = '並沒有此款遊戲'))
    elif msg == '想取消預約':
        games = cursor.execute("SELECT * FROM reservation where user_id = ?", (user_id,))
        canceled_game_name = []
        found = False
        for game in games:
            canceled_game_name.append(game[1])
        
        for game in canceled_game_name:
            cursor.execute("UPDATE reservation \
                           SET user_id = ? \
                           WHERE game = ? ", (None, game))
            connect.commit()
            found =  True
        if found == True:
            line_bot_api.reply_message(event.reply_token, 
                                       TextSendMessage(text = '已為您取消預約'))
    else:
        line_bot_api.reply_message(event.reply_token, 
                                   TextSendMessage(text = '親愛的' + user_name + '您好！\n請問需要什麼樣的服務？'))

# run app
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=12345)