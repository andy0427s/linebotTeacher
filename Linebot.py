# 匯入所需模組

import os, time, string
from datetime import datetime

from flask import Flask, render_template, abort, request
from app import *
# https://github.com/line/line-bot-sdk-python
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError

# Linebot message handing
from linebot.models import *
from linebot.models import (
    MessageEvent,
    TextSendMessage,
    TemplateSendMessage,
    ButtonsTemplate,
    MessageTemplateAction,
    PostbackEvent,
    PostbackTemplateAction
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

'''
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    get_message = event.message.text

    # Send To Line
    # reply = TextSendMessage(text=f"{get_message}")
    # line_bot_api.reply_message(event.reply_token, reply)
'''

# Linebot 功能列(文字跟語音)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    msg = event.message.text
    msg = msg.encode('utf-8') 
    page_keyword = ['hi', 'back', 'main','Back','Main','Hi']
    questions = str(list(range(101)))

    # Send To Line
    # reply = TextSendMessage(text=f"{get_message}")
    # line_bot_api.reply_message(event.reply_token, reply)

    # if event.message.text == "文字":
    #     line_bot_api.reply_message(event.reply_token,TextSendMessage(text=event.message.text))

   # LineBot 主選單
    if event.message.text in page_keyword:
        line_bot_api.reply_message(event.reply_token, TemplateSendMessage(alt_text='目錄 template',
        template=ButtonsTemplate(
            title='歡迎使用英語口說Linebot',
            text='請選擇服務：',
            thumbnail_image_url='https://powerlanguage.net/wp-content/uploads/2019/09/welcome-300x129.jpg', #圖片
            actions=[
                PostbackTemplateAction(
                    label='上傳錄音',
                    text='上傳錄音',
                    data='A&上傳錄音'
                ),
                MessageTemplateAction(
                    label='查看題庫',
                    text='查看題庫',
                    data='B&查看題庫'
                ),
                MessageTemplateAction(
                    label='功能3',
                    text='功能3',
                    data='C&功能3'
                ),
                MessageTemplateAction(
                    label='功能4',
                    text='功能4',
                    data='D&功能5'
                )
            ])))

    # 學生選擇題目，需要和Azure指定題庫進行綁定
    elif event.message.text in questions:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"確認題目編號，請開始錄音!\n或輸入'back'返回主選單"))
        saveid_hw = event.message.text # 題目編號for DB

        while False:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"無此題目編號，請重新輸入assignID\n或輸入'back'返回主選單"))
            break


# 主頁面-'上傳錄音'功能/ 學生選擇題目編號

@handler.add(PostbackEvent)
def handle_post_message(event):
# can not get event text

    if event.postback.data[0:1] == "A":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請輸入題庫assign ID：'))



# Line錄音回傳功能 / 回傳mp3/wav音檔至本機端 

@handler.add(MessageEvent, message=AudioMessage)
def handle_audio(event):

    now = time.strftime("%Y%m%d-%H%M",time.localtime(time.time()))  # 按照時間順序新增檔名
    audio_name = '_recording_hw'
    audio_content = line_bot_api.get_message_content(event.message.id)
    mp3file = now+audio_name+'.mp3'
    wavfile = now+audio_name+'.wav'
    txtfile = now+audio_name+'.txt'

    path='./recording/'+mp3file  # mp3 file path for DB
    path_wav='./recording_wav/'+wavfile # wav file path for DB
    path_txt='./text/'+txtfile # txt file path

    with open(path, 'wb') as fd:
        for chunk in audio_content.iter_content():
            fd.write(chunk)

    # mp3 to wav converter - ffmpeg in same path
    os.system('ffmpeg -y -i ' + path + ' ' + path_wav + ' -loglevel quiet')

    

    '''
    # audio to txt converter 
    audio_filename = "./recording_wav/{now}{audio_name}.wav".format(now=now ,audio_name='_recording_hw')
    
    text = transcribe(audio_filename)
  
    # print('Transcribe:', text)
    # line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text))

    if text == None:
        print('Google did not understand the sound, please try again')
    
    else:
        print('Successful Uploading for TTS')

        with open(path_txt, 'w') as ft:
            ft.write(text)
            ft.close()

    '''
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

    referenceText = 'Hello my name is Andy'  # input 指定題庫 from DB
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
    path_result='./text/'+result_file # result file path for DB

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


    #show result in txt file

    if resultJson == None:
        print('Azure did not understand the sound, please try again')
        line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text='辨認音檔失敗，請重新錄製，或輸入"back"返回主選單'))
        os.remove(path)
        os.remove(path_wav)

    else:
        print('Successful Uploading for result')
        line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text='辨認音檔成功，可以繼續錄製，或輸入"back"返回主選單'))
        with open(path_result, 'w') as fr:
            fr.write(json.dumps(resultJson, indent=4))
            fr.close()


# add txt file(audio) to database 

'''
@app.route('/addtest')
def addTest():
    addHomework(assignmentID, LINEID, path, label)
'''


# audio convert to text (Linebot)
    
#     os.system('ffmpeg -y -i ' + audio_name_mp3 + ' ' + audio_name_wav + ' -loglevel quiet')
#     text = transcribe(audio_name_wav)
#     print('Transcribe:', text)
#     line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text))

# run app
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=12345)
