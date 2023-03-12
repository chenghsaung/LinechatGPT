import os
import re
import openai
from flask import Flask, redirect, render_template, request, url_for, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")
line_bot_api = LineBotApi(os.getenv("LINE_API_KEY"))
handler = WebhookHandler(os.getenv("LINE_CHANEL_SECRET"))

@app.route("/", methods=("GET", "POST"))
def root():
    return "Build web success!"


# 監聽所有來自 /callback 的 Post Request
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
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    
    response = openai.Completion.create(
            model="text-davinci-002",
            prompt=event.message.text,
            temperature=0.6,
        )
    message_init = TextSendMessage(text=response.choices[0].text)
    line_bot_api.reply_message(event.reply_token, message_init)

if __name__ == '__main__':
    app.run(debug=True, port=33507)