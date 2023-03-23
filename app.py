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

channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
channel_secret = os.getenv('LINE_CHANNEL_SECRET',  None)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

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

button_template_message =ButtonsTemplate(
                            thumbnail_image_url="https://i.imgur.com/i8tEmlY.jpg",
                            title='哼！', 
                            text='選擇動作',
                            ratio="1.51:1",
                            image_size="cover",
                            actions=[
#                                PostbackTemplateAction 點擊選項後，
#                                 除了文字會顯示在聊天室中，
#                                 還回傳data中的資料，可
#                                 此類透過 Postback event 處理。
                                PostbackTemplateAction(
                                    label='填單', 
                                    text='填單',
                                    data='action=buy&itemid=1'
                                ),
                                URITemplateAction(
                                    label='chatGPT web chat', uri='https://chat.openai.com/chat'
                                ),
                                URITemplateAction(
                                    label='chatGPT API 文件', uri='https://platform.openai.com/docs/api-reference'
                                ),
                                URITemplateAction(
                                    label='chatGPT examples', uri='https://platform.openai.com/examples'
                                )
                            ]
                        )

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == "Hi":
        line_bot_api.reply_message(event.reply_token, TemplateSendMessage(alt_text="Template Example", template=button_template_message))
        return
    response = openai.Completion.create(
            model="text-davinci-002",
            prompt=event.message.text,
            temperature=0.6,
            max_tokens=300,
            presence_penalty=0,
            frequency_penalty=0
        )
    print(f"response=\n{response}")
    message_init = TextSendMessage(text=response.choices[0].text)
    line_bot_api.reply_message(event.reply_token, message_init)

if __name__ == '__main__':
    app.run(debug=True, port=33507)