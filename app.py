from flask import Flask
app = Flask(__name__)

from flask import Flask, render_template, request, redirect, abort
from linebot import  LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os
import time

openai.api_key = os.getenv('OPENAI_API_KEY')
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler1 = WebhookHandler(os.getenv('CHANNEL_SECRET'))

chat_language = os.getenv("INIT_LANGUAGE", default = "zh")
LANGUAGE_TABLE = {
  "zh": "哈囉！",
  "en": "Hello!"
}
# Define the role of the bot
role = 'MIS'

# Define the impersonated role with instructions
impersonated_role = f"""
    From now on, I want you to act as an interviewer. I will be the candidate, and you will ask me the interview questions for the {position} position. 
    I want you to only reply as the interviewer. Do not write all the conservation at once. I want you to only do the interview with me.
    Ask me the questions and wait for my answers. Do not write explanations. 
    Ask me the questions one by one like an interviewer does and wait for my answers. My first sentence is “Hi”
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
    text1=event.message.text
    response = openai.ChatCompletion.create(
        messages=[
            {"role": "system", "content": f"{impersonated_role}"},
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
