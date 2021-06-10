# 匯入所需模組

import os, time, string
from datetime import datetime

from flask import Flask, render_template, abort, request
from app import *
# https://github.com/line/line-bot-sdk-python
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError

# Audio file handing
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, AudioMessage,
    LocationSendMessage, ImageSendMessage, StickerSendMessage
)

# audio to text (google api)
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


# Linebot 基本設定


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


# Google 語音轉文字 API

def transcribe(wav_path):
    
    # Speech to Text by Google free API
    # language: en-US, zh-TW
    
    
    r = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio = r.record(source)
    try:
        return r.recognize_google(audio, language="en-US")
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
    return None
        


# 接收 LINE 的資訊 / 回傳相同資訊

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    get_message = event.message.text

    # Send To Line
    reply = TextSendMessage(text=f"{get_message}")
    line_bot_api.reply_message(event.reply_token, reply)



# 1. Line錄音回傳功能 (本機端-mp3) 
# 2. 同步mp3音檔轉wav (mp3 to wav)
# 3. Google API寫入文字檔 (txt)

@handler.add(MessageEvent, message=AudioMessage)
def handle_audio(event):

    now = time.strftime("%Y%m%d-%H%M",time.localtime(time.time()))  # 按照時間順序新增檔名
    audio_name = '_recording_hw'
    audio_content = line_bot_api.get_message_content(event.message.id)
    mp3file = now+audio_name+'.mp3'
    wavfile = now+audio_name+'.wav'
    txtfile = now+audio_name+'.txt'

    path='./recording/'+mp3file  # mp3 file path 
    path_wav='./recording_wav/'+wavfile # wav file path
    path_txt='./text/'+txtfile # txt file path

    with open(path, 'wb') as fd:
        for chunk in audio_content.iter_content():
            fd.write(chunk)

    # mp3 to wav converter - ffmpeg in same path
    os.system('ffmpeg -y -i ' + path + ' ' + path_wav + ' -loglevel quiet')


    # audio to txt converter - google api
    audio_filename = "./recording_wav/{now}{audio_name}.wav".format(now=now ,audio_name='_recording_hw')
    text = transcribe(audio_filename)
    # print('Transcribe:', text)
    # line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text))


    # Text result testing 
    if text == None:
        print('Google did not understand the sound, please try again')
    
    else:
        print('Successful Uploading')
        with open(path_txt, 'w') as ft:
            ft.write(text)
            ft.close()
    

#LINE ID, Assignment ID, path, label(string from voice recognition)



# Run app on Heroku server
if __name__ == "__main__":
    app.run(debug=True)
