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

import (string, random, time, os)
import azure.cognitiveservices.speech as speechsdk



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

    
# Line錄音回傳功能 / 回傳mp3音檔至本機端 

@handler.add(MessageEvent, message=AudioMessage)
def handle_audio(event):

    now = time.strftime("%Y-%m-%d-%H-%M",time.localtime(time.time()))  # 按照時間順序新增檔名
    audio_name = '_recording_hw'
    audio_content = line_bot_api.get_message_content(event.message.id)
    audio_name = now+audio_name+'.mp3'
    wavfile = now+audio_name+'.wav'


    path='./recording/'+audio_name  # mp3 file path 
    path_wav='./recording_wav/'+wavfile # wav file path

    with open(path, 'wb') as fd:
        for chunk in audio_content.iter_content():
            fd.write(chunk)

# mp3 file converter (to wav file) - ffmpeg in same path
    os.system('ffmpeg -y -i ' + path + ' ' + path_wav + ' -loglevel quiet')



# run app
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=12345)


'''

speech_key, service_region = "c6d717109b46431e9ae8f4be76592b0f", "southcentralus"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

# Creates an audio configuration that points to an audio file.
# Replace with your own audio filename.
audio_filename = "narration.wav"
audio_input = speechsdk.audio.AudioConfig(filename=audio_filename)

# Creates a recognizer with the given settings
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

print("Recognizing first result...")

esult = speech_recognizer.recognize_once()

# Checks result.
if result.reason == speechsdk.ResultReason.RecognizedSpeech:
    print("Recognized: {}".format(result.text))
elif result.reason == speechsdk.ResultReason.NoMatch:
    print("No speech could be recognized: {}".format(result.no_match_details))
elif result.reason == speechsdk.ResultReason.Canceled:
    cancellation_details = result.cancellation_details
    print("Speech Recognition canceled: {}".format(cancellation_details.reason))
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
        print("Error details: {}".format(cancellation_details.error_details))



