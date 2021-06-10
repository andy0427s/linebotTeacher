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

import string, random, time, os
# import azure.cognitiveservices.speech as speechsdk

# audio to text (google api)
import speech_recognition as sr

# import azure.cognitiveservices.speech as speechsdk

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


# Google Audio Recognitioner 語音轉文字功能
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

    
# Line錄音回傳功能 / 回傳mp3音檔至本機端 

@handler.add(MessageEvent, message=AudioMessage)
def handle_audio(event):

    now = time.strftime("%Y%m%d-%H%M",time.localtime(time.time()))  # 按照時間順序新增檔名
    audio_name = '_recording_hw'
    audio_content = line_bot_api.get_message_content(event.message.id)
    mp3file = now+audio_name+'.mp3'
    wavfile = now+audio_name+'.wav'
    txtfile = now+audio_name+'.txt'

    path_txt='./text/'+txtfile
    path='./recording/'+mp3file  # mp3 file path 
    path_wav='./recording_wav/'+wavfile # wav file path

    with open(path, 'wb') as fd:
        for chunk in audio_content.iter_content():
            fd.write(chunk)

    # mp3 file converter (to wav file) - ffmpeg in same path
    os.system('ffmpeg -y -i ' + path + ' ' + path_wav + ' -loglevel quiet')


    # audio to txt converter 
    audio_filename = "./recording_wav/{now}{audio_name}.wav".format(now=now ,audio_name='_recording_hw')
    text = transcribe(audio_filename)

    # print('Transcribe:', text)

    # LineBot respond function
    # line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text))


    # Google speech recognition testing
    if text == None:
        print('Google did not understand the sound, please try again')
    
    else:
        print('Successful Uploading')
        with open(path_txt, 'w') as ft:
            ft.write(text)
            ft.close()


# audio convert to text (Linebot)
    
#     os.system('ffmpeg -y -i ' + audio_name_mp3 + ' ' + audio_name_wav + ' -loglevel quiet')
#     text = transcribe(audio_name_wav)
#     print('Transcribe:', text)
#     line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text))

# run app
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=12345)
  

'''
import azure.cognitiveservices.speech as speechsdk

# Creates an instance of a speech config with specified subscription key and service region.
# Replace with your own subscription key and region identifier from here: https://aka.ms/speech/sdkregion
speech_key, service_region = "b8a6c86042ea49df86d9b0ead79eff31", "southcentralus"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

# Creates an audio configuration that points to an audio file.
# Replace with your own audio filename.
audio_filename = './recording_wav/{now}+{audio_name}.wav'.format(now='time.strftime("%Y%m%d-%H%M",time.localtime(time.time()))', audio_name='_recording_hw')
audio_input = speechsdk.audio.AudioConfig(filename=audio_filename)


# Creates a recognizer with the given settings
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

# print("Recognizing first result...")

# Starts speech recognition, and returns after a single utterance is recognized. The end of a
# single utterance is determined by listening for silence at the end or until a maximum of 15
# seconds of audio is processed.  The task returns the recognition text as result. 
# Note: Since recognize_once() returns only a single utterance, it is suitable only for single
# shot recognition like command or query. 
# For long-running multi-utterance recognition, use start_continuous_recognition() instead.
result = speech_recognizer.recognize_once()
result_txt = result.text

# text output 
txtfile = now+audio_name+'.txt'
path_txt='./text/'+txtfile

with open(path_txt, 'w') as ft:
    ft.write(result_txt)
    ft.close()


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
'''


