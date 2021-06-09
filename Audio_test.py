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
    MessageEvent, TextMessage, TextSendMessage, AudioMessage,
    LocationSendMessage, ImageSendMessage, StickerSendMessage
)

import string
import random

# create flask server
app = Flask(__name__)
# your linebot message API - Channel access token (from LINE Developer)
line_bot_api = LineBotApi('8Ts4CK+L4y61wlM8vH+isb6A/mjewJ2Mo0El/M/oyLN9LRjPtug+5aHn8UHkh9kGpdSF7R4ozJI1N/6+XZJAs1vHPJT+lMfLvDZ8Or1i4dy+MwwP9ezTZvGwNn6dlbqz+Pf3i7LjNsDLjSN0PAaEuwdB04t89/1O/w1cDnyilFU=')
# your linebot message API - Channel secret
handler = WebhookHandler('7a9fd1a414a2222f84906dac60356264')


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'

# handle msg
# import os
# import speech_recognition as sr

# def transcribe(wav_path):
#     '''
#     Speech to Text by Google free API
#     language: en-US, zh-TW
#     '''
    
#     r = sr.Recognizer()
#     with sr.AudioFile(wav_path) as source:
#         audio = r.record(source)
#     try:
#         return r.recognize_google(audio, language="zh-TW")
#     except sr.UnknownValueError:
#         print("Google Speech Recognition could not understand audio")
#     except sr.RequestError as e:
#         print("Could not request results from Google Speech Recognition service; {0}".format(e))
#     return None
    
@handler.add(MessageEvent, message=AudioMessage)
def handle_audio(event):

    audio_name = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(4))
    audio_content = line_bot_api.get_message_content(event.message.id)
    audio_name = audio_name.upper()+'.mp3'
    path='./static/'+audio_name

    with open(path, 'wb') as fd:
        for chunk in audio_content.iter_content():
            fd.write(chunk)
    

    
    # os.system('ffmpeg -y -i ' + name_mp3 + ' ' + name_wav + ' -loglevel quiet')
    # text = transcribe(name_wav)
    # print('Transcribe:', text)
    # line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text))





# run app
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=12345)