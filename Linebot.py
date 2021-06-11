# 匯入所需模組

import os, time, string
from datetime import datetime

from flask import Flask, render_template, abort, request
from app import *
# https://github.com/line/line-bot-sdk-python
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError

# Linebot message handing
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, AudioMessage,
    LocationSendMessage, ImageSendMessage, StickerSendMessage
)

# Azure related plug-in

import requests
import base64
import json
import time
import azure.cognitiveservices.speech as speechsdk

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

    path='./recording/'+mp3file  # mp3 file path 
    path_wav='./recording_wav/'+wavfile # wav file path

    with open(path, 'wb') as fd:
        for chunk in audio_content.iter_content():
            fd.write(chunk)

    # mp3 to wav converter - ffmpeg in same path
    os.system('ffmpeg -y -i ' + path + ' ' + path_wav + ' -loglevel quiet')


    # LineBot 回傳功能(if needed)

    # line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text)



    # Azure 語音辨識功能 / 同時產生評分結果


    # Creates an instance of a speech config with specified subscription key and service region.
    # Replace with your own subscription key and region identifier from here: https://aka.ms/speech/sdkregion
    speech_key, service_region = "b8a6c86042ea49df86d9b0ead79eff31", "southcentralus"
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)


    # a common wave header, with zero audio length
    # since stream data doesn't contain header, but the API requires header to fetch format information, so you need post this header as first chunk for each query
    WaveHeader16K16BitMono = bytes([ 82, 73, 70, 70, 78, 128, 0, 0, 87, 65, 86, 69, 102, 109, 116, 32, 18, 0, 0, 0, 1, 0, 1, 0, 128, 62, 0, 0, 0, 125, 0, 0, 2, 0, 16, 0, 0, 0, 100, 97, 116, 97, 0, 0, 0, 0 ])

    def get_chunk(audio_source, chunk_size=1024):
        yield WaveHeader16K16BitMono
        while True:
            time.sleep(chunk_size / 32000) # to simulate human speaking rate
            chunk = audio_source.read(chunk_size)
            if not chunk:
                global uploadFinishTime
                uploadFinishTime = time.time()
                break
            yield chunk

    referenceText = 'Hello my name is Andy'  # input 指定題庫  
    pronAssessmentParamsJson = "{\"ReferenceText\":\"%s\",\"GradingSystem\":\"HundredMark\",\"Dimension\":\"Comprehensive\"}" % referenceText
    pronAssessmentParamsBase64 = base64.b64encode(bytes(pronAssessmentParamsJson, 'utf-8'))
    pronAssessmentParams = str(pronAssessmentParamsBase64, "utf-8")


    # build request
    url = "https://southcentralus.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language=en-us" 
    headers = { 'Accept': 'application/json;text/xml',
                'Connection': 'Keep-Alive',
                'Content-Type': 'audio/wav; codecs=audio/pcm; samplerate=16000',
                'Ocp-Apim-Subscription-Key': speech_key,
                'Pronunciation-Assessment': pronAssessmentParams,
                'Transfer-Encoding': 'chunked',
                'Expect': '100-continue' }

    # create txt file for result storage
    result_name = '_final_result'
    result_file = now+result_name+'.txt'
    path_result='./text/'+result_file # txt file path

    # input wav file 

    audio_filename = "./recording_wav/{now}{audio_name}.wav".format(now=now ,audio_name='_recording_hw')
    audioFile = open(audio_filename, 'rb')

    response = requests.post(url=url, data=get_chunk(audioFile), headers=headers)
    getResponseTime = time.time()
    audioFile.close()

    resultJson = json.loads(response.text)
    # print(json.dumps(resultJson, indent=4))

    # latency = getResponseTime - uploadFinishTime
    # print("Latency = %sms" % int(latency * 1000))


    # Result uploading test

    if resultJson == None:
        print('Azure did not understand the sound, please try again')
    
    else:
        print('Successful Uploading for result')

        #顯示評分結果於txt檔
        with open(path_result, 'w') as fr:
            fr.write(json.dumps(resultJson, indent=4))
            fr.close()


#LINE ID, Assignment ID, path, label(string from voice recognition)

# output = addHomework(assignmentID, LINEID, path_db, label)


# Run app on Heroku server
if __name__ == "__main__":
    app.run(debug=True)
