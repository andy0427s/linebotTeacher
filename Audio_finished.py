# import flask related
from flask import Flask, request, abort

# import Database
from flask_sqlalchemy import SQLAlchemy
from app import *

# import linebot related
from linebot import (
    LineBotApi, WebhookHandler, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
import boto3
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

# from linebot.models import (
#     MessageEvent, TextMessage, TextSendMessage, AudioMessage,
#     LocationSendMessage, ImageSendMessage, StickerSendMessage,
#     TemplateSendMessage, ButtonsTemplate, MessageTemplateAction
# )


# import urllib

import string
import time
import os
# import azure.cognitiveservices.speech as speechsdk


# Azure related plug-in

import requests
import base64
import json
import time
import azure.cognitiveservices.speech as speechsdk


# 題目匯入 for 本機端

import csv


# print(data)

# create flask server
# app = Flask(__name__)
# your linebot message API - Channel access token (from LINE Developer)
# line_bot_api = LineBotApi('8Ts4CK+L4y61wlM8vH+isb6A/mjewJ2Mo0El/M/oyLN9LRjPtug+5aHn8UHkh9kGpdSF7R4ozJI1N/6+XZJAs1vHPJT+lMfLvDZ8Or1i4dy+MwwP9ezTZvGwNn6dlbqz+Pf3i7LjNsDLjSN0PAaEuwdB04t89/1O/w1cDnyilFU=')
# your linebot message API - Channel secret
# handler = WebhookHandler('7a9fd1a414a2222f84906dac60356264')

# Heroku deployment
line_bot_api = LineBotApi(os.environ.get("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("CHANNEL_SECRET"))


@app.route("/callback", methods=['GET', 'POST'])
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


'''
# 題庫匯入 (本機端) 
with open('./dataset_table.csv', newline='') as f:  # path for 題庫
    reader = csv.reader(f)
    data = list(reader)  # Dataset from OS

num = 0
sample = []  # list of (My name is Andy, Good Morning.....)
index = []  # list of (1, 2, 3......)
# list of value for Linebot reply (1: My name is Andy, 2: Good Morning....)
line_sample = []

# 選擇列出多少題庫於LineBot上
for i in data:
    num += 1
    sample.append(i[1])
    index.append(i[0])
    new = i[0]+':'+' ' + i[1]  # Combine list of index & list of assignment
    line_sample.append(new)
    if num == 30:  # Select 30 samples from dataset
        break

# Linebot 回覆本機題庫結果
final_sample = "".join(line_sample)
'''


# 題庫匯入(DB端)

all_assign = Assignment.query.all()

clean_view_list = []
clean_view = ""
saID_list = []
ssen_list = []

for z in all_assign:
    saID = str(z.aId)
    ssen = str(z.prompt)
    clean_view = saID + "." + " " + ssen
    # print(clean_view)
    clean_view_list.append(clean_view)
    saID_list.append(saID)
    ssen_list.append(ssen)
    # print(saID_list, ssen_list)

final_sample = "\n".join(clean_view_list)


# 指定題庫同步功能/依照學生選擇的題目，想對應地匯入指定題庫至Azure進行辨識 (DB端)

azure_text="" #Reference txt for Azure
saveid_hw=""# Assign ID for DB 

user_id=""
path_wav=""

def handle_assignmentID(user_input):
    # global azure_text
    # global saveid_hw
    saveid_hw = ""
    # 對比本機題庫內的Assign ID
    for a , b in zip(saID_list, ssen_list): 
        if user_input == a:
            azure_text = b
            saveid_hw = a   
            break
    print(user_input)
    print(saveid_hw)
    # 儲存對比結果(句子內容) & 指定題庫id
    return azure_text , saveid_hw 

'''

#指定題庫同步功能/依照學生選擇的題目，想對應地匯入指定題庫至Azure進行辨識 (本機端)

azure_text="" #Reference txt for Azure
saveid_hw="" # Assign ID for DB 
user_id=""
path_wav=""

def handle_assignmentID(user_input):
    global azure_text, saveid_hw
    # 對比本機題庫內的Assign ID
    for a in data: 
        if user_input == a[0]:
            azure_text = a[1]
            saveid_hw = a[0]   
            break

    # 儲存對比結果(句子內容) & 指定題庫id
    return azure_text , saveid_hw 

'''

score_view = ""
# score_view = ""


def handle_result(o1, o2, o3, o4, o5):
    global score_view
    score_view = "題目: " + o1 + '\n' + "精確度: " + o2 + '\n' + \
        "流暢度: " + o3 + '\n' + "完整度: " + o4 + '\n' + "綜合分數: " + o5[:5]
    print(score_view)
    return score_view  # Result for DB



# Linebot 功能列(文字跟語音)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global user_id
    global saveid_hw
    global azure_text
    # 產生user ID
    user_id = event.source.user_id  # student id for DB
    user_name = line_bot_api.get_profile(
        user_id).display_name  # student name for DB (Optional)
    msg = event.message.text
    msg = msg.encode('utf-8')
    page_keyword = ['hi', 'back', 'main', 'Back',
                    'Main', 'Hi']  # shortcut for Linebot 主選單
    result_keyword = 'result'
    # questions = str(list(range(101)))  # 題目編號for本機端

    if event.message.text.lower() == "status":
        # let the student check if LINE ID is registered to a Student ID
        checkExisting = Student.query.filter_by(lineId=user_id).first()
        # print(checkExisting)
        if not checkExisting:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(
                text=f"Your account is currently not associated with a student, please register your account to your student ID (ex: 'register 1')"))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(
                text=f"Hello {checkExisting.sName}!"))

    if event.message.text.lower()[0:8] == "register":
        # let student register LINE ID to Student ID
        try:
            student_id = int(msg[8:])
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(
                text=f"please enter a valid ID (ex: 'register 1')"))
        else:
            feedback = registerStudent(student_id, newLineId=user_id)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(
                text=f"{feedback}"))

   # LineBot 主選單
    if event.message.text in page_keyword:
        line_bot_api.reply_message(event.reply_token, TemplateSendMessage(alt_text='目錄 template',
                                                                          template=ButtonsTemplate(
                                                                              title='歡迎使用英語口說Linebot',
                                                                              text='請選擇服務：',
                                                                              thumbnail_image_url='https://powerlanguage.net/wp-content/uploads/2019/09/welcome-300x129.jpg',  # 圖片
                                                                              actions=[
                                                                                  PostbackTemplateAction(
                                                                                      label='上傳錄音',
                                                                                      text='上傳錄音',
                                                                                      data='A&上傳錄音'
                                                                                  ),
                                                                                  PostbackTemplateAction(
                                                                                      label='查看題庫',
                                                                                      text='查看題庫',
                                                                                      data='G&查看題庫'
                                                                                  ),
                                                                                  MessageTemplateAction(
                                                                                      label='功能3',
                                                                                      text='功能3',
                                                                                      data='C&功能3'
                                                                                  ),
                                                                                  MessageTemplateAction(
                                                                                      label='功能4',
                                                                                      text='功能4',
                                                                                      data='D&功能4'
                                                                                  )
                                                                              ])))

    '''
    # 學生選擇題目 from 本機端

    if event.message.text.isdigit():
        if event.message.text in questions:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(
                text=f"確認題目編號，請開始錄音!或按下方按鈕返回主選單"))

            # call 題目連結功能
            handle_assignmentID(event.message.text)

        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(
                text=f"無此題目編號，請重新輸入assignID，或按下方按鈕返回主選單"))

    return user_id
    
    '''

    # 學生選擇題目from DB

    if event.message.text.isdigit():
        if event.message.text in saID_list:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"確認題目編號，請開始錄音!\n或按下方按鈕返回主選單"))

            # call 題目連結功能
            azure_text , saveid_hw  = handle_assignmentID(event.message.text)

        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"無此題目編號，請重新輸入assignID，或按下方按鈕返回主選單"))

    return user_id


    if event.message.text in result_keyword:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(
            text='請查看評分結果:' + '\n' + '{score_view}'.format(score_view=score_view)))

# 主選單按鈕所有功能


@handler.add(PostbackEvent)
def handle_post_message(event):
    # can not get event text

    # call 主選單-錄音功能
    if event.postback.data[0:1] == "A":
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='請輸入題庫assign ID：'))

    '''
    # call 主選單-題庫功能-本機端
    if event.postback.data[0:1] == "G":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(
            text='本次題庫如下:' + '' + '{final_sample}'.format(final_sample=final_sample)))
    '''

    # call 主選單-題庫功能-DB端 
    if event.postback.data[0:1] == "G":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='本次題庫如下:'+ '\n' + '{final_sample}'.format(final_sample=final_sample)))

    # call Richmenu-主選單功能
    elif event.postback.data[0:1] == "E":
        line_bot_api.reply_message(event.reply_token, TemplateSendMessage(alt_text='目錄 template',
                                                                          template=ButtonsTemplate(
                                                                              title='歡迎使用英語口說Linebot',
                                                                              text='請選擇服務：',
                                                                              thumbnail_image_url='https://powerlanguage.net/wp-content/uploads/2019/09/welcome-300x129.jpg',  # 圖片
                                                                              actions=[
                                                                                  PostbackTemplateAction(
                                                                                      label='上傳錄音',
                                                                                      text='上傳錄音',
                                                                                      data='A&上傳錄音'
                                                                                  ),
                                                                                  PostbackTemplateAction(
                                                                                      label='查看題庫',
                                                                                      text='查看題庫',
                                                                                      data='G&查看題庫'
                                                                                  ),
                                                                                  MessageTemplateAction(
                                                                                      label='功能3',
                                                                                      text='功能3',
                                                                                      data='C&功能3'
                                                                                  ),
                                                                                  MessageTemplateAction(
                                                                                      label='功能4',
                                                                                      text='功能4',
                                                                                      data='D&功能4'
                                                                                  )
                                                                              ])))

    # call Richmenu-評分功能
    elif event.postback.data[0:1] == "F":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(
            text='請查看評分結果:' + '\n' + '{score_view}'.format(score_view=score_view)))


# Line錄音回傳功能 / 回傳mp3音檔至本機端

@handler.add(MessageEvent, message=AudioMessage)
def handle_audio(event):

    now = time.strftime(
        "%Y%m%d-%H%M", time.localtime(time.time()))  # 按照時間順序新增檔名
    audio_name = '_hw'
    audio_content = line_bot_api.get_message_content(event.message.id)
    mp3file = now+audio_name+'.mp3'
    wavfile = now+audio_name+'.wav'
    txtfile = now+audio_name+'.txt'

    path = './recording/'+mp3file  # mp3 file path for DB
    path_wav = './recording_wav/'+wavfile  # wav file path for DB
    path_txt = './text/'+txtfile  # txt file path

    with open(path, 'wb') as fd:
        for chunk in audio_content.iter_content():
            fd.write(chunk)

    # mp3 to wav converter - ffmpeg in same path
    os.system('ffmpeg -y -i ' + path + ' ' + path_wav + ' -loglevel quiet')


# Azure 語音辨識功能 / 同時產生評分結果

    # Creates an instance of a speech config with specified subscription key and service region.
    # Replace with your own subscription key and region identifier from here: https://aka.ms/speech/sdkregion
    speech_key, service_region = "b8a6c86042ea49df86d9b0ead79eff31", "southcentralus"
    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key, region=service_region)

    # a common wave header, with zero audio length
    # since stream data doesn't contain header, but the API requires header to fetch format information, so you need post this header as first chunk for each query
    WaveHeader16K16BitMono = bytes([82, 73, 70, 70, 78, 128, 0, 0, 87, 65, 86, 69, 102, 109, 116, 32, 18,
                                   0, 0, 0, 1, 0, 1, 0, 128, 62, 0, 0, 0, 125, 0, 0, 2, 0, 16, 0, 0, 0, 100, 97, 116, 97, 0, 0, 0, 0])

    def get_chunk(audio_source, chunk_size=1024):
        yield WaveHeader16K16BitMono
        while True:
            time.sleep(chunk_size / 32000)  # to simulate human speaking rate
            chunk = audio_source.read(chunk_size)
            if not chunk:
                global uploadFinishTime
                uploadFinishTime = time.time()
                break
            yield chunk

    referenceText = azure_text  # 依照學生輸入，匯入指定題庫進行辨識(DB端)
    # referenceText = 'Hello my name is Andy'  # 依照學生輸入，匯入指定題庫進行辨識(DB端)

    # 如要show個別單字 \"Granularity\":\"FullText\"
    pronAssessmentParamsJson = "{\"ReferenceText\":\"%s\",\"GradingSystem\":\"HundredMark\",\"Dimension\":\"Comprehensive\",\"Granularity\":\"FullText\"}" % referenceText
    pronAssessmentParamsBase64 = base64.b64encode(
        bytes(pronAssessmentParamsJson, 'utf-8'))
    pronAssessmentParams = str(pronAssessmentParamsBase64, "utf-8")

    # build request
    url = "https://southcentralus.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language=en-us"
    headers = {'Accept': 'application/json;text/xml',
               'Connection': 'Keep-Alive',
               'Content-Type': 'audio/wav; codecs=audio/pcm; samplerate=16000',
               'Ocp-Apim-Subscription-Key': speech_key,
               'Pronunciation-Assessment': pronAssessmentParams,
               'Transfer-Encoding': 'chunked',
               'Expect': '100-continue'}

    # create txt file for result storage
    result_name = '_final_result'
    result_file = now+result_name+'.txt'
    path_result = './text/'+result_file  # result file path for DB

    # input wav file

    audio_filename = "./recording_wav/{now}{audio_name}.wav".format(
        now=now, audio_name='_hw')
    audioFile = open(audio_filename, 'rb')

    response = requests.post(
        url=url, data=get_chunk(audioFile), headers=headers)
    getResponseTime = time.time()
    audioFile.close()

    resultJson = json.loads(response.text)  # List of dict [{}]

    finalresult = resultJson['NBest'][0]  # for DB outout (dict format)
    value1 = str.capitalize(finalresult['Lexical'])
    value2 = str(finalresult['AccuracyScore'])
    value3 = str(finalresult['FluencyScore'])
    value4 = str(finalresult['CompletenessScore'])
    value5 = str(finalresult['PronScore'])

    # print(json.dumps(resultJson, indent=4))

    # latency = getResponseTime - uploadFinishTime
    # print("Latency = %sms" % int(latency * 1000))

    # show result in txt file

    if resultJson == None:
        print('Azure did not understand the sound, please try again')
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='辨認音檔失敗，請重新錄製，或按下方按鈕返回主選單'))
        os.remove(path)
        os.remove(path_wav)

    else:
        print('Successful Uploading for result')
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='辨認音檔成功，可以繼續錄製，或按下方按鈕查看評分結果'))

        # only for testing
        # print(value1, value2, value3, value4, value5)

        # call 分數字串處理 function
        handle_result(value1, value2, value3, value4, value5)

        # Testing part
        # print(int(saveid_hw),user_id,path_wav,score_view) 
        # print(type(int(saveid_hw)),type(user_id),type(path_wav),type(score_view))

        # aId = 2 <class 'int'>
        # lineId = U0be2f158b710af92ccb62fa85a9b9e52 <class 'str'>
        # file = ./recording_wav/20210614-2128_recording_hw.wav <class 'str'>
        # label = I have to go to sleep. <class 'str'>


        with open(path_result, 'w') as fr:
            # Only 擷取score部分的資訊 / 匯入json至os txt檔
            fr.write(json.dumps(resultJson['NBest'][0], indent=4))
            fr.close()

        # Output Linebot訊息內容 to DB (Most important part!)
        addHomework(int(saveid_hw), user_id, "https://engscoreaud.s3.amazonaws.com/"+mp3file, score_view)

        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

        def upload_aws(file, bucket, s3file):
            s3 = boto3.client('s3',
                              aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key)
            s3.upload_file(file, bucket, s3file, ExtraArgs={
                "ContentType": "mp3"
            })
            print('uploaded')
            return True

        uploaded = upload_aws(path, "engscoreaud", mp3file)
    return path_wav, finalresult, resultJson, value1, value2, value3, value4, value5

# run app on Ngrok (本機端)
# if __name__ == "__main__":
#     app.run(host='127.0.0.1', port=12345)

# run app on Heroku (Server端)

if __name__ == "__main__":
    app.run(debug=True)
