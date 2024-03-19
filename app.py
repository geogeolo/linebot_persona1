from flask import Flask, render_template, request, redirect, abort
from linebot import  LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os
import time

app = Flask(__name__)
counter = 1
openai.api_key = os.getenv('OPENAI_API_KEY')
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler1 = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# Define the position of the job
position = 'MIS'

# Define the impersonated role with instructions
impersonated_role = f"""
    From now on, I want you to act as a dream interpreter. 
    I will give you descriptions of my dreams, and you will provide interpretations based on the symbols and themes present in the dream. 
    Do not provide personal opinions or assumptions about the dreamer. 
    Provide only factual interpretations based on the information given.
    YOU ARE NOT AN AI MODEL!
"""

@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler1.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler1.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global counter
    counter += 1
    return str(counter)

    text1=event.message.text
    response = openai.ChatCompletion.create(
        messages=[
            {"role": "system", "content": f"Chat only in zh-TW, {impersonated_role}"},
            {"role": "user", "content": text1}
        ],
        model="gpt-3.5-turbo-0125",
        temperature = 0.5,
    )
    try:
        ret = response['choices'][0]['message']['content'].strip() 
    except:
        ret = '發生錯誤！'
        
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=ret))

if __name__ == '__main__':
    app.run()
